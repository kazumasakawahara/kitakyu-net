# -*- coding: utf-8 -*-
"""
モニタリング記録ページ
"""
import streamlit as st
import requests
from datetime import datetime, date
from typing import Dict, List, Any
from loguru import logger

# ページ設定
st.set_page_config(
    page_title="モニタリング記録",
    page_icon="📊",
    layout="wide"
)

# API設定
API_BASE_URL = "http://localhost:8001/api"

# セッション状態の初期化
if "monitoring_step" not in st.session_state:
    st.session_state["monitoring_step"] = 0

if "monitoring_data" not in st.session_state:
    st.session_state["monitoring_data"] = {
        "monitoring_date": datetime.now(),
        "monitoring_type": "定期",
        "status": "進行中",
        "goal_evaluations": [],
        "service_evaluations": [],
        "strengths": [],
        "challenges": [],
        "family_feedback": "",
        "plan_revision_needed": False,
        "revision_reason": "",
        "new_goals": [],
        "service_changes": []
    }


# API Helper Functions
def get_users():
    """利用者一覧を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/users")
        response.raise_for_status()
        data = response.json()
        # APIは {"users": [...]} 形式で返すので、users配列を取り出す
        return data.get("users", []) if isinstance(data, dict) else data
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        return []


def get_user_plans(user_id: str):
    """利用者の計画一覧を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/plans/user/{user_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching plans: {e}")
        return []


def get_plan(plan_id: str):
    """計画詳細を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/plans/{plan_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching plan: {e}")
        return None


def get_monitoring_records(plan_id: str):
    """モニタリング記録一覧を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/monitoring/plans/{plan_id}/monitoring")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching monitoring records: {e}")
        return []


