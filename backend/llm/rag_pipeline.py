"""
RAG (Retrieval Augmented Generation) pipeline for facility search.

This module combines:
1. Query analysis using LLM
2. Neo4j graph database search
3. Context construction
4. Answer generation using LLM
"""
from typing import Dict, List, Optional, Any
from loguru import logger

from backend.llm.ollama_client import get_ollama_client
from backend.neo4j.client import get_neo4j_client


class RAGPipeline:
    """RAG pipeline for natural language facility search."""

    def __init__(self):
        """Initialize RAG pipeline."""
        self.llm = get_ollama_client()
        self.db = get_neo4j_client()
        logger.info("RAG pipeline initialized")

    def search(self, user_query: str) -> Dict[str, Any]:
        """
        Execute RAG search pipeline.

        Args:
            user_query: User's natural language question

        Returns:
            Dict containing answer, facilities, and metadata
        """
        logger.info(f"Starting RAG search for query: {user_query}")

        # Step 1: Analyze query using LLM
        search_params = self._analyze_query(user_query)
        logger.debug(f"Query analysis result: {search_params}")

        # Step 2: Search Neo4j database
        facilities = self._search_facilities(search_params)
        logger.info(f"Found {len(facilities)} facilities")

        # Step 3: Generate answer using LLM with retrieved context
        answer = self._generate_answer(user_query, facilities)

        return {
            "query": user_query,
            "answer": answer,
            "facilities": facilities,
            "search_params": search_params,
            "facility_count": len(facilities),
        }

    def _analyze_query(self, user_query: str) -> Dict[str, Any]:
        """
        Analyze user query to extract search parameters.

        Args:
            user_query: User's natural language question

        Returns:
            Dict with service_type, district, keywords, etc.
        """
        system_prompt = """あなたは福祉サービス検索の専門家です。
ユーザーの質問から以下の情報を抽出してください:

【重要】事業所名が質問に含まれている場合は、必ず facility_name に抽出してください。
- facility_name: 事業所名（「〜ヘルパーセンター」「〜事業所」「〜支援センター」など）
- service_type: サービス種別の正式名称（後述の変換リストを参照）
- district: 地域（小倉北区、小倉南区、八幡西区など。必ず「〜区」を含める）
- keywords: サービス内容に関するキーワード（送迎、医療的ケアなど）
  ※「について」「詳細」「教えて」などの質問表現はkeywordsに含めない

【サービス種別の別名→正式名称 変換リスト】
一般的な呼び方を正式名称に変換してください:
- 「ショートステイ」「ショート」→「短期入所」
- 「グループホーム」「GH」→「共同生活援助」
- 「ヘルパー」「訪問介護」「訪問ヘルパー」→「居宅介護」
- 「デイサービス」「デイ」「通所」→「生活介護」
- 「就労B」「B型」「就労継続B型」→「就労継続支援B型」
- 「就労A」「A型」「就労継続A型」→「就労継続支援A型」
- 「移動支援」「ガイドヘルプ」「外出支援」→「同行援護」
- 「行動援護」「強度行動障害支援」→「行動援護」
- 「重訪」「重度訪問」→「重度訪問介護」
- 「療養介護」→「療養介護」

【データベース内の主要サービス種別】(優先的にマッチング):
- 重度訪問介護 (126件)
- 生活介護 (105件)
- 同行援護 (63件)
- 短期入所 (45件)
- 居宅介護 (19件)
- 行動援護 (5件)
- 療養介護 (4件)
- 就労継続支援B型 (1件)
- 共同生活援助 (1件)

【抽出ルール】
1. 事業所名の判定が最優先:
   - 固有名詞（みんなの〜、〜ヘルパーセンター、〜事業所、〜支援センターなど）
   - 「について」「の詳細」「を教えて」などが続く場合は事業所名の可能性大
   - 事業所名に「ショート」「デイ」などが含まれていても、それは名称の一部として facility_name に抽出
2. サービス種別は必ず正式名称に変換（上記リスト参照）
   - ただし、事業所名の一部として使われている場合は変換しない
3. 地域は必ず「〜区」の形式で抽出（「小倉南」→「小倉南区」）
4. keywords にはサービス内容に関する実質的なキーワードのみを含める
   - 含める: 送迎、医療的ケア、重度対応、土日営業など
   - 含めない: について、詳細、教えて、を、は、など助詞や質問表現

【重要な判定例】
- 「みんなのhome黒崎ショートについて」 → facility_name: "みんなのhome黒崎ショート", service_type: null
- 「八幡西区でショートステイを探す」 → facility_name: null, service_type: "短期入所"

以下のJSON形式で返答してください:
{
  "facility_name": "事業所名 or null",
  "service_type": "正式なサービス種別名 or null",
  "district": "区名 or null",
  "keywords": ["キーワード1", "キーワード2"] or []
}

JSON形式のみで返答し、説明文は含めないでください。"""

        try:
            response = self.llm.generate(
                prompt=user_query, system=system_prompt, temperature=0.1
            )

            # Parse JSON response
            import json

            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(
                    line for line in lines if not line.startswith("```")
                )

            params = json.loads(response)

            # Validate and clean parameters
            return {
                "facility_name": params.get("facility_name"),
                "service_type": params.get("service_type"),
                "district": params.get("district"),
                "keywords": params.get("keywords", []),
            }

        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            # Fallback to basic keyword search
            return {"service_type": None, "district": None, "keywords": [user_query]}

    def _search_facilities(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search facilities in Neo4j based on analyzed parameters.

        Args:
            search_params: Extracted search parameters

        Returns:
            List of matching facilities
        """
        conditions = []
        params = {}

        # Facility name filter (highest priority - most specific)
        if search_params.get("facility_name"):
            conditions.append("f.name CONTAINS $facility_name")
            params["facility_name"] = search_params["facility_name"]

        # Service type filter
        if search_params.get("service_type"):
            conditions.append("f.service_type = $service_type")
            params["service_type"] = search_params["service_type"]

        # District filter
        if search_params.get("district"):
            conditions.append("f.district = $district")
            params["district"] = search_params["district"]

        # Keyword search (name or address)
        keywords = search_params.get("keywords", [])
        if keywords:
            keyword_conditions = []
            for i, keyword in enumerate(keywords):
                key = f"keyword{i}"
                keyword_conditions.append(
                    f"(f.name CONTAINS ${key} OR f.address CONTAINS ${key})"
                )
                params[key] = keyword
            if keyword_conditions:
                conditions.append(f"({' OR '.join(keyword_conditions)})")

        # Build Cypher query
        where_clause = " AND ".join(conditions) if conditions else "true"

        query = f"""
        MATCH (f:Facility)
        WHERE {where_clause}
        RETURN f
        ORDER BY f.name
        LIMIT 20
        """

        try:
            results = self.db.execute_query(query, params)
            facilities = []
            for record in results:
                facility_node = record["f"]
                # Convert Neo4j node to dict
                facility = dict(facility_node)

                # Convert Neo4j DateTime to ISO string
                if "created_at" in facility:
                    facility["created_at"] = facility["created_at"].iso_format() if hasattr(facility["created_at"], "iso_format") else str(facility["created_at"])
                if "updated_at" in facility:
                    facility["updated_at"] = facility["updated_at"].iso_format() if hasattr(facility["updated_at"], "iso_format") else str(facility["updated_at"])

                facilities.append(facility)

            return facilities

        except Exception as e:
            logger.error(f"Facility search failed: {e}")
            return []

    def _generate_answer(
        self, user_query: str, facilities: List[Dict[str, Any]]
    ) -> str:
        """
        Generate natural language answer using LLM with retrieved facilities.

        Args:
            user_query: Original user question
            facilities: Retrieved facilities from Neo4j

        Returns:
            Natural language answer
        """
        if not facilities:
            return "申し訳ございません。該当する事業所が見つかりませんでした。検索条件を変えて再度お試しください。"

        # Construct context from facilities
        context = self._build_context(facilities)

        system_prompt = """あなたは北九州市の障害福祉サービスに詳しい相談支援専門員です。
データベースから検索された事業所情報を基に、利用者にわかりやすく丁寧に説明してください。

回答のガイドライン:
1. 検索結果の概要（該当件数、地域など）を最初に伝える
2. 各事業所の基本情報を簡潔に紹介する
3. サービス内容や特徴がある場合は説明する
4. 問い合わせ先（電話番号）を必ず記載する
5. 丁寧で親しみやすい言葉遣いを心がける
"""

        prompt = f"""質問: {user_query}

検索結果:
{context}

上記の事業所情報を基に、質問に対して適切な回答を生成してください。"""

        try:
            answer = self.llm.generate(
                prompt=prompt, system=system_prompt, temperature=0.3, max_tokens=1024
            )
            return answer

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            # Fallback to basic facility list
            return self._format_basic_list(facilities)

    def _build_context(self, facilities: List[Dict[str, Any]]) -> str:
        """
        Build context string from facilities for LLM prompt.

        Args:
            facilities: List of facility dicts

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, facility in enumerate(facilities, 1):
            parts = [
                f"\n【事業所 {i}】",
                f"名称: {facility.get('name', 'N/A')}",
                f"法人: {facility.get('corporation_name', 'N/A')}",
                f"サービス種別: {facility.get('service_type', 'N/A')}",
                f"所在地: {facility.get('address', 'N/A')}",
                f"電話: {facility.get('phone', 'N/A')}",
            ]

            # Add optional fields if available
            if capacity := facility.get("capacity"):
                parts.append(f"定員: {capacity}名")

            if availability := facility.get("availability_status"):
                parts.append(f"空き状況: {availability}")

            context_parts.append("\n".join(parts))

        return "\n".join(context_parts)

    def _format_basic_list(self, facilities: List[Dict[str, Any]]) -> str:
        """
        Format facilities as a basic list (fallback when LLM generation fails).

        Args:
            facilities: List of facility dicts

        Returns:
            Formatted facility list string
        """
        lines = [
            f"該当する事業所が{len(facilities)}件見つかりました:\n",
        ]

        for i, facility in enumerate(facilities, 1):
            lines.append(
                f"{i}. {facility.get('name', 'N/A')} ({facility.get('service_type', 'N/A')})"
            )
            lines.append(f"   所在地: {facility.get('address', 'N/A')}")
            lines.append(f"   電話: {facility.get('phone', 'N/A')}\n")

        return "\n".join(lines)


# Global RAG pipeline instance
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """Get or create RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
