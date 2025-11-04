# Neo4j スキーマ定義

## 概要

このドキュメントでは、kitakyu-netプロジェクトで使用するNeo4jグラフデータベースのスキーマを定義します。

## グラフモデルの設計思想

### 基本方針

1. **ノード**: エンティティ（事業所、利用者、計画等）を表現
2. **リレーションシップ**: エンティティ間の関係を表現
3. **プロパティ**: ノードとリレーションシップの属性情報

### 拡張性の確保

- 将来的な利用者ノード、計画ノードの追加を想定
- 柔軟なリレーションシップ設計
- プロパティの動的な追加が可能

## ノード定義

### Facility（事業所）ノード

障害福祉サービス提供事業所を表すノード。

#### ラベル
```cypher
:Facility
```

#### プロパティ

**必須プロパティ:**
```cypher
{
  facility_id: string,           // UUID形式の一意識別子
  name: string,                  // 事業所名
  corporation_name: string,      // 法人名
  facility_number: string,       // 10桁の指定番号
  service_type: string,          // サービス種別
  service_category: string,      // 「介護給付」「訓練等給付」
  address: string,               // 住所
  district: string,              // 所在区
  phone: string,                 // 電話番号
  data_source: string,           // データソース
  created_at: datetime,          // 作成日時
  updated_at: datetime           // 更新日時
}
```

**推奨プロパティ:**
```cypher
{
  postal_code: string,           // 郵便番号
  fax: string,                   // FAX番号
  email: string,                 // メールアドレス
  capacity: integer,             // 定員
  availability_status: string,   // 空き状況
  operating_days: string,        // 営業日
  operating_hours: string,       // 営業時間
  transportation: boolean,       // 送迎の有無
  transportation_area: string,   // 送迎エリア
  meal_service: boolean,         // 食事提供
  disability_types: list[string], // 対応障害種別
  support_levels: list[string],  // 対応支援区分
  medical_care_support: boolean, // 医療的ケア対応
  behavioral_support: boolean    // 強度行動障害対応
}
```

**詳細プロパティ（オプション）:**
```cypher
{
  service_manager: string,       // サービス管理責任者名
  facility_manager: string,      // 管理者名
  main_activities: string,       // 主な活動内容
  work_programs: list[string],   // 作業種目
  wage_info: string,             // 工賃情報
  consultation_history: boolean, // 相談支援連携実績
  transition_record: string,     // 地域移行実績
  employment_record: string,     // 就労移行実績
  support_notes: string,         // 支援上の注意点
  coordination_notes: string,    // 連携時の特記事項
  updated_by: string             // 更新者
}
```

## 制約（Constraints）

### 一意性制約

```cypher
// facility_idの一意性制約
CREATE CONSTRAINT facility_id_unique IF NOT EXISTS
FOR (f:Facility) REQUIRE f.facility_id IS UNIQUE;

// facility_numberの一意性制約
CREATE CONSTRAINT facility_number_unique IF NOT EXISTS
FOR (f:Facility) REQUIRE f.facility_number IS UNIQUE;
```

### 存在性制約

```cypher
// 必須プロパティの存在性制約
CREATE CONSTRAINT facility_name_exists IF NOT EXISTS
FOR (f:Facility) REQUIRE f.name IS NOT NULL;

CREATE CONSTRAINT facility_service_type_exists IF NOT EXISTS
FOR (f:Facility) REQUIRE f.service_type IS NOT NULL;

CREATE CONSTRAINT facility_phone_exists IF NOT EXISTS
FOR (f:Facility) REQUIRE f.phone IS NOT NULL;

CREATE CONSTRAINT facility_address_exists IF NOT EXISTS
FOR (f:Facility) REQUIRE f.address IS NOT NULL;
```

## インデックス（Indexes）

### 検索用インデックス

