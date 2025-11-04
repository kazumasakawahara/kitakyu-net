"""Verify imported data in Neo4j"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.neo4j.client import get_neo4j_client

client = get_neo4j_client()

print("\n" + "=" * 60)
print("データベース内容確認")
print("=" * 60)

# Get all facilities
facilities = client.search_facilities(limit=10)

print(f"\n総事業所数: {len(facilities)}")
print("\n登録済み事業所:")
for i, fac in enumerate(facilities, 1):
    print(f"\n{i}. {fac['name']}")
    print(f"   法人: {fac['corporation_name']}")
    print(f"   種別: {fac['service_type']} ({fac['service_category']})")
    print(f"   所在: {fac['district']} - {fac['address']}")
    print(f"   電話: {fac['phone']}")
    print(f"   定員: {fac.get('capacity', 'N/A')}名")

# Get statistics
stats = client.get_statistics()
print("\n" + "=" * 60)
print("統計情報")
print("=" * 60)
print(f"\nサービス種別ごとの件数:")
for service_type, count in stats['by_service_type'].items():
    print(f"  - {service_type}: {count}件")

print(f"\n区ごとの件数:")
for district, count in stats['by_district'].items():
    print(f"  - {district}: {count}件")

print("\n" + "=" * 60)
