# データディクショナリ

## 事業所情報データ項目定義

### 基本情報テーブル (basic_info)

| 項目名(日本語) | 項目名(英語) | データ型 | 長さ | 必須 | ユニーク | 説明 | 例 |
|--------------|------------|---------|------|------|---------|------|-----|
| 事業所ID | facility_id | string | UUID | ○ | ○ | 一意識別子 | 550e8400-e29b-41d4-a716-446655440000 |
| 事業所名 | name | string | 255 | ○ | - | 正式な事業所名 | ○○作業所 |
| 法人名 | corporation_name | string | 255 | ○ | - | 運営法人の正式名称 | 社会福祉法人△△会 |
| 事業所番号 | facility_number | string | 10 | ○ | ○ | 指定事業所番号 | 4010100123 |
| サービス種別 | service_type | string | 50 | ○ | - | サービスの種類 | 就労継続支援B型 |
| サービスカテゴリ | service_category | string | 20 | ○ | - | 介護給付/訓練等給付 | 訓練等給付 |
| 郵便番号 | postal_code | string | 8 | - | - | 000-0000形式 | 802-0001 |
| 住所 | address | string | 500 | ○ | - | 完全な住所 | 福岡県北九州市小倉北区○○1-2-3 |
| 所在区 | district | string | 20 | ○ | - | 北九州市の区 | 小倉北区 |
| 電話番号 | phone | string | 20 | ○ | - | 代表電話番号 | 093-123-4567 |
| FAX番号 | fax | string | 20 | - | - | FAX番号 | 093-123-4568 |
| メールアドレス | email | string | 255 | - | - | 代表メールアドレス | info@example.com |
| 定員 | capacity | integer | - | - | - | 利用定員 | 20 |
| 空き状況 | availability_status | string | 20 | - | - | 空き状況（選択式） | 空きあり |
| 営業日 | operating_days | string | 100 | - | - | 営業日の説明 | 月〜金 |
| 営業時間 | operating_hours | string | 100 | - | - | 営業時間の説明 | 9:00〜16:00 |
| データソース | data_source | string | 50 | ○ | - | データの出所 | WAM_NET |
| 最終更新日 | updated_at | datetime | - | ○ | - | 最終更新日時 | 2025-10-31T10:00:00 |
| 更新者 | updated_by | string | 100 | - | - | 更新者名 | Kazumasa |
| 作成日 | created_at | datetime | - | ○ | - | 作成日時 | 2025-10-31T10:00:00 |

### サービス詳細テーブル (service_details)

| 項目名(日本語) | 項目名(英語) | データ型 | 必須 | 説明 | 例 |
|--------------|------------|---------|------|------|-----|
| 事業所ID | facility_id | string | ○ | basic_infoと紐付け | 550e8400-... |
| 対応障害種別 | disability_types | list[string] | - | 対応可能な障害種別 | [知的障害, 精神障害] |
| 対応支援区分 | support_levels | list[string] | - | 対応可能な支援区分 | [区分3, 区分4] |
| 送迎の有無 | transportation | boolean | - | 送迎サービスの有無 | true |
| 送迎エリア | transportation_area | string | - | 送迎可能エリア | 小倉北区全域 |
| 食事提供 | meal_service | boolean | - | 食事提供の有無 | true |
| 医療的ケア対応 | medical_care_support | boolean | - | 医療的ケアの可否 | false |
| 強度行動障害対応 | behavioral_support | boolean | - | 強度行動障害への対応 | false |
| 主な活動内容 | main_activities | string | - | メインの活動内容 | 軽作業・創作活動 |
| 作業種目 | work_programs | list[string] | - | 具体的な作業内容 | [箱折り, クリーニング] |
| 工賃情報 | wage_info | string | - | 平均工賃等 | 月平均15,000円 |

### 連携・実績テーブル (coordination)

