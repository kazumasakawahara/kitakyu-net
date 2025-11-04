# -*- coding: utf-8 -*-
"""
Service coordination using LLM and Neo4j facility search.
"""
import json
from typing import Dict, Any, List
from loguru import logger

from backend.llm.ollama_client import get_ollama_client
from backend.neo4j.client import get_neo4j_client


SERVICE_SUGGESTION_PROMPT = """あなたは計画相談支援専門員です。
以下の利用者情報と目標から、最適なサービスを提案してください。

【重要】このシステムは主に知的障害・精神障害のある方を対象としています。
身体障害のみの方は例外的なケースです。

【利用者情報】
年齢: {age}歳
障害種別: {disability_type}
障害支援区分: {support_level}
生活状況: {living_situation}

【アセスメント結果】
本人の希望: {preferences}
分析されたニーズ: {analyzed_needs}
強み: {strengths}
課題: {challenges}

【目標】
{goals}

【提案するサービス種別の候補】
{available_service_types}

以下の観点でサービスを提案してください:
1. 目標達成に必要なサービス種別
2. 週当たりの利用頻度（週1回、週3回など）
3. 優先順位（必須、推奨、オプション）
4. サービスを選んだ理由

JSON形式で返答してください。JSONのみを返し、他の説明は含めないでください。

{{
  "service_needs": [
    {{
      "service_type": "サービス種別",
      "frequency": "週3回",
      "priority": "必須",
      "reason": "このサービスが必要な理由",
      "duration_hours": 4.0,
      "preferred_time": "午前",
      "special_requirements": "特別な要件があれば"
    }}
  ]
}}
"""


FACILITY_MATCHING_PROMPT = """以下の条件に最適な事業所を評価してください。

【重要】このシステムは主に知的障害・精神障害のある方を対象としています。
評価時は、認知面・精神面への支援体制、コミュニケーション方法、環境調整を重視してください。

【利用者の条件】
- 障害種別: {disability_type}
- 支援区分: {support_level}
- 希望: {preferences}
- 居住地: {district}

【事業所情報】
{facility_info}

【評価基準】
1. 対応可能性（障害種別、支援区分、支援体制）
2. 希望との適合性
3. 通所の利便性（同じ区内か）
4. 空き状況

スコア（0.0-1.0）と推薦理由を返してください。

{{
  "match_score": 0.85,
  "reasons": ["理由1", "理由2", "理由3"],
  "concerns": ["懸念点1"]
}}
"""


