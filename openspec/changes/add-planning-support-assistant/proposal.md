# Proposal: Add Planning Support AI Assistant (MVP2)

## Why

計画相談支援専門員がサービス等利用計画書を作成する際、以下の課題があります：

- 利用者のニーズを網羅的に把握し、構造化して整理するのに時間がかかる
- 適切な目標設定（SMART原則）が難しく、具体性や実現可能性の評価に経験が必要
- 複数のサービス種別を組み合わせた最適なプラン作成が複雑
- 計画書の様式記入に時間がかかり、本質的な相談支援に時間を割けない
- 過去の計画書や知見の活用が属人化している

ローカルLLM（Ollama）を活用した計画書作成支援により、これらの課題を解決し、相談支援の質と効率を向上させます。

## What Changes

以下の5つの新規ケイパビリティを追加します：

1. **User Profile Management** - 利用者情報の登録・管理機能
2. **Needs Assessment AI** - LLMによるニーズ分析と構造化支援
3. **Goal Setting AI** - SMART原則に基づいた目標提案と評価
4. **Service Coordination AI** - 最適なサービス組み合わせの提案と週間スケジュール生成
5. **Document Generation** - 計画書（様式1、様式5）の自動生成とエクスポート

これにより、以下のような支援が可能になります：

```
入力: 「45歳男性、知的障害（重度）、グループホーム入居希望。
      日中は作業をしたいが、体力的に長時間は難しい。
      家族は就労を希望しているが、本人は無理のないペースを望んでいる。」

LLM分析:
- 潜在的ニーズ: 自己実現、社会参加、健康管理
- 推奨目標: 「週3日、午前中の軽作業で収入を得る」
- 推奨サービス: 就労継続支援B型（短時間利用）+ 共同生活援助
- 週間スケジュール: 月水金の午前中作業、火木は余暇活動

出力: 完成した計画書（Word/PDF形式）
```

## Impact

### 新規追加されるコンポーネント

```
backend/
├── api/
│   └── routes/
│       ├── users.py          # 新規: 利用者管理API
│       ├── plans.py          # 新規: 計画書管理API
│       └── assessments.py    # 新規: アセスメントAPI
├── llm/
│   ├── needs_analyzer.py     # 新規: ニーズ分析
│   ├── goal_generator.py     # 新規: 目標設定支援
│   └── plan_generator.py     # 新規: 計画書生成
├── neo4j/
│   └── schema_extensions.py  # 新規: User/Plan/Goal ノード追加
└── documents/                # 新規: ドキュメント生成
    ├── templates/
    │   ├── plan_form1.docx   # 様式1テンプレート
    │   └── plan_form5.docx   # 様式5テンプレート
    ├── docx_generator.py
    └── pdf_generator.py

frontend/
└── pages/                    # 新規: Streamlit マルチページ
    ├── 1_Facility_Search.py  # 既存のapp.pyから移動
    ├── 2_User_Management.py  # 新規: 利用者管理
    ├── 3_Needs_Assessment.py # 新規: アセスメント
    └── 4_Plan_Creation.py    # 新規: 計画書作成
```

### 既存システムへの影響

- Neo4jスキーマに新規ノードラベル追加（User, Plan, Goal, ServiceNeed）
- FastAPI APIに新規エンドポイント追加（/users, /plans, /assessments）
- Streamlitをマルチページアプリに拡張
- 新規依存関係: python-docx, reportlab

### 非機能要件

- **プライバシー**: すべての処理をローカルで実行（個人情報は外部送信なし）
- **データ保護**: Neo4jへのアクセス制御、バックアップ機能
- **生成品質**: LLM生成内容は必ず人間が最終確認する設計
- **柔軟性**: 様式変更に対応できるテンプレート駆動設計

### 前提条件

- MVP1（施設検索AIアシスタント）完了済み ✅
- 既存のNeo4j、Ollama環境を活用 ✅
- 計画書様式（様式1、様式5）のWordテンプレート準備が必要