```cypher
// 事業所名の検索用インデックス
CREATE INDEX facility_name_index IF NOT EXISTS
FOR (f:Facility) ON (f.name);

// サービス種別の検索用インデックス
CREATE INDEX facility_service_type_index IF NOT EXISTS
FOR (f:Facility) ON (f.service_type);

// 所在区の検索用インデックス
CREATE INDEX facility_district_index IF NOT EXISTS
FOR (f:Facility) ON (f.district);

// 空き状況の検索用インデックス
CREATE INDEX facility_availability_index IF NOT EXISTS
FOR (f:Facility) ON (f.availability_status);

// 法人名の検索用インデックス
CREATE INDEX facility_corporation_index IF NOT EXISTS
FOR (f:Facility) ON (f.corporation_name);
```

### 複合インデックス

```cypher
// サービス種別と区の複合インデックス
CREATE INDEX facility_service_district_index IF NOT EXISTS
FOR (f:Facility) ON (f.service_type, f.district);
```

## 基本クエリ例

### ノードの作成

```cypher
// 事業所ノードの作成
CREATE (f:Facility {
  facility_id: $facility_id,
  name: $name,
  corporation_name: $corporation_name,
  facility_number: $facility_number,
  service_type: $service_type,
  service_category: $service_category,
  postal_code: $postal_code,
  address: $address,
  district: $district,
  phone: $phone,
  data_source: $data_source,
  created_at: datetime(),
  updated_at: datetime()
})
RETURN f
```

### ノードの更新（MERGE使用）

```cypher
// 存在すれば更新、なければ作成
MERGE (f:Facility {facility_id: $facility_id})
ON CREATE SET
  f.name = $name,
  f.corporation_name = $corporation_name,
  f.facility_number = $facility_number,
  f.service_type = $service_type,
  f.service_category = $service_category,
  f.address = $address,
  f.district = $district,
  f.phone = $phone,
  f.data_source = $data_source,
  f.created_at = datetime(),
  f.updated_at = datetime()
ON MATCH SET
  f.name = $name,
  f.corporation_name = $corporation_name,
  f.service_type = $service_type,
  f.address = $address,
  f.phone = $phone,
  f.updated_at = datetime()
RETURN f
```

### 検索クエリ

```cypher
// サービス種別で検索
MATCH (f:Facility)
WHERE f.service_type = '就労継続支援B型'
RETURN f
ORDER BY f.name

// 所在区とサービス種別で検索
MATCH (f:Facility)
WHERE f.district = '小倉北区'
  AND f.service_type = '生活介護'
RETURN f
ORDER BY f.name

// 空きがある事業所を検索
MATCH (f:Facility)
WHERE f.availability_status = '空きあり'
RETURN f
ORDER BY f.district, f.name

// 複数の条件で検索
MATCH (f:Facility)
WHERE f.district IN ['小倉北区', '小倉南区']
  AND f.service_category = '訓練等給付'
  AND f.availability_status IN ['空きあり', '要確認']
  AND '知的障害' IN f.disability_types
RETURN f
ORDER BY f.availability_status, f.name

// テキスト検索（部分一致）
MATCH (f:Facility)
WHERE f.name CONTAINS '作業所'
   OR f.corporation_name CONTAINS '作業所'
RETURN f
ORDER BY f.name
```

### 集計クエリ

```cypher
// 区ごとの事業所数
MATCH (f:Facility)
RETURN f.district AS 区, count(f) AS 事業所数
ORDER BY 事業所数 DESC

// サービス種別ごとの事業所数
MATCH (f:Facility)
RETURN f.service_type AS サービス種別, count(f) AS 事業所数
ORDER BY 事業所数 DESC

// 空き状況の集計
MATCH (f:Facility)
WHERE f.availability_status IS NOT NULL
RETURN f.availability_status AS 空き状況, count(f) AS 件数
ORDER BY 件数 DESC

// 送迎ありの事業所数
MATCH (f:Facility)
WHERE f.transportation = true
RETURN f.district AS 区, count(f) AS 送迎あり事業所数
ORDER BY 送迎あり事業所数 DESC
```

### データ更新クエリ

```cypher
// 特定事業所の空き状況を更新
MATCH (f:Facility {facility_id: $facility_id})
SET f.availability_status = $new_status,
    f.updated_at = datetime(),
    f.updated_by = $updater
RETURN f

// 複数事業所の一括更新
UNWIND $updates AS update
MATCH (f:Facility {facility_id: update.facility_id})
SET f += update.properties,
    f.updated_at = datetime()
RETURN count(f) AS updated_count
```

