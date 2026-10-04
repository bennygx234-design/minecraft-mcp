"""Read/write Minecraft NBT (Named Binary Tag), big-endian, as used by Java Edition.

Values decode to plain Python types by default: compounds -> dict, lists ->
list, byte/int/long arrays -> list[int]. `read(..., typed=True)` instead wraps
every value in `Tag` so it can be written back losslessly. Writing infers types
for plain values (int -> INT, float -> DOUBLE) and honours explicit `Tag`s.
Also parses/prints SNBT, the text form used inside commands.
"""

from __future__ import annotations

import gzip
import io
import struct
import zlib
from dataclasses import dataclass
from typing import Any

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY, LONG_ARRAY = range(13)


@dataclass
class Tag:
    type: int
    value: Any


class _Reader:
    def __init__(self, data: bytes, typed: bool = False):
        self.d = memoryview(data)
        self.i = 0
        self.typed = typed

    def take(self, n: int) -> memoryview:
        v = self.d[self.i:self.i + n]
        self.i += n
        return v

    def unpack(self, fmt: str):
        size = struct.calcsize(fmt)
        return struct.unpack(fmt, self.take(size))

    def string(self) -> str:
        (n,) = self.unpack(">H")
        # Java "modified UTF-8"; plain UTF-8 decoding is right for everything Minecraft writes in practice.
        return bytes(self.take(n)).decode("utf-8", errors="replace")

    def payload(self, t: int) -> Any:
        v = self._payload(t)
        return Tag(t, v) if self.typed else v

    def _payload(self, t: int) -> Any:
        if t == BYTE:
            return self.unpack(">b")[0]
        if t == SHORT:
            return self.unpack(">h")[0]
        if t == INT:
            return self.unpack(">i")[0]
        if t == LONG:
            return self.unpack(">q")[0]
        if t == FLOAT:
            return self.unpack(">f")[0]
        if t == DOUBLE:
            return self.unpack(">d")[0]
        if t == BYTE_ARRAY:
            (n,) = self.unpack(">i")
            return list(struct.unpack(f">{n}b", self.take(n)))
        if t == STRING:
            return self.string()
        if t == LIST:
            et, n = self.unpack(">bi")
            items = [self.payload(et) for _ in range(max(n, 0))]
            if et == COMPOUND and not self.typed:
                # Since 1.21.5, lists of mixed types wrap each non-compound
                # element as {"": value}; unwrap those back to the value.
                items = [x[""] if len(x) == 1 and "" in x else x for x in items]
            return items
        if t == COMPOUND:
            out = {}
            while True:
                (ct,) = self.unpack(">b")
                if ct == END:
                    return out
                name = self.string()
                out[name] = self.payload(ct)
        if t == INT_ARRAY:
            (n,) = self.unpack(">i")
            return list(struct.unpack(f">{n}i", self.take(4 * n)))
        if t == LONG_ARRAY:
            (n,) = self.unpack(">i")
            return list(struct.unpack(f">{n}q", self.take(8 * n)))
        raise ValueError(f"unknown NBT tag type {t}")


def decompress(data: bytes) -> bytes:
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data)
    if data[:1] == b"\x78":
        return zlib.decompress(data)
    return data


def read(data: bytes, typed: bool = False) -> dict:
    """Parse a (possibly compressed) NBT root compound and return its contents."""
    r = _Reader(decompress(data), typed)
    (t,) = r.unpack(">b")
    if t != COMPOUND:
        raise ValueError("NBT root is not a compound")
    r.string()  # root name, usually empty
    return r._payload(COMPOUND)


def untag(v: Any) -> Any:
    """Typed tree -> plain Python values."""
    if isinstance(v, Tag):
        v = v.value
    if isinstance(v, dict):
        return {k: untag(x) for k, x in v.items()}
    if isinstance(v, list):
        return [untag(x) for x in v]
    return v


# -- writing ---------------------------------------------------------------

def _infer(v: Any) -> Tag:
    if isinstance(v, Tag):
        return v
    if isinstance(v, bool):
        return Tag(BYTE, int(v))
    if isinstance(v, int):
        return Tag(INT, v)
    if isinstance(v, float):
        return Tag(DOUBLE, v)
    if isinstance(v, str):
        return Tag(STRING, v)
    if isinstance(v, dict):
        return Tag(COMPOUND, v)
    if isinstance(v, list):
        return Tag(LIST, v)
    raise TypeError(f"cannot infer NBT type for {type(v).__name__}")


def _write_payload(out: io.BytesIO, tag: Tag) -> None:
    t, v = tag.type, tag.value
    if t == BYTE:
        out.write(struct.pack(">b", v))
    elif t == SHORT:
        out.write(struct.pack(">h", v))
    elif t == INT:
        out.write(struct.pack(">i", v))
    elif t == LONG:
        out.write(struct.pack(">q", v))
    elif t == FLOAT:
        out.write(struct.pack(">f", v))
    elif t == DOUBLE:
        out.write(struct.pack(">d", v))
    elif t == BYTE_ARRAY:
        out.write(struct.pack(">i", len(v)) + bytes(x & 0xFF for x in v))
    elif t == STRING:
        b = v.encode("utf-8")
        out.write(struct.pack(">H", len(b)) + b)
    elif t == LIST:
        items = [_infer(x) for x in v]
        et = items[0].type if items else END
        if any(it.type != et for it in items):
            # Mixed list: wrap non-compounds as {"": value} like Minecraft does.
            items = [it if it.type == COMPOUND else Tag(COMPOUND, {"": it}) for it in items]
            et = COMPOUND
        out.write(struct.pack(">bi", et, len(items)))
        for it in items:
            _write_payload(out, it)
    elif t == COMPOUND:
        for k, x in v.items():
            it = _infer(x)
            out.write(struct.pack(">b", it.type))
            _write_payload(out, Tag(STRING, k))
            _write_payload(out, it)
        out.write(b"\x00")
    elif t == INT_ARRAY:
        out.write(struct.pack(f">i{len(v)}i", len(v), *v))
    elif t == LONG_ARRAY:
        out.write(struct.pack(f">i{len(v)}q", len(v), *v))
    else:
        raise ValueError(f"unknown NBT tag type {t}")


