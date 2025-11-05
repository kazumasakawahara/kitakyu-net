# -*- coding: utf-8 -*-
"""
Streamlit frontend for facility search assistant.

User-friendly chat interface for searching disability welfare facilities.
"""
import streamlit as st
import requests
from typing import Dict, Any
import json

# API endpoint configuration
API_BASE_URL = "http://localhost:8000"


def get_health_status() -> Dict[str, Any]:
    """Get API health status."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_stats() -> Dict[str, Any]:
    """Get database statistics."""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def search_facilities(query: str) -> Dict[str, Any]:
    """Search facilities using natural language."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/search",
            json={"query": query},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        # Debug logging
        print(f"DEBUG: API Response status={response.status_code}")
        print(f"DEBUG: facility_count={data.get('facility_count', 0)}")
        print(f"DEBUG: search_params={data.get('search_params')}")
        return data
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return {"error": str(e)}


# Page configuration
st.set_page_config(
    page_title="北九州市障害福祉サービス検索",
    page_icon="🏥",
    layout="wide",
)

# Main title
st.title("🏥 北九州市障害福祉サービス事業所検索")

# クイックナビゲーション
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    if st.button("👤 利用者管理", use_container_width=True):
        st.switch_page("pages/1_👤_User_Management.py")
with col2:
    if st.button("📊 アセスメント", use_container_width=True):
        st.switch_page("pages/2_📊_Assessment.py")
with col3:
    if st.button("🎯 支援計画", use_container_width=True):
        st.switch_page("pages/3_🎯_Plan_Creation.py")
with col4:
    if st.button("📈 モニタリング", use_container_width=True):
        st.switch_page("pages/4_📊_Monitoring.py")

st.markdown("---")

st.markdown("AI搭載の自然言語検索で、必要なサービスをすぐに見つけられます")

# Sidebar with system info
with st.sidebar:
    st.header("システム情報")

    # Health check
    health = get_health_status()
    if health.get("status") == "healthy":
        st.success("✓ システム正常")
        st.caption(f"Neo4j: {'接続中' if health.get('neo4j_connected') else '切断'}")
        st.caption(
            f"Ollama: {'利用可能' if health.get('ollama_available') else '利用不可'}"
        )
    else:
        st.error("✗ システムエラー")

    st.divider()

    # Statistics
    st.header("データベース統計")
    stats = get_stats()

    if "error" not in stats:
        st.metric("総事業所数", stats.get("total_facilities", 0))

        st.subheader("サービス種別")
        for service_type, count in stats.get("by_service_type", {}).items():
            st.caption(f"{service_type}: {count}件")

        st.subheader("地域別")
        for district, count in stats.get("by_district", {}).items():
            st.caption(f"{district}: {count}件")
    else:
        st.error("統計情報取得エラー")

    st.divider()

    # Usage instructions
    st.header("使い方")
    st.markdown(
        """
    ### 検索例:
    - 「小倉北区の生活介護事業所を教えて」
    - 「就労継続支援B型はどこにありますか？」
    - 「八幡西区で利用できるサービスは？」
    - 「送迎サービスがある事業所を探しています」

    ### 自然な質問でOK！
    普段使っている言葉で検索できます。
    """
    )

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Display facility details if available
        if message["role"] == "assistant" and "facilities" in message:
            with st.expander(f"該当事業所 ({len(message['facilities'])}件)", expanded=False):
                for i, facility in enumerate(message["facilities"], 1):
                    st.markdown(f"**{i}. {facility.get('name', 'N/A')}**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"法人: {facility.get('corporation_name', 'N/A')}")
                        st.caption(f"種別: {facility.get('service_type', 'N/A')}")
                        st.caption(f"所在: {facility.get('district', 'N/A')}")
                    with col2:
                        st.caption(f"電話: {facility.get('phone', 'N/A')}")
                        st.caption(f"定員: {facility.get('capacity', 'N/A')}名")
                        if availability := facility.get("availability_status"):
                            st.caption(f"空き: {availability}")
                        # ホームページリンク表示
                        if website_url := facility.get("website_url"):
                            st.markdown(f"🌐 [ホームページを開く]({website_url})")
                    st.divider()

# Chat input
if prompt := st.chat_input("事業所について質問してください..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("検索中..."):
            result = search_facilities(prompt)

            if "error" in result:
                error_msg = f"エラーが発生しました: {result['error']}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )
            else:
                # Display answer
                answer = result.get("answer", "回答を生成できませんでした")
                st.markdown(answer)

                # Display facility cards
                facilities = result.get("facilities", [])
                if facilities:
                    with st.expander(
                        f"該当事業所 ({len(facilities)}件)", expanded=False
                    ):
                        for i, facility in enumerate(facilities, 1):
                            st.markdown(f"**{i}. {facility.get('name', 'N/A')}**")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.caption(
                                    f"法人: {facility.get('corporation_name', 'N/A')}"
                                )
                                st.caption(
                                    f"種別: {facility.get('service_type', 'N/A')}"
                                )
                                st.caption(f"所在: {facility.get('district', 'N/A')}")
                            with col2:
                                st.caption(f"電話: {facility.get('phone', 'N/A')}")
                                st.caption(
                                    f"定員: {facility.get('capacity', 'N/A')}名"
                                )
                                if availability := facility.get("availability_status"):
                                    st.caption(f"空き: {availability}")
                                # ホームページリンク表示
                                if website_url := facility.get("website_url"):
                                    st.markdown(f"🌐 [ホームページを開く]({website_url})")
                            st.divider()

                # Save to chat history
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "facilities": facilities,
                    }
                )

# Footer
st.divider()
st.caption("北九州市障害福祉サービス事業所検索システム v1.0.0")
st.caption("Powered by Ollama (gpt-oss:20b) + Neo4j + FastAPI + Streamlit")
