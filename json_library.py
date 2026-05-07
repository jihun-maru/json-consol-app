"""
JSON 데이터 파싱 및 파일 저장 라이브러리
"""

import json
import os
from typing import Any, Optional, Union


def parse(json_string: str) -> Any:
    """JSON 문자열을 Python 객체로 변환합니다."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"유효하지 않은 JSON 문자열: {e}") from e


def serialize(data: Any, indent: Optional[int] = 2, ensure_ascii: bool = False) -> str:
    """Python 객체를 JSON 문자열로 변환합니다."""
    try:
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
    except (TypeError, ValueError) as e:
        raise ValueError(f"JSON 직렬화 실패: {e}") from e


def load_file(file_path: str, encoding: str = "utf-8") -> Any:
    """JSON 파일을 읽어 Python 객체로 반환합니다."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파일 파싱 실패 ({file_path}): {e}") from e


def save_file(
    data: Any,
    file_path: str,
    indent: Optional[int] = 2,
    ensure_ascii: bool = False,
    encoding: str = "utf-8",
    create_dirs: bool = True,
) -> None:
    """Python 객체를 JSON 파일로 저장합니다."""
    if create_dirs:
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
    try:
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
    except (TypeError, ValueError) as e:
        raise ValueError(f"JSON 파일 저장 실패: {e}") from e


def merge(base: dict, override: dict, deep: bool = True) -> dict:
    """두 딕셔너리를 병합합니다. deep=True이면 중첩 딕셔너리도 재귀적으로 병합합니다."""
    result = base.copy()
    for key, value in override.items():
        if deep and key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge(result[key], value, deep=True)
        else:
            result[key] = value
    return result


def query(data: Any, path: str, default: Any = None) -> Any:
    """점(.) 표기법으로 중첩 데이터에 접근합니다. 예: 'user.address.city'"""
    keys = path.split(".")
    current = data
    for key in keys:
        try:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                current = current[int(key)]
            else:
                return default
        except (KeyError, IndexError, ValueError):
            return default
    return current


def validate_keys(data: dict, required_keys: list[str]) -> list[str]:
    """딕셔너리에 필수 키가 있는지 검사하고, 누락된 키 목록을 반환합니다."""
    return [key for key in required_keys if key not in data]
