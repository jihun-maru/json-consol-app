from datetime import datetime
from typing import Optional

import json_library as jl
from models import Contact


class ContactRepository:
    def __init__(self, file_path: str = "data/contacts.json"):
        self._path = file_path
        self._init_storage()

    def _init_storage(self) -> None:
        try:
            jl.load_file(self._path)
        except FileNotFoundError:
            jl.save_file([], self._path)

    def _load(self) -> list[dict]:
        return jl.load_file(self._path)

    def _save(self, records: list[dict]) -> None:
        jl.save_file(records, self._path)

    # ── Create ──────────────────────────────────────────────────────────────────
    def create(self, contact: Contact) -> Contact:
        records = self._load()
        records.append(contact.to_dict())
        self._save(records)
        return contact

    # ── Read ─────────────────────────────────────────────────────────────────────
    def find_all(self) -> list[Contact]:
        return [Contact.from_dict(r) for r in self._load()]

    def find_by_id(self, contact_id: str) -> Optional[Contact]:
        record = next((r for r in self._load() if r["id"] == contact_id), None)
        return Contact.from_dict(record) if record else None

    def search(self, keyword: str) -> list[Contact]:
        keyword_lower = keyword.lower()
        matches = [
            r for r in self._load()
            if any(keyword_lower in str(v).lower() for v in r.values())
        ]
        return [Contact.from_dict(r) for r in matches]

    # ── Update ───────────────────────────────────────────────────────────────────
    def update(self, contact_id: str, updates: dict) -> Optional[Contact]:
        records = self._load()
        for i, r in enumerate(records):
            if r["id"] == contact_id:
                records[i] = jl.merge(r, updates)
                records[i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save(records)
                return Contact.from_dict(records[i])
        return None

    # ── Delete ───────────────────────────────────────────────────────────────────
    def delete(self, contact_id: str) -> bool:
        records = self._load()
        filtered = [r for r in records if r["id"] != contact_id]
        if len(filtered) == len(records):
            return False
        self._save(filtered)
        return True