def write_root(root: dict, compress: bool = True) -> bytes:
    out = io.BytesIO()
    out.write(b"\x0a")
    _write_payload(out, Tag(STRING, ""))
    _write_payload(out, Tag(COMPOUND, root))
    data = out.getvalue()
    return gzip.compress(data, compresslevel=5) if compress else data


# -- SNBT (the text form used in commands) -----------------------------------

class SnbtError(ValueError):
    pass


_SUFFIX = {"b": BYTE, "s": SHORT, "l": LONG, "f": FLOAT, "d": DOUBLE}
_QUOTES = "\"'"
_BARE = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.+:")


def parse_snbt(text: str) -> Tag:
    """Parse SNBT like '{Items:[{Slot:0b,id:"minecraft:diamond",count:5}]}' into a typed Tag."""
    p = _Snbt(text)
    v = p.value()
    p.ws()
    if p.i != len(p.s):
        raise SnbtError(f"trailing characters at {p.i}: {p.s[p.i:p.i + 20]!r}")
    return v


class _Snbt:
    def __init__(self, s: str):
        self.s, self.i = s, 0

    def ws(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    def peek(self) -> str:
        self.ws()
        return self.s[self.i] if self.i < len(self.s) else ""

    def expect(self, c: str):
        if self.peek() != c:
            raise SnbtError(f"expected {c!r} at {self.i}: {self.s[self.i:self.i + 20]!r}")
        self.i += 1

    def quoted(self) -> str:
        q = self.s[self.i]
        self.i += 1
        out = []
        while self.i < len(self.s):
            c = self.s[self.i]
            if c == "\\":
                out.append(self.s[self.i + 1])
                self.i += 2
                continue
            if c == q:
                self.i += 1
                return "".join(out)
            out.append(c)
            self.i += 1
        raise SnbtError("unterminated string")

    def bare(self, allow_colon: bool = True) -> str:
        j = self.i
        while self.i < len(self.s) and self.s[self.i] in _BARE and (allow_colon or self.s[self.i] != ":"):
            self.i += 1
        if j == self.i:
            raise SnbtError(f"unexpected {self.s[self.i:self.i + 20]!r} at {self.i}")
        return self.s[j:self.i]

    def key(self) -> str:
        return self.quoted() if self.peek() in _QUOTES else self.bare(allow_colon=False)

    def value(self) -> Tag:
        c = self.peek()
        if c == "{":
            self.i += 1
            out = {}
            if self.peek() == "}":
                self.i += 1
                return Tag(COMPOUND, out)
            while True:
                k = self.key()
                self.expect(":")
                out[k] = self.value()
                if self.peek() == ",":
                    self.i += 1
                    continue
                self.expect("}")
                return Tag(COMPOUND, out)
        if c == "[":
            self.i += 1
            arrays = {"B": BYTE_ARRAY, "I": INT_ARRAY, "L": LONG_ARRAY}
            if self.peek() in arrays and self.s[self.i + 1:self.i + 2] == ";":
                t = arrays[self.s[self.i]]
                self.i += 2
                vals = []
                while self.peek() != "]":
                    vals.append(int(untag(self.value())))
                    if self.peek() == ",":
                        self.i += 1
                self.i += 1
                return Tag(t, vals)
            items = []
            while self.peek() != "]":
                if not self.peek():
                    raise SnbtError("unterminated list")
                items.append(self.value())
                if self.peek() == ",":
                    self.i += 1
            self.i += 1
            return Tag(LIST, items)
        if c and c in _QUOTES:
            return Tag(STRING, self.quoted())
        tok = self.bare()
        low = tok.lower()
        if low == "true":
            return Tag(BYTE, 1)
        if low == "false":
            return Tag(BYTE, 0)
        try:
            if low[-1] in _SUFFIX and low[:-1].lstrip("+-").replace(".", "", 1).isdigit():
                t = _SUFFIX[low[-1]]
                num = low[:-1]
                return Tag(t, float(num) if t in (FLOAT, DOUBLE) else int(num))
            if low.lstrip("+-").isdigit():
                return Tag(INT, int(low))
            return Tag(DOUBLE, float(low))
        except ValueError:
            return Tag(STRING, tok)


def to_snbt(v: Any) -> str:
    """Typed (or plain) value -> SNBT text, for /data merge and /summon."""
    t = _infer(v)
    x = t.value
    if t.type == COMPOUND:
        return "{" + ",".join(f"{_key(k)}:{to_snbt(val)}" for k, val in x.items()) + "}"
    if t.type == LIST:
        return "[" + ",".join(to_snbt(i) for i in x) + "]"
    if t.type == STRING:
        return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if t.type in (BYTE_ARRAY, INT_ARRAY, LONG_ARRAY):
        p = {BYTE_ARRAY: "B", INT_ARRAY: "I", LONG_ARRAY: "L"}[t.type]
        return f"[{p};" + ",".join(str(i) for i in x) + "]"
    suf = {BYTE: "b", SHORT: "s", INT: "", LONG: "L", FLOAT: "f", DOUBLE: "d"}[t.type]
    return f"{x}{suf}"


def _key(k: str) -> str:
    return k if k and all(c in _BARE and c != ":" for c in k) else '"' + k.replace('"', '\\"') + '"'
