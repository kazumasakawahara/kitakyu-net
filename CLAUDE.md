<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# kitakyu-net: 北九州市障害福祉サービス事業所管理システム

## プロジェクト概要

### 目的
計画相談支援専門員が北九州市内の障害福祉サービス事業所の情報を効率的に管理し、エコマップ作成や利用者へのサービス紹介を円滑に行うための情報管理システム。

### 主要機能
1. WAM NET（福祉医療機構）からの事業所基本情報の取得・整形
2. Googleスプレッドシートでの情報管理・共同編集
3. Neo4jグラフデータベースへのインポート
4. エコマップシステムとの連携

### 対象ユーザー
- 計画相談支援専門員
- 北九州市内で活動する相談支援事業所スタッフ

---

## システムアーキテクチャ

```
[WAM NET] 
    ↓ (データ取得)
[Python Scraper] 
    ↓ (整形・加工)
[Googleスプレッドシート] ← (手動追記・編集)
    ↓ (定期インポート)
[Neo4j Database] 
    ↓ (連携)
[エコマップ可視化システム]
```

---

## プロジェクト構成

```
kitakyu-net/
├── CLAUDE.md                    # このファイル（プロジェクト仕様書）
├── README.md                    # プロジェクト概要
├── requirements.txt             # Python依存パッケージ
├── config.yaml                  # 設定ファイル
├── .env.example                 # 環境変数テンプレート
├── .gitignore                   # Git除外設定
│
├── data/                        # データファイル格納
│   ├── raw/                     # WAM NETから取得した生データ
│   ├── processed/               # 加工済みデータ
│   └── templates/               # テンプレートファイル
│       └── facility_template.xlsx
│
├── scripts/                     # スクリプト類
│   ├── 01_wamnet_scraper.py    # WAM NETデータ取得
│   ├── 02_data_processor.py    # データ整形・加工
│   ├── 03_sheets_updater.py    # Googleスプレッドシート更新
│   ├── 04_neo4j_importer.py    # Neo4jインポート
│   └── utils/                   # ユーティリティ
│       ├── logger.py
│       └── validators.py
│
├── docs/                        # ドキュメント
│   ├── data_dictionary.md      # データ項目定義
│   ├── wamnet_guide.md         # WAM NET利用ガイド
│   └── neo4j_schema.md         # Neo4jスキーマ定義
│
└── tests/                       # テストコード
    └── test_data_processor.py
```

---

## データモデル

### 事業所ノード (Facility)

#### 必須プロパティ（フェーズ1：最小限）
```yaml
facility_id: string           # 一意識別子 (自動生成UUID)
name: string                  # 事業所名
corporation_name: string      # 法人名
facility_number: string       # 指定番号（10桁）
service_type: string          # サービス種別
service_category: string      # 「介護給付」「訓練等給付」
postal_code: string          # 郵便番号
address: string              # 住所
district: string             # 所在区（小倉北区等）
phone: string                # 電話番号
capacity: integer            # 定員
availability_status: string  # 「空きあり」「待機中」「満員」
created_at: datetime         # 作成日時
updated_at: datetime         # 更新日時
data_source: string          # 「WAM_NET」「手動入力」等
```

#### 推奨プロパティ（フェーズ2：サービス調整用）
```yaml
fax: string                  # FAX番号
email: string                # メールアドレス
operating_days: string       # 営業日
operating_hours: string      # 営業時間
transportation: boolean      # 送迎の有無
transportation_area: string  # 送迎対応エリア
meal_service: boolean        # 食事提供
disability_types: list       # 対応可能な障害種別
support_levels: list         # 対応可能な支援区分
medical_care_support: boolean # 医療的ケア対応
behavioral_support: boolean  # 強度行動障害対応
```

#### 詳細プロパティ（フェーズ3：実務蓄積）
```yaml
service_manager: string      # サービス管理責任者名
facility_manager: string     # 管理者名
main_activities: string      # 主な活動内容
work_programs: list          # 作業種目
wage_info: string           # 工賃・賃金情報
consultation_history: boolean # 相談支援連携実績
support_notes: string        # 支援上の注意点
compatibility_note: string   # 本人との相性
family_feedback: string      # 家族の評価
```

---

## WAM NET データ取得仕様

### 対象URL
```
https://www.wam.go.jp/sfkohyoout/COP000100E0000.do
```

### 検索条件
- 都道府県: 福岡県
- 市区町村: 北九州市
- サービス種別: 全種別（個別に取得）

### 取得項目マッピング
```python
WAMNET_MAPPING = {
    '事業所番号': 'facility_number',
    '事業所名': 'name',
    '法人名': 'corporation_name',
    'サービス種類': 'service_type',
    '郵便番号': 'postal_code',
    '所在地': 'address',
    '電話番号': 'phone',
    'FAX番号': 'fax',
    '定員': 'capacity',
}
```

