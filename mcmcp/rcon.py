"""Minimal, thread-safe Source RCON client for the vanilla Minecraft server.

Protocol: little-endian int32 length, int32 request id, int32 type, ASCII body,
two NUL bytes. Type 3 = login, 2 = command, 0 = response.

Vanilla splits long responses into 4096-byte packets but never marks the last
one, and it drops the connection on the usual "empty marker packet" trick. So a
response is complete when a packet body is shorter than 4096 bytes; a body of
exactly 4096 bytes means more may follow, which we wait for with a short timeout.
"""

from __future__ import annotations

import socket
import struct
import threading

LOGIN, COMMAND, RESPONSE = 3, 2, 0
# Vanilla rejects request bodies above 1446 bytes.
MAX_COMMAND_BYTES = 1446
FRAGMENT_BYTES = 4096


class RconError(RuntimeError):
    pass


class Rcon:
    def __init__(self, host: str, port: int, password: str, timeout: float = 15.0):
        self.host, self.port, self.password, self.timeout = host, port, password, timeout
        self._sock: socket.socket | None = None
        self._lock = threading.Lock()
        self._next_id = 1

    # -- connection -------------------------------------------------------
    def _connect(self) -> None:
        sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
        self._sock = sock
        rid = self._send(LOGIN, self.password)
        got_id, _, _ = self._recv()
        if got_id == -1 or got_id != rid:
            self.close()
            raise RconError("RCON login rejected (check rcon.password in server.properties)")

    def close(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            finally:
                self._sock = None

    @property
    def connected(self) -> bool:
        return self._sock is not None

    # -- framing ----------------------------------------------------------
    def _send(self, ptype: int, body: str) -> int:
        rid = self._next_id
        self._next_id = (self._next_id % 0x7FFFFFFF) + 1
        payload = struct.pack("<ii", rid, ptype) + body.encode("utf-8") + b"\x00\x00"
        self._sock.sendall(struct.pack("<i", len(payload)) + payload)
        return rid

    def _read_exact(self, n: int) -> bytes:
        buf = bytearray()
        while len(buf) < n:
            chunk = self._sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("RCON connection closed by server")
            buf += chunk
        return bytes(buf)

    def _recv_raw(self) -> tuple[int, int, bytes]:
        (length,) = struct.unpack("<i", self._read_exact(4))
        data = self._read_exact(length)
        rid, ptype = struct.unpack("<ii", data[:8])
        return rid, ptype, data[8:-2]

    def _recv(self) -> tuple[int, int, str]:
        rid, ptype, body = self._recv_raw()
        return rid, ptype, body.decode("utf-8", errors="replace")

    # -- public -----------------------------------------------------------
    def command(self, cmd: str) -> str:
        cmd = cmd.lstrip("/")
        if len(cmd.encode("utf-8")) > MAX_COMMAND_BYTES:
            raise RconError(f"command is {len(cmd)} bytes; RCON limit is {MAX_COMMAND_BYTES}")
        with self._lock:
            # Only retry when the command provably never reached the server, so
            # an edit is never applied twice.
            for attempt in (0, 1):
                try:
                    if not self._sock:
                        self._connect()
                    rid = self._send(COMMAND, cmd)
                    break
                except OSError:
                    self.close()
                    if attempt:
                        raise
            try:
                parts: list[bytes] = []
                while True:
                    if parts:
                        self._sock.settimeout(0.3)
                    try:
                        got, _, body = self._recv_raw()
                    except socket.timeout:
                        # Response was an exact multiple of 4096 bytes. Drop the
                        # socket in case the timeout hit mid-packet.
                        self.close()
                        break
                    finally:
                        if self._sock:
                            self._sock.settimeout(self.timeout)
                    if got != rid:
                        continue
                    parts.append(body)
                    if len(body) < FRAGMENT_BYTES:
                        break
                return b"".join(parts).decode("utf-8", errors="replace")
            except OSError:
                self.close()
                raise
