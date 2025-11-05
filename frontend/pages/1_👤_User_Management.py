# -*- coding: utf-8 -*-
"""
利用者管理ページ

利用者の登録・編集・一覧表示を行います。
"""
import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime
from typing import Optional, Dict, Any


def kata_to_hira(text: str) -> str:
    """カタカナをひらがなに変換"""
    if not text:
        return ""
    return "".join(
        chr(ord(c) - 96) if 'ァ' <= c <= 'ヶ' else c
        for c in text
    )


def is_valid_kana(text: str) -> bool:
    """
    ふりがなが有効か検証（ひらがな・カタカナ・スペースのみ）

    Args:
        text: 検証する文字列

    Returns:
        有効な場合True、無効な場合False
    """
    if not text:
        return True

    for char in text:
        # ひらがな（ぁ-ん）、カタカナ（ァ-ヶ）、スペース、長音記号、中点のみ許可
        if not (
            ('ぁ' <= char <= 'ん') or
            ('ァ' <= char <= 'ヶ') or
            char in [' ', '　', 'ー', '・']
        ):
            return False
    return True


# ページ設定
st.set_page_config(
    page_title="利用者管理",
    page_icon="👤",
    layout="wide"
)

# API設定
API_BASE_URL = "http://localhost:8000/api"

# セッションステートの初期化
if "selected_user_id" not in st.session_state:
    st.session_state["selected_user_id"] = None
if "edit_mode" not in st.session_state:
    st.session_state["edit_mode"] = False
if "view_user_id" not in st.session_state:
    st.session_state["view_user_id"] = None


def get_users(page: int = 1, page_size: int = 50):
    """利用者一覧を取得"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/users",
            params={"page": page, "page_size": page_size}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"利用者情報の取得に失敗しました: {e}")
        return {"users": [], "total": 0, "page": 1, "page_size": page_size}


def get_user_detail(user_id: str):
    """利用者詳細を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"利用者詳細の取得に失敗しました: {e}")
        return None


def check_duplicate_user(name: str, birth_date: str, exclude_user_id: str = None) -> Optional[Dict[str, Any]]:
    """
    氏名と生年月日で重複ユーザーをチェック

    Args:
        name: 氏名
        birth_date: 生年月日 (YYYY-MM-DD形式)
        exclude_user_id: 除外するユーザーID（編集時に自分自身を除外）

    Returns:
        重複するユーザー情報、または None
    """
    try:
        response = requests.get(f"{API_BASE_URL}/users", params={"page": 1, "page_size": 1000})
        response.raise_for_status()
        all_users = response.json().get("users", [])

        for user in all_users:
            # 編集時は自分自身を除外
            if exclude_user_id and user.get("user_id") == exclude_user_id:
                continue

            # 氏名と生年月日が一致する場合は重複
            if user.get("name") == name and user.get("birth_date") == birth_date:
                return user

        return None
    except Exception as e:
        st.warning(f"重複チェック中にエラーが発生しました: {e}")
        return None


def create_user(user_data: Dict[str, Any]):
    """利用者を登録"""
    try:
        response = requests.post(f"{API_BASE_URL}/users", json=user_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"利用者登録に失敗しました: {e}")
        return None


def update_user(user_id: str, user_data: Dict[str, Any]):
    """利用者情報を更新"""
    try:
        response = requests.put(f"{API_BASE_URL}/users/{user_id}", json=user_data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"利用者情報の更新に失敗しました: {e}")
        return None


