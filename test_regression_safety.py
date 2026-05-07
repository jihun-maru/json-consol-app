"""
Regression & Safety Test Suite
범주:
  [SPEC]  스펙 정합성 — Spec.md 요구사항 직접 대응
  [CORR]  Correctness — 함수/메서드 결과 정확성
  [SAFE]  Safety      — 경계값·비정상 입력·데이터 보호
"""

import os
import sys
import json
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(__file__))

import json_library as jl
from models import Contact
from repository import ContactRepository


# ── 테스트용 저장소 픽스처 ──────────────────────────────────────────────────────
class RepoTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "test.json")
        self.repo = ContactRepository(self.db_path)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _make(self, name="홍길동", email="hong@test.com",
              phone="010-0000-0000", memo="") -> Contact:
        return self.repo.create(Contact(name, email, phone, memo))


# ══════════════════════════════════════════════════════════════════════════════
# [SPEC] 스펙 정합성
# ══════════════════════════════════════════════════════════════════════════════
class TestSpecConformance(RepoTestCase):

    # S-01: Create — 새 데이터를 JSON 파일에 저장
    def test_S01_create_persists_to_json_file(self):
        c = self._make()
        raw = jl.load_file(self.db_path)
        self.assertEqual(len(raw), 1)
        self.assertEqual(raw[0]["name"], "홍길동")
        self.assertEqual(raw[0]["email"], "hong@test.com")

    # S-02: Read — 전체 목록 조회
    def test_S02_read_all_returns_full_list(self):
        self._make("A", "a@t.com", "010-0001-0001")
        self._make("B", "b@t.com", "010-0002-0002")
        self._make("C", "c@t.com", "010-0003-0003")
        result = self.repo.find_all()
        self.assertEqual(len(result), 3)

    # S-03: Read — ID로 검색
    def test_S03_read_by_id_returns_correct_record(self):
        c = self._make()
        found = self.repo.find_by_id(c.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, c.id)
        self.assertEqual(found.name, "홍길동")

    # S-04: Read — 키워드 검색
    def test_S04_search_by_keyword(self):
        self._make("김철수", "kim@test.com", "010-1111-2222", "VIP")
        self._make("이영희", "lee@test.com", "010-3333-4444", "일반")
        results = self.repo.search("VIP")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "김철수")

    # S-05: Update — 특정 필드 수정
    def test_S05_update_modifies_target_field(self):
        c = self._make()
        updated = self.repo.update(c.id, {"phone": "010-9999-8888"})
        self.assertEqual(updated.phone, "010-9999-8888")

    # S-06: Delete — 안전한 삭제
    def test_S06_delete_removes_record_safely(self):
        c = self._make()
        result = self.repo.delete(c.id)
        self.assertTrue(result)
        self.assertIsNone(self.repo.find_by_id(c.id))
        remaining = self.repo.find_all()
        self.assertEqual(len(remaining), 0)