class ServiceCoordinator:
    """Coordinate services using LLM and facility search."""

    def __init__(self):
        """Initialize service coordinator."""
        self.llm = get_ollama_client()
        self.db = get_neo4j_client()
        logger.info("Service coordinator initialized")

    def suggest_services(
        self, user_data: Dict[str, Any], assessment_data: Dict[str, Any], goals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest optimal services based on user needs and goals.

        Args:
            user_data: User profile information
            assessment_data: Assessment results
            goals: List of goals

        Returns:
            List of service suggestions
        """
        logger.info("Suggesting services based on goals...")

        # Get available service types from database
        available_types = self._get_available_service_types()

        # Format goals for prompt
        goals_text = "\n".join(
            [f"- {goal.get('goal_type', '目標')}: {goal['goal_text']}" for goal in goals]
        )

        # Build prompt
        prompt = SERVICE_SUGGESTION_PROMPT.format(
            age=user_data.get("age", "不明"),
            disability_type=user_data.get("disability_type", ""),
            support_level=user_data.get("support_level", ""),
            living_situation=user_data.get("living_situation", ""),
            preferences=", ".join(assessment_data.get("preferences", [])),
            analyzed_needs=", ".join(assessment_data.get("analyzed_needs", [])),
            strengths=", ".join(assessment_data.get("strengths", [])),
            challenges=", ".join(assessment_data.get("challenges", [])),
            goals=goals_text,
            available_service_types=", ".join(available_types),
        )

        try:
            response = self.llm.generate(
                prompt=prompt, temperature=0.3, max_tokens=2048
            )

            # Parse response
            suggestions = self._parse_response(response)
            service_needs = suggestions.get("service_needs", [])

            logger.success(f"Suggested {len(service_needs)} services")
            return service_needs

        except Exception as e:
            logger.error(f"Service suggestion failed: {e}")
            raise

    def match_facilities(
        self, service_type: str, user_data: Dict[str, Any], assessment_data: Dict[str, Any], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find and rank facilities that match service requirements.

        Args:
            service_type: Type of service needed
            user_data: User profile
            assessment_data: Assessment results
            limit: Max facilities to return

        Returns:
            List of matched facilities with scores
        """
        logger.info(f"Matching facilities for service: {service_type}")

        # Search facilities by service type
        facilities = self.db.search_facilities(
            service_type=service_type,
            district=user_data.get("district"),  # Prefer same district
            limit=limit * 2,  # Get more for scoring
        )

        if not facilities:
            logger.warning(f"No facilities found for service type: {service_type}")
            return []

        # Score each facility
        scored_facilities = []
        for facility in facilities[:limit]:  # Limit LLM calls
            try:
                score_data = self._score_facility(facility, user_data, assessment_data)
                scored_facilities.append({
                    **facility,
                    "match_score": score_data["match_score"],
                    "match_reasons": score_data["reasons"],
                    "match_concerns": score_data.get("concerns", []),
                })
            except Exception as e:
                logger.warning(f"Failed to score facility {facility.get('name')}: {e}")
                # Add with default score
                scored_facilities.append({
                    **facility,
                    "match_score": 0.5,
                    "match_reasons": ["自動評価失敗"],
                    "match_concerns": [],
                })

        # Sort by score
        scored_facilities.sort(key=lambda x: x["match_score"], reverse=True)

        logger.success(f"Matched {len(scored_facilities)} facilities")
        return scored_facilities

    def _get_available_service_types(self) -> List[str]:
        """Get list of available service types from database."""
        query = """
        MATCH (f:Facility)
        RETURN DISTINCT f.service_type AS service_type
        ORDER BY service_type
        """

        try:
            results = self.db.execute_query(query)
            service_types = [r["service_type"] for r in results if r["service_type"]]
            return service_types
        except Exception as e:
            logger.error(f"Failed to get service types: {e}")
            return [
                "就労継続支援B型",
                "就労継続支援A型",
                "生活介護",
                "就労移行支援",
                "自立訓練",
                "グループホーム",
            ]

    def _score_facility(
        self, facility: Dict[str, Any], user_data: Dict[str, Any], assessment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Score facility match using LLM."""
        # Format facility info
        facility_info = f"""
事業所名: {facility.get('name')}
法人名: {facility.get('corporation_name')}
所在地: {facility.get('address')}
所在区: {facility.get('district')}
定員: {facility.get('capacity')}
空き状況: {facility.get('availability_status', '不明')}
"""

        prompt = FACILITY_MATCHING_PROMPT.format(
            disability_type=user_data.get("disability_type", ""),
            support_level=user_data.get("support_level", ""),
            preferences=", ".join(assessment_data.get("preferences", [])),
            district=user_data.get("district", "不明"),
            facility_info=facility_info,
        )

        try:
            response = self.llm.generate(
                prompt=prompt, temperature=0.2, max_tokens=1024
            )
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Facility scoring failed: {e}")
            return {"match_score": 0.5, "reasons": ["評価失敗"], "concerns": []}

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response."""
        logger.debug(f"Parsing response: {response[:200]}...")

        response = response.strip()

        # Remove markdown
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end > start:
                response = response[start:end].strip()
        elif response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(line for line in lines if not line.startswith("```"))

        # Extract JSON
        if "{" in response and "}" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            response = response[start:end]

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}")
            logger.error(f"Response: {response[:500]}")
            raise ValueError(f"Invalid JSON: {e}")


# Global instance
_service_coordinator = None


def get_service_coordinator() -> ServiceCoordinator:
    """Get or create service coordinator instance."""
    global _service_coordinator
    if _service_coordinator is None:
        _service_coordinator = ServiceCoordinator()
    return _service_coordinator