def delete_user(user_id: str):
    """利用者を削除"""
    try:
        response = requests.delete(f"{API_BASE_URL}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"利用者の削除に失敗しました: {e}")
        return None


def render_user_form(user_data: Optional[Dict[str, Any]] = None, is_edit: bool = False):
    """利用者登録・編集フォーム"""

    # デフォルト値設定
    if user_data:
        default_name = user_data.get("name", "")
        default_kana = user_data.get("kana", "")
        default_birth_date = datetime.strptime(user_data.get("birth_date", "2000-01-01"), "%Y-%m-%d").date()
        default_gender = user_data.get("gender", "その他")
        default_disability_types = user_data.get("disability_types", "").split(", ") if user_data.get("disability_types") else []
        default_support_level = user_data.get("support_level", "未判定")
        default_address = user_data.get("address", "")
        default_phone = user_data.get("phone", "")
        default_guardian_name = user_data.get("guardian_name", "")
        default_guardian_relation = user_data.get("guardian_relation", "")
        default_notes = user_data.get("notes", "")
    else:
        default_name = ""
        default_kana = ""
        default_birth_date = date(2000, 1, 1)
        default_gender = "その他"
        default_disability_types = []
        default_support_level = "未判定"
        default_address = ""
        default_phone = ""
        default_guardian_name = ""
        default_guardian_relation = ""
        default_notes = ""

    with st.form("user_form"):
        st.subheader("基本情報")

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("氏名（必須）", value=default_name)
            kana = st.text_input(
                "ふりがな（必須）",
                value=default_kana,
                placeholder="例: さとうたろう",
                help="ひらがな・カタカナのみ入力可能です"
            )

            # ふりがなのバリデーション
            if kana and not is_valid_kana(kana):
                st.error("⚠️ ふりがなには漢字や数字、記号は使用できません。ひらがな・カタカナのみで入力してください。")

            birth_date = st.date_input(
                "生年月日",
                value=default_birth_date,
                min_value=date(1920, 1, 1),
                max_value=date.today()
            )
            gender = st.selectbox(
                "性別",
                ["男性", "女性", "その他"],
                index=["男性", "女性", "その他"].index(default_gender) if default_gender in ["男性", "女性", "その他"] else 2
            )

        with col2:
            disability_types = st.multiselect(
                "障害種別（必須・複数選択可）",
                ["知的障害", "精神障害", "知的障害（発達障害）", "身体障害", "難病"],
                default=default_disability_types,
                help="最低1つは選択してください"
            )
            support_level = st.selectbox(
                "障害支援区分",
                ["未判定", "区分1", "区分2", "区分3", "区分4", "区分5", "区分6"],
                index=["未判定", "区分1", "区分2", "区分3", "区分4", "区分5", "区分6"].index(default_support_level) if default_support_level in ["未判定", "区分1", "区分2", "区分3", "区分4", "区分5", "区分6"] else 0
            )

        st.subheader("手帳情報")

        col_notebook1, col_notebook2 = st.columns(2)

        with col_notebook1:
            st.write("**療育手帳**")
            therapy_notebook = st.checkbox(
                "療育手帳あり",
                value=user_data.get("therapy_notebook", False) if user_data else False
            )
            therapy_notebook_grade = st.selectbox(
                "療育手帳等級",
                ["未取得", "A", "B1", "B2", "A3"],
                index=0 if not therapy_notebook else (
                    ["未取得", "A", "B1", "B2", "A3"].index(user_data.get("therapy_notebook_grade", "未取得"))
                    if user_data and user_data.get("therapy_notebook_grade") in ["未取得", "A", "B1", "B2", "A3"]
                    else 0
                ),
                disabled=not therapy_notebook
            )

        with col_notebook2:
            st.write("**精神保健福祉手帳**")
            mental_health_notebook = st.checkbox(
                "精神保健福祉手帳あり",
                value=user_data.get("mental_health_notebook", False) if user_data else False
            )
            mental_health_notebook_grade = st.selectbox(
                "精神保健福祉手帳等級",
                ["未取得", "1級", "2級", "3級"],
                index=0 if not mental_health_notebook else (
                    ["未取得", "1級", "2級", "3級"].index(user_data.get("mental_health_notebook_grade", "未取得"))
                    if user_data and user_data.get("mental_health_notebook_grade") in ["未取得", "1級", "2級", "3級"]
                    else 0
                ),
                disabled=not mental_health_notebook
            )

            # 精神保健福祉手帳の有効期限
            mental_health_notebook_expiry = None
            if mental_health_notebook:
                default_expiry = None
                if user_data and user_data.get("mental_health_notebook_expiry"):
                    try:
                        default_expiry = datetime.strptime(
                            user_data.get("mental_health_notebook_expiry"), "%Y-%m-%d"
                        ).date()
                    except:
                        default_expiry = None

                mental_health_notebook_expiry = st.date_input(
                    "有効期限",
                    value=default_expiry if default_expiry else date.today(),
                    min_value=date.today(),
                    help="精神保健福祉手帳の有効期限（通常2年間）"
                )

        st.subheader("連絡先情報")

        col3, col4 = st.columns(2)

        with col3:
            address = st.text_input("住所", value=default_address)
            phone = st.text_input("電話番号", value=default_phone)

        with col4:
            guardian_name = st.text_input("保護者・緊急連絡先氏名", value=default_guardian_name)
            guardian_relation = st.text_input("続柄", value=default_guardian_relation)

        st.subheader("備考")
        notes = st.text_area(
            "特記事項",
            value=default_notes,
            height=100,
            placeholder="その他、特記すべき情報があれば記載してください"
        )

        submitted = st.form_submit_button(
            "更新" if is_edit else "登録",
            type="primary",
            use_container_width=True
        )

        if submitted:
            if not name:
                st.error("氏名は必須項目です")
                return None
            if not kana:
                st.error("ふりがなは必須項目です")
                return None
            if not is_valid_kana(kana):
                st.error("⚠️ ふりがなには漢字や数字、記号は使用できません。ひらがな・カタカナのみで入力してください。")
                return None
            if not disability_types:
                st.error("⚠️ 障害種別は必須項目です。最低1つ選択してください。")
                return None

            # 重複チェック（新規登録時のみ、または編集時は自分以外）
            birth_date_str = birth_date.strftime("%Y-%m-%d")
            exclude_id = user_data.get("user_id") if user_data else None
            duplicate_user = check_duplicate_user(name, birth_date_str, exclude_user_id=exclude_id)

            if duplicate_user:
                st.error(f"⚠️ この利用者は既に登録されています")
                st.warning(f"既存の利用者: {duplicate_user.get('name')} ({duplicate_user.get('birth_date')})")
                st.info("同姓同名で生年月日が異なる場合は登録可能です")
                return None

            # カタカナが入力された場合はひらがなに変換
            kana_hira = kata_to_hira(kana)

            # バックエンドのUserCreateモデルに合わせたフィールド名
            user_data_dict = {
                "name": name,
                "kana": kana_hira,
                "birth_date": birth_date.strftime("%Y-%m-%d"),
                "gender": gender if gender else None,
                "disability_type": ", ".join(disability_types) if disability_types else "未設定",  # 必須フィールド
                "support_level": support_level if support_level else None,
                "therapy_notebook": therapy_notebook,
                "therapy_notebook_grade": therapy_notebook_grade if therapy_notebook and therapy_notebook_grade != "未取得" else None,
                "mental_health_notebook": mental_health_notebook,
                "mental_health_notebook_grade": mental_health_notebook_grade if mental_health_notebook and mental_health_notebook_grade != "未取得" else None,
                "mental_health_notebook_expiry": mental_health_notebook_expiry.strftime("%Y-%m-%d") if mental_health_notebook and mental_health_notebook_expiry else None,
                "contact_address": address if address else None,  # addressではなくcontact_address
                "contact_phone": phone if phone else None,  # phoneではなくcontact_phone
                "guardian_name": guardian_name if guardian_name else None,
                "guardian_relation": guardian_relation if guardian_relation else None,
                # notesフィールドはバックエンドに存在しないため削除
            }

            return user_data_dict

    return None


def render_user_list():
    """利用者一覧表示"""
    st.subheader("📋 利用者一覧")

    # 削除成功メッセージの表示
    if "delete_success_message" in st.session_state:
        st.success(st.session_state["delete_success_message"])
        del st.session_state["delete_success_message"]

    # 検索フィルター
    # 利用者一覧取得（フィルタリング前に全件取得）
    users_data = get_users()
    all_users = users_data.get("users", [])

    # 左右2列レイアウト
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.subheader("🔍 検索条件")

        # 障害種別で絞り込み
        filter_disability = st.selectbox(
            "障害種別",
            ["すべて", "知的障害", "精神障害", "知的障害（発達障害）", "身体障害", "難病"]
        )

        # 支援区分で絞り込み
        filter_support_level = st.selectbox(
            "支援区分",
            ["すべて", "未判定", "区分1", "区分2", "区分3", "区分4", "区分5", "区分6"]
        )

        # 氏名検索（テキスト入力）
        search_name = st.text_input(
            "氏名で絞り込み（ふりがな検索）",
            placeholder="例: やま",
            help="ふりがなの一部を入力してEnterキーを押すと、該当する利用者のみが右側に表示されます",
            key="user_search_input"
        )

    # フィルタリング処理
    filtered_users = all_users

    # 障害種別でフィルタリング
    if filter_disability != "すべて":
        temp_users = []
        for u in filtered_users:
            # APIからはdisability_type（単数形）で返される
            disability_type_str = u.get("disability_type", "")
            if disability_type_str:
                disability_list = [d.strip() for d in disability_type_str.split(",")]
                if filter_disability in disability_list:
                    temp_users.append(u)
        filtered_users = temp_users

    # 支援区分でフィルタリング
    if filter_support_level != "すべて":
        filtered_users = [u for u in filtered_users if filter_support_level == u.get("support_level", "")]

    # 氏名でフィルタリング（ふりがなでの曖昧検索）
    if search_name:
        search_name_hira = kata_to_hira(search_name.lower())
        # ふりがな（kana）フィールドで検索（ひらがな・カタカナ両方に対応）
        # 例: 「さ」を入力すると「さとうたろう」または「サトウタロウ」が検索される
        filtered_users = [
            u for u in filtered_users
            if search_name_hira in kata_to_hira((u.get("kana") or "").lower()) or  # ふりがなで検索（カタカナ→ひらがな変換）
               search_name_hira in (u.get("name") or "").lower()      # 氏名でも検索
        ]

    # 右側に候補リスト表示
    with right_col:
        st.subheader(f"📋 該当利用者 ({len(filtered_users)}件)")

        if not filtered_users:
            st.info("該当する利用者がいません")
        else:
            # シンプルなテーブル形式で表示
            st.markdown("クリックして選択してください")

            for idx, user in enumerate(filtered_users):
                # 1行ずつ表示（クリック可能）
                col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 2, 2, 2.5])

                with col1:
                    st.write(f"**{user['name']}**")
                with col2:
                    kana = user.get('kana') or '未登録'
                    st.caption(f"({kana})")
                with col3:
                    st.write(f"{user['age']}歳")
                with col4:
                    # APIからはdisability_type（単数形）で返される
                    disability = user.get('disability_type', '未設定')
                    if len(disability) > 10:
                        st.write(disability[:10] + "...")
                    else:
                        st.write(disability)
                with col5:
                    st.write(user.get('support_level', '未判定'))
                with col6:
                    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                    with action_col1:
                        if st.button("👁️", key=f"view_{user['user_id']}", help="詳細"):
                            st.session_state["view_user_id"] = user["user_id"]
                            st.rerun()
                    with action_col2:
                        if st.button("✏️", key=f"edit_{user['user_id']}", help="編集"):
                            st.session_state["selected_user_id"] = user["user_id"]
                            st.session_state["edit_mode"] = True
                            st.rerun()
                    with action_col3:
                        if st.button("📊", key=f"assess_{user['user_id']}", help="アセスメント"):
                            st.session_state["selected_user_id"] = user["user_id"]
                            st.switch_page("pages/2_📊_Assessment.py")
                    with action_col4:
                        if st.button("🗑️", key=f"delete_{user['user_id']}", help="削除"):
                            st.session_state["confirm_delete_list_user_id"] = user["user_id"]
                            st.rerun()

                # 削除確認ダイアログ（この利用者行の下に表示）
                if st.session_state.get("confirm_delete_list_user_id") == user["user_id"]:
                    st.warning(f"⚠️ 本当に **{user['name']}** さんを削除しますか？この操作は取り消せません。")
                    confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 4])

                    with confirm_col1:
                        if st.button("✓ 削除実行", type="primary", key=f"confirm_delete_{user['user_id']}", use_container_width=True):
                            user_name = user['name']
                            result = delete_user(user["user_id"])
                            # 削除処理完了後、セッションステートをクリアして即座にリロード
                            st.session_state["confirm_delete_list_user_id"] = None
                            if result:
                                st.session_state["delete_success_message"] = f"✓ {user_name}さんの情報を削除しました"
                            st.rerun()

                    with confirm_col2:
                        if st.button("✗ キャンセル", key=f"cancel_delete_{user['user_id']}", use_container_width=True):
                            st.session_state["confirm_delete_list_user_id"] = None
                            st.rerun()

                if idx < len(filtered_users) - 1:
                    st.divider()


