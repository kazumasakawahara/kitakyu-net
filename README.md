# kitakyu-net

北九州市障害福祉サービス事業所情報管理システム

## 概要

計画相談支援専門員が北九州市内の障害福祉サービス事業所の情報を効率的に管理し、エコマップ作成や利用者へのサービス紹介を円滑に行うためのシステムです。

## 主な機能

- WAM NET（福祉医療機構）からの事業所基本情報の取得・整形
- Googleスプレッドシートでの情報管理・共同編集
- Neo4jグラフデータベースへのインポート
- エコマップシステムとの連携

## クイックスタート

```bash
# プロジェクトディレクトリに移動
cd ~/AI-Workspace/kitakyu-net

# 仮想環境の作成と有効化
uv venv
source .venv/bin/activate

# 依存パッケージのインストール
uv pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してください
```

## プロジェクト構成

```
kitakyu-net/
├── CLAUDE.md              # 詳細な仕様書（Claude Code用）
├── README.md              # このファイル
├── requirements.txt       # Python依存パッケージ
├── config.yaml           # 設定ファイル
├── data/                 # データファイル
│   ├── raw/             # 生データ
│   ├── processed/       # 加工済みデータ
│   └── templates/       # テンプレート
├── scripts/              # スクリプト
│   ├── 01_wamnet_scraper.py
│   ├── 02_data_processor.py
│   ├── 03_sheets_updater.py
│   └── 04_neo4j_importer.py
└── docs/                 # ドキュメント
```

## 詳細ドキュメント

詳しい仕様や実装ガイドは [CLAUDE.md](./CLAUDE.md) をご覧ください。

## 開発環境

- Python 3.11+
- Neo4j 5.x
- Google Sheets API
- uv (パッケージ管理)

## ライセンス

内部利用限定

## 開発者

Kazumasa (計画相談支援専門員)
