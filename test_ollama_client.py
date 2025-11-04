"""Test Ollama client"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.llm.ollama_client import get_ollama_client
from loguru import logger

def main():
    logger.info("=" * 60)
    logger.info("Ollama Client Test")
    logger.info("=" * 60)

    client = get_ollama_client()

    # Check availability
    logger.info("Checking Ollama server availability...")
    if not client.check_availability():
        logger.error("Ollama server is not available")
        return False

    logger.success("✓ Ollama server is available")

    # Check model
    logger.info(f"Checking model '{client.model}' availability...")
    if not client.check_model_available():
        logger.error(f"Model '{client.model}' is not available")
        return False

    logger.success(f"✓ Model '{client.model}' is available")

    # Test generation
    logger.info("Testing text generation...")
    prompt = "北九州市について簡潔に説明してください（50文字以内）"
    
    try:
        response = client.generate(prompt)
        logger.success("✓ Text generation successful")
        print(f"\n質問: {prompt}")
        print(f"回答: {response}\n")
    except Exception as e:
        logger.error(f"✗ Text generation failed: {e}")
        return False

    # Test chat
    logger.info("Testing chat format...")
    messages = [
        {"role": "system", "content": "あなたは北九州市の障害福祉サービスに詳しいアシスタントです。"},
        {"role": "user", "content": "こんにちは"}
    ]
    
    try:
        response = client.chat(messages)
        logger.success("✓ Chat test successful")
        print(f"\nチャット応答: {response}\n")
    except Exception as e:
        logger.error(f"✗ Chat test failed: {e}")
        return False

    logger.info("=" * 60)
    logger.success("All Ollama tests passed!")
    logger.info("=" * 60)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
