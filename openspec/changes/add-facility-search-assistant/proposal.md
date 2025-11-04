# Proposal: Add Facility Search AI Assistant

## Why

計画相談支援専門員が北九州市内の障害福祉サービス事業所を検索する際、以下の課題があります：

- 複雑な条件（障害種別、サービス種別、送迎有無、地域など）の組み合わせ検索が困難
- Excelやスプレッドシートでの手動検索に時間がかかる
- 利用者の状況を説明しながら適切な事業所を探すのが難しい
- 最新の空き状況や詳細情報へのアクセスが煩雑

ローカルLLM（Ollama）を活用した自然言語検索により、これらの課題を解決し、支援業務の効率化と質の向上を実現します。

## What Changes

以下の5つの新規ケイパビリティを追加します：

1. **WAM NET Scraper** - WAM NET（福祉医療機構）からの事業所データ自動取得
2. **Facility Data Processor** - データ検証・正規化・UUID生成処理
3. **Neo4j Integration** - グラフデータベースへのインポートとクエリ機能
4. **LLM RAG System** - Ollama統合とRAG（検索拡張生成）パイプライン
5. **Chat Interface** - StreamlitによるユーザーフレンドリーなチャットUI

これにより、以下のような自然言語での検索が可能になります：

```
「強度行動障害に対応できる生活介護事業所を教えて」
「小倉北区で送迎ありの就労継続支援B型は？」
「医療的ケアができる事業所で、空きがあるところは？」
```

## Impact

### 新規追加されるコンポーネント

```
backend/                      # 新規
├── api/                      # FastAPI REST API
│   ├── main.py
│   ├── routes/
│   │   ├── chat.py
│   │   └── facilities.py
│   └── models/
│       └── schemas.py
├── llm/                      # LLM統合
│   ├── ollama_client.py
│   ├── prompts.py
│   └── rag_pipeline.py
├── neo4j/                    # Neo4j統合
│   ├── client.py
│   ├── queries.py
│   └── schema.py
└── config.py

frontend/                     # 新規
└── streamlit_app.py         # チャットUI

scripts/                      # 既存を拡張
├── 01_wamnet_scraper.py     # 実装
├── 02_data_processor.py     # 実装
└── 03_neo4j_importer.py     # 新規（既存の04を統合）
```

### 既存システムへの影響

- `data/` ディレクトリ構造はそのまま活用
- `config.yaml` に新規設定を追加（Ollama, Neo4j接続情報）
- `requirements.txt` に新規依存関係を追加
- Neo4j Desktopの既存インスタンス（disability-support）を活用

### 前提条件

- Neo4j Desktop インストール済み ✅
- Ollama インストール必要（提案に含む）
- Python 3.11+ ✅
- 8GB以上のRAM推奨（LLMモデル実行用）

### 非機能要件

- **プライバシー**: すべての処理をローカルで実行（外部API不使用）
- **レスポンス**: 検索クエリから回答まで5秒以内
- **可用性**: オフライン環境でも動作
- **拡張性**: 将来的に他のMVP（支援記録作成等）との統合を考慮
