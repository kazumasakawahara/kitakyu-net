# kitakyu-net プロジェクト開始ガイド

## Claude Codeでの作業を始める前に

このガイドは、Claude Codeを使ってkitakyu-netプロジェクトを開発するための手順を説明します。

## 前提条件

- macOS環境
- Python 3.11以降がインストール済み
- uvパッケージマネージャがインストール済み
- Claude Code（ターミナルで使用可能）

## 初回セットアップ（Claude Codeで実行）

### 1. プロジェクトディレクトリへ移動

```bash
cd ~/AI-Workspace/kitakyu-net
```

### 2. Python仮想環境の作成

```bash
uv venv
source .venv/bin/activate
```

### 3. 依存パッケージのインストール

```bash
uv pip install -r requirements.txt
```

### 4. 環境変数の設定

```bash
cp .env.example .env
# .envファイルを編集して、必要な情報を設定
```

### 5. データディレクトリの作成

```bash
mkdir -p data/raw
mkdir -p data/processed
mkdir -p logs
```

## プロジェクト構成の確認

```
kitakyu-net/
├── CLAUDE.md                    ★ 詳細な仕様書（重要）
├── README.md                    # プロジェクト概要
├── requirements.txt             # Python依存パッケージ
├── config.yaml                  # 設定ファイル
├── .env.example                 # 環境変数テンプレート
├── .gitignore                   # Git除外設定
│
├── data/                        # データファイル
│   ├── raw/                     # 生データ（WAM NET等）
│   ├── processed/               # 加工済みデータ
│   └── templates/               # テンプレート
│       └── template_guide.md
│
├── scripts/                     # スクリプト類
│   ├── utils/                   # ユーティリティ
│   │   ├── logger.py           # ログ管理
│   │   └── validators.py       # データ検証
│   ├── 01_wamnet_scraper.py    # WAM NETデータ取得（未実装）
│   ├── 02_data_processor.py    # データ整形（未実装）
│   ├── 03_sheets_updater.py    # Sheets更新（未実装）
│   └── 04_neo4j_importer.py    # Neo4jインポート（未実装）
│
└── docs/                        # ドキュメント
    ├── data_dictionary.md       # データ項目定義
    ├── wamnet_guide.md          # WAM NET利用ガイド
    └── neo4j_schema.md          # Neo4jスキーマ定義
```

## 優先実装タスク

### タスク1: データ整形スクリプト（02_data_processor.py）

**目的:** WAM NETからダウンロードしたCSVファイルを整形

**主な機能:**
- CSVファイルの読み込み（Shift-JIS対応）
- 列名の英語化
- データ型の変換
- 欠損値の処理
- 重複データの除去
- 所在区の抽出
- UUID生成

**期待される入力:**
- `data/raw/wamnet_kitakyushu_YYYYMMDD.csv`

**期待される出力:**
- `data/processed/facilities_YYYYMMDD.csv`

### タスク2: Googleスプレッドシートテンプレート作成

**目的:** 事業所情報を管理するためのスプレッドシート作成

**作成するシート:**
1. basic_info（基本情報）
2. service_details（サービス詳細）
3. coordination（連携・実績）
4. individual_notes（個別メモ）
5. master_data（マスターデータ）

**機能:**
- データ検証（ドロップダウン）
- 条件付き書式
- シート保護

### タスク3: Neo4jインポートスクリプト（04_neo4j_importer.py）

**目的:** 処理済みデータをNeo4jに投入

**主な機能:**
- Neo4j接続
- 制約・インデックスの作成
- データのバルクインポート
- エラーハンドリング
- ログ出力

## 開発の進め方

### Claude Codeでの作業フロー

1. **CLAUDE.mdを熟読**
   - プロジェクトの全体像を理解
   - 実装すべき機能を確認

2. **優先タスクから着手**
   - タスク1から順番に実装推奨
   - 各タスク完了後にテスト

3. **ドキュメントの参照**
   - `docs/`フォルダ内のドキュメントを活用
   - データ項目定義を確認

4. **段階的な実装**
   - まず最小限の機能を実装
   - 動作確認後に機能追加

## 実装時の注意点

### コーディング規約

- PEP 8準拠
- 型ヒントを使用
- docstringを必ず記述
- エラーハンドリングを適切に実装

### ログ出力

```python
from scripts.utils.logger import get_logger

logger = get_logger()
logger.info("処理を開始します")
logger.error(f"エラーが発生: {error}")
```

### データ検証

```python
from scripts.utils.validators import validate_facility_data

is_valid, errors = validate_facility_data(data)
if not is_valid:
    logger.error(f"バリデーションエラー: {errors}")
```

## 次のステップ

1. **タスク1の実装:**
   ```bash
   # scripts/02_data_processor.py の作成
   # テストデータでの動作確認
   ```

2. **手動でのWAM NETデータ取得:**
   ```
   - WAM NETにアクセス
   - 北九州市で検索
   - CSVダウンロード
   - data/raw/に保存
   ```

3. **データ処理の実行:**
   ```bash
   python scripts/02_data_processor.py
   ```

4. **結果の確認:**
   ```bash
   # 処理済みデータを確認
   cat data/processed/facilities_*.csv | head
   ```

## よくある質問

### Q1: WAM NETからデータをダウンロードできません

**A:** docs/wamnet_guide.mdを参照してください。詳細な手順が記載されています。

### Q2: 文字化けが発生します

**A:** WAM NETのCSVはShift-JISエンコーディングです。データ処理スクリプトで自動変換されます。

### Q3: Neo4jの接続方法が分かりません

**A:** .envファイルに接続情報を設定してください。docs/neo4j_schema.mdも参照してください。

## サポートドキュメント

- **詳細仕様:** `CLAUDE.md`
- **データ定義:** `docs/data_dictionary.md`
- **WAM NET利用:** `docs/wamnet_guide.md`
- **Neo4jスキーマ:** `docs/neo4j_schema.md`
- **テンプレート:** `data/templates/template_guide.md`

## 連絡先

開発者: Kazumasa
プロジェクトパス: ~/AI-Workspace/kitakyu-net

---

**重要:** 実装を始める前に、必ず `CLAUDE.md` を読んでください。すべての詳細な仕様が記載されています。
