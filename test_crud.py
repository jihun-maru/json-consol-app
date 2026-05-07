"""CRUD 기능 자동화 검증"""
import os, sys

sys.path.insert(0, os.path.dirname(__file__))

from models import Contact
from repository import ContactRepository

TEST_DB = "data/test_contacts.json"


def cleanup():
    try:
        os.remove(TEST_DB)
    except FileNotFoundError:
        pass


def test_create():
    repo = ContactRepository(TEST_DB)
    c = Contact(name="홍길동", email="hong@example.com", phone="010-1234-5678")
    saved = repo.create(c)
    assert saved.id == c.id
    print(f"  [PASS] Create — ID: {saved.id}")
    return saved.id


def test_read(cid: str):
    repo = ContactRepository(TEST_DB)

    # find_all
    all_contacts = repo.find_all()
    assert len(all_contacts) == 1

    # find_by_id
    found = repo.find_by_id(cid)
    assert found is not None and found.name == "홍길동"

    # search
    results = repo.search("hong")
    assert len(results) == 1

    results_none = repo.search("없는값xyz")
    assert len(results_none) == 0

    print("  [PASS] Read — find_all / find_by_id / search")


def test_update(cid: str):
    repo = ContactRepository(TEST_DB)
    updated = repo.update(cid, {"name": "김철수", "memo": "VIP 고객"})
    assert updated is not None
    assert updated.name == "김철수"
    assert updated.memo == "VIP 고객"
    assert updated.email == "hong@example.com"  # 기존 필드 보존

    not_found = repo.update("XXXXXXXX", {"name": "없음"})
    assert not_found is None

    print("  [PASS] Update — 필드 수정 및 기존 필드 보존")


def test_delete(cid: str):
    repo = ContactRepository(TEST_DB)
    result = repo.delete(cid)
    assert result is True

    result_again = repo.delete(cid)
    assert result_again is False

    assert len(repo.find_all()) == 0

    print("  [PASS] Delete — 삭제 및 중복 삭제 방지")


if __name__ == "__main__":
    cleanup()
    print("\n=== CRUD 자동화 테스트 ===")
    cid = test_create()
    test_read(cid)
    test_update(cid)
    test_delete(cid)
    cleanup()
    print("\n모든 테스트 통과.")
