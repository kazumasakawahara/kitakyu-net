# -*- coding: utf-8 -*-
"""
アセスメントページ - 既存利用者を選択してアセスメント実施
"""
import streamlit as st
import requests
from datetime import date
from loguru import logger


def kata_to_hira(text: str) -> str:
    """カタカナをひらがなに変換"""
    if not text:
        return ""
    return "".join(
        chr(ord(c) - 96) if 'ァ' <= c <= 'ヶ' else c
        for c in text
    )


# ページ設定
st.set_page_config(page_title="アセスメント", page_icon="📊", layout="wide")

# CSSでセレクトボックスのドロップダウンリストを右にオフセット
st.markdown("""
<style>
    /* セレクトボックスのドロップダウンメニューを右に200pxずらす（約5cm） */
    div[data-baseweb="select"] > div:last-child {
        margin-left: 200px !important;
    }
    /* ドロップダウンリストの幅を調整 */
    div[data-baseweb="popover"] {
        margin-left: 200px !important;
    }
</style>
""", unsafe_allow_html=True)

# API設定
API_BASE_URL = "http://localhost:8000/api"

# セッション状態の初期化
if "selected_user_id" not in st.session_state:
    st.session_state.selected_user_id = None
if "selected_user_name" not in st.session_state:
    st.session_state.selected_user_name = None
if "assessment_id" not in st.session_state:
    st.session_state.assessment_id = None

# ページタイトル
st.title("📊 アセスメント")

# クイックナビゲーション
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    if st.button("👤 利用者管理", use_container_width=True):
        st.switch_page("pages/1_👤_User_Management.py")
with col2:
    if st.button("🎯 支援計画", use_container_width=True):
        st.switch_page("pages/3_🎯_Plan_Creation.py")
with col3:
    if st.button("🏥 施設検索", use_container_width=True):
        st.switch_page("pages/4_🏥_Facility_Search.py")
with col4:
    if st.button("📈 モニタリング", use_container_width=True):
        st.switch_page("pages/4_📊_Monitoring.py")

st.markdown("---")

# 利用者選択セクション
st.header("1️⃣ 利用者選択")