def create_monitoring_record(plan_id: str, record_data: Dict[str, Any]):
    """モニタリング記録を作成"""
    try:
        # 日時をISO形式に変換
        if isinstance(record_data.get("monitoring_date"), datetime):
            record_data["monitoring_date"] = record_data["monitoring_date"].isoformat()

        response = requests.post(
            f"{API_BASE_URL}/monitoring/plans/{plan_id}/monitoring",
            json=record_data
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error creating monitoring record: {e}")
        raise


# ページタイトル
st.title("📊 モニタリング記録")
st.markdown("---")

# 利用者・計画選択セクション
st.header("1️⃣ 利用者・計画の選択")

col1, col2 = st.columns(2)

with col1:
    # 利用者選択
    users = get_users()
    if users:
        user_options = {f"{user['name']} ({user['user_id'][:8]})": user['user_id'] for user in users}
        selected_user_display = st.selectbox(
            "利用者を選択",
            options=list(user_options.keys()),
            key="selected_user_display"
        )
        selected_user_id = user_options[selected_user_display]
    else:
        st.warning("利用者が登録されていません")
        st.stop()

with col2:
    # 計画選択
    if selected_user_id:
        plans = get_user_plans(selected_user_id)
        if plans:
            plan_options = {
                f"{plan.get('plan_type', '個別支援計画')} (作成日: {plan.get('created_at', '')[:10]})": plan['plan_id']
                for plan in plans
            }
            selected_plan_display = st.selectbox(
                "計画を選択",
                options=list(plan_options.keys()),
                key="selected_plan_display"
            )
            selected_plan_id = plan_options[selected_plan_display]

            # 選択した計画の詳細を取得
            if selected_plan_id:
                selected_plan = get_plan(selected_plan_id)
        else:
            st.warning("この利用者の計画がありません")
            st.stop()

st.markdown("---")

# 既存のモニタリング記録表示
if selected_plan_id:
    st.header("📋 過去のモニタリング記録")

    records = get_monitoring_records(selected_plan_id)

    if records:
        st.write(f"**記録件数**: {len(records)}件")

        for record in records:
            with st.expander(
                f"📅 {record['monitoring_date'][:10]} - {record['monitoring_type']} (ステータス: {record['status']})"
            ):
                col_a, col_b = st.columns(2)

                with col_a:
                    st.write("**基本情報**")
                    st.write(f"- 記録日: {record['monitoring_date'][:10]}")
                    st.write(f"- 種別: {record['monitoring_type']}")
                    st.write(f"- ステータス: {record['status']}")

                with col_b:
                    st.write("**評価サマリー**")
                    st.write(f"- 目標評価数: {len(record.get('goal_evaluations', []))}件")
                    st.write(f"- サービス評価数: {len(record.get('service_evaluations', []))}件")

                if record.get('overall_summary'):
                    st.write("**総合評価**")
                    st.info(record['overall_summary'])

                # PDF/Wordダウンロードボタン
                col_pdf, col_word = st.columns(2)
                with col_pdf:
                    pdf_url = f"{API_BASE_URL}/monitoring/{record['monitoring_id']}/pdf"
                    st.link_button("📄 PDFダウンロード", pdf_url, use_container_width=True)
                with col_word:
                    word_url = f"{API_BASE_URL}/monitoring/{record['monitoring_id']}/word"
                    st.link_button("📝 Wordダウンロード", word_url, use_container_width=True)
    else:
        st.info("まだモニタリング記録がありません")

st.markdown("---")

# 新規作成ボタン
st.header("✨ 新規モニタリング記録作成")

if st.button("🆕 新しいモニタリング記録を作成", type="primary", use_container_width=True):
    st.session_state["monitoring_step"] = 1
    st.session_state["creating_monitoring"] = True
    st.session_state["monitoring_plan_id"] = selected_plan_id
    st.session_state["monitoring_plan"] = selected_plan
    st.rerun()

# モニタリング記録作成フロー
if st.session_state.get("creating_monitoring"):
    st.markdown("---")
    st.header("📝 モニタリング記録作成")

    # プログレスバー
    progress_step = st.session_state["monitoring_step"]
    st.progress(progress_step / 5)

    # ステップ表示
    steps = ["基本情報", "目標評価", "サービス評価", "総合評価", "計画変更提案"]
    st.write(f"**ステップ {progress_step}/5**: {steps[progress_step - 1] if progress_step > 0 else ''}")

    st.markdown("---")

    # Step 1: 基本情報
    if st.session_state["monitoring_step"] == 1:
        st.subheader("1️⃣ 基本情報")

        col1, col2, col3 = st.columns(3)

        with col1:
            monitoring_date = st.date_input(
                "記録日",
                value=date.today(),
                key="monitoring_date_input"
            )
            st.session_state["monitoring_data"]["monitoring_date"] = datetime.combine(
                monitoring_date, datetime.min.time()
            )

        with col2:
            monitoring_type = st.selectbox(
                "モニタリング種別",
                options=["定期", "臨時", "終結時"],
                key="monitoring_type_input"
            )
            st.session_state["monitoring_data"]["monitoring_type"] = monitoring_type

        with col3:
            status = st.selectbox(
                "ステータス",
                options=["進行中", "完了", "要改善"],
                key="status_input"
            )
            st.session_state["monitoring_data"]["status"] = status

        # 次へボタン
        if st.button("次へ ➡️", type="primary"):
            st.session_state["monitoring_step"] = 2
            st.rerun()

    # Step 2: 目標評価
    elif st.session_state["monitoring_step"] == 2:
        st.subheader("2️⃣ 目標評価")

        plan = st.session_state["monitoring_plan"]

        # 長期目標評価
        st.write("**長期目標の評価**")
        long_term_evaluations = []

        for i, goal in enumerate(plan.get("long_term_goals", []), 1):
            with st.expander(f"長期目標 {i}: {goal.get('goal_text', goal.get('goal', ''))}"):
                col1, col2 = st.columns(2)

                with col1:
                    achievement_rate = st.slider(
                        "達成率 (%)",
                        min_value=0,
                        max_value=100,
                        value=50,
                        key=f"lt_achievement_{i}"
                    )

                    achievement_status = st.selectbox(
                        "達成状況",
                        options=["未達成", "一部達成", "達成", "超過達成"],
                        key=f"lt_status_{i}"
                    )

                with col2:
                    evaluation_comment = st.text_area(
                        "評価コメント",
                        key=f"lt_comment_{i}",
                        height=100
                    )

                    evidence = st.text_input(
                        "根拠・具体例",
                        key=f"lt_evidence_{i}"
                    )

                next_action = st.text_input(
                    "次のアクション",
                    key=f"lt_next_{i}"
                )

                long_term_evaluations.append({
                    "goal_id": goal.get("goal_id"),
                    "goal_type": "long_term",
                    "achievement_rate": achievement_rate,
                    "evaluation_comment": evaluation_comment,
                    "achievement_status": achievement_status,
                    "evidence": evidence if evidence else None,
                    "next_action": next_action if next_action else None
                })

        # 短期目標評価
        st.write("**短期目標の評価**")
        short_term_evaluations = []

        for i, goal in enumerate(plan.get("short_term_goals", []), 1):
            with st.expander(f"短期目標 {i}: {goal.get('goal_text', goal.get('goal', ''))}"):
                col1, col2 = st.columns(2)

                with col1:
                    achievement_rate = st.slider(
                        "達成率 (%)",
                        min_value=0,
                        max_value=100,
                        value=50,
                        key=f"st_achievement_{i}"
                    )

                    achievement_status = st.selectbox(
                        "達成状況",
                        options=["未達成", "一部達成", "達成", "超過達成"],
                        key=f"st_status_{i}"
                    )

                with col2:
                    evaluation_comment = st.text_area(
                        "評価コメント",
                        key=f"st_comment_{i}",
                        height=100
                    )

                    evidence = st.text_input(
                        "根拠・具体例",
                        key=f"st_evidence_{i}"
                    )

                next_action = st.text_input(
                    "次のアクション",
                    key=f"st_next_{i}"
                )

                short_term_evaluations.append({
                    "goal_id": goal.get("goal_id"),
                    "goal_type": "short_term",
                    "achievement_rate": achievement_rate,
                    "evaluation_comment": evaluation_comment,
                    "achievement_status": achievement_status,
                    "evidence": evidence if evidence else None,
                    "next_action": next_action if next_action else None
                })

        # 評価データを保存
        st.session_state["monitoring_data"]["goal_evaluations"] = (
            long_term_evaluations + short_term_evaluations
        )

        # ナビゲーションボタン
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("⬅️ 戻る"):
                st.session_state["monitoring_step"] = 1
                st.rerun()
        with col_next:
            if st.button("次へ ➡️", type="primary"):
                st.session_state["monitoring_step"] = 3
                st.rerun()

    # Step 3: サービス評価
    elif st.session_state["monitoring_step"] == 3:
        st.subheader("3️⃣ サービス評価")

        st.info("💡 利用しているサービスについて評価してください。サービスがない場合はスキップできます。")

        # サービス評価数の管理
        if "service_eval_count" not in st.session_state:
            st.session_state["service_eval_count"] = 0

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**登録済みサービス評価**: {st.session_state['service_eval_count']}件")
        with col2:
            if st.button("➕ サービス追加"):
                st.session_state["service_eval_count"] += 1
                st.rerun()

        service_evaluations = []

        # サービス評価フォーム
        for i in range(1, st.session_state["service_eval_count"] + 1):
            with st.expander(f"サービス {i}", expanded=(i == st.session_state["service_eval_count"])):
                service_name = st.text_input(
                    "サービス名",
                    key=f"service_name_{i}",
                    placeholder="例: 生活介護（A事業所）"
                )

                col1, col2 = st.columns(2)

                with col1:
                    attendance_rate = st.slider(
                        "出席率 (%)",
                        min_value=0,
                        max_value=100,
                        value=80,
                        key=f"service_attendance_{i}"
                    )

                    satisfaction = st.selectbox(
                        "満足度",
                        options=["非常に良好", "良好", "普通", "やや不満", "不満"],
                        index=1,
                        key=f"service_satisfaction_{i}"
                    )

                with col2:
                    evaluation = st.text_area(
                        "評価コメント",
                        key=f"service_evaluation_{i}",
                        height=100,
                        placeholder="サービス利用の効果や変化について"
                    )

                if service_name:  # サービス名が入力されている場合のみ追加
                    service_evaluations.append({
                        "service_name": service_name,
                        "attendance_rate": attendance_rate,
                        "satisfaction": satisfaction,
                        "evaluation": evaluation if evaluation else None
                    })

        st.session_state["monitoring_data"]["service_evaluations"] = service_evaluations

        # ナビゲーションボタン
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("⬅️ 戻る"):
                st.session_state["monitoring_step"] = 2
                st.rerun()
        with col_next:
            if st.button("次へ ➡️", type="primary"):
                st.session_state["monitoring_step"] = 4
                st.rerun()

    # Step 4: 総合評価
    elif st.session_state["monitoring_step"] == 4:
        st.subheader("4️⃣ 総合評価")

        overall_summary = st.text_area(
            "総合評価サマリー",
            height=150,
            placeholder="全体的な進捗状況や変化について記載してください",
            key="overall_summary_input"
        )
        st.session_state["monitoring_data"]["overall_summary"] = overall_summary

        col1, col2 = st.columns(2)

        with col1:
            st.write("**良かった点**")
            strength_count = st.number_input("項目数", min_value=1, max_value=10, value=3, key="strength_count")
            strengths = []
            for i in range(strength_count):
                strength = st.text_input(f"良かった点 {i+1}", key=f"strength_{i}")
                if strength:
                    strengths.append(strength)
            st.session_state["monitoring_data"]["strengths"] = strengths

        with col2:
            st.write("**課題**")
            challenge_count = st.number_input("項目数", min_value=1, max_value=10, value=3, key="challenge_count")
            challenges = []
            for i in range(challenge_count):
                challenge = st.text_input(f"課題 {i+1}", key=f"challenge_{i}")
                if challenge:
                    challenges.append(challenge)
            st.session_state["monitoring_data"]["challenges"] = challenges

        family_feedback = st.text_area(
            "家族の意見",
            height=100,
            key="family_feedback_input"
        )
        st.session_state["monitoring_data"]["family_feedback"] = family_feedback if family_feedback else None

        # ナビゲーションボタン
        col_back, col_next = st.columns(2)
        with col_back:
            if st.button("⬅️ 戻る"):
                st.session_state["monitoring_step"] = 3
                st.rerun()
        with col_next:
            if st.button("次へ ➡️", type="primary"):
                st.session_state["monitoring_step"] = 5
                st.rerun()

    # Step 5: 計画変更提案
    elif st.session_state["monitoring_step"] == 5:
        st.subheader("5️⃣ 計画変更提案")

        plan_revision_needed = st.checkbox(
            "計画の変更が必要",
            key="plan_revision_needed_input"
        )
        st.session_state["monitoring_data"]["plan_revision_needed"] = plan_revision_needed

        if plan_revision_needed:
            revision_reason = st.text_area(
                "変更理由",
                height=100,
                key="revision_reason_input"
            )
            st.session_state["monitoring_data"]["revision_reason"] = revision_reason

            # 新目標案（簡易実装）
            st.write("**新目標案** (オプション)")
            new_goal_text = st.text_area("新しい目標", key="new_goal_text")
            if new_goal_text:
                st.session_state["monitoring_data"]["new_goals"] = [{
                    "goal_text": new_goal_text,
                    "goal_type": "long_term",
                    "evaluation_period": None,
                    "evaluation_criteria": None
                }]

            # サービス変更案（簡易実装）
            st.write("**サービス変更案** (オプション)")
            service_change_reason = st.text_area("変更理由", key="service_change_reason")
            if service_change_reason:
                st.session_state["monitoring_data"]["service_changes"] = [{
                    "change_type": "変更",
                    "service_id": None,
                    "service_type": None,
                    "facility_name": None,
                    "reason": service_change_reason
                }]

        # 保存ボタン
        col_back, col_save = st.columns(2)
        with col_back:
            if st.button("⬅️ 戻る"):
                st.session_state["monitoring_step"] = 4
                st.rerun()
        with col_save:
            if st.button("💾 保存", type="primary", use_container_width=True):
                try:
                    # 作成者IDを追加（仮）
                    monitoring_data = st.session_state["monitoring_data"].copy()
                    monitoring_data["plan_id"] = st.session_state["monitoring_plan_id"]
                    monitoring_data["created_by"] = "staff_demo"  # TODO: 実際のスタッフID

                    # モニタリング記録を作成
                    result = create_monitoring_record(
                        st.session_state["monitoring_plan_id"],
                        monitoring_data
                    )

                    st.success(f"✅ モニタリング記録を保存しました！ (ID: {result['monitoring_id']})")

                    # 状態をリセット
                    st.session_state["creating_monitoring"] = False
                    st.session_state["monitoring_step"] = 0
                    st.session_state["monitoring_data"] = {
                        "monitoring_date": datetime.now(),
                        "monitoring_type": "定期",
                        "status": "進行中",
                        "goal_evaluations": [],
                        "service_evaluations": [],
                        "strengths": [],
                        "challenges": [],
                        "family_feedback": "",
                        "plan_revision_needed": False,
                        "revision_reason": "",
                        "new_goals": [],
                        "service_changes": []
                    }

                    st.balloons()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")