def render_user_detail(user_id: str):
    """利用者詳細表示"""
    user = get_user_detail(user_id)

    if not user:
        st.error("利用者情報が見つかりません")
        return

    st.subheader(f"👤 {user['name']} さんの詳細情報")

    # 戻るボタン
    if st.button("← 一覧に戻る"):
        st.session_state["view_user_id"] = None
        st.rerun()

    st.markdown("---")

    # 基本情報
    st.write("### 📝 基本情報")
    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**氏名**: {user['name']}")
        st.write(f"**生年月日**: {user['birth_date']}")
        st.write(f"**年齢**: {user['age']}歳")
        st.write(f"**性別**: {user['gender']}")

    with col2:
        st.write(f"**障害種別**: {user.get('disability_type', '未設定')}")
        st.write(f"**支援区分**: {user.get('support_level', '未判定')}")
        st.write(f"**居住状況**: {user.get('living_situation', '未設定')}")
        st.write(f"**電話**: {user.get('contact_phone', '未設定')}")

    # 手帳情報
    disability_type = user.get("disability_type", "")
    therapy_notebook_grade = user.get("therapy_notebook_grade", "")
    mental_health_notebook_grade = user.get("mental_health_notebook_grade", "")
    mental_health_notebook_expiry = user.get("mental_health_notebook_expiry", "")

    if therapy_notebook_grade or mental_health_notebook_grade:
        st.write("")
        st.write("**📋 手帳情報**")

        if "知的" in disability_type and therapy_notebook_grade:
            st.write(f"  • 療育手帳: {therapy_notebook_grade}")

        if "精神" in disability_type and mental_health_notebook_grade:
            expiry_info = ""
            if mental_health_notebook_expiry:
                expiry_date_str = mental_health_notebook_expiry[:10]
                expiry_info = f" (有効期限: {expiry_date_str})"

                # 有効期限警告
                try:
                    from datetime import datetime
                    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                    today = datetime.now().date()
                    days_until = (expiry_date - today).days

                    if days_until < 0:
                        expiry_info += " ⚠️期限切れ"
                    elif days_until <= 90:
                        expiry_info += f" ⚠️残り{days_until}日"
                except:
                    pass

            st.write(f"  • 精神保健福祉手帳: {mental_health_notebook_grade}{expiry_info}")

    if user.get("guardian_name"):
        st.write("")
        st.write(f"**保護者**: {user['guardian_name']} ({user.get('guardian_relation', '')})")

    st.markdown("---")

    # アセスメント履歴
    st.write("### 📊 アセスメント履歴")
    try:
        assessments_response = requests.get(f"{API_BASE_URL}/assessments/user/{user_id}")
        if assessments_response.status_code == 200:
            assessments = assessments_response.json()
            if assessments:
                assessment_df = pd.DataFrame([
                    {
                        "実施日": a.get("interview_date", ""),
                        "参加者": a.get("interview_participants", ""),
                        "信頼度": f"{a.get('confidence_score', 0):.0%}" if a.get('confidence_score') else "未分析",
                        "作成日": a.get("created_at", "")[:10] if a.get("created_at") else "",
                        "ID": a.get("assessment_id", "")
                    }
                    for a in assessments
                ])
                st.dataframe(assessment_df, use_container_width=True, hide_index=True)
            else:
                st.info("アセスメント履歴がありません")
        else:
            st.warning("アセスメント履歴の取得に失敗しました")
    except Exception as e:
        st.error(f"エラー: {str(e)}")

    # 支援計画履歴
    st.write("### 🎯 支援計画履歴")
    try:
        plans_response = requests.get(f"{API_BASE_URL}/plans/user/{user_id}")
        if plans_response.status_code == 200:
            plans = plans_response.json()
            if plans:
                plan_df = pd.DataFrame([
                    {
                        "計画期間": f"{p.get('start_date', '')} 〜 {p.get('end_date', '')}",
                        "長期目標数": len(p.get('long_term_goals', [])),
                        "短期目標数": len(p.get('short_term_goals', [])),
                        "ステータス": p.get('status', ''),
                        "作成日": p.get("created_at", "")[:10] if p.get("created_at") else "",
                        "ID": p.get("plan_id", "")
                    }
                    for p in plans
                ])
                st.dataframe(plan_df, use_container_width=True, hide_index=True)
            else:
                st.info("支援計画履歴がありません")
        else:
            st.warning("支援計画履歴の取得に失敗しました")
    except Exception as e:
        st.error(f"エラー: {str(e)}")

    # アクションボタン
    st.markdown("---")

    # 主要アクション
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📝 編集", type="primary", use_container_width=True):
            st.session_state["selected_user_id"] = user_id
            st.session_state["edit_mode"] = True
            st.session_state["view_user_id"] = None
            st.rerun()

    with col2:
        if st.button("📊 アセスメント実施", use_container_width=True):
            st.session_state["selected_user_id"] = user_id
            st.switch_page("pages/2_📊_Assessment.py")

    with col3:
        if st.button("🎯 支援計画作成", use_container_width=True):
            st.session_state["selected_user_id"] = user_id
            st.switch_page("pages/3_🎯_Plan_Creation.py")

    with col4:
        if st.button("📈 詳細ダッシュボード", use_container_width=True):
            st.session_state["selected_user_id"] = user_id
            st.switch_page("pages/5_👤_User_Detail.py")

    # 削除ボタン（別行）
    st.write("")
    col_delete1, col_delete2, col_delete3 = st.columns([3, 1, 3])
    with col_delete2:
        if st.button("🗑️ 削除", use_container_width=True):
            st.session_state["confirm_delete_user_id"] = user_id
            st.rerun()

    # 削除確認ダイアログ
    if st.session_state.get("confirm_delete_user_id") == user_id:
        st.warning("⚠️ 本当に削除しますか？この操作は取り消せません。")
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("✓ 削除実行", type="primary", use_container_width=True):
                result = delete_user(user_id)
                if result:
                    st.success(f"✓ {user['name']}さんの情報を削除しました")
                    # 削除後は一覧に戻る
                    st.session_state["view_user_id"] = None
                    st.session_state["confirm_delete_user_id"] = None
                    st.rerun()
                else:
                    st.session_state["confirm_delete_user_id"] = None

        with col2:
            if st.button("✗ キャンセル", use_container_width=True):
                st.session_state["confirm_delete_user_id"] = None
                st.rerun()


