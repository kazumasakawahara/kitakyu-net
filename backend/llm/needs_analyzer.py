# -*- coding: utf-8 -*-
"""
Needs analysis using LLM.

Analyzes interview content and extracts structured needs information.
"""
import json
from typing import Dict, Any, List
from loguru import logger

from backend.llm.ollama_client import get_ollama_client


NEEDS_ANALYSIS_PROMPT = """あなたは経験豊富な計画相談支援専門員です。
以下のヒアリング内容から、利用者の潜在的なニーズを分析してください。

【ヒアリング内容】
{interview_content}

【分析の観点】
1. ICFモデルに基づく分類
   - 心身機能（body functions）: 身体的・精神的機能の状態
   - 活動（activities）: 日常生活動作や活動の実施状況
   - 参加（participation）: 社会参加や役割遂行の状況
   - 環境因子（environmental factors）: 物理的・社会的・制度的環境
   - 個人因子（personal factors）: 年齢、性別、価値観、ライフスタイル

2. 構造化
   - 本人の希望: 本人が明示的に述べた希望
   - 家族の希望: 家族が期待していること
   - 本人の強み: 活用できる能力や資源
   - 支援が必要な課題: 解決すべき困難や障壁
   - 潜在的なニーズ: 明示されていないが重要なニーズ

**重要**: 必ず以下の正確なJSON形式で返答してください。他の説明やテキストは一切含めず、JSON構造のみを返してください。

```json
{{
  "analyzed_needs": ["一人暮らしを実現するための生活スキル習得支援", "経済的自立に向けた就労支援", "金銭管理スキルの習得"],
  "strengths": ["明確な目標を持っている", "就労への意欲がある", "貯金を通じた計画性"],
  "challenges": ["生活スキルの習得", "安定した就労の実現", "金銭管理能力の向上"],
  "preferences": ["一人暮らしをしたい", "就職して貯金を貯めたい"],
  "family_wishes": [],
  "icf_classification": {{
    "body_functions": "ヒアリング内容から判断される心身機能の状態",
    "activities": "就労や生活管理などの日常活動の実施状況",
    "participation": "社会参加や就労への参加意欲",
    "environmental_factors": "住環境や就労環境などの環境要因",
    "personal_factors": "目標志向性や計画性などの個人特性"
  }}
}}
```"""


