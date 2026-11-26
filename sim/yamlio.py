"""Minimal YAML reader for the persona cards.

Supports maps, lists, scalars, and nested list items. No anchors.
"""

from __future__ import annotations


def _coerce(raw: str):
    text = raw.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        return text[1:-1]
    if text == "[]":
        return []
    if text == "{}":
        return {}
    lowered = text.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "~"}:
        return None
    try:
        if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
            return int(text)
        return float(text)
    except ValueError:
        return text


class _Pending:
    def __init__(self, parent, key, indent: int):
        self.parent = parent
        self.key = key
        self.indent = indent


def parse_yaml(text: str):
    root: dict = {}
    stack: list[tuple[int, object]] = [(-1, root)]

    def parent_container():
        return stack[-1][1]

    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()
        while len(stack) > 1 and indent <= stack[-1][0] and not isinstance(stack[-1][1], _Pending):
            stack.pop()
        if stack and isinstance(stack[-1][1], _Pending) and indent <= stack[-1][0]:
            pending = stack.pop()[1]
            assert isinstance(pending, _Pending)
            pending.parent[pending.key] = {}
        top = stack[-1][1]
        if isinstance(top, _Pending):
            if line.startswith("- "):
                container: object = []
            else:
                container = {}
            top.parent[top.key] = container
            stack[-1] = (top.indent, container)
            top = container
        if line.startswith("- "):
            if not isinstance(top, list):
                raise ValueError(f"list item without a list: {line}")
            item = line[2:].strip()
            if item.endswith(":") and ": " not in item:
                node: dict = {}
                top.append(node)
                stack.append((indent, _Pending(node, item[:-1].strip(), indent + 2)))
                continue
            if ": " in item:
                key, value = item.split(": ", 1)
                node = {key.strip(): _coerce(value)}
                top.append(node)
                stack.append((indent, node))
                continue
            top.append(_coerce(item))
            continue
        if ":" not in line:
            raise ValueError(f"expected key: {line}")
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not isinstance(top, dict):
            raise ValueError(f"key under a non-map: {line}")
        if value == "":
            stack.append((indent, _Pending(top, key, indent)))
        else:
            top[key] = _coerce(value)
    while len(stack) > 1:
        item = stack.pop()[1]
        if isinstance(item, _Pending):
            item.parent[item.key] = {}
    return root