### データ取得手順
1. WAM NETサイトにアクセス
2. 北九州市で検索
3. 各サービス種別ごとにCSVダウンロード
4. `data/raw/` フォルダに保存（日付付きファイル名）

---

## Googleスプレッドシート仕様

### シート構成

#### シート1: 基本情報 (basic_info)
```
列名:
A: 事業所ID
B: 事業所名
C: 法人名
D: 事業所番号
E: サービス種別
F: サービスカテゴリ
G: 郵便番号
H: 住所
I: 所在区
J: 電話番号
K: FAX
L: メール
M: 定員
N: 空き状況
O: 営業日
P: 営業時間
Q: データソース
R: 最終更新日
S: 更新者
```

#### シート2: サービス詳細 (service_details)
```
列名:
A: 事業所ID
B: 対応障害種別（複数選択）
C: 対応支援区分（複数選択）
D: 送迎の有無
E: 送迎エリア
F: 食事提供
G: 医療的ケア対応
H: 強度行動障害対応
I: 主な活動内容
J: 作業種目
K: 工賃情報
```

#### シート3: 連携・実績 (coordination)
```
列名:
A: 事業所ID
B: 相談支援連携実績
C: サービス管理責任者名
D: 管理者名
E: 連携時の特記事項
F: 地域移行実績
G: 就労移行実績
```

#### シート4: 個別メモ (individual_notes)
```
列名:
A: 事業所ID
B: 利用者ID（該当する場合）
C: 本人との相性
D: 家族の評価
E: 支援上の注意点
F: 最終連絡日
G: 次回連絡予定
```

#### シート5: マスターデータ (master_data)
```
- サービス種別一覧
- 障害種別一覧
- 所在区一覧
- 空き状況選択肢
等のドロップダウン用データ
```

### スプレッドシートの保存先
- Googleドライブ: `マイドライブ > AI-Managed-Sheets > kitakyu-facilities.xlsx`

---

## Neo4j スキーマ定義

### ノードラベル

#### Facility（事業所）
```cypher
CREATE CONSTRAINT facility_id_unique IF NOT EXISTS
FOR (f:Facility) REQUIRE f.facility_id IS UNIQUE;

CREATE INDEX facility_name IF NOT EXISTS
FOR (f:Facility) ON (f.name);

CREATE INDEX facility_service_type IF NOT EXISTS
FOR (f:Facility) ON (f.service_type);

CREATE INDEX facility_district IF NOT EXISTS
FOR (f:Facility) ON (f.district);
```

### インポートクエリ例

```cypher
// 事業所ノード作成
MERGE (f:Facility {facility_id: $facility_id})
SET f.name = $name,
    f.corporation_name = $corporation_name,
    f.facility_number = $facility_number,
    f.service_type = $service_type,
    f.service_category = $service_category,
    f.postal_code = $postal_code,
    f.address = $address,
    f.district = $district,
    f.phone = $phone,
    f.capacity = $capacity,
    f.availability_status = $availability_status,
    f.updated_at = datetime()
RETURN f
```

---

## 実装フェーズ

### フェーズ1: データ収集基盤構築（1-2週間）
```
□ WAM NETからのデータ取得スクリプト作成
□ データ整形・加工処理の実装
□ Googleスプレッドシートテンプレート作成
□ 基本データのインポート
```

### フェーズ2: Neo4j連携（1週間）
```
□ Neo4jスキーマ定義
□ インポートスクリプト作成
□ データ検証・整合性チェック
□ 基本クエリ動作確認
```

### フェーズ3: 運用フロー確立（1週間）
```
□ 定期更新スクリプトの自動化
□ データ入力マニュアル作成
□ エラー通知機能実装
□ バックアップ体制構築
```

### フェーズ4: エコマップ連携（2週間）
```
□ エコマップシステムとのAPI連携
□ 可視化機能の実装
□ ユーザーインターフェース改善
```

---

## 技術スタック

### 言語・フレームワーク
- Python 3.11+
- uv（パッケージ管理）

### 主要ライブラリ
```
pandas >= 2.1.0          # データ処理
openpyxl >= 3.1.0        # Excel操作
gspread >= 5.12.0        # Googleスプレッドシート連携
neo4j >= 5.14.0          # Neo4jドライバー
pyyaml >= 6.0            # 設定ファイル読み込み
python-dotenv >= 1.0.0   # 環境変数管理
requests >= 2.31.0       # HTTP通信
beautifulsoup4 >= 4.12.0 # HTML解析（必要に応じて）
```

### データベース
- Neo4j 5.x（グラフDB）

### 外部サービス
- Google Sheets API
- WAM NET（データソース）

---

## セットアップ手順

### 1. 環境構築