# メイン処理
st.title("👤 利用者管理")

# クイックナビゲーション
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    if st.button("📊 アセスメント", use_container_width=True):
        st.switch_page("pages/2_📊_Assessment.py")
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

# タブ構成
tab1, tab2, tab3 = st.tabs(["📋 利用者一覧", "➕ 新規登録", "✏️ 編集"])

with tab1:
    # 詳細表示モード
    if st.session_state.get("view_user_id"):
        render_user_detail(st.session_state["view_user_id"])
    else:
        render_user_list()

with tab2:
    st.subheader("➕ 新規利用者登録")
    user_data = render_user_form(is_edit=False)

    if user_data:
        result = create_user(user_data)
        if result:
            st.success(f"✅ {user_data['name']} さんを登録しました")
            st.session_state["selected_user_id"] = result.get("user_id")

            # アセスメントへ進むか確認
            if st.button("アセスメント実施へ →", type="primary", use_container_width=True):
                st.switch_page("pages/2_📊_Assessment.py")

with tab3:
    if st.session_state.get("edit_mode") and st.session_state.get("selected_user_id"):
        user = get_user_detail(st.session_state["selected_user_id"])

        if user:
            st.subheader(f"✏️ {user['name']} さんの情報を編集")

            if st.button("← キャンセル"):
                st.session_state["edit_mode"] = False
                st.session_state["selected_user_id"] = None
                st.rerun()

            updated_data = render_user_form(user_data=user, is_edit=True)

            if updated_data:
                result = update_user(st.session_state["selected_user_id"], updated_data)
                if result:
                    st.success(f"✅ {updated_data['name']} さんの情報を更新しました")
                    st.session_state["edit_mode"] = False
                    st.session_state["selected_user_id"] = None
                    st.rerun()
    else:
        st.info("編集する利用者を一覧から選択してください")
