# -*- coding: utf-8 -*-
"""
アセスメントフォームへのテストデータ投入スクリプト
"""
import requests
from datetime import date
from loguru import logger

API_BASE_URL = "http://localhost:8001/api"

# テストデータ
TEST_ASSESSMENT_DATA = {
    "user_id": None,  # 実際の利用者IDを取得して設定
    "interview_date": date.today().isoformat(),
    "interview_participants": "本人、母親、相談支援専門員（田中）",
    "interview_content": """【本人の希望・目標】
・就労継続支援B型で働きたい
・将来は一人暮らしをしてみたい
・友達を作りたい
・パソコンのスキルを身につけたい

【家族の希望・心配事】
・無理のない範囲で社会参加してほしい
・金銭管理が心配なので、サポートを受けながら自立してほしい
・健康管理（服薬）をきちんとしてほしい
・将来的にグループホームへの入居も検討したい

【本人の強み・得意なこと】
・単純作業は丁寧に取り組める
・服薬管理は自分でできている
・音楽が好きで、音楽療法プログラムでは積極的に参加
・パソコンの基本操作（文字入力、インターネット検索）ができる
・挨拶など基本的なコミュニケーションはできる

【生活状況・日常生活】
・現在は母親と二人暮らし
・生活リズムは比較的安定している（夜10時就寝、朝7時起床）
・食事は母親が準備しているが、簡単な調理（レトルト温め、米炊き）はできる
・掃除、洗濯は母親と一緒に行っている
・買い物は母親と一緒に週1回スーパーへ
・金銭管理は母親が行っており、本人は小遣い（週1000円）を管理

【支援が必要な課題】
・対人関係に不安があり、初対面の人との会話が苦手
・金銭管理が苦手で、計画的な買い物ができない
・複雑な指示の理解が難しい
・注意集中の持続が短い（約30分程度）
・一度にたくさんのことを言われると混乱する
・ストレスがかかると家に引きこもりがちになる

【社会参加・人との関わり】
・現在は週2回デイケアに通所（精神科クリニック併設）
・外出は週1-2回程度（通院、買い物、デイケア）
・友人はデイケアに1-2名いるが、自主的な交流はない
・以前は作業所に通っていたが、人間関係のトラブルで退所（2年前）

【現在利用しているサービス】
・精神科クリニック（月1回通院、服薬管理）
・精神科デイケア（週2回）
・相談支援事業所による定期訪問（月1回）

【健康状態・医療的ケア】
・診断名: 統合失調症（20歳で発症、現在25歳）
・服薬: 抗精神病薬（朝夕）、睡眠薬（就寝前）
・服薬管理は本人ができており、飲み忘れはほぼない
・副作用: 眠気、体重増加（要経過観察）
・アレルギー: なし
・その他: 定期的な血液検査が必要（3ヶ月に1回）

【その他・特記事項】
・視覚的な指示（絵カード、手順書）が理解しやすい
・大きな音や人混みが苦手
・午前中は比較的調子が良く、活動的
・午後は疲れやすく、休憩が必要
・ルーチン化された作業は得意
・予定変更への対応が苦手で、事前の説明が必要
""",
    "analyze": True
}


def get_first_user_id():
    """最初の利用者IDを取得"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/users",
            params={"page": 1, "page_size": 10},
            timeout=10
        )
        if response.status_code == 200:
            users_data = response.json()
            users = users_data.get("users", [])
            if users:
                return users[0]["user_id"]
            else:
                logger.error("利用者が見つかりません")
                return None
        else:
            logger.error(f"利用者取得失敗: {response.text}")
            return None
    except Exception as e:
        logger.error(f"エラー: {e}")
        return None


def submit_test_assessment():
    """テストアセスメントをAPIに投入"""
    # 利用者IDを取得
    user_id = get_first_user_id()
    if not user_id:
        logger.error("利用者IDが取得できませんでした")
        return False

    TEST_ASSESSMENT_DATA["user_id"] = user_id
    logger.info(f"利用者ID: {user_id} でアセスメント投入開始")

    try:
        response = requests.post(
            f"{API_BASE_URL}/assessments",
            json=TEST_ASSESSMENT_DATA,
            timeout=60
        )

        if response.status_code == 201:
            assessment = response.json()
            logger.success(f"✅ アセスメント作成成功")
            logger.info(f"Assessment ID: {assessment.get('assessment_id')}")

            # 分析結果の表示
            logger.info("=== 分析結果 ===")

            if assessment.get("analyzed_needs"):
                logger.info("【分析されたニーズ】")
                for i, need in enumerate(assessment.get("analyzed_needs", []), 1):
                    logger.info(f"  {i}. {need}")

            if assessment.get("strengths"):
                logger.info("【強み】")
                for i, strength in enumerate(assessment.get("strengths", []), 1):
                    logger.info(f"  {i}. {strength}")

            if assessment.get("challenges"):
                logger.info("【課題】")
                for i, challenge in enumerate(assessment.get("challenges", []), 1):
                    logger.info(f"  {i}. {challenge}")

            if assessment.get("confidence_score"):
                logger.info(f"【信頼度スコア】: {assessment.get('confidence_score'):.2f}")

            return True
        else:
            logger.error(f"❌ アセスメント作成失敗: {response.status_code}")
            logger.error(response.text)
            return False

    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        return False


if __name__ == "__main__":
    logger.info("=== アセスメントテストデータ投入開始 ===")
    success = submit_test_assessment()
    if success:
        logger.success("=== テストデータ投入完了 ===")
    else:
        logger.error("=== テストデータ投入失敗 ===")