```bash
# プロジェクトディレクトリに移動
cd ~/AI-Workspace/kitakyu-net

# uvでPython環境を初期化
uv venv
source .venv/bin/activate  # 仮想環境有効化

# 依存パッケージのインストール
uv pip install -r requirements.txt
```

### 2. 環境変数設定

```bash
# .envファイルを作成
cp .env.example .env

# .envファイルを編集
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=your_password
# GOOGLE_CREDENTIALS_PATH=path/to/credentials.json
```

### 3. Google Sheets API認証設定

```bash
# Google Cloud Consoleでプロジェクト作成
# Google Sheets API有効化
# サービスアカウント作成
# 認証情報JSONをダウンロード
# プロジェクトルートに配置
```

### 4. Neo4jセットアップ

```bash
# Neo4j Desktopまたはローカルインストール
# データベース作成
# 接続情報を.envに記載
```

---

## 運用フロー

### 初回データ投入
```bash
# 1. WAM NETからデータ取得（手動ダウンロード）
# data/raw/ フォルダにCSVファイルを配置

# 2. データ整形・加工
python scripts/02_data_processor.py

# 3. Googleスプレッドシート作成・更新
python scripts/03_sheets_updater.py --initial

# 4. Neo4jへインポート
python scripts/04_neo4j_importer.py --initial
```

### 定期更新（月次想定）
```bash
# 1. 新規データの取得・整形
python scripts/02_data_processor.py --update

# 2. スプレッドシートとの差分更新
python scripts/03_sheets_updater.py --sync

# 3. Neo4jへ反映
python scripts/04_neo4j_importer.py --sync
```

### 手動追記後の反映
```bash
# Googleスプレッドシートで情報を手動追記した後
python scripts/04_neo4j_importer.py --from-sheets
```

---

## 開発ガイドライン

### コーディング規約
- PEP 8準拠
- 関数・クラスには必ずdocstringを記述
- 型ヒントを活用
- ログ出力を適切に実装

### エラーハンドリング
- 外部API呼び出しは必ずtry-exceptで囲む
- ユーザーフレンドリーなエラーメッセージ
- ログファイルへの詳細記録

### データ検証
- 必須項目のチェック
- データ型の検証
- 重複データの検出
- 異常値の検出・通知

### テスト
- 単体テスト（pytest使用）
- データ整合性テスト
- 統合テスト

---

## トラブルシューティング

### WAM NETからのデータ取得失敗
```
原因: サイト構造の変更、ネットワークエラー
対処: 手動ダウンロード、スクリプト修正
```

### Google Sheets API認証エラー
```
原因: 認証情報の期限切れ、権限不足
対処: 認証情報の再取得、共有設定確認
```

### Neo4jインポートエラー
```
原因: データ型不一致、制約違反
対処: データ検証、スキーマ確認
```

---

## 今後の拡張予定

### 短期（3ヶ月以内）
- [ ] 利用者ノードとの関係性管理
- [ ] サービス担当者会議記録の紐付け
- [ ] モニタリング記録の管理

### 中期（6ヶ月以内）
- [ ] エコマップ自動生成機能
- [ ] レポート出力機能
- [ ] 検索・フィルタリング機能強化

### 長期（1年以内）
- [ ] 他市町村への展開
- [ ] AIによる事業所推薦機能
- [ ] 地域資源マッピング

---

## 参考資料

### 公式ドキュメント
- [WAM NET](https://www.wam.go.jp/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)

### 関連法規
- 障害者総合支援法
- 北九州市障害者支援施策

---

## ライセンス
このプロジェクトは内部利用を目的としています。

---

## 変更履歴
- 2025-10-31: プロジェクト初期化、基本設計完了

---

## 連絡先
- 開発者: Kazumasa
- 利用組織: 北九州市内計画相談支援事業所

---

## Claude Codeでの作業開始方法

```bash
# 1. プロジェクトディレクトリに移動
cd ~/AI-Workspace/kitakyu-net

# 2. Claude Codeを起動
# ターミナルで以下を実行
# このCLAUDE.mdを読み込んで理解

# 3. 最初のタスク提案
# - WAM NETデータ取得スクリプトの実装
# - Googleスプレッドシートテンプレートの作成
# - Neo4jスキーマの定義
```

### 優先実装タスク
1. **データ整形スクリプト** (`02_data_processor.py`)
   - WAM NET CSVを読み込み
   - データクリーニング
   - 標準フォーマットへ変換

2. **Googleスプレッドシートテンプレート作成**
   - マニュアル作成を含む
   - 実際のテンプレートファイル生成

3. **Neo4jインポートスクリプト** (`04_neo4j_importer.py`)
   - スプレッドシートからの読み込み
   - バリデーション
   - Neo4jへの投入

---

このドキュメントは、プロジェクトの進行に応じて随時更新してください。
