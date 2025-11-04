# -*- coding: utf-8 -*-
"""
ドキュメント出力機能のテストスクリプト
"""
import requests
from loguru import logger
import os

API_BASE_URL = "http://localhost:8001/api"
OUTPUT_DIR = "/Users/k-kawahara/Ai-Workspace/kitakyu-net/test_outputs"


def setup_output_dir():
    """出力ディレクトリ作成"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"出力ディレクトリ作成: {OUTPUT_DIR}")


def get_test_data():
    """テストデータ取得 (利用者、計画、モニタリング)"""
    try:
        # 1. 利用者を取得
        response = requests.get(f"{API_BASE_URL}/users", params={"page": 1, "page_size": 10})
        response.raise_for_status()
        users_data = response.json()
        users = users_data.get("users", [])

        if not users:
            logger.error("利用者が見つかりません")
            return None, None, None

        user = users[0]
        user_id = user["user_id"]
        logger.info(f"利用者: {user['name']} (ID: {user_id})")

        # 2. 計画を取得
        response = requests.get(f"{API_BASE_URL}/plans/user/{user_id}")
        response.raise_for_status()
        plans = response.json()

        if not plans:
            logger.error(f"利用者 {user_id} の計画が見つかりません")
            return user, None, None

        plan = plans[0]
        plan_id = plan["plan_id"]
        logger.info(f"計画ID: {plan_id}")

        # 3. モニタリング記録を取得
        response = requests.get(f"{API_BASE_URL}/monitoring/plans/{plan_id}/monitoring")
        response.raise_for_status()
        monitoring_records = response.json()

        if monitoring_records:
            monitoring = monitoring_records[0]
            logger.info(f"モニタリングID: {monitoring['monitoring_id']}")
        else:
            monitoring = None
            logger.warning("モニタリング記録が見つかりません")

        return user, plan, monitoring

    except Exception as e:
        logger.error(f"テストデータ取得エラー: {e}")
        return None, None, None


def test_plan_pdf_export(plan_id: str):
    """支援計画PDF出力テスト"""
    try:
        logger.info("\n=== 支援計画PDF出力テスト ===")
        response = requests.get(f"{API_BASE_URL}/plans/{plan_id}/pdf", timeout=30)
        response.raise_for_status()

        # PDFを保存
        output_path = os.path.join(OUTPUT_DIR, f"plan_{plan_id[:8]}.pdf")
        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.success(f"✅ PDF出力成功: {output_path}")
        logger.info(f"ファイルサイズ: {len(response.content)} bytes")
        return True

    except Exception as e:
        logger.error(f"❌ PDF出力失敗: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return False


def test_plan_word_export(plan_id: str):
    """支援計画Word出力テスト"""
    try:
        logger.info("\n=== 支援計画Word出力テスト ===")
        response = requests.get(f"{API_BASE_URL}/plans/{plan_id}/word", timeout=30)
        response.raise_for_status()

        # Wordを保存
        output_path = os.path.join(OUTPUT_DIR, f"plan_{plan_id[:8]}.docx")
        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.success(f"✅ Word出力成功: {output_path}")
        logger.info(f"ファイルサイズ: {len(response.content)} bytes")
        return True

    except Exception as e:
        logger.error(f"❌ Word出力失敗: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return False


def test_monitoring_pdf_export(monitoring_id: str):
    """モニタリングPDF出力テスト"""
    try:
        logger.info("\n=== モニタリングPDF出力テスト ===")
        response = requests.get(f"{API_BASE_URL}/monitoring/{monitoring_id}/pdf", timeout=30)
        response.raise_for_status()

        # PDFを保存
        output_path = os.path.join(OUTPUT_DIR, f"monitoring_{monitoring_id}.pdf")
        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.success(f"✅ PDF出力成功: {output_path}")
        logger.info(f"ファイルサイズ: {len(response.content)} bytes")
        return True

    except Exception as e:
        logger.error(f"❌ PDF出力失敗: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return False


def test_monitoring_word_export(monitoring_id: str):
    """モニタリングWord出力テスト"""
    try:
        logger.info("\n=== モニタリングWord出力テスト ===")
        response = requests.get(f"{API_BASE_URL}/monitoring/{monitoring_id}/word", timeout=30)
        response.raise_for_status()

        # Wordを保存
        output_path = os.path.join(OUTPUT_DIR, f"monitoring_{monitoring_id}.docx")
        with open(output_path, "wb") as f:
            f.write(response.content)

        logger.success(f"✅ Word出力成功: {output_path}")
        logger.info(f"ファイルサイズ: {len(response.content)} bytes")
        return True

    except Exception as e:
        logger.error(f"❌ Word出力失敗: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return False


if __name__ == "__main__":
    logger.info("=== ドキュメント出力機能テスト開始 ===\n")

    # 出力ディレクトリ準備
    setup_output_dir()

    # テストデータ取得
    user, plan, monitoring = get_test_data()

    if not plan:
        logger.error("計画データが見つかりません。テスト終了。")
        exit(1)

    plan_id = plan["plan_id"]

    # 支援計画の出力テスト
    results = []
    results.append(("支援計画PDF", test_plan_pdf_export(plan_id)))
    results.append(("支援計画Word", test_plan_word_export(plan_id)))

    # モニタリング記録の出力テスト
    if monitoring:
        monitoring_id = monitoring["monitoring_id"]
        results.append(("モニタリングPDF", test_monitoring_pdf_export(monitoring_id)))
        results.append(("モニタリングWord", test_monitoring_word_export(monitoring_id)))
    else:
        logger.warning("モニタリング記録がないため、モニタリング出力テストはスキップします")

    # 結果サマリー
    logger.info("\n=== テスト結果サマリー ===")
    for test_name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        logger.info(f"{test_name}: {status}")

    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    logger.info(f"\n成功: {success_count}/{total_count}")

    if success_count == total_count:
        logger.success("\n✅ すべてのテスト完了")
        logger.info(f"出力ファイルは {OUTPUT_DIR} に保存されています")
    else:
        logger.warning(f"\n⚠️ 一部のテストが失敗しました ({total_count - success_count}件)")
