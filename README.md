# kitakyu-net

北九州市障害福祉サービス利用者支援管理システム（AI支援機能搭載）

## 概要

計画相談支援専門員が障害福祉サービス利用者の支援を効率的に行うための、AI支援機能を備えた包括的な利用者管理・支援計画システムです。

## 主な機能

### ✅ 実装済み（MVP完成）
- **利用者管理**: CRUD操作、検索、フィルタリング、手帳情報管理（療育手帳・精神保健福祉手帳）
- **AI支援アセスメント**: 自然言語によるニーズ分析、ICF分類、追加質問生成
- **支援計画作成**: アセスメント結果からの目標設定、サービス選定
- **モニタリング**: 進捗確認、サービス別評価、計画見直し判断
- **施設検索**: RAGベースの自然言語検索
- **利用者詳細ビュー**: 包括的な支援情報ダッシュボード（タイムライン、アラート機能、期限警告）

### 🔜 今後の拡張
- 認証・認可システム
- データバックアップ自動化
- WAM NET連携（事業所データ自動取得）
- エコマップ可視化

## 技術スタック

- **Backend**: FastAPI + Neo4j + Ollama (GPT-OSS 20B)
- **Frontend**: Streamlit
- **AI**: RAG pipeline, Needs analysis, Follow-up question generation
- **Database**: Neo4j (グラフデータベース)

## クイックスタート

### 1. 環境セットアップ

```bash
# プロジェクトディレクトリに移動
cd ~/Ai-Workspace/kitakyu-net

# 仮想環境の作成と有効化
uv venv
source .venv/bin/activate

# 依存パッケージのインストール
uv pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してNeo4j接続情報を設定
```

### 2. Neo4jセットアップ

```bash
# Neo4j Desktopまたはローカルインストール
# データベース作成
# 接続情報を.envに記載
```

### 3. アプリケーション起動

```bash
# バックエンドAPI起動 (ターミナル1)
python run_api.py

# フロントエンド起動 (ターミナル2)
streamlit run frontend/app.py --server.port 8501
```

### 4. アクセス

- フロントエンド: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## プロジェクト構成

```
kitakyu-net/
├── CLAUDE.md                    # 詳細な仕様書（Claude Code用）
├── README.md                    # このファイル
├── requirements.txt             # Python依存パッケージ
├── config.yaml                  # 設定ファイル
├── backend/                     # FastAPIバックエンド
│   ├── api/                     # REST APIエンドポイント
│   ├── services/                # ビジネスロジック
│   ├── llm/                     # AI機能（RAG、ニーズ分析）
│   └── neo4j/                   # Neo4jクライアント
├── frontend/                    # Streamlitフロントエンド
│   ├── app.py                   # メインアプリ
│   └── pages/                   # 各ページ
│       ├── 1_👤_User_Management.py
│       ├── 2_📊_Assessment.py
│       ├── 3_🎯_Plan_Creation.py
│       ├── 4_📊_Monitoring.py
│       ├── 4_🏥_Facility_Search.py
│       └── 5_👤_User_Detail.py
├── scripts/                     # ユーティリティスクリプト
└── docs/                        # ドキュメント
    └── page_structure_analysis.md  # ページ構造設計書
```

## ワークフロー

```
1. 利用者登録（User Management）
      ↓
2. アセスメント実施（Assessment）
   - AI支援によるニーズ分析
   - ICF分類
   - 追加質問生成
      ↓
3. 支援計画作成（Plan Creation）
   - 目標設定（長期・短期）
   - サービス種別選定
      ↓
4. モニタリング（Monitoring）
   - 進捗確認
   - サービス評価
   - 計画見直し判断
      ↓
5. 利用者詳細ビュー（User Detail）
   - 包括的な支援情報確認
   - アラート確認
```

## データ統計（現在）

- **47 Python files**: クリーンなコードベース
- **1 TODO comment**: 技術的負債は最小限
- **29 Assessments**: テストユーザーで実証済み
- **複数回アセスメント**: 同一利用者で履歴管理可能
- **事業所データ**: WAM NETから一部取得済み（今後補充予定）

## 詳細ドキュメント

詳しい仕様や実装ガイドは [CLAUDE.md](./CLAUDE.md) をご覧ください。

## 開発環境

- Python 3.11+
- Neo4j 5.x
- Ollama (GPT-OSS 20B)
- uv (パッケージ管理)

## ライセンス

内部利用限定

## 開発者

Kazumasa Kawahara (計画相談支援専門員)

---

🤖 Powered by AI-assisted development with Claude Code
