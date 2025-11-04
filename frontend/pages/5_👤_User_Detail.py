# -*- coding: utf-8 -*-
"""
利用者詳細ページ
"""
import streamlit as st
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional

API_BASE_URL = "http://localhost:8001/api"

st.set_page_config(page_title="利用者詳細", page_icon="👤", layout="wide")


def fetch_users():
    """利用者一覧を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/users", params={"page": 1, "page_size": 100})
        response.raise_for_status()
        data = response.json()
        return data.get("users", [])
    except Exception as e:
        st.error(f"利用者一覧取得エラー: {e}")
        return []


def fetch_user_detail(user_id: str):
    """利用者詳細情報を取得"""
    try:
        response = requests.get(f"{API_BASE_URL}/users/{user_id}/detail")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"詳細情報取得エラー: {e}")
        return None


def display_alerts(alerts: List[Dict[str, str]]):
    """アラート表示"""
    if not alerts:
        st.success("✅ 期限内です")
        return

    for alert in alerts:
        severity = alert.get("severity", "medium")
        message = alert.get("message", "")

        if severity == "high":
            st.error(f"🚨 {message}")
        elif severity == "medium":
            st.warning(f"⚠️ {message}")
        else:
            st.info(f"ℹ️ {message}")


def display_basic_info(basic_info: Dict[str, Any]):
    """基本情報カード"""
    st.subheader("📋 基本情報")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("氏名", basic_info.get("name", ""))
        st.write(f"**カナ**: {basic_info.get('name_kana', '')}")

    with col2:
        gender = basic_info.get("gender", "")
        birth_date = basic_info.get("birth_date", "")
        st.metric("性別", gender)
        st.write(f"**生年月日**: {birth_date[:10] if birth_date else ''}")

    with col3:
        disability_type = basic_info.get("disability_type", "")
        support_level = basic_info.get("support_level", "")
        st.metric("障害種別", disability_type)
        st.write(f"**支援区分**: {support_level}")

    with col4:
        living_situation = basic_info.get("living_situation", "")
        st.metric("居住状況", living_situation)


def display_current_services(services: List[Dict[str, Any]]):
    """現在利用中のサービス"""
    st.subheader("🏢 現在利用中のサービス")

    if not services:
        st.info("現在利用中のサービスはありません")
        return

    for service in services:
        with st.expander(f"{service.get('service_type', 'サービス')} - {service.get('facility_name', '')}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**事業所**: {service.get('facility_name', '')}")
                st.write(f"**サービス種別**: {service.get('service_type', '')}")
                st.write(f"**利用頻度**: {service.get('frequency', '')}")

            with col2:
                st.write(f"**開始日**: {service.get('start_date', '')[:10] if service.get('start_date') else ''}")
                st.write(f"**終了予定日**: {service.get('end_date', '')[:10] if service.get('end_date') else ''}")
                st.write(f"**備考**: {service.get('notes', '')}")


def display_recent_monitoring(monitoring: Optional[Dict[str, Any]]):
    """直近のモニタリング結果"""
    st.subheader("📊 直近のモニタリング結果")

    if not monitoring:
        st.info("モニタリング記録がありません")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        monitoring_date = monitoring.get("monitoring_date", "")
        st.metric("実施日", monitoring_date[:10] if monitoring_date else "")

    with col2:
        overall_progress = monitoring.get("overall_progress", "")
        st.metric("全体的な進捗", overall_progress)

    with col3:
        conducted_by = monitoring.get("conducted_by", "")
        st.metric("実施者", conducted_by)

    # 詳細
    with st.expander("詳細を表示"):
        st.write(f"**全体サマリー**: {monitoring.get('overall_summary', monitoring.get('overall_progress', ''))}")

        # 強み
        strengths = monitoring.get('strengths', [])
        if strengths:
            st.write("**強み・進展**:")
            for strength in strengths:
                st.write(f"  • {strength}")

        # 課題
        challenges = monitoring.get('challenges', [])
        if challenges:
            st.write("**課題・懸念事項**:")
            for challenge in challenges:
                st.write(f"  • {challenge}")

        # 家族フィードバック
        family_feedback = monitoring.get('family_feedback', '')
        if family_feedback:
            st.write(f"**家族からのフィードバック**: {family_feedback}")

        # 計画見直しの必要性
        if monitoring.get('plan_revision_needed'):
            st.warning(f"⚠️ 計画見直しが必要: {monitoring.get('revision_reason', '')}")

        # サービス評価
        import json
        service_evals_raw = monitoring.get('service_evaluations_json', [])
        service_evals = []
        if service_evals_raw:
            # JSON文字列の場合はパース
            if isinstance(service_evals_raw, str):
                try:
                    service_evals = json.loads(service_evals_raw)
                except:
                    service_evals = []
            elif isinstance(service_evals_raw, list):
                service_evals = service_evals_raw

        if service_evals:
            st.write("**サービス別評価**:")
            for svc in service_evals:
                with st.container():
                    st.write(f"  📍 {svc.get('service_name', '')}")
                    st.write(f"    出席率: {svc.get('attendance_rate', 0)}% | 満足度: {svc.get('service_satisfaction', 0)}/5")
                    st.write(f"    効果: {svc.get('effectiveness', '')}")
                    if svc.get('issues'):
                        st.write(f"    課題: {svc.get('issues')}")


def display_goal_progress(goals: List[Dict[str, Any]]):
    """目標達成状況"""
    st.subheader("🎯 目標達成状況")

    if not goals:
        st.info("設定されている目標がありません")
        return

    for goal in goals:
        goal_text = goal.get("goal_text", goal.get("goal", "目標"))
        achievement_status = goal.get("achievement_status", "未達成")

        # 進捗率を算出（簡易版）
        progress = 0
        if achievement_status == "達成":
            progress = 100
        elif achievement_status == "一部達成":
            progress = 50
        elif achievement_status == "継続中":
            progress = 30

        st.write(f"**{goal.get('goal_type', '目標')}**: {goal_text}")
        st.progress(progress / 100)
        st.caption(f"状況: {achievement_status}")
        st.divider()


def display_support_timeline(timeline: List[Dict[str, Any]]):
    """支援タイムライン"""
    st.subheader("📅 支援タイムライン")

    if not timeline:
        st.info("記録がありません")
        return

    for event in timeline:
        event_type = event.get("event_type", "")
        event_date = event.get("event_date", "")
        description = event.get("description", "")

        # イベントタイプに応じたアイコン
        icon_map = {
            "assessment": "📝",
            "plan": "📋",
            "monitoring": "📊"
        }
        icon = icon_map.get(event_type, "📌")

        # イベントタイプの日本語名
        type_label_map = {
            "assessment": "アセスメント",
            "plan": "支援計画",
            "monitoring": "モニタリング"
        }
        type_label = type_label_map.get(event_type, event_type)

        # 日付のフォーマット
        date_str = event_date[:10] if event_date else ""

        col1, col2 = st.columns([1, 4])

        with col1:
            st.write(f"**{date_str}**")

        with col2:
            st.write(f"{icon} **{type_label}**: {description}")

        st.divider()


def main():
    st.title("👤 利用者詳細")

    st.markdown("""
    利用者の詳細情報、現在のサービス利用状況、目標達成進捗、支援履歴を確認できます。
    """)

    # 利用者選択
    users = fetch_users()

    if not users:
        st.warning("利用者データがありません。")
        return

    user_options = {f"{user['name']} (ID: {user['user_id'][:8]})": user['user_id'] for user in users}
    selected_user_label = st.selectbox("利用者を選択", options=list(user_options.keys()))

    if not selected_user_label:
        return

    selected_user_id = user_options[selected_user_label]

    if st.button("詳細情報を表示", type="primary"):
        with st.spinner("データ取得中..."):
            detail = fetch_user_detail(selected_user_id)

            if not detail:
                st.error("詳細情報が取得できませんでした")
                return

            # アラート表示（最上部）
            st.markdown("### 🚨 アラート")
            display_alerts(detail.get("alerts", []))
            st.divider()

            # 基本情報
            display_basic_info(detail.get("basic_info", {}))
            st.divider()

            # 2カラムレイアウト
            col1, col2 = st.columns(2)

            with col1:
                # 現在利用中のサービス
                display_current_services(detail.get("current_services", []))

                # 目標達成状況
                display_goal_progress(detail.get("goal_progress", []))

            with col2:
                # 直近のモニタリング
                display_recent_monitoring(detail.get("recent_monitoring"))

                # 支援タイムライン
                display_support_timeline(detail.get("support_timeline", []))


if __name__ == "__main__":
    main()