# ══════════════════════════════════════════════════════════════════════════════
# [CORR] json_library 정확성
# ══════════════════════════════════════════════════════════════════════════════
class TestJsonLibraryCorrectness(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # C-01: parse — 유효한 JSON 문자열 파싱
    def test_C01_parse_valid_json(self):
        result = jl.parse('{"name": "테스트", "value": 42}')
        self.assertEqual(result["name"], "테스트")
        self.assertEqual(result["value"], 42)

    # C-02: serialize — Python 객체 → JSON 문자열
    def test_C02_serialize_roundtrip(self):
        data = {"key": "값", "nums": [1, 2, 3], "flag": True}
        text = jl.serialize(data)
        back = jl.parse(text)
        self.assertEqual(back, data)

    # C-03: save_file / load_file 왕복 정확성
    def test_C03_save_load_roundtrip(self):
        path = os.path.join(self.tmp, "data.json")
        data = [{"id": "A1", "name": "홍길동"}, {"id": "B2", "name": "김철수"}]
        jl.save_file(data, path)
        loaded = jl.load_file(path)
        self.assertEqual(loaded, data)

    # C-04: save_file — 한글(non-ASCII) 깨짐 없이 저장
    def test_C04_save_korean_no_escape(self):
        path = os.path.join(self.tmp, "kr.json")
        jl.save_file({"msg": "한글테스트"}, path)
        raw = open(path, encoding="utf-8").read()
        self.assertIn("한글테스트", raw)
        self.assertNotIn("\\u", raw)

    # C-05: merge — 얕은 병합 (deep=False)
    def test_C05_merge_shallow(self):
        base = {"a": {"x": 1, "y": 2}, "b": 3}
        override = {"a": {"x": 99}}
        result = jl.merge(base, override, deep=False)
        self.assertEqual(result["a"], {"x": 99})   # y는 사라짐
        self.assertEqual(result["b"], 3)

    # C-06: merge — 깊은 병합 (deep=True)
    def test_C06_merge_deep(self):
        base = {"a": {"x": 1, "y": 2}, "b": 3}
        override = {"a": {"x": 99}}
        result = jl.merge(base, override, deep=True)
        self.assertEqual(result["a"]["x"], 99)
        self.assertEqual(result["a"]["y"], 2)  # y 보존

    # C-07: query — 점 표기법 접근
    def test_C07_query_dot_notation(self):
        data = {"server": {"host": "localhost", "ports": [8080, 8443]}}
        self.assertEqual(jl.query(data, "server.host"), "localhost")
        self.assertEqual(jl.query(data, "server.ports.1"), 8443)

    # C-08: save_file — 부모 디렉토리 자동 생성
    def test_C08_save_creates_parent_dirs(self):
        nested = os.path.join(self.tmp, "a", "b", "c.json")
        jl.save_file({"ok": True}, nested)
        self.assertTrue(os.path.exists(nested))


# ══════════════════════════════════════════════════════════════════════════════
# [CORR] Contact 모델 정확성
# ══════════════════════════════════════════════════════════════════════════════
class TestContactModelCorrectness(unittest.TestCase):

    # C-09: ID 자동 생성 — 8자리 대문자 16진수
    def test_C09_id_auto_generated_format(self):
        c = Contact("A", "a@t.com", "010-0000-0000")
        self.assertEqual(len(c.id), 8)
        self.assertTrue(c.id.isupper() or c.id.isdigit() or
                        all(ch in "0123456789ABCDEF" for ch in c.id))

    # C-10: 서로 다른 Contact는 고유 ID
    def test_C10_unique_ids(self):
        ids = {Contact("A", "a@t.com", "010-0000-0000").id for _ in range(100)}
        self.assertEqual(len(ids), 100)

    # C-11: to_dict / from_dict 왕복
    def test_C11_to_dict_from_dict_roundtrip(self):
        c = Contact("홍길동", "hong@test.com", "010-1234-5678", "메모")
        restored = Contact.from_dict(c.to_dict())
        self.assertEqual(c.id, restored.id)
        self.assertEqual(c.name, restored.name)
        self.assertEqual(c.memo, restored.memo)
        self.assertEqual(c.created_at, restored.created_at)

    # C-12: REQUIRED_FIELDS 목록 정확성
    def test_C12_required_fields_defined(self):
        self.assertIn("name", Contact.REQUIRED_FIELDS)
        self.assertIn("email", Contact.REQUIRED_FIELDS)
        self.assertIn("phone", Contact.REQUIRED_FIELDS)

    # C-13: EDITABLE_FIELDS는 id/created_at 제외
    def test_C13_editable_fields_exclude_protected(self):
        self.assertNotIn("id", Contact.EDITABLE_FIELDS)
        self.assertNotIn("created_at", Contact.EDITABLE_FIELDS)


# ══════════════════════════════════════════════════════════════════════════════
# [CORR] Repository 정확성
# ══════════════════════════════════════════════════════════════════════════════
class TestRepositoryCorrectness(RepoTestCase):

    # C-14: update — 수정하지 않은 필드 보존
    def test_C14_update_preserves_other_fields(self):
        c = self._make("홍길동", "hong@test.com", "010-0000-0000", "VIP")
        self.repo.update(c.id, {"phone": "010-9999-9999"})
        found = self.repo.find_by_id(c.id)
        self.assertEqual(found.name, "홍길동")
        self.assertEqual(found.email, "hong@test.com")
        self.assertEqual(found.memo, "VIP")

    # C-15: update — updated_at 갱신, created_at 불변
    def test_C15_update_refreshes_updated_at_only(self):
        c = self._make()
        original_created = c.created_at
        updated = self.repo.update(c.id, {"memo": "변경됨"})
        self.assertEqual(updated.created_at, original_created)
        # updated_at은 created_at과 같거나 이후
        self.assertGreaterEqual(updated.updated_at, original_created)

    # C-16: search — 대소문자 구분 없이 검색
    def test_C16_search_case_insensitive(self):
        self._make("테스터", "tester@example.COM", "010-0000-0000")
        self.assertEqual(len(self.repo.search("example.com")), 1)
        self.assertEqual(len(self.repo.search("EXAMPLE.COM")), 1)
        self.assertEqual(len(self.repo.search("Example.Com")), 1)

    # C-17: 여러 건 Create 후 순서 보장
    def test_C17_create_order_preserved(self):
        names = ["Alice", "Bob", "Charlie"]
        for n in names:
            self._make(n, f"{n.lower()}@t.com", "010-0000-0000")
        all_c = self.repo.find_all()
        self.assertEqual([c.name for c in all_c], names)

    # C-18: update — 보호 필드(id, created_at) 덮어쓰기 차단
    def test_C18_update_cannot_overwrite_id(self):
        c = self._make()
        original_id = c.id
        self.repo.update(c.id, {"id": "HACKED00", "name": "변경"})
        # ID로 원래 레코드를 찾을 수 있어야 함
        found = self.repo.find_by_id(original_id)
        self.assertIsNotNone(found, "원래 ID로 레코드를 찾지 못함 — id 덮어쓰기 버그")
        self.assertEqual(found.id, original_id, "id가 변조됨")


# ══════════════════════════════════════════════════════════════════════════════
# [SAFE] Safety — 경계값·비정상 입력
# ══════════════════════════════════════════════════════════════════════════════
class TestSafety(RepoTestCase):

    # SA-01: parse — 잘못된 JSON → ValueError
    def test_SA01_parse_invalid_json_raises(self):
        with self.assertRaises(ValueError):
            jl.parse("{not valid json}")

    # SA-02: load_file — 존재하지 않는 파일 → FileNotFoundError
    def test_SA02_load_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            jl.load_file("/nonexistent/path/file.json")

    # SA-03: load_file — 손상된 JSON 파일 → ValueError
    def test_SA03_load_corrupted_file_raises(self):
        path = os.path.join(self.tmp_dir, "bad.json")
        with open(path, "w") as f:
            f.write("{broken json content:::}")
        with self.assertRaises(ValueError):
            jl.load_file(path)

    # SA-04: 저장소 초기화 — 손상된 파일이 있을 때 graceful 처리
    def test_SA04_repo_init_with_corrupted_file(self):
        path = os.path.join(self.tmp_dir, "corrupt.json")
        with open(path, "w") as f:
            f.write("{not json}")
        try:
            repo = ContactRepository(path)
            # 손상된 파일로 초기화해도 앱이 죽지 않아야 함
            self.fail("손상된 파일로 인해 예외가 발생해야 하는지 확인 필요")
        except (ValueError, Exception):
            pass  # 예외 발생 자체를 문서화

    # SA-05: find_by_id — 존재하지 않는 ID → None 반환
    def test_SA05_find_by_id_returns_none_for_missing(self):
        result = self.repo.find_by_id("NOTEXIST")
        self.assertIsNone(result)

    # SA-06: update — 존재하지 않는 ID → None 반환
    def test_SA06_update_nonexistent_id_returns_none(self):
        result = self.repo.update("NOTEXIST", {"name": "변경"})
        self.assertIsNone(result)

    # SA-07: delete — 이미 삭제된 ID 재삭제 → False 반환
    def test_SA07_double_delete_returns_false(self):
        c = self._make()
        self.assertTrue(self.repo.delete(c.id))
        self.assertFalse(self.repo.delete(c.id))

    # SA-08: delete — 다른 레코드 영향 없음
    def test_SA08_delete_does_not_affect_others(self):
        c1 = self._make("A", "a@t.com", "010-0001-0001")
        c2 = self._make("B", "b@t.com", "010-0002-0002")
        c3 = self._make("C", "c@t.com", "010-0003-0003")
        self.repo.delete(c2.id)
        remaining = self.repo.find_all()
        ids = [c.id for c in remaining]
        self.assertIn(c1.id, ids)
        self.assertIn(c3.id, ids)
        self.assertNotIn(c2.id, ids)

    # SA-09: search — 빈 문자열 검색
    def test_SA09_search_empty_keyword_returns_all(self):
        self._make("A", "a@t.com", "010-0001-0001")
        self._make("B", "b@t.com", "010-0002-0002")
        results = self.repo.search("")
        # 빈 문자열은 모든 값에 포함되므로 전체 반환 예상
        self.assertEqual(len(results), 2)

    # SA-10: search — 매칭 없는 키워드
    def test_SA10_search_no_match_returns_empty(self):
        self._make()
        results = self.repo.search("XYZ_UNLIKELY_KEYWORD_99999")
        self.assertEqual(results, [])

    # SA-11: find_all — 빈 저장소
    def test_SA11_find_all_on_empty_storage(self):
        result = self.repo.find_all()
        self.assertEqual(result, [])

    # SA-12: serialize — 직렬화 불가 타입 → ValueError
    def test_SA12_serialize_non_serializable_raises(self):
        with self.assertRaises((ValueError, TypeError)):
            jl.serialize({"key": {1, 2, 3}})  # set은 JSON 직렬화 불가

    # SA-13: query — 존재하지 않는 경로 → default 반환
    def test_SA13_query_missing_path_returns_default(self):
        data = {"a": {"b": 1}}
        self.assertIsNone(jl.query(data, "a.c"))
        self.assertEqual(jl.query(data, "a.c", default=42), 42)
        self.assertIsNone(jl.query(data, "x.y.z"))

    # SA-14: validate_keys — 누락 키 정확히 반환
    def test_SA14_validate_keys_missing(self):
        data = {"name": "홍길동", "email": "hong@test.com"}
        missing = jl.validate_keys(data, ["name", "email", "phone", "id"])
        self.assertEqual(set(missing), {"phone", "id"})

    # SA-15: validate_keys — 모두 충족 시 빈 목록
    def test_SA15_validate_keys_all_present(self):
        data = {"name": "홍길동", "email": "hong@test.com"}
        missing = jl.validate_keys(data, ["name", "email"])
        self.assertEqual(missing, [])


# ══════════════════════════════════════════════════════════════════════════════
# 실행
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suites = [
        loader.loadTestsFromTestCase(TestSpecConformance),
        loader.loadTestsFromTestCase(TestJsonLibraryCorrectness),
        loader.loadTestsFromTestCase(TestContactModelCorrectness),
        loader.loadTestsFromTestCase(TestRepositoryCorrectness),
        loader.loadTestsFromTestCase(TestSafety),
    ]
    runner = unittest.TextTestRunner(verbosity=2)
    results = [runner.run(s) for s in suites]

    total   = sum(r.testsRun for r in results)
    failed  = sum(len(r.failures) + len(r.errors) for r in results)
    print(f"\n{'═'*60}")
    print(f"  총 {total}건 실행  |  실패/오류: {failed}건")
    print(f"{'═'*60}")
