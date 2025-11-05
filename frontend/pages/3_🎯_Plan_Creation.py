# -*- coding: utf-8 -*-
"""
支援計画作成ページ

アセスメント結果をもとに長期・短期目標を設定し、サービス利用計画を作成します。
"""
import streamlit as st
import requests
from datetime import date, datetime, timedelta
from loguru import logger

# ページ設定
st.set_page_config(
    page_title="支援計画作成",
    page_icon="🎯",
    layout="wide"
)


# API設定
API_BASE_URL = "http://localhost:8000/api"

# セッションステート初期化
if "selected_user_id" not in st.session_state:
    st.session_state["selected_user_id"] = None
if "selected_assessment_id" not in st.session_state:
    st.session_state["selected_assessment_id"] = None
if "current_plan_id" not in st.session_state:
    st.session_state["current_plan_id"] = None
if "long_term_goals" not in st.session_state:
    st.session_state["long_term_goals"] = []
if "short_term_goals" not in st.session_state:
    st.session_state["short_term_goals"] = []
if "services" not in st.session_state:
    st.session_state["services"] = []


def adopt_long_term_goal(goal):
    """長期目標を採用するコールバック関数"""
    if goal not in st.session_state["long_term_goals"]:
        st.session_state["long_term_goals"].append(goal)
        logger.info(f"Long-term goal adopted. Total: {len(st.session_state['long_term_goals'])}")


def adopt_short_term_goal(goal):
    """短期目標を採用するコールバック関数"""
    if goal not in st.session_state["short_term_goals"]:
        st.session_state["short_term_goals"].append(goal)
        logger.info(f"Short-term goal adopted. Total: {len(st.session_state['short_term_goals'])}")