class NeedsAnalyzer:
    """Analyze interview content and extract structured needs."""

    def __init__(self):
        """Initialize needs analyzer."""
        self.llm = get_ollama_client()
        logger.info("Needs analyzer initialized")

    def analyze(
        self, interview_content: str
    ) -> Dict[str, Any]:
        """
        Analyze interview content using LLM.

        Args:
            interview_content: Raw interview text

        Returns:
            Dict with analyzed needs, strengths, challenges, etc.
        """
        logger.info("Starting needs analysis...")

        prompt = NEEDS_ANALYSIS_PROMPT.format(interview_content=interview_content)

        try:
            # Generate analysis
            response = self.llm.generate(
                prompt=prompt, temperature=0.7, max_tokens=4096
            )

            # Parse JSON response
            analysis = self._parse_response(response)

            # Validate analysis
            self._validate_analysis(analysis)

            logger.success("Needs analysis completed successfully")
            return analysis

        except Exception as e:
            logger.error(f"Needs analysis failed: {e}")
            raise

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured dict.

        Args:
            response: LLM response text

        Returns:
            Parsed dict

        Raises:
            ValueError: If response is not valid JSON
        """
        logger.debug(f"Raw LLM response (first 300 chars): {response[:300]}...")

        # Remove markdown code blocks if present
        response = response.strip()
        if "```json" in response:
            start_marker = "```json"
            end_marker = "```"
            start = response.find(start_marker) + len(start_marker)
            end = response.find(end_marker, start)
            if end > start:
                response = response[start:end].strip()
        elif response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(
                line for line in lines if not line.startswith("```")
            )
            response = response.strip()

        # Try to find JSON content
        if "{" in response and "}" in response:
            start = response.index("{")
            end = response.rindex("}") + 1
            response = response[start:end]

        # Remove any leading/trailing whitespace or newlines
        response = response.strip()

        try:
            analysis = json.loads(response)
            logger.debug(f"Parsed analysis keys: {analysis.keys()}")
            return analysis
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Cleaned response (first 500 chars): {response[:500]}...")
            logger.error(f"Response type: {type(response)}, length: {len(response)}")

            # More aggressive cleaning for common issues
            try:
                # Remove any control characters
                cleaned = ''.join(char for char in response if ord(char) >= 32 or char in '\n\r\t')
                analysis = json.loads(cleaned)
                logger.warning("Fallback parsing succeeded after removing control characters")
                return analysis
            except:
                raise ValueError(f"Invalid JSON response from LLM: {e}\nResponse snippet: {response[:200]}")

    def _validate_analysis(self, analysis: Dict[str, Any]) -> None:
        """
        Validate analysis structure and content.

        Args:
            analysis: Parsed analysis dict

        Raises:
            ValueError: If analysis is invalid
        """
        required_keys = [
            "analyzed_needs",
            "strengths",
            "challenges",
            "preferences",
            "family_wishes",
            "icf_classification",
        ]

        for key in required_keys:
            if key not in analysis:
                raise ValueError(f"Missing required key: {key}")

        # Validate ICF classification
        icf = analysis.get("icf_classification", {})
        icf_keys = [
            "body_functions",
            "activities",
            "participation",
            "environmental_factors",
            "personal_factors",
        ]

        for key in icf_keys:
            if key not in icf:
                logger.warning(f"Missing ICF classification: {key}")
                icf[key] = ""

        # Validate lists
        for key in ["analyzed_needs", "strengths", "challenges", "preferences", "family_wishes"]:
            if not isinstance(analysis[key], list):
                raise ValueError(f"{key} must be a list")

        # Check completeness
        if len(analysis["analyzed_needs"]) < 1:
            logger.warning("Analysis has no identified needs")

        if len(analysis["strengths"]) < 1:
            logger.warning("Analysis has no identified strengths")

        if len(analysis["challenges"]) < 1:
            logger.warning("Analysis has no identified challenges")

    def calculate_confidence_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence score for analysis quality.

        Args:
            analysis: Parsed analysis dict

        Returns:
            Confidence score (0.0-1.0)
        """
        score = 0.0
        total_checks = 0

        # Check completeness (40%)
        total_checks += 5
        if len(analysis.get("analyzed_needs", [])) >= 3:
            score += 0.08
        if len(analysis.get("strengths", [])) >= 2:
            score += 0.08
        if len(analysis.get("challenges", [])) >= 2:
            score += 0.08
        if len(analysis.get("preferences", [])) >= 1:
            score += 0.08
        if len(analysis.get("family_wishes", [])) >= 1:
            score += 0.08

        # Check ICF classification (30%)
        icf = analysis.get("icf_classification", {})
        for key in ["body_functions", "activities", "participation", "environmental_factors", "personal_factors"]:
            total_checks += 1
            if icf.get(key) and len(icf[key]) > 10:  # Non-trivial content
                score += 0.06

        # Check balance (20%)
        total_checks += 2
        needs_count = len(analysis.get("analyzed_needs", []))
        strengths_count = len(analysis.get("strengths", []))
        if strengths_count > 0 and needs_count > 0:
            ratio = strengths_count / (strengths_count + needs_count)
            if 0.2 <= ratio <= 0.6:  # Balanced view
                score += 0.2

        # Check specificity (10%)
        total_checks += 1
        avg_length = sum(len(str(item)) for item in analysis.get("analyzed_needs", [])) / max(1, len(analysis.get("analyzed_needs", [])))
        if avg_length > 15:  # Specific, not generic
            score += 0.1

        return round(score, 2)

    def generate_followup_questions(self, interview_content: str) -> Dict[str, Any]:
        """
        Generate follow-up questions for incomplete assessment.

        Args:
            interview_content: Current interview text

        Returns:
            Dict with missing_areas, questions, completeness_score, is_sufficient
        """
        logger.info("Generating follow-up questions...")

        prompt = FOLLOWUP_QUESTIONS_PROMPT.format(interview_content=interview_content)

        try:
            response = self.llm.generate(
                prompt=prompt, temperature=0.3, max_tokens=2048
            )

            questions_data = self._parse_response(response)

            logger.success(f"Generated {len(questions_data.get('questions', []))} follow-up questions")
            return questions_data

        except Exception as e:
            logger.error(f"Follow-up question generation failed: {e}")
            raise


# Global analyzer instance
_needs_analyzer = None


def get_needs_analyzer() -> NeedsAnalyzer:
    """Get or create needs analyzer instance."""
    global _needs_analyzer
    if _needs_analyzer is None:
        _needs_analyzer = NeedsAnalyzer()
    return _needs_analyzer


FOLLOWUP_QUESTIONS_PROMPT = """あなたは経験豊富な計画相談支援専門員です。
以下のヒアリング内容を確認し、不足している情報を特定して追加質問を生成してください。

【ヒアリング内容】
{interview_content}

【確認すべき重要項目】
1. 本人の希望や目標（どんな生活がしたいか）
2. 本人の強み・得意なこと・好きなこと
3. 家族の希望や心配事
4. 日常生活での困りごと
5. 社会参加や人との関わり
6. 現在利用しているサービス
7. 健康状態や医療的ケア

【質問生成のルール】
- 不足している項目について、3-5個の具体的な質問を生成
- 質問は優しく、答えやすい形式にする
- はい/いいえで答えられるものと、具体的に聞くものを組み合わせる
- 既に十分な情報がある項目は質問しない

JSON形式で返答してください。JSONのみを返し、他の説明は含めないでください。

{{
  "missing_areas": ["不足している情報の分野1", "不足している情報の分野2"],
  "questions": [
    {{
      "category": "本人の強み",
      "question": "ご本人が得意なことや好きなことはありますか？",
      "purpose": "本人の強みを活用した支援計画を立てるため"
    }},
    {{
      "category": "家族の希望",
      "question": "ご家族はどのような生活を望んでいますか？",
      "purpose": "家族のニーズも考慮した計画を立てるため"
    }}
  ],
  "completeness_score": 0.6,
  "is_sufficient": false
}}
"""
