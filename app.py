import sys

from models import Contact
from repository import ContactRepository


SEPARATOR = "─" * 55


def _hr() -> None:
    print(SEPARATOR)


def _print_contact(contact: Contact, index: int = None) -> None:
    prefix = f"[{index}] " if index is not None else ""
    print(f"{prefix}ID: {contact.id}  이름: {contact.name}")
    print(f"     이메일: {contact.email}  전화: {contact.phone}")
    if contact.memo:
        print(f"     메모: {contact.memo}")
    print(f"     생성: {contact.created_at}  수정: {contact.updated_at}")


def _input(prompt: str) -> str:
    return input(f"  {prompt}: ").strip()


def _confirm(message: str) -> bool:
    answer = input(f"  {message} (y/n): ").strip().lower()
    return answer == "y"


# ── Create ─────────────────────────────────────────────────────────────────────
def cmd_create(repo: ContactRepository) -> None:
    print("\n[ 새 연락처 추가 ]")
    _hr()
    name = _input("이름")
    email = _input("이메일")
    phone = _input("전화번호")
    memo = _input("메모 (선택)")

    values = {"name": name, "email": email, "phone": phone}
    missing = [f for f in Contact.REQUIRED_FIELDS if not values[f]]
    if missing:
        labels = [Contact.FIELD_LABELS[f] for f in missing]
        print(f"  오류: 필수 항목이 비어 있습니다 → {', '.join(labels)}")
        return

    contact = Contact(name=name, email=email, phone=phone, memo=memo)
    repo.create(contact)
    _hr()
    print(f"  저장 완료 (ID: {contact.id})")


# ── Read ───────────────────────────────────────────────────────────────────────
def cmd_read(repo: ContactRepository) -> None:
    print("\n[ 조회 ]")
    _hr()
    print("  1) 전체 목록")
    print("  2) ID로 검색")
    print("  3) 키워드 검색")
    choice = _input("선택")

    if choice == "1":
        contacts = repo.find_all()
        _hr()
        if not contacts:
            print("  데이터가 없습니다.")
            return
        print(f"  총 {len(contacts)}건")
        _hr()
        for i, c in enumerate(contacts, 1):
            _print_contact(c, i)
            print()

    elif choice == "2":
        cid = _input("ID").upper()
        contact = repo.find_by_id(cid)
        _hr()
        if contact:
            _print_contact(contact)
        else:
            print(f"  ID '{cid}'를 찾을 수 없습니다.")

    elif choice == "3":
        keyword = _input("검색어")
        results = repo.search(keyword)
        _hr()
        if not results:
            print(f"  '{keyword}'에 해당하는 결과가 없습니다.")
            return
        print(f"  '{keyword}' 검색 결과: {len(results)}건")
        _hr()
        for i, c in enumerate(results, 1):
            _print_contact(c, i)
            print()

    else:
        print("  잘못된 선택입니다.")


# ── Update ─────────────────────────────────────────────────────────────────────
def cmd_update(repo: ContactRepository) -> None:
    print("\n[ 수정 ]")
    _hr()
    cid = _input("수정할 ID").upper()
    contact = repo.find_by_id(cid)

    if not contact:
        print(f"  ID '{cid}'를 찾을 수 없습니다.")
        return

    _hr()
    _print_contact(contact)
    _hr()
    print("  수정할 필드를 선택하세요 (쉼표로 여러 개 입력 가능)")
    for i, f in enumerate(Contact.EDITABLE_FIELDS, 1):
        print(f"    {i}) {Contact.FIELD_LABELS[f]}")

    raw = _input("선택 (예: 1,3)")
    selected_indices = []
    for token in raw.split(","):
        token = token.strip()
        if token.isdigit() and 1 <= int(token) <= len(Contact.EDITABLE_FIELDS):
            selected_indices.append(int(token) - 1)

    if not selected_indices:
        print("  유효한 선택이 없습니다.")
        return

    updates = {}
    for idx in selected_indices:
        field = Contact.EDITABLE_FIELDS[idx]
        label = Contact.FIELD_LABELS[field]
        current = getattr(contact, field)
        new_val = _input(f"{label} (현재: '{current}')")
        if new_val:
            updates[field] = new_val

    if not updates:
        print("  변경된 내용이 없습니다.")
        return

    updated = repo.update(cid, updates)
    _hr()
    if updated:
        print("  수정 완료")
        _print_contact(updated)
    else:
        print("  수정에 실패했습니다.")


# ── Delete ─────────────────────────────────────────────────────────────────────
def cmd_delete(repo: ContactRepository) -> None:
    print("\n[ 삭제 ]")
    _hr()
    cid = _input("삭제할 ID").upper()
    contact = repo.find_by_id(cid)

    if not contact:
        print(f"  ID '{cid}'를 찾을 수 없습니다.")
        return

    _hr()
    _print_contact(contact)
    _hr()

    if not _confirm(f"'{contact.name}' 을(를) 삭제하시겠습니까?"):
        print("  취소되었습니다.")
        return

    if repo.delete(cid):
        print(f"  삭제 완료 (ID: {cid})")
    else:
        print("  삭제에 실패했습니다.")


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    repo = ContactRepository("data/contacts.json")

    menu = {
        "1": ("Create  새 연락처 추가", cmd_create),
        "2": ("Read    목록 / 검색",    cmd_read),
        "3": ("Update  연락처 수정",    cmd_update),
        "4": ("Delete  연락처 삭제",    cmd_delete),
        "0": ("종료",                   None),
    }

    while True:
        print(f"\n{'═' * 55}")
        print("  연락처 관리 시스템")
        print(f"{'═' * 55}")
        for key, (label, _) in menu.items():
            print(f"  {key}. {label}")
        _hr()

        choice = _input("메뉴 선택")

        if choice == "0":
            print("\n  종료합니다.")
            sys.exit(0)

        if choice not in menu:
            print("  잘못된 입력입니다. 다시 선택하세요.")
            continue

        _, handler = menu[choice]
        try:
            handler(repo)
        except KeyboardInterrupt:
            print("\n  (메인 메뉴로 돌아갑니다)")


if __name__ == "__main__":
    main()
