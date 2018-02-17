import json

from typing import Any, Dict, TypeVar

T = TypeVar('T')


def require(value: T, msg="Value cannot be None") -> T:
    if value is None:
        raise ValueError(msg)
    else:
        return value


def require_not_empty(value: T, msg="Value cannot be empty") -> T:
    if len(value) == 0:
        raise ValueError(msg)
    else:
        return value


def jsonify(obj: Any) -> str:
    return json.dumps(require(obj), indent=True)


def unjsonify(data: str) -> Dict[str, Any]:
    return json.loads(data)