## 将来の拡張: リレーションシップ定義（参考）

### USES（利用関係）

利用者が事業所のサービスを利用する関係。

```cypher
(:User)-[USES {
  contract_id: string,
  start_date: date,
  status: string,
  usage_pattern: string,
  // その他のプロパティ
}]->(:Facility)
```

### COORDINATES_WITH（連携関係）

計画相談支援事業所と他の事業所との連携関係。

```cypher
(:Facility)-[COORDINATES_WITH {
  frequency: string,
  last_contact: date,
  coordination_type: string
}]->(:Facility)
```

### NEAR（地理的近接性）

事業所間の地理的な近さを表現。

```cypher
(:Facility)-[NEAR {
  distance: float,
  transport_time: integer
}]->(:Facility)
```

## データインポート手順

### 1. 制約とインデックスの作成

```cypher
// すべての制約を作成
CREATE CONSTRAINT facility_id_unique IF NOT EXISTS
FOR (f:Facility) REQUIRE f.facility_id IS UNIQUE;

CREATE CONSTRAINT facility_number_unique IF NOT EXISTS
FOR (f:Facility) REQUIRE f.facility_number IS UNIQUE;

// すべてのインデックスを作成
CREATE INDEX facility_name_index IF NOT EXISTS
FOR (f:Facility) ON (f.name);

// ... その他のインデックス
```

### 2. データのインポート

```cypher
// CSVファイルからのインポート例
LOAD CSV WITH HEADERS FROM 'file:///facilities.csv' AS row
MERGE (f:Facility {facility_id: row.facility_id})
ON CREATE SET
  f.name = row.name,
  f.corporation_name = row.corporation_name,
  f.facility_number = row.facility_number,
  f.service_type = row.service_type,
  f.service_category = row.service_category,
  f.address = row.address,
  f.district = row.district,
  f.phone = row.phone,
  f.data_source = row.data_source,
  f.created_at = datetime(),
  f.updated_at = datetime()
ON MATCH SET
  f.name = row.name,
  f.updated_at = datetime()
```

### 3. データの検証

```cypher
// 重複チェック
MATCH (f:Facility)
WITH f.facility_number AS number, collect(f) AS facilities
WHERE size(facilities) > 1
RETURN number, size(facilities) AS count

// 必須項目の欠損チェック
MATCH (f:Facility)
WHERE f.name IS NULL OR f.phone IS NULL
RETURN f

// 統計情報
MATCH (f:Facility)
RETURN 
  count(f) AS total_facilities,
  count(DISTINCT f.district) AS districts,
  count(DISTINCT f.service_type) AS service_types
```

## パフォーマンスチューニング

### クエリ最適化のベストプラクティス

1. **インデックスの活用**
   - WHERE句で使用するプロパティにはインデックスを作成
   - 複合検索には複合インデックスを検討

2. **LIMIT句の使用**
   - 大量データの取得時はLIMITで制限

3. **プロファイリング**
   ```cypher
   PROFILE
   MATCH (f:Facility)
   WHERE f.service_type = '就労継続支援B型'
   RETURN f
   ```

## バックアップとリストア

### バックアップ

```bash
# Neo4j Desktopから: Manage → Create Dump
# または、neo4j-adminコマンド
neo4j-admin database dump neo4j --to-path=/path/to/backup
```

### リストア

```bash
neo4j-admin database load neo4j --from-path=/path/to/backup
```

## セキュリティ

### アクセス制御

```cypher
// 読み取り専用ユーザーの作成（Enterprise版）
CREATE USER reader SET PASSWORD 'password' CHANGE NOT REQUIRED;
GRANT TRAVERSE ON GRAPH * NODES * TO reader;
GRANT READ {*} ON GRAPH * TO reader;
```

## 監視とメンテナンス

### 統計情報の確認

```cypher
// データベースの統計
CALL db.stats.retrieve('GRAPH COUNTS')

// ノード数
MATCH (f:Facility) RETURN count(f) AS facility_count

// インデックスの使用状況
CALL db.indexes()
```

## 更新履歴

- 2025-10-31: 初版作成