def get_user_detail(user_id: str):
    """利用者詳細を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return None


def get_assessment_detail(assessment_id: str):
    """アセスメント詳細を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/assessments/{assessment_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error getting assessment: {e}")
        return None


def get_user_assessments(user_id: str):
    """利用者のアセスメント一覧を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/assessments")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error getting assessments: {e}")
        return []


def suggest_goals(assessment_id: str, goal_type: str):
    """AI目標提案を取得"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/goals/suggest",
            json={"assessment_id": assessment_id, "goal_type": goal_type},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error suggesting goals: {e}")
        return None


def search_facilities(service_type: str = None, district: str = None, keyword: str = None):
    """施設を検索"""
    try:
        params = {}
        if service_type:
            params["service_type"] = service_type
        if district:
            params["district"] = district
        if keyword:
            params["keyword"] = keyword

        response = requests.get(f"{API_BASE_URL}/facilities", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error searching facilities: {e}")
        return []


def get_facility_detail(facility_id: str):
    """施設詳細を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/facilities/{facility_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error getting facility: {e}")
        return None


# ページタイトル
st.title("🎯 支援計画作成")

# クイックナビゲーション
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("👤 利用者管理", use_container_width=True):
        st.switch_page("pages/1_👤_User_Management.py")
with col2:
    if st.button("📊 アセスメント", use_container_width=True):
        st.switch_page("pages/2_📊_Assessment.py")
with col3:
    if st.button("🏥 施設検索", use_container_width=True):
        st.switch_page("pages/4_🏥_Facility_Search.py")

st.markdown("---")

# Step 1: 利用者・アセスメント選択
st.header("1️⃣ 利用者・アセスメント選択")

col1, col2 = st.columns(2)

with col1:
    st.subheader("利用者選択")

    # 利用者一覧取得
    try:
        response = requests.get(f"{API_BASE_URL}/users", params={"page": 1, "page_size": 100})
        if response.status_code == 200:
            users_data = response.json()
            all_users = users_data.get("users", [])

            if all_users:
                # 利用者を名前とふりがなで選択できるようにする
                # セレクトボックスの選択肢に「氏名（ふりがな）年齢」を表示
                user_options = {
                    f"{user['name']}（{user.get('kana', '')}） {user['age']}歳": user
                    for user in all_users
                }

                st.caption(f"登録利用者数: {len(all_users)}件")

                selected_user_display = st.selectbox(
                    "利用者を選択",
                    options=["選択してください"] + list(user_options.keys()),
                    key="plan_user_selector",
                    help="ドロップダウンをクリックして、氏名やふりがなの一部を入力すると絞り込まれます"
                )

                if selected_user_display != "選択してください":
                    selected_user = user_options[selected_user_display]
                    st.session_state["selected_user_id"] = selected_user["user_id"]

                    st.success(f"✅ {selected_user['name']} さんを選択")
                    st.write(f"**障害種別**: {selected_user.get('disability_type', '未設定')}")
                    st.write(f"**支援区分**: {selected_user.get('support_level', '未判定')}")
            else:
                st.warning("利用者が登録されていません")
                if st.button("利用者管理へ →", type="primary"):
                    st.switch_page("pages/1_👤_User_Management.py")
    except Exception as e:
        st.error(f"利用者情報の取得に失敗: {e}")

with col2:
    st.subheader("アセスメント選択")

    if st.session_state.get("selected_user_id"):
        assessments = get_user_assessments(st.session_state["selected_user_id"])

        if assessments:
            assessment_options = {
                f"{a['interview_date']} (ID: {a['assessment_id'][:8]}...)": a
                for a in assessments
            }

            selected_assessment_display = st.selectbox(
                "アセスメントを選択",
                options=["選択してください"] + list(assessment_options.keys()),
                key="plan_assessment_selector"
            )

            if selected_assessment_display != "選択してください":
                selected_assessment = assessment_options[selected_assessment_display]
                st.session_state["selected_assessment_id"] = selected_assessment["assessment_id"]

                st.success(f"✅ {selected_assessment['interview_date']} のアセスメントを選択")

                # アセスメントサマリー表示
                with st.expander("アセスメント概要", expanded=False):
                    # 構造化されたデータがある場合
                    if selected_assessment.get("analyzed_needs") and len(selected_assessment["analyzed_needs"]) > 0:
                        st.write("**分析されたニーズ**:")
                        for need in selected_assessment["analyzed_needs"][:3]:
                            st.write(f"- {need}")

                    if selected_assessment.get("strengths") and len(selected_assessment["strengths"]) > 0:
                        st.write("**本人の強み**:")
                        for strength in selected_assessment["strengths"][:3]:
                            st.write(f"- {strength}")

                    if selected_assessment.get("challenges") and len(selected_assessment["challenges"]) > 0:
                        st.write("**課題**:")
                        for challenge in selected_assessment["challenges"][:3]:
                            st.write(f"- {challenge}")

                    # 面談記録がある場合（構造化データがない場合の代替表示）
                    if selected_assessment.get("interview_content"):
                        st.write("**面談記録**:")
                        # 長い場合は最初の300文字だけ表示
                        content = selected_assessment["interview_content"]
                        if len(content) > 300:
                            st.write(content[:300] + "...")
                        else:
                            st.write(content)

                    # 何もデータがない場合
                    if (not selected_assessment.get("analyzed_needs") and
                        not selected_assessment.get("strengths") and
                        not selected_assessment.get("interview_content")):
                        st.info("アセスメントデータがありません")
        else:
            st.warning("アセスメントがありません")
            if st.button("アセスメント実施へ →", type="primary"):
                st.switch_page("pages/2_📊_Assessment.py")
    else:
        st.info("まず利用者を選択してください")

st.markdown("---")

# Step 2: 長期目標設定
if st.session_state.get("selected_assessment_id"):
    st.header("2️⃣ 長期目標の設定")

    # デバッグ表示（一時的）
    with st.expander("🐛 デバッグ情報", expanded=False):
        st.write(f"採用済み長期目標数: {len(st.session_state['long_term_goals'])}")
        if st.session_state["long_term_goals"]:
            st.json(st.session_state["long_term_goals"])

    tab1, tab2 = st.tabs(["AI提案", "手動入力"])

    with tab1:
        st.subheader("AIによる長期目標提案")

        if st.button("💡 長期目標を提案してもらう", type="primary", use_container_width=True):
            with st.spinner("AIが長期目標を生成中..."):
                suggestions = suggest_goals(st.session_state["selected_assessment_id"], "長期目標")

                if suggestions and suggestions.get("suggestions"):
                    st.success(f"✅ {len(suggestions['suggestions'])}件の目標を提案しました")

                    for i, goal in enumerate(suggestions["suggestions"], 1):
                        with st.expander(f"提案 {i}: {goal['goal_text'][:50]}...", expanded=(i == 1)):
                            st.write(f"**目標**: {goal['goal_text']}")
                            st.write(f"**理由**: {goal['goal_reason']}")
                            st.write(f"**評価期間**: {goal['evaluation_period']}")
                            st.write(f"**評価方法**: {goal['evaluation_method']}")

                            # SMART評価
                            smart = goal.get("smart_evaluation", {})
                            col1, col2, col3, col4, col5 = st.columns(5)
                            with col1:
                                st.metric("Specific", "✅" if smart.get("is_specific") else "❌")
                            with col2:
                                st.metric("Measurable", "✅" if smart.get("is_measurable") else "❌")
                            with col3:
                                st.metric("Achievable", "✅" if smart.get("is_achievable") else "❌")
                            with col4:
                                st.metric("Relevant", "✅" if smart.get("is_relevant") else "❌")
                            with col5:
                                st.metric("Time-bound", "✅" if smart.get("is_time_bound") else "❌")

                            st.metric("信頼度", f"{goal.get('confidence', 0):.0%}")

                            # コールバック関数を使ってsession_stateの更新を確実に実行
                            st.button(
                                f"この目標を採用",
                                key=f"adopt_long_{i}",
                                use_container_width=True,
                                on_click=adopt_long_term_goal,
                                args=(goal,)
                            )
                else:
                    st.error("目標の提案に失敗しました")

    with tab2:
        st.subheader("手動で長期目標を入力")

        with st.form("manual_long_term_goal"):
            goal_text = st.text_area(
                "長期目標",
                placeholder="例: 週に2回、作業所に通所し、軽作業を通じて働く喜びを感じられるようになる",
                height=100
            )

            col1, col2 = st.columns(2)
            with col1:
                evaluation_period = st.selectbox("評価期間", ["6ヶ月", "1年", "2年", "3年"])
            with col2:
                evaluation_method = st.text_input(
                    "評価方法",
                    placeholder="例: 通所回数、作業への取り組み姿勢"
                )

            goal_reason = st.text_area(
                "目標設定の理由",
                placeholder="本人の希望や、アセスメント結果に基づく理由を記載",
                height=80
            )

            submitted = st.form_submit_button("長期目標を追加", type="primary", use_container_width=True)

            if submitted and goal_text:
                manual_goal = {
                    "goal_text": goal_text,
                    "goal_reason": goal_reason,
                    "evaluation_period": evaluation_period,
                    "evaluation_method": evaluation_method,
                    "confidence": 1.0,
                    "smart_evaluation": {
                        "is_specific": True,
                        "is_measurable": True,
                        "is_achievable": True,
                        "is_relevant": True,
                        "is_time_bound": True
                    }
                }
                st.session_state["long_term_goals"].append(manual_goal)
                st.success("✅ 長期目標を追加しました")
                st.rerun()

    # 採用済み長期目標の表示
    if st.session_state["long_term_goals"]:
        st.markdown("---")
        st.subheader("📌 採用した長期目標")

        for i, goal in enumerate(st.session_state["long_term_goals"], 1):
            with st.expander(f"長期目標 {i}: {goal['goal_text'][:50]}...", expanded=True):
                st.write(f"**目標**: {goal['goal_text']}")
                st.write(f"**評価期間**: {goal['evaluation_period']}")

                if st.button(f"削除", key=f"delete_long_{i}", type="secondary"):
                    st.session_state["long_term_goals"].remove(goal)
                    st.rerun()

st.markdown("---")

# Step 3: 短期目標設定
if st.session_state.get("selected_assessment_id") and st.session_state["long_term_goals"]:
    st.header("3️⃣ 短期目標の設定")

    tab1, tab2 = st.tabs(["AI提案", "手動入力"])

    with tab1:
        st.subheader("AIによる短期目標提案")
        st.info("長期目標を達成するための、具体的で実行可能な短期目標を提案します")

        if st.button("💡 短期目標を提案してもらう", type="primary", use_container_width=True):
            with st.spinner("AIが短期目標を生成中..."):
                suggestions = suggest_goals(st.session_state["selected_assessment_id"], "短期目標")

                if suggestions and suggestions.get("suggestions"):
                    st.success(f"✅ {len(suggestions['suggestions'])}件の短期目標を提案しました")

                    for i, goal in enumerate(suggestions["suggestions"], 1):
                        with st.expander(f"提案 {i}: {goal['goal_text'][:50]}...", expanded=(i == 1)):
                            st.write(f"**目標**: {goal['goal_text']}")
                            st.write(f"**理由**: {goal['goal_reason']}")
                            st.write(f"**評価期間**: {goal['evaluation_period']}")
                            st.write(f"**評価方法**: {goal['evaluation_method']}")

                            # コールバック関数を使ってsession_stateの更新を確実に実行
                            st.button(
                                f"この短期目標を採用",
                                key=f"adopt_short_{i}",
                                use_container_width=True,
                                on_click=adopt_short_term_goal,
                                args=(goal,)
                            )

    with tab2:
        st.subheader("手動で短期目標を入力")

        with st.form("manual_short_term_goal"):
            goal_text = st.text_area(
                "短期目標",
                placeholder="例: 1ヶ月間、週1回の通所を継続する",
                height=100
            )

            col1, col2 = st.columns(2)
            with col1:
                evaluation_period = st.selectbox("評価期間", ["1ヶ月", "3ヶ月", "6ヶ月"])
            with col2:
                evaluation_method = st.text_input(
                    "評価方法",
                    placeholder="例: 通所記録の確認"
                )

            submitted = st.form_submit_button("短期目標を追加", type="primary", use_container_width=True)

            if submitted and goal_text:
                manual_goal = {
                    "goal_text": goal_text,
                    "goal_reason": "",
                    "evaluation_period": evaluation_period,
                    "evaluation_method": evaluation_method,
                    "confidence": 1.0
                }
                st.session_state["short_term_goals"].append(manual_goal)
                st.success("✅ 短期目標を追加しました")
                st.rerun()

    # 採用済み短期目標の表示
    if st.session_state["short_term_goals"]:
        st.markdown("---")
        st.subheader("📌 採用した短期目標")

        for i, goal in enumerate(st.session_state["short_term_goals"], 1):
            with st.expander(f"短期目標 {i}: {goal['goal_text'][:50]}...", expanded=True):
                st.write(f"**目標**: {goal['goal_text']}")
                st.write(f"**評価期間**: {goal['evaluation_period']}")

                if st.button(f"削除", key=f"delete_short_{i}", type="secondary"):
                    st.session_state["short_term_goals"].remove(goal)
                    st.rerun()

st.markdown("---")

# Step 4: サービス調整・連絡記録
if st.session_state["long_term_goals"] and st.session_state["short_term_goals"]:
    st.header("4️⃣ サービス調整・連絡記録")

    st.info("💡 利用予定または利用中の事業所との確認事項、連絡内容を記録します。\n事業所の検索は「Facility Search」ページで行えます。")

    # サービス追加フォーム
    with st.expander("➕ サービス連絡記録を追加", expanded=len(st.session_state["services"]) == 0):
        with st.form("add_service_form"):
            st.subheader("サービス連絡記録")

            col1, col2 = st.columns(2)

            with col1:
                facility_name = st.text_input(
                    "事業所名",
                    placeholder="例: ○○作業所",
                    key="service_facility_name"
                )
                service_type = st.selectbox(
                    "サービス種別",
                    [
                        "就労継続支援B型",
                        "就労継続支援A型",
                        "就労移行支援",
                        "生活介護",
                        "自立訓練（生活訓練）",
                        "自立訓練（機能訓練）",
                        "共同生活援助（グループホーム）",
                        "短期入所（ショートステイ）",
                        "居宅介護（ホームヘルプ）",
                        "重度訪問介護",
                        "同行援護",
                        "行動援護",
                        "その他"
                    ],
                    key="service_type_select"
                )
                contact_date = st.date_input(
                    "連絡日",
                    value=date.today(),
                    key="service_contact_date"
                )

            with col2:
                contact_person = st.text_input(
                    "対応者名",
                    placeholder="例: サービス管理責任者 山田太郎",
                    key="service_contact_person"
                )
                contact_method = st.selectbox(
                    "連絡方法",
                    ["電話", "訪問", "メール", "FAX", "その他"],
                    key="service_contact_method"
                )

            contact_content = st.text_area(
                "連絡内容・確認事項",
                placeholder="例:\n・利用開始日: 2025年1月10日\n・利用頻度: 週2回（月曜・水曜）\n・送迎: あり（自宅前 8:30発）\n・利用時間: 9:00-15:00\n・昼食: 事業所で提供\n・本人の特性について情報共有\n・初日は職員が同行予定",
                height=150,
                key="service_contact_content"
            )

            submitted = st.form_submit_button("✅ 記録を追加", use_container_width=True)

            if submitted and facility_name and contact_content:
                service_data = {
                    "facility_name": facility_name,
                    "service_type": service_type,
                    "contact_date": contact_date.isoformat() if contact_date else None,
                    "contact_person": contact_person,
                    "contact_method": contact_method,
                    "contact_content": contact_content
                }

                st.session_state["services"].append(service_data)
                st.success(f"✅ {facility_name}の連絡記録を追加しました")
                st.rerun()

    # 追加済みサービス記録の表示
    if st.session_state["services"]:
        st.markdown("---")
        st.subheader("📋 サービス連絡記録")

        for i, service in enumerate(st.session_state["services"], 1):
            with st.expander(f"記録 {i}: {service['facility_name']} ({service.get('contact_date', '日付未設定')})", expanded=True):
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.write(f"**事業所名**: {service['facility_name']}")
                    st.write(f"**サービス種別**: {service.get('service_type', '未設定')}")
                    st.write(f"**連絡日**: {service.get('contact_date', '未設定')}")
                    st.write(f"**対応者**: {service.get('contact_person', '未記載')}")
                    st.write(f"**連絡方法**: {service.get('contact_method', '未記載')}")
                    st.write(f"**連絡内容**:\n{service.get('contact_content', '')}")

                with col2:
                    if st.button("削除", key=f"delete_service_{i}", type="secondary"):
                        st.session_state["services"].remove(service)
                        st.rerun()
    else:
        st.info("💡 利用予定の事業所との連絡記録を追加してください。")

st.markdown("---")

# Step 5: 計画書生成（プレビュー）
if st.session_state["long_term_goals"]:
    st.header("5️⃣ 計画書プレビュー")

    with st.expander("📄 サービス等利用計画書（案）", expanded=True):
        st.write("## サービス等利用計画書")

        if st.session_state.get("selected_user_id"):
            user = get_user_detail(st.session_state["selected_user_id"])
            if user:
                st.write(f"**利用者名**: {user['name']}")
                st.write(f"**生年月日**: {user['birth_date']} ({user['age']}歳)")
                st.write(f"**障害種別**: {user.get('disability_types', '未設定')}")

        st.write("### 長期目標")
        for i, goal in enumerate(st.session_state["long_term_goals"], 1):
            st.write(f"{i}. {goal['goal_text']}")
            st.write(f"   - 評価期間: {goal['evaluation_period']}")
            st.write(f"   - 評価方法: {goal['evaluation_method']}")

        if st.session_state["short_term_goals"]:
            st.write("### 短期目標")
            for i, goal in enumerate(st.session_state["short_term_goals"], 1):
                st.write(f"{i}. {goal['goal_text']}")
                st.write(f"   - 評価期間: {goal['evaluation_period']}")

        if st.session_state["services"]:
            st.write("### サービス調整")
            for i, service in enumerate(st.session_state["services"], 1):
                st.write(f"{i}. **{service['facility_name']}** ({service['service_type']})")
                st.write(f"   - 利用頻度: {service.get('frequency', '未設定')}")
                st.write(f"   - 利用開始予定日: {service.get('start_date', '未設定')}")

        st.info("📝 正式な計画書生成機能（PDF/Word出力）は今後実装予定です")

    # 保存ボタン
    st.markdown("---")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.caption("⚠️ 計画を保存すると、Neo4jデータベースに永続化されます")

    with col2:
        if st.button("💾 計画を保存", type="primary", use_container_width=True, key="save_plan_button"):
            # 必須項目のチェック
            if not st.session_state.get("selected_user_id"):
                st.error("❌ 利用者を選択してください")
            elif not st.session_state.get("selected_assessment_id"):
                st.error("❌ アセスメントを選択してください")
            elif not st.session_state.get("long_term_goals"):
                st.error("❌ 長期目標を設定してください")
            else:
                try:
                    # 計画データの準備
                    long_term_goals_data = [
                        {
                            "goal": goal["goal_text"],
                            "period": goal.get("evaluation_period", ""),
                            "criteria": goal.get("evaluation_method", "")
                        }
                        for goal in st.session_state["long_term_goals"]
                    ]

                    short_term_goals_data = [
                        {
                            "goal": goal["goal_text"],
                            "period": goal.get("evaluation_period", ""),
                            "criteria": goal.get("evaluation_method", "")
                        }
                        for goal in st.session_state.get("short_term_goals", [])
                    ]

                    services_data = [
                        {
                            "service_type": service["service_type"],
                            "facility_id": service.get("facility_id"),
                            "facility_name": service.get("facility_name"),
                            "frequency": service.get("frequency"),
                            "start_date": service.get("start_date")
                        }
                        for service in st.session_state.get("services", [])
                    ]

                    plan_data = {
                        "user_id": st.session_state["selected_user_id"],
                        "assessment_id": st.session_state["selected_assessment_id"],
                        "long_term_goals": long_term_goals_data,
                        "short_term_goals": short_term_goals_data,
                        "services": services_data,
                        "plan_type": "個別支援計画",
                        "status": "draft"
                    }

                    # API呼び出し
                    response = requests.post(f"{API_BASE_URL}/plans", json=plan_data)

                    if response.status_code == 201:
                        plan = response.json()
                        st.session_state["plan_id"] = plan["plan_id"]
                        logger.info(f"Plan saved successfully: {plan['plan_id']}")

                        st.success(f"✅ 計画を保存しました（計画ID: {plan['plan_id']}）")
                        st.balloons()

                        # 保存後のアクション
                        with st.expander("🎉 保存完了！次のステップ"):
                            st.write("**計画が正常に保存されました**")
                            st.write(f"- 計画ID: `{plan['plan_id']}`")
                            st.write(f"- 長期目標: {len(plan.get('long_term_goals', []))}件")
                            st.write(f"- 短期目標: {len(plan.get('short_term_goals', []))}件")
                            st.write(f"- サービス: {len(plan.get('services', []))}件")
                            st.write("")
                            st.write("**次にできること:**")
                            st.write("1. モニタリングページで進捗を記録")
                            st.write("2. 計画内容を修正（実装予定）")
                            st.write("3. PDF/Wordで出力")

                            # PDF/Wordダウンロードボタン
                            st.markdown("---")
                            col_pdf, col_word = st.columns(2)

                            with col_pdf:
                                pdf_url = f"{API_BASE_URL}/plans/{plan['plan_id']}/pdf"
                                st.link_button(
                                    "📄 PDFをダウンロード",
                                    pdf_url,
                                    use_container_width=True
                                )

                            with col_word:
                                word_url = f"{API_BASE_URL}/plans/{plan['plan_id']}/word"
                                st.link_button(
                                    "📝 Wordをダウンロード",
                                    word_url,
                                    use_container_width=True
                                )

                    else:
                        st.error(f"❌ 保存に失敗しました: {response.text}")
                        logger.error(f"Failed to save plan: {response.status_code} - {response.text}")

                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")
                    logger.error(f"Plan save error: {e}")
