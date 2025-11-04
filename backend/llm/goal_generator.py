# -*- coding: utf-8 -*-
"""
Goal generation using LLM with SMART evaluation.
"""
import json
from typing import Dict, Any, List
from loguru import logger

from backend.llm.ollama_client import get_ollama_client


GOAL_GENERATION_PROMPT = """あなたは計画相談支援専門員です。
以下のアセスメント結果から、SMART原則に基づいた{goal_type}を提案してください。

【重要】このシステムは主に知的障害・精神障害のある方を対象としています。
目標設定時は、認知特性、コミュニケーション方法、環境調整、精神的安定を考慮してください。

【アセスメント結果】
利用者の希望: {preferences}
家族の希望: {family_wishes}
分析されたニーズ: {analyzed_needs}
強み: {strengths}
課題: {challenges}

【面談記録】
{interview_content}

【ICF分類による評価】
心身機能: {body_functions}
活動: {activities}
参加: {participation}
環境因子: {environmental_factors}
個人因子: {personal_factors}

【目標設定の指針】
- 本人と家族の希望を最優先に考える
- 本人の強みを活かせる目標にする
- 課題に対応しつつ、実現可能性を重視する
- ICF評価を踏まえた包括的な目標にする

【SMART原則】
- Specific (具体的): 何を、どのように達成するか明確
- Measurable (測定可能): 達成度を測定できる基準がある
- Achievable (達成可能): 利用者の能力と環境で実現可能
- Relevant (関連性): ニーズや希望と関連している
- Time-bound (期限付き): いつまでに達成するか明確

JSON形式で3-5個の目標案を提案してください。JSONのみを返し、他の説明は含めないでください。

{{
  "goals": [
    {{
      "goal_text": "目標の内容（具体的に記述）",
      "goal_reason": "この目標を設定する理由",
      "evaluation_period": "評価期間（例: 6ヶ月、1年）",
      "evaluation_method": "評価方法（どう測定するか）",
      "smart_evaluation": {{
        "is_specific": true,
        "is_measurable": true,
        "is_achievable": true,
        "is_relevant": true,
        "is_time_bound": true
      }},
      "confidence": 0.85
    }}
  ]
}}
"""


class GoalGenerator:
    """Generate goal suggestions using LLM."""

    def __init__(self):
        """Initialize goal generator."""
        self.llm = get_ollama_client()
        logger.info("Goal generator initialized")

    def suggest_goals(
        self, assessment_data: Dict[str, Any], goal_type: str = "長期目標"
    ) -> List[Dict[str, Any]]:
        """
        Generate goal suggestions based on assessment.

        Args:
            assessment_data: Assessment dict with needs, strengths, challenges
            goal_type: "長期目標" or "短期目標"

        Returns:
            List of goal suggestions
        """
        logger.info(f"Generating {goal_type} suggestions...")

        # Extract ICF classification
        icf = assessment_data.get("icf_classification", {})

        # Build prompt with all assessment information
        prompt = GOAL_GENERATION_PROMPT.format(
            goal_type=goal_type,
            preferences=", ".join(assessment_data.get("preferences", [])) or "未記載",
            family_wishes=", ".join(assessment_data.get("family_wishes", [])) or "未記載",
            analyzed_needs=", ".join(assessment_data.get("analyzed_needs", [])) or "分析中",
            strengths=", ".join(assessment_data.get("strengths", [])) or "評価中",
            challenges=", ".join(assessment_data.get("challenges", [])) or "評価中",
            interview_content=assessment_data.get("interview_content", "未記載"),
            body_functions=icf.get("body_functions", "未評価"),
            activities=icf.get("activities", "未評価"),
            participation=icf.get("participation", "未評価"),
            environmental_factors=icf.get("environmental_factors", "未評価"),
            personal_factors=icf.get("personal_factors", "未評価"),
        )

        try:
            response = self.llm.generate(
                prompt=prompt, temperature=0.7, max_tokens=4096
            )

            # Parse response
            goals_data = self._parse_response(response)
            goals = goals_data.get("goals", [])

            logger.success(f"Generated {len(goals)} {goal_type} suggestions")
            return goals

        except Exception as e:
            logger.error(f"Goal generation failed: {e}")
            raise

    def evaluate_goal_smart(self, goal_text: str) -> Dict[str, Any]:
        """
        Evaluate goal against SMART criteria.

        Args:
            goal_text: Goal text to evaluate

        Returns:
            SMART evaluation dict
        """
        logger.info("Evaluating goal with SMART criteria...")

        prompt = f"""以下の目標をSMART原則で評価してください。

目標: {goal_text}

SMART原則:
- Specific (具体的): 何を、どのように達成するか明確か
- Measurable (測定可能): 達成度を測定できる基準があるか
- Achievable (達成可能): 現実的に実現可能か
- Relevant (関連性): 本人のニーズと関連しているか
- Time-bound (期限付き): いつまでに達成するか明確か

JSON形式で評価結果を返してください。JSONのみを返してください。

{{
  "is_specific": true/false,
  "is_measurable": true/false,
  "is_achievable": true/false,
  "is_relevant": true/false,
  "is_time_bound": true/false,
  "smart_score": 0.0-1.0,
  "suggestions": ["改善提案1", "改善提案2"]
}}
"""

        try:
            response = self.llm.generate(
                prompt=prompt, temperature=0.5, max_tokens=2048
            )
            evaluation = self._parse_response(response)

            # Calculate SMART score if not provided
            if "smart_score" not in evaluation:
                score = sum(
                    [
                        evaluation.get("is_specific", False),
                        evaluation.get("is_measurable", False),
                        evaluation.get("is_achievable", False),
                        evaluation.get("is_relevant", False),
                        evaluation.get("is_time_bound", False),
                    ]
                ) / 5.0
                evaluation["smart_score"] = round(score, 2)

            logger.success(f"SMART score: {evaluation['smart_score']}")
            return evaluation

        except Exception as e:
            logger.error(f"SMART evaluation failed: {e}")
            raise

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
_goal_generator = None


def get_goal_generator() -> GoalGenerator:
    """Get or create goal generator instance."""
    global _goal_generator
    if _goal_generator is None:
        _goal_generator = GoalGenerator()
    return _goal_generator
