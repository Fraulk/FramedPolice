# talks to the PocketBase instance on Coolify that actually holds the betting data.
# used to be a local sqlite file, now it's just an HTTP client - same class/method
from __future__ import annotations

import os
import datetime
import aiohttp
from logger import log_info, log_error

POCKETBASE_URL = os.getenv("POCKETBASE_URL", "").rstrip("/")
BETTING_API_TOKEN = os.getenv("BETTING_API_TOKEN", "")


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _parse_pb_dt(raw: str) -> datetime.datetime:
    raw = raw.strip().replace("Z", "+00:00").replace(" ", "T")
    if "." in raw:
        head, _, rest = raw.partition(".")
        frac, plus, tz = rest.partition("+")
        frac = (frac + "000000")[:6]
        raw = f"{head}.{frac}+{tz}" if plus else f"{head}.{frac}"
    return datetime.datetime.fromisoformat(raw)


def _clean_dt_str(raw: str | None) -> str | None:
    if not raw:
        return None
    return _parse_pb_dt(raw).isoformat()


def _to_int(raw) -> int | None:
    if raw is None or raw == "":
        return None
    return int(raw)


def _normalize_prediction(row: dict) -> dict:
    row = dict(row)
    row["creator_id"] = _to_int(row.get("creator_id"))
    row["message_id"] = _to_int(row.get("message_id"))
    row["channel_id"] = _to_int(row.get("channel_id"))
    row["guild_id"] = _to_int(row.get("guild_id"))
    row["created_at"] = _clean_dt_str(row.get("created_at"))
    row["closes_at"] = _clean_dt_str(row.get("closes_at"))
    row["winner"] = row.get("winner") or None
    return row


def _normalize_vote(row: dict) -> dict:
    row = dict(row)
    row["user_id"] = _to_int(row.get("user_id"))
    return row


def _normalize_score(row: dict) -> dict:
    row = dict(row)
    row["user_id"] = _to_int(row.get("user_id"))
    return row