try:
    # 利用者一覧を取得
    response = requests.get(
        f"{API_BASE_URL}/users",
        params={"page": 1, "page_size": 100},
        timeout=10
    )

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

            # セレクトボックスによる選択（曖昧検索対応）
            st.caption("💡 セレクトボックスで氏名やふりがなの一部を入力すると絞り込めます（例: す、すずき、鈴木）")

            # セレクトボックス用のオプションを作成（ひらがな検索対応）
            # 表示文字列にひらがなも含めることで、ひらがな入力でも検索可能にする
            user_select_options = {}
            user_select_options["選択してください"] = None

            for user in all_users:
                # カタカナとひらがな両方を含む検索用文字列
                kana = user.get('kana', '')
                hira = kata_to_hira(kana)
                # 表示用の文字列（カタカナとひらがな両方を含める）
                display_name = f"{user['name']}（{kana} {hira}） {user['age']}歳"
                # 元の表示名もマッピングに追加（既存のuser_optionsとの互換性のため）
                original_display = f"{user['name']}（{kana}） {user['age']}歳"
                user_select_options[display_name] = original_display
                # 既存のuser_optionsも保持
                user_options[original_display] = user

            # セレクトボックス（Streamlitの標準検索機能を使用）
            selected_search_name = st.selectbox(
                "利用者選択",
                options=list(user_select_options.keys()),
                key="user_select"
            )

            if selected_search_name != "選択してください":
                # 元の表示名を取得
                original_display_name = user_select_options[selected_search_name]
                selected_user = user_options[original_display_name]
                st.session_state.selected_user_id = selected_user["user_id"]
                st.session_state.selected_user_name = selected_user["name"]

                # 選択された利用者の基本情報を表示
                with st.expander("📝 利用者基本情報", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**氏名**: {selected_user['name']}")
                        st.write(f"**年齢**: {selected_user.get('age')}歳")
                    with col2:
                        st.write(f"**障害種別**: {selected_user.get('disability_type')}")
                        st.write(f"**支援区分**: {selected_user.get('support_level')}")
                    with col3:
                        st.write(f"**居住状況**: {selected_user.get('living_situation')}")
                        st.write(f"**電話番号**: {selected_user.get('contact_phone')}")
        else:
            st.warning("⚠️ 登録されている利用者がいません。先に利用者登録を行ってください。")

    else:
        st.error(f"利用者一覧の取得に失敗しました: {response.text}")

except Exception as e:
    st.error(f"エラー: {e}")

# アセスメント実施セクション（利用者が選択されている場合のみ表示）
if st.session_state.selected_user_id:
    st.markdown("---")
    st.header("2️⃣ アセスメント実施")

    st.info(f"**対象利用者**: {st.session_state.selected_user_name}")

    # アセスメント情報入力
    interview_date = st.date_input("ヒアリング実施日", value=date.today())

    interview_participants = st.text_input(
        "ヒアリング参加者",
        placeholder="例: 本人、家族（母）、相談支援専門員",
        help="面談に参加した方を記載してください"
    )

    st.subheader("📝 ヒアリング内容")
    st.caption("各項目について聞き取った内容を入力してください")

    # 本人の希望
    with st.expander("💭 本人の希望・目標", expanded=True):
        st.caption("本人がどのような生活を送りたいか、何を目指しているか")
        user_wishes = st.text_area(
            "本人の希望",
            height=100,
            placeholder="例：\n- 働きたい\n- 一人暮らしをしたい\n- 友達を作りたい",
            key="user_wishes",
            label_visibility="collapsed"
        )

    # 家族の希望
    with st.expander("👨‍👩‍👧 家族の希望・心配事", expanded=True):
        st.caption("家族が期待していること、心配していること")
        family_wishes = st.text_area(
            "家族の希望",
            height=100,
            placeholder="例：\n- 無理のない範囲で社会参加してほしい\n- 健康管理をしっかりしてほしい",
            key="family_wishes",
            label_visibility="collapsed"
        )

    # 本人の強み・得意なこと
    with st.expander("✨ 本人の強み・得意なこと・好きなこと", expanded=True):
        st.caption("本人ができること、得意なこと、興味があること")
        strengths = st.text_area(
            "強み",
            height=100,
            placeholder="例：\n- 単純作業は丁寧にできる\n- 服薬管理はできている\n- 音楽が好き",
            key="strengths_input",
            label_visibility="collapsed"
        )

    # 生活状況・日常生活
    with st.expander("🏠 生活状況・日常生活の様子", expanded=True):
        st.caption("現在の生活環境、日常の過ごし方")
        daily_life = st.text_area(
            "生活状況",
            height=100,
            placeholder="例：\n- 現在は家族と同居\n- 生活リズムが不規則\n- 金銭管理が苦手",
            key="daily_life",
            label_visibility="collapsed"
        )

    # 支援が必要な課題
    with st.expander("⚠️ 支援が必要な課題・困りごと", expanded=True):
        st.caption("本人が困っていること、支援が必要なこと")
        challenges = st.text_area(
            "課題",
            height=100,
            placeholder="例：\n- 対人関係に不安がある\n- 金銭管理ができない\n- コミュニケーションが苦手",
            key="challenges_input",
            label_visibility="collapsed"
        )

    # 社会参加・人との関わり
    with st.expander("🤝 社会参加・人との関わり", expanded=True):
        st.caption("現在の社会参加状況、人間関係")
        social_participation = st.text_area(
            "社会参加",
            height=100,
            placeholder="例：\n- 外出は週1回程度\n- 友人はいない\n- デイサービスに通っている",
            key="social_participation",
            label_visibility="collapsed"
        )

    # 現在利用しているサービス
    with st.expander("🏢 現在利用しているサービス", expanded=True):
        st.caption("既に利用している福祉サービス、医療機関等")
        current_services = st.text_area(
            "現在のサービス",
            height=100,
            placeholder="例：\n- 就労継続支援B型（週3日）\n- 精神科クリニック（月1回通院）",
            key="current_services",
            label_visibility="collapsed"
        )

    # 健康状態・医療的ケア
    with st.expander("💊 健康状態・医療的ケア", expanded=True):
        st.caption("健康状態、服薬状況、医療的配慮が必要なこと")
        health_status = st.text_area(
            "健康状態",
            height=100,
            placeholder="例：\n- 統合失調症（服薬中）\n- てんかんの既往あり\n- アレルギーなし",
            key="health_status",
            label_visibility="collapsed"
        )

    # その他・特記事項
    with st.expander("📌 その他・特記事項", expanded=False):
        st.caption("上記以外で重要な情報、特に配慮が必要なこと")
        other_notes = st.text_area(
            "特記事項",
            height=100,
            placeholder="例：\n- 大きな音が苦手\n- 視覚的な指示が分かりやすい\n- 午前中は調子が悪い",
            key="other_notes",
            label_visibility="collapsed"
        )

    if st.button("アセスメント実施 (AI分析)", type="primary"):
        # 入力内容を統合
        interview_sections = []

        if user_wishes:
            interview_sections.append(f"【本人の希望・目標】\n{user_wishes}")
        if family_wishes:
            interview_sections.append(f"【家族の希望・心配事】\n{family_wishes}")
        if strengths:
            interview_sections.append(f"【本人の強み・得意なこと】\n{strengths}")
        if daily_life:
            interview_sections.append(f"【生活状況・日常生活】\n{daily_life}")
        if challenges:
            interview_sections.append(f"【支援が必要な課題】\n{challenges}")
        if social_participation:
            interview_sections.append(f"【社会参加・人との関わり】\n{social_participation}")
        if current_services:
            interview_sections.append(f"【現在利用しているサービス】\n{current_services}")
        if health_status:
            interview_sections.append(f"【健康状態・医療的ケア】\n{health_status}")
        if other_notes:
            interview_sections.append(f"【その他・特記事項】\n{other_notes}")

        interview_content = "\n\n".join(interview_sections)

        if not interview_content:
            st.error("少なくとも1つの項目にヒアリング内容を入力してください")
        else:
            assessment_data = {
                "user_id": st.session_state.selected_user_id,
                "interview_date": str(interview_date),
                "interview_participants": interview_participants if interview_participants else None,
                "interview_content": interview_content,
                "analyze": True,
            }

            with st.spinner("AI分析中..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/assessments",
                        json=assessment_data,
                        timeout=60
                    )

                    if response.status_code == 201:
                        assessment = response.json()
                        st.session_state.assessment_id = assessment["assessment_id"]

                        st.success("✅ アセスメント完了")

                        # 分析結果の表示
                        st.markdown("---")
                        st.header("3️⃣ AI分析結果")

                        # 分析されたニーズ
                        with st.expander("🎯 分析されたニーズ", expanded=True):
                            if assessment.get("analyzed_needs"):
                                for i, need in enumerate(assessment.get("analyzed_needs", []), 1):
                                    st.markdown(f"**{i}.** {need}")
                            else:
                                st.info("ニーズが分析されませんでした")

                        # 本人の強み
                        with st.expander("✨ 本人の強み・活用できる能力", expanded=True):
                            if assessment.get("strengths"):
                                for i, strength in enumerate(assessment.get("strengths", []), 1):
                                    st.markdown(f"**{i}.** {strength}")
                            else:
                                st.info("強みが特定されませんでした")

                        # 支援が必要な課題
                        with st.expander("⚠️ 支援が必要な課題", expanded=True):
                            if assessment.get("challenges"):
                                for i, challenge in enumerate(assessment.get("challenges", []), 1):
                                    st.markdown(f"**{i}.** {challenge}")
                            else:
                                st.info("課題が特定されませんでした")

                        # 本人の希望
                        if assessment.get("preferences"):
                            with st.expander("💭 本人の希望", expanded=False):
                                for i, pref in enumerate(assessment.get("preferences", []), 1):
                                    st.markdown(f"**{i}.** {pref}")

                        # 家族の希望
                        if assessment.get("family_wishes"):
                            with st.expander("👨‍👩‍👧 家族の希望", expanded=False):
                                for i, wish in enumerate(assessment.get("family_wishes", []), 1):
                                    st.markdown(f"**{i}.** {wish}")

                        # ICF分類（詳細情報として折りたたみ）
                        if assessment.get("icf_classification"):
                            with st.expander("📊 ICF分類による分析", expanded=False):
                                icf = assessment.get("icf_classification", {})
                                if icf.get("body_functions"):
                                    st.markdown(f"**心身機能**: {icf.get('body_functions')}")
                                if icf.get("activities"):
                                    st.markdown(f"**活動**: {icf.get('activities')}")
                                if icf.get("participation"):
                                    st.markdown(f"**参加**: {icf.get('participation')}")
                                if icf.get("environmental_factors"):
                                    st.markdown(f"**環境因子**: {icf.get('environmental_factors')}")
                                if icf.get("personal_factors"):
                                    st.markdown(f"**個人因子**: {icf.get('personal_factors')}")

                        # 追加質問の生成（エラーがあってもアセスメント結果は表示済み）
                        st.markdown("---")
                        try:
                            with st.spinner("追加質問を生成中..."):
                                questions_response = requests.post(
                                    f"{API_BASE_URL}/assessments/followup-questions",
                                    json={"interview_content": interview_content},
                                    timeout=30
                                )

                                if questions_response.status_code == 200:
                                    questions_data = questions_response.json()

                                    if not questions_data.get("is_sufficient", True):
                                        st.warning("💡 さらに詳しくお聞かせください")
                                        st.write(f"**不足している情報**: {', '.join(questions_data.get('missing_areas', []))}")

                                        # 追加質問の表示
                                        st.subheader("📝 追加のヒアリング項目")
                                        for i, q in enumerate(questions_data.get("questions", []), 1):
                                            with st.expander(f"{i}. {q.get('category')}: {q.get('question')}"):
                                                st.write(f"**目的**: {q.get('purpose')}")
                                                additional_answer = st.text_area(
                                                    "回答",
                                                    key=f"additional_q_{i}",
                                                    placeholder="ここに回答を入力してください..."
                                                )

                                        # 追加情報を反映するボタン
                                        if st.button("追加情報を反映して再分析", type="secondary"):
                                            # 追加回答を収集
                                            additional_info = []
                                            for i, q in enumerate(questions_data.get("questions", []), 1):
                                                answer = st.session_state.get(f"additional_q_{i}")
                                                if answer:
                                                    additional_info.append(f"Q: {q.get('question')}\nA: {answer}")

                                            if additional_info:
                                                # ヒアリング内容に追加
                                                updated_content = interview_content + "\n\n【追加情報】\n" + "\n\n".join(additional_info)

                                                # 再分析
                                                with st.spinner("再分析中..."):
                                                    reanalyze_data = {
                                                        "user_id": st.session_state.selected_user_id,
                                                        "interview_date": str(interview_date),
                                                        "interview_content": updated_content,
                                                        "analyze": True,
                                                    }
                                                    response = requests.post(
                                                        f"{API_BASE_URL}/assessments",
                                                        json=reanalyze_data,
                                                        timeout=60
                                                    )
                                                    if response.status_code == 201:
                                                        st.success("✅ 再分析完了しました。ページをリロードして確認してください。")
                                                        st.rerun()
                                    else:
                                        st.success("✅ 十分な情報が揃っています")
                                else:
                                    st.info("追加質問の生成をスキップしました")
                        except Exception as e:
                            st.info("追加質問の生成をスキップしました（アセスメント結果は正常に保存されています）")
                            logger.warning(f"追加質問生成に失敗: {e}")

                        # 次のステップへの案内
                        st.markdown("---")
                        st.subheader("📋 次のステップ")

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.info("アセスメントが完了しました。次は計画作成ページでサービス利用計画を作成しましょう。")
                        with col2:
                            if st.button("計画作成へ →", type="primary", use_container_width=True, key="goto_plan_creation"):
                                # アセスメントIDを計画作成用に保存
                                if "assessment_id" in st.session_state:
                                    st.session_state["selected_assessment_id"] = st.session_state["assessment_id"]
                                    logger.info(f"Navigating to plan creation with assessment_id: {st.session_state['assessment_id']}")
                                    st.switch_page("pages/3_🎯_Plan_Creation.py")
                                else:
                                    st.error("アセスメントIDが見つかりません。もう一度アセスメントを実施してください。")

                    else:
                        st.error(f"エラー: {response.text}")

                except Exception as e:
                    st.error(f"分析失敗: {e}")
