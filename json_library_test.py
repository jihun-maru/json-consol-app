"""
json_library 사용 예제 및 테스트
"""

import os
import json_library as jl


# ── 1. JSON 파싱 (문자열 → 객체) ──────────────────────────────────────────────
print("=== 1. JSON 파싱 ===")
json_str = '{"name": "홍길동", "age": 30, "skills": ["Python", "Go"]}'
data = jl.parse(json_str)
print(f"이름: {data['name']}, 나이: {data['age']}")
print(f"스킬: {data['skills']}")

# ── 2. JSON 직렬화 (객체 → 문자열) ────────────────────────────────────────────
print("\n=== 2. JSON 직렬화 ===")
obj = {
    "product": "노트북",
    "price": 1500000,
    "in_stock": True,
    "tags": ["전자제품", "컴퓨터"],
}
serialized = jl.serialize(obj)
print(serialized)

# ── 3. JSON 파일 저장 ──────────────────────────────────────────────────────────
print("\n=== 3. JSON 파일 저장 ===")
save_path = "output/sample.json"
jl.save_file(obj, save_path)
print(f"저장 완료: {save_path}")

# ── 4. JSON 파일 읽기 ──────────────────────────────────────────────────────────
print("\n=== 4. JSON 파일 읽기 ===")
loaded = jl.load_file(save_path)
print(f"불러온 데이터: {loaded}")

# ── 5. 딕셔너리 병합 ───────────────────────────────────────────────────────────
print("\n=== 5. 딕셔너리 병합 ===")
base = {"user": {"name": "Alice", "role": "admin"}, "version": 1}
override = {"user": {"name": "Bob"}, "debug": True}
merged = jl.merge(base, override)
print(f"병합 결과: {jl.serialize(merged)}")

# ── 6. 점 표기법 쿼리 ──────────────────────────────────────────────────────────
print("\n=== 6. 중첩 데이터 쿼리 ===")
nested = {"server": {"host": "localhost", "ports": [8080, 8443]}}
print(f"host: {jl.query(nested, 'server.host')}")
print(f"첫 번째 port: {jl.query(nested, 'server.ports.0')}")
print(f"없는 키: {jl.query(nested, 'server.timeout', default=30)}")

# ── 7. 필수 키 검증 ────────────────────────────────────────────────────────────
print("\n=== 7. 필수 키 검증 ===")
record = {"id": 1, "name": "테스트"}
missing = jl.validate_keys(record, ["id", "name", "email", "created_at"])
print(f"누락된 키: {missing}")

# ── 정리 ───────────────────────────────────────────────────────────────────────
os.remove(save_path)
os.rmdir("output")
print("\n테스트 완료.")
