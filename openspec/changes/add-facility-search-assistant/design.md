# Design: Facility Search AI Assistant

## Context

### 背景

計画相談支援専門員は、利用者の障害特性や希望に応じて適切な福祉サービス事業所を探す必要があります。しかし、北九州市内には数百の事業所があり、各事業所の特性（対応可能な障害種別、サービス内容、空き状況など）を把握するのは困難です。

### 制約

- **プライバシー重視**: 利用者情報を外部に送信できない
- **オフライン動作**: ネット環境が不安定な現場でも使用可能
- **コスト**: API課金なし、オープンソース技術のみ
- **保守性**: 専門的なITスキルがなくても運用可能

### ステークホルダー

- 計画相談支援専門員（主要ユーザー）
- 相談支援事業所スタッフ
- 将来的に: 利用者・家族（情報提供用）

## Goals / Non-Goals

### Goals

- ✅ 自然言語での事業所検索を実現
- ✅ WAM NETデータの自動取得・更新
- ✅ Neo4jグラフDBでの柔軟なクエリ
- ✅ ローカルLLMでのプライバシー保護
- ✅ ユーザーフレンドリーなチャットUI

### Non-Goals

- ❌ 利用者個人情報の管理（別MVP）
- ❌ サービス等利用計画の作成（別MVP）
- ❌ 複雑な権限管理（シングルユーザー想定）
- ❌ モバイルアプリ化（Web UIのみ）

## Architecture

### システム構成図

```
┌─────────────────────────────────────────────────┐
│           Streamlit Chat UI (Frontend)          │
│  - チャット画面                                   │
│  - 検索結果表示                                   │
│  - 会話履歴管理                                   │
└────────────┬────────────────────────────────────┘
             │ HTTP (REST API)
┌────────────▼────────────────────────────────────┐
│          FastAPI Backend (Python)                │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │        LLM RAG Pipeline                   │  │
│  │  1. クエリ解析                            │  │
│  │  2. Neo4j検索                             │  │
│  │  3. コンテキスト構築                       │  │
│  │  4. Ollama回答生成                        │  │
│  └───────────┬──────────────┬───────────────┘  │
│              │              │                   │
│     ┌────────▼──────┐  ┌───▼──────────┐       │
│     │ Ollama Client │  │ Neo4j Client │       │
│     └────────┬──────┘  └───┬──────────┘       │
└──────────────┼─────────────┼──────────────────┘
               │             │
       ┌───────▼──────┐  ┌──▼───────────────┐
       │    Ollama    │  │  Neo4j Database  │
       │   (Local)    │  │  (disability-    │
       │   LLM Server │  │   support)       │
       └──────────────┘  └──────────────────┘

┌─────────────────────────────────────────────────┐
│      Data Ingestion Pipeline (Scripts)          │
│  WAM NET → Data Processor → Neo4j Importer      │
└─────────────────────────────────────────────────┘
```

### RAG (検索拡張生成) フロー

```
1. ユーザー入力
   「強度行動障害に対応できる生活介護事業所は？」

2. クエリ解析（LLM）
   → サービス種別: 生活介護
   → 対応障害: 強度行動障害
   → 地域: 指定なし

3. Neo4j Cypher生成
   MATCH (f:Facility)
   WHERE f.service_type = '生活介護'
     AND 'behavioral_support' IN f.support_types
   RETURN f

4. 検索結果取得
   → 5件の事業所データ

5. コンテキスト構築
   事業所リスト + メタデータ → プロンプト

6. Ollama回答生成
   「北九州市内で強度行動障害に対応できる生活介護事業所を5件見つけました...」
```

## Decisions

### 1. UI Framework: Streamlit

**選択理由:**
- Pythonのみで実装可能（React不要）
- チャットインターフェースが標準サポート
- 高速なプロトタイピング
- セットアップが簡単

**代替案:**
- React + TypeScript: 学習コスト高、オーバースペック
- Gradio: チャット機能が弱い

### 2. LLM: Ollama (qwen2.5:7b 推奨)

**選択理由:**
- 完全ローカル実行（プライバシー保護）
- API課金なし
- 日本語性能が高い（qwen2.5）
- 8GBメモリで動作可能

**代替案:**
- OpenAI API: プライバシー懸念、課金
- llama3.1:8b: 日本語やや弱い

**推奨モデル:**
```bash
# 日本語メイン（推奨）
ollama pull qwen2.5:7b

# 英語も使う場合
ollama pull llama3.1:8b

# 高品質（9GB必要）
ollama pull gemma2:9b
```

### 3. Database: Neo4j (Graph DB)

**選択理由:**
- 事業所間の関係性（法人、地域、連携等）を表現
- 柔軟なクエリ（Cypher言語）
- 将来的なエコマップ生成に最適
- 既にインスタンス準備済み

