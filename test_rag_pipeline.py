"""Test RAG pipeline"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.llm.rag_pipeline import get_rag_pipeline
from loguru import logger


def main():
    logger.info("=" * 60)
    logger.info("RAG Pipeline Test")
    logger.info("=" * 60)

    pipeline = get_rag_pipeline()

    # Test queries
    test_queries = [
        "小倉北区の生活介護事業所を教えてください",
        "就労継続支援B型の事業所はどこにありますか？",
        "八幡西区で利用できる福祉サービスを探しています",
    ]

    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Test Query {i}: {query}")
        logger.info("=" * 60)

        try:
            result = pipeline.search(query)

            print(f"\n質問: {result['query']}")
            print(f"\n検索パラメータ: {result['search_params']}")
            print(f"\n該当件数: {result['facility_count']}件")
            print(f"\n回答:\n{result['answer']}")

            logger.success(f"✓ Test {i} completed successfully")

        except Exception as e:
            logger.error(f"✗ Test {i} failed: {e}")
            import traceback

            traceback.print_exc()

    logger.info("\n" + "=" * 60)
    logger.success("All RAG pipeline tests completed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
