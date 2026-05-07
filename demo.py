"""CRUD 전체 흐름 시연 — 실제 app.py 로직을 직접 호출"""
import os, sys

sys.path.insert(0, os.path.dirname(__file__))

from models import Contact
from repository import ContactRepository

DEMO_DB = "data/demo_contacts.json"
SEP = "─" * 55


def hr(): print(SEP)
def title(t): print(f"\n{'═'*55}\n  {t}\n{'═'*55}")


def cleanup():
    try: os.remove(DEMO_DB)
    except FileNotFoundError: pass


cleanup()
repo = ContactRepository(DEMO_DB)

# ── CREATE ────────────────────────────────────────────────────────────────────
title("1. CREATE — 연락처 3건 추가")

c1 = repo.create(Contact("홍길동", "hong@example.com", "010-1111-2222", "VIP 고객"))
c2 = repo.create(Contact("김철수", "kim@example.com",  "010-3333-4444", "신규 가입"))
c3 = repo.create(Contact("이영희", "lee@example.com",  "010-5555-6666"))

for c in [c1, c2, c3]:
    print(f"  저장 완료 → ID: {c.id}  이름: {c.name}  이메일: {c.email}")

# ── READ : 전체 목록 ──────────────────────────────────────────────────────────
title("2. READ — 전체 목록")
all_contacts = repo.find_all()
print(f"  총 {len(all_contacts)}건")
hr()
for i, c in enumerate(all_contacts, 1):
    print(f"  [{i}] ID:{c.id}  이름:{c.name}  이메일:{c.email}  전화:{c.phone}")
    if c.memo: print(f"       메모:{c.memo}")

# ── READ : ID 검색 ────────────────────────────────────────────────────────────
title("3. READ — ID로 검색")
found = repo.find_by_id(c2.id)
print(f"  검색 ID: {c2.id}")
hr()
if found:
    print(f"  이름: {found.name}  이메일: {found.email}  전화: {found.phone}")

# ── READ : 키워드 검색 ────────────────────────────────────────────────────────
title("4. READ — 키워드 검색 ('VIP')")
results = repo.search("VIP")
print(f"  검색 결과: {len(results)}건")
hr()
for r in results:
    print(f"  ID:{r.id}  이름:{r.name}  메모:{r.memo}")

# ── UPDATE ────────────────────────────────────────────────────────────────────
title("5. UPDATE — 김철수 전화번호 & 메모 수정")
print(f"  수정 전 → 전화: {c2.phone}  메모: '{c2.memo}'")
updated = repo.update(c2.id, {"phone": "010-9999-0000", "memo": "등급 상향: VIP"})
hr()
print(f"  수정 후 → 전화: {updated.phone}  메모: '{updated.memo}'")
print(f"  수정 시각: {updated.updated_at}")

# ── DELETE ────────────────────────────────────────────────────────────────────
title("6. DELETE — 이영희 삭제")
print(f"  삭제 대상 → ID: {c3.id}  이름: {c3.name}")
result = repo.delete(c3.id)
hr()
print(f"  삭제 {'성공' if result else '실패'}")

# 삭제 후 전체 목록 확인
remaining = repo.find_all()
print(f"\n  삭제 후 잔여 레코드: {len(remaining)}건")
for c in remaining:
    print(f"    ID:{c.id}  이름:{c.name}")

# ── 저장된 JSON 파일 확인 ─────────────────────────────────────────────────────
title("7. JSON 파일 직접 확인")
import json_library as jl
raw = jl.load_file(DEMO_DB)
print(jl.serialize(raw))

cleanup()
print(f"\n{'═'*55}\n  시연 완료\n{'═'*55}")