**代替案:**
- PostgreSQL: リレーショナルDB、グラフ検索が弱い
- Elasticsearch: 全文検索特化、オーバースペック

### 4. Backend: FastAPI

**選択理由:**
- 高速（非同期処理）
- 自動API ドキュメント生成
- Pythonの型ヒント活用
- Streamlitと相性良好

**代替案:**
- Flask: 同期処理のみ、やや古い
- Django: 重厚すぎる

### 5. Data Source: WAM NET

**選択理由:**
- 公式データソース（信頼性高）
- 全国の事業所情報を網羅
- 無料で利用可能

**制約:**
- 手動ダウンロード必要（自動スクレイピングはグレーゾーン）
- 月次更新想定

## Data Model

### Neo4j Schema

```cypher
// Facility Node
CREATE CONSTRAINT facility_id_unique IF NOT EXISTS
FOR (f:Facility) REQUIRE f.facility_id IS UNIQUE;

CREATE INDEX facility_name IF NOT EXISTS
FOR (f:Facility) ON (f.name);

CREATE INDEX facility_service_type IF NOT EXISTS
FOR (f:Facility) ON (f.service_type);

CREATE INDEX facility_district IF NOT EXISTS
FOR (f:Facility) ON (f.district);
```

### Facility Properties (Phase 1)

```yaml
# 必須プロパティ
facility_id: string          # UUID
name: string                 # 事業所名
corporation_name: string     # 法人名
facility_number: string      # 指定番号（10桁）
service_type: string         # サービス種別
service_category: string     # 「介護給付」「訓練等給付」
postal_code: string         # 郵便番号
address: string             # 住所
district: string            # 所在区
phone: string               # 電話番号
capacity: integer           # 定員
availability_status: string # 「空きあり」「待機中」「満員」
created_at: datetime        # 作成日時
updated_at: datetime        # 更新日時
data_source: string         # 「WAM_NET」「手動入力」

# 推奨プロパティ（Phase 1で部分対応）
transportation: boolean      # 送迎の有無
meal_service: boolean        # 食事提供
disability_types: list       # 対応障害種別
support_types: list          # 特殊対応（医療的ケア、行動障害等）
```

## Risks / Trade-offs

### Risk 1: LLMの回答精度

**リスク**: LLMが不正確な情報を生成（ハルシネーション）

**緩和策**:
- RAGで実データのみを参照
- プロンプトで「データに基づいてのみ回答」を指示
- 検索結果を明示的に表示（検証可能性）

### Risk 2: データ品質

**リスク**: WAM NETデータが古い・不完全

**緩和策**:
- 月次更新フローを確立
- 手動追記機能（Googleスプレッドシート経由）
- データ検証スクリプト実装

### Risk 3: 初期セットアップの複雑さ

**リスク**: Ollama, Neo4j, Python環境のセットアップでつまずく

**緩和策**:
- 詳細なセットアップガイド作成
- 自動セットアップスクリプト提供
- トラブルシューティングドキュメント

### Risk 4: パフォーマンス

**リスク**: LLM推論に時間がかかる（>10秒）

**緩和策**:
- 軽量モデル使用（7B-8Bパラメータ）
- Neo4jクエリの最適化
- 非同期処理でUI応答性維持

## Migration Plan

このプロジェクトは新規機能追加のため、マイグレーションは不要です。

ただし、既存の `scripts/` ディレクトリ内のスクリプト番号を調整：
- `04_neo4j_importer.py` → `03_neo4j_importer.py` に統合
- Googleスプレッドシート連携は Phase 2 に延期

## Implementation Phases

### Phase 1.1: 基盤構築（Week 1）
- Ollama セットアップ・動作確認
- Neo4j 接続確認
- WAM NET データ取得（手動）

### Phase 1.2: データパイプライン（Week 2）
- データ処理スクリプト実装
- Neo4j インポート実装
- データ検証

### Phase 1.3: RAG システム（Week 3）
- Ollama クライアント実装
- Neo4j クエリ生成
- RAG パイプライン統合

### Phase 1.4: UI 実装（Week 4）
- Streamlit チャット画面
- FastAPI バックエンド
- 統合テスト

## Open Questions

1. **LLMモデルの選択**
   - qwen2.5:7b (日本語特化) vs llama3.1:8b (バランス型)
   - ユーザーの好みで決定

2. **UI言語**
   - 日本語のみ or 多言語対応
   - 当面は日本語のみで開始推奨

3. **データ更新頻度**
   - 月次 or 週次 or 手動
   - 当面は月次で開始

4. **アクセス制御**
   - シングルユーザー or 複数ユーザー
   - Phase 1 はシングルユーザー想定