class BettingDB:
    def __init__(self):
        self._ready: bool = False
        self._session: aiohttp.ClientSession | None = None

    async def connect(self) -> bool:
        if not POCKETBASE_URL or not BETTING_API_TOKEN:
            await log_error("[DB] POCKETBASE_URL / BETTING_API_TOKEN not set in .env")
            self._ready = False
            return False

        self._session = aiohttp.ClientSession(
            base_url=POCKETBASE_URL,
            headers={"Authorization": f"Bearer {BETTING_API_TOKEN}"},
            timeout=aiohttp.ClientTimeout(total=10),
        )
        try:
            async with self._session.get("/api/health") as resp:
                self._ready = resp.status == 200
        except Exception as e:
            await log_error(f"[DB] Can't reach PocketBase at {POCKETBASE_URL}: {e}")
            self._ready = False

        if self._ready:
            await log_info(f"[DB] Connected to PocketBase at {POCKETBASE_URL}")
        return self._ready

    def is_connected(self) -> bool:
        return self._ready

    async def _get(self, path: str, **params):
        try:
            async with self._session.get(path, params=params) as resp:
                if resp.status >= 400:
                    await log_error(f"[DB] GET {path} -> {resp.status}: {await resp.text()}")
                    return None
                return await resp.json()
        except Exception as e:
            await log_error(f"[DB] GET {path} failed: {e}")
            return None

    async def _send(self, method: str, path: str, body: dict | None = None) -> bool:
        try:
            async with self._session.request(method, path, json=body) as resp:
                if resp.status >= 400:
                    await log_error(f"[DB] {method} {path} -> {resp.status}: {await resp.text()}")
                    return False
                return True
        except Exception as e:
            await log_error(f"[DB] {method} {path} failed: {e}")
            return False

    # ─── writes ─────────────────────────────────────────────────────────

    async def create_prediction(self, pred) -> bool:
        if not self.is_connected():
            return False
        return await self._send("POST", "/api/betting/predictions", {
            "prediction_id": pred.prediction_id,
            "display_id": pred.display_id,
            "creator_id": str(pred.creator_id),
            "creator_name": pred.creator_name,
            "question": pred.question,
            "description": pred.description or "",
            "option_a": pred.option_a,
            "option_b": pred.option_b,
            "created_at": pred.created_at.isoformat(),
            "closes_at": pred.closes_at.isoformat(),
            "duration_minutes": pred.duration_minutes,
            "message_id": str(pred.message_id) if pred.message_id else None,
            "channel_id": str(pred.channel_id),
            "guild_id": str(pred.guild_id),
        })

    async def update_message_id(self, prediction_id: str, message_id: int):
        if not self.is_connected():
            return
        await self._send("PATCH", f"/api/betting/predictions/{prediction_id}/message", {"message_id": str(message_id)})

    async def close_prediction(self, prediction_id: str):
        if not self.is_connected():
            return
        await self._send("POST", f"/api/betting/predictions/{prediction_id}/close")

    async def resolve_prediction(self, prediction_id: str, winner: str, scores: dict[int, float]):
        if not self.is_connected():
            return
        await self._send("POST", f"/api/betting/predictions/{prediction_id}/resolve", {
            "winner": winner,
            "scores": {str(user_id): score for user_id, score in scores.items()},
        })

    async def record_vote(self, prediction_id: str, user_id: int, username: str, choice: str):
        if not self.is_connected():
            return
        await self._send("POST", f"/api/betting/predictions/{prediction_id}/votes", {
            "user_id": str(user_id),
            "username": username,
            "choice": choice,
            "placed_at": _now_iso(),
        })

    # ─── reads ──────────────────────────────────────────────────────────

    async def get_open_predictions(self) -> list[dict]:
        if not self.is_connected():
            return []
        rows = await self._get("/api/betting/predictions")
        return [_normalize_prediction(r) for r in rows] if rows else []

    async def get_prediction(self, prediction_id: str) -> dict | None:
        if not self.is_connected():
            return None
        row = await self._get(f"/api/betting/predictions/{prediction_id}")
        return _normalize_prediction(row) if row else None

    async def get_global_leaderboard(self, limit: int = 10) -> list[dict]:
        if not self.is_connected():
            return []
        rows = await self._get("/api/betting/leaderboard/global", limit=limit)
        return [_normalize_score(r) for r in rows] if rows else []

    async def get_event_leaderboard(self, prediction_id: str, limit: int = 10) -> list[dict]:
        if not self.is_connected():
            return []
        rows = await self._get(f"/api/betting/predictions/{prediction_id}/leaderboard", limit=limit)
        return [_normalize_vote(r) for r in rows] if rows else []

    async def get_user_stats(self, user_id: int) -> dict | None:
        if not self.is_connected():
            return None
        row = await self._get(f"/api/betting/users/{user_id}/stats")
        return _normalize_score(row) if row else None

    async def get_user_bets(self, user_id: int, limit: int = 10) -> list[dict]:
        if not self.is_connected():
            return []
        rows = await self._get(f"/api/betting/users/{user_id}/bets", limit=limit)
        return [_normalize_vote(r) for r in rows] if rows else []

    async def get_bet_participants(self, prediction_id: str) -> list[dict]:
        if not self.is_connected():
            return []
        rows = await self._get(f"/api/betting/predictions/{prediction_id}/participants")
        return [_normalize_vote(r) for r in rows] if rows else []

    async def get_max_display_id(self) -> int:
        if not self.is_connected():
            return 0
        row = await self._get("/api/betting/max-display-id")
        return row["max_display_id"] if row else 0

    async def get_unresolved_predictions(self) -> list[dict]:
        if not self.is_connected():
            return []
        rows = await self._get("/api/betting/unresolved-predictions")
        if not rows:
            return []
        out = []
        for raw in rows:
            pred = _normalize_prediction(raw)
            pred["votes"] = {int(uid): choice for uid, choice in raw.get("votes", {}).items()}
            out.append(pred)
        return out

    async def export_all(self) -> dict | None:
        if not self.is_connected():
            return None
        return await self._get("/api/betting/export")


betting_db = BettingDB()