| 項目名(日本語) | 項目名(英語) | データ型 | 必須 | 説明 | 例 |
|--------------|------------|---------|------|------|-----|
| 事業所ID | facility_id | string | ○ | basic_infoと紐付け | 550e8400-... |
| 相談支援連携実績 | consultation_history | boolean | - | 連携実績の有無 | true |
| サービス管理責任者名 | service_manager | string | - | サビ管の氏名 | 山田太郎 |
| 管理者名 | facility_manager | string | - | 管理者の氏名 | 鈴木花子 |
| 連携時の特記事項 | coordination_notes | string | - | 連携上の注意点等 | 月初に連絡が取りやすい |
| 地域移行実績 | transition_record | string | - | 施設からの移行実績 | 過去3年で2名 |
| 就労移行実績 | employment_record | string | - | 一般就労への移行実績 | 過去3年で5名 |

### 個別メモテーブル (individual_notes) ※要注意：個人情報

| 項目名(日本語) | 項目名(英語) | データ型 | 必須 | 説明 | 例 |
|--------------|------------|---------|------|------|-----|
| 事業所ID | facility_id | string | ○ | basic_infoと紐付け | 550e8400-... |
| 利用者ID | user_id | string | - | 利用者識別子（匿名化） | USER001 |
| 本人との相性 | compatibility_note | string | - | 本人の反応・評価 | 活動内容が合っている |
| 家族の評価 | family_feedback | string | - | 家族の感想・評価 | 満足している |
| 支援上の注意点 | support_notes | string | - | 支援時の留意事項 | 午前中の集中力が高い |
| 最終連絡日 | last_contact_date | date | - | 最後に連絡した日 | 2025-10-15 |
| 次回連絡予定 | next_contact_date | date | - | 次回連絡予定日 | 2025-11-15 |

## マスターデータ

### サービス種別リスト

#### 介護給付
- 居宅介護（ホームヘルプ）
- 重度訪問介護
- 同行援護
- 行動援護
- 療養介護
- 生活介護
- 短期入所（ショートステイ）
- 施設入所支援
- 共同生活援助（グループホーム）

#### 訓練等給付
- 自立訓練（機能訓練）
- 自立訓練（生活訓練）
- 就労移行支援
- 就労継続支援A型
- 就労継続支援B型
- 就労定着支援
- 自立生活援助

#### 相談支援
- 計画相談支援
- 地域移行支援
- 地域定着支援

### 障害種別リスト
- 身体障害
- 知的障害
- 精神障害
- 発達障害
- 難病
- 高次脳機能障害

### 障害支援区分リスト
- 区分なし
- 区分1
- 区分2
- 区分3
- 区分4
- 区分5
- 区分6

### 所在区リスト（北九州市）
- 門司区
- 若松区
- 戸畑区
- 小倉北区
- 小倉南区
- 八幡東区
- 八幡西区

### 空き状況リスト
- 空きあり
- 要確認
- 待機中
- 満員
- 不明

## データ型定義

### string
- 文字列型
- UTF-8エンコーディング
- 最大長は項目により異なる

### integer
- 整数型
- 負の値は不可（定員等）

### boolean
- 真偽値型
- true/false

### datetime
- 日時型
- ISO 8601形式: YYYY-MM-DDTHH:MM:SS
- タイムゾーン: JST (UTC+9)

### date
- 日付型
- ISO 8601形式: YYYY-MM-DD

### list[string]
- 文字列の配列
- カンマ区切りで格納される場合あり

## データ制約

### 一意性制約
- facility_id: 全レコードで一意
- facility_number: 全レコードで一意

### 外部キー制約
- service_details.facility_id → basic_info.facility_id
- coordination.facility_id → basic_info.facility_id
- individual_notes.facility_id → basic_info.facility_id

### 値域制約
- service_category: ["介護給付", "訓練等給付", "相談支援"]
- district: 北九州市の7区のいずれか
- availability_status: 空き状況リストのいずれか

### 形式制約
- phone: 0XX-XXXX-XXXX または 0XXXXXXXXXX
- postal_code: XXX-XXXX
- facility_number: XXXXXXXXXX (10桁)
- email: RFC 5322準拠

## データ品質ルール

### 必須項目の保証
- 必須項目は常に値が設定されている必要がある
- 空文字列やnullは不可

### データの一貫性
- 同一事業所の情報は各テーブルで一貫している
- 更新時は関連テーブルも同期更新

### データの正確性
- 公開情報（WAM NET等）と照合可能
- 定期的な更新と検証

### データの適時性
- updated_atフィールドで管理
- 古いデータには警告表示

## 変更履歴
- 2025-10-31: 初版作成
