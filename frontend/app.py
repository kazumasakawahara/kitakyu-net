# -*- coding: utf-8 -*-
"""
Kitakyu-Net: 北九州市障害福祉サービス総合支援システム

MVP1: 施設検索 (Facility Search)
MVP2: 計画作成支援 (Planning Support Assistant)
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="北九州市障害福祉サービス総合支援システム",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Main page
st.title("🏥 北九州市障害福祉サービス総合支援システム")
st.markdown("---")

st.markdown("""
## 📋 システム概要

このシステムは計画相談支援専門員の業務を支援する2つの主要機能を提供します:

### MVP1: 🔍 施設検索 (Facility Search)
- AI powered自然言語検索
- 北九州市内の369事業所データベース
- サービス種別・所在区での絞り込み

### MVP2: 🎯 計画作成支援 (Planning Support Assistant)
- AI powered needs assessment (ICFモデル)
- SMART原則に基づく目標提案
- 事業所の自動マッチング
- サービス等利用計画書の自動生成

## 🚀 使い方

左のサイドバーから機能を選択してください:

1. **👤 利用者管理 (User Management)**
   - 利用者の登録・編集・一覧表示
   - 基本情報の管理

2. **📊 アセスメント (Assessment)**
   - ヒアリング内容の構造化入力
   - AIによるニーズ分析

3. **🎯 支援計画作成 (Plan Creation)**
   - 長期・短期目標の設定
   - AI目標提案機能
   - サービス調整と計画書生成

4. **🏥 施設検索 (Facility Search)**
   - AI搭載の自然言語検索
   - 369事業所から最適なサービスを発見

5. **📈 モニタリング (Monitoring)**
   - 支援計画の進捗状況記録
   - 目標達成度の評価
   - 再アセスメント判定

## ⚙️ システム構成

- **Backend**: FastAPI + Neo4j + Ollama LLM
- **Frontend**: Streamlit
- **LLM Model**: gpt-oss:20b (13GB)
- **Database**: Neo4j Graph Database

## 📊 データ統計

- 登録事業所数: 369件
- サービス種別: 30種類以上
- 対応区域: 北九州市全7区
""")

st.markdown("---")
st.info("👈 左のサイドバーから機能を選択してください")

# Footer
st.markdown("---")
st.caption("北九州市障害福祉サービス総合支援システム | Powered by AI & Neo4j")
