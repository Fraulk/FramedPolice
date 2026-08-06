# sqlite layer for the betting stuff, uses aiosqlite so it doesn't block the event loop
# betting.db gets created next to the bot on first run, nothing to configure
from __future__ import annotations

import os
import aiosqlite
import datetime
from contextlib import asynccontextmanager
from logger import log_info, log_error


DB_PATH = os.path.abspath(os.getenv("DB_PATH", "./betting.db"))

_CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS predictions (
        prediction_id   TEXT PRIMARY KEY,
        display_id      INTEGER UNIQUE NOT NULL,
        creator_id      INTEGER NOT NULL,
        creator_name    TEXT NOT NULL,
        question        TEXT NOT NULL,
        description     TEXT NOT NULL DEFAULT '',
        option_a        TEXT NOT NULL DEFAULT 'YES',
        option_b        TEXT NOT NULL DEFAULT 'NO',
        created_at      TEXT NOT NULL,
        closes_at       TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL DEFAULT 1440,
        status          TEXT NOT NULL DEFAULT 'open',
        winner          TEXT,
        message_id      INTEGER,
        channel_id      INTEGER,
        guild_id        INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS prediction_votes (
        vote_id         INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_id   TEXT NOT NULL REFERENCES predictions(prediction_id) ON DELETE CASCADE,
        user_id         INTEGER NOT NULL,
        username        TEXT,
        chosen_option   TEXT NOT NULL,
        placed_at       TEXT NOT NULL,
        is_correct      INTEGER,
        score_awarded   REAL,
        UNIQUE (prediction_id, user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS user_scores (
        user_id         INTEGER PRIMARY KEY,
        username        TEXT NOT NULL,
        global_score    REAL NOT NULL DEFAULT 0,
        total_bets      INTEGER NOT NULL DEFAULT 0,
        correct_bets    INTEGER NOT NULL DEFAULT 0,
        last_updated    TEXT NOT NULL
    )
    """,
]


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


@asynccontextmanager
async def _get_conn():
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")
        yield conn


class BettingDB:
    def __init__(self):
        self._ready: bool = False

    async def connect(self):
        try:
            async with _get_conn() as conn:
                for sql in _CREATE_TABLES:
                    await conn.execute(sql)
                await conn.commit()
            self._ready = True
            await log_info(f"[DB] SQLite database ready at {DB_PATH}")
            return True
        except Exception as e:
            await log_error(f"[DB] Failed to initialise SQLite: {e}")
            self._ready = False
            return False

    def is_connected(self) -> bool:
        return self._ready

    async def create_prediction(self, pred) -> bool:
        if not self.is_connected():
            return False
        try:
            async with _get_conn() as conn:
                await conn.execute(
                    """
                    INSERT INTO predictions
                        (prediction_id, display_id, creator_id, creator_name, question, description,
                         option_a, option_b, created_at, closes_at, duration_minutes, message_id, channel_id, guild_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        pred.prediction_id,
                        pred.display_id,
                        pred.creator_id,
                        pred.creator_name,
                        pred.question,
                        pred.description or "",
                        pred.option_a,
                        pred.option_b,
                        pred.created_at.isoformat(),
                        pred.closes_at.isoformat(),
                        pred.duration_minutes,
                        pred.message_id,
                        pred.channel_id,
                        pred.guild_id,
                    ),
                )
                await conn.commit()
            return True
        except Exception as e:
            await log_error(f"[DB] create_prediction failed: {e}")
            return False

    async def update_message_id(self, prediction_id: str, message_id: int):
        if not self.is_connected():
            return
        try:
            async with _get_conn() as conn:
                await conn.execute(
                    "UPDATE predictions SET message_id = ? WHERE prediction_id = ?",
                    (message_id, prediction_id),
                )
                await conn.commit()
        except Exception as e:
            await log_error(f"[DB] update_message_id failed: {e}")

    async def close_prediction(self, prediction_id: str):
        if not self.is_connected():
            return
        try:
            async with _get_conn() as conn:
                await conn.execute(
                    "UPDATE predictions SET status = 'closed' WHERE prediction_id = ?",
                    (prediction_id,),
                )
                await conn.commit()
        except Exception as e:
            await log_error(f"[DB] close_prediction failed: {e}")

    async def resolve_prediction(
        self, prediction_id: str, winner: str, scores: dict[int, float]
    ):
        if not self.is_connected():
            return
        try:
            async with _get_conn() as conn:
                await conn.execute(
                    "UPDATE predictions SET status='resolved', winner=? WHERE prediction_id=?",
                    (winner, prediction_id),
                )
                now = _now_iso()
                for user_id, score in scores.items():
                    is_correct = 1 if score > 0 else 0
                    await conn.execute(
                        """
                        UPDATE prediction_votes
                        SET is_correct = ?, score_awarded = ?
                        WHERE prediction_id = ? AND user_id = ?
                        """,
                        (is_correct, score, prediction_id, user_id),
                    )
                    cursor = await conn.execute(
                        "SELECT username FROM prediction_votes WHERE user_id = ? LIMIT 1",
                        (user_id,),
                    )
                    row = await cursor.fetchone()
                    username = row["username"] if row else str(user_id)
                    await conn.execute(
                        """
                        INSERT INTO user_scores (user_id, username, global_score, total_bets, correct_bets, last_updated)
                        VALUES (?, ?, ?, 1, ?, ?)
                        ON CONFLICT (user_id) DO UPDATE SET
                            global_score = user_scores.global_score + excluded.global_score,
                            total_bets   = user_scores.total_bets + 1,
                            correct_bets = user_scores.correct_bets + excluded.correct_bets,
                            last_updated = excluded.last_updated
                        """,
                        (user_id, username, score, is_correct, now),
                    )
                await conn.commit()
        except Exception as e:
            await log_error(f"[DB] resolve_prediction failed: {e}")

    async def record_vote(
        self, prediction_id: str, user_id: int, username: str, choice: str
    ):
        if not self.is_connected():
            return
        try:
            async with _get_conn() as conn:
                await conn.execute(
                    """
                    INSERT INTO prediction_votes (prediction_id, user_id, username, chosen_option, placed_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT (prediction_id, user_id) DO UPDATE SET
                        chosen_option = excluded.chosen_option,
                        placed_at     = excluded.placed_at,
                        username      = excluded.username
                    """,
                    (prediction_id, user_id, username, choice, _now_iso()),
                )
                await conn.commit()
        except Exception as e:
            await log_error(f"[DB] record_vote failed: {e}")

    async def get_open_predictions(self) -> list[dict]:
        if not self.is_connected():
            return []
        try:
            async with _get_conn() as conn:
                cursor = await conn.execute(
                    "SELECT * FROM predictions WHERE status IN ('open','closed') ORDER BY created_at DESC"
                )
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            await log_error(f"[DB] get_open_predictions failed: {e}")
            return []

    async def get_prediction(self, prediction_id: str) -> dict | None:
        if not self.is_connected():
            return None
        try:
            async with _get_conn() as conn:
                cursor = await conn.execute(
                    "SELECT * FROM predictions WHERE prediction_id = ?", (prediction_id,)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            await log_error(f"[DB] get_prediction failed: {e}")
            return None

    async def get_global_leaderboard(self, limit: int = 10) -> list[dict]:
        if not self.is_connected():
            return []
        try:
            async with _get_conn() as conn:
                cursor = await conn.execute(
                    """
                    SELECT user_id, username, global_score, total_bets, correct_bets,
                           CASE WHEN total_bets > 0
                                THEN ROUND(CAST(correct_bets AS REAL) / total_bets * 100, 1)
                                ELSE 0 END AS accuracy
                    FROM user_scores
                    ORDER BY global_score DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            await log_error(f"[DB] get_global_leaderboard failed: {e}")
            return []

    async def get_event_leaderboard(self, prediction_id: str, limit: int = 10) -> list[dict]:
        if not self.is_connected():
            return []
        try:
            async with _get_conn() as conn:
                cursor = await conn.execute(
                    """
                    SELECT user_id, username, score_awarded, is_correct
                    FROM prediction_votes
                    WHERE prediction_id = ? AND score_awarded IS NOT NULL
                    ORDER BY score_awarded DESC
                    LIMIT ?
                    """,
                    (prediction_id, limit),
                )
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            await log_error(f"[DB] get_event_leaderboard failed: {e}")
            return []

    async def get_user_stats(self, user_id: int) -> dict | None:
        if not self.is_connected():
            return None
        try:
            async with _get_conn() as conn:
                cursor = await conn.execute(
                    """
                    SELECT *,
                           CASE WHEN total_bets > 0
                                THEN ROUND(CAST(correct_bets AS REAL) / total_bets * 100, 1)
                                ELSE 0 END AS accuracy
                    FROM user_scores
                    WHERE user_id = ?
                    """,
                    (user_id,),
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            await log_error(f"[DB] get_user_stats failed: {e}")
            return None

    async def get_user_bets(self, user_id: int, limit: int = 10) -> list[dict]:
        if not self.is_connected():
            return []
        try:
            async with _get_conn() as conn:
                cursor = await conn.execute(
                    """
                    SELECT pv.*, p.question, p.option_a, p.option_b, p.status, p.winner
                    FROM prediction_votes pv
                    JOIN predictions p ON p.prediction_id = pv.prediction_id
                    WHERE pv.user_id = ?
                    ORDER BY pv.placed_at DESC
                    LIMIT ?
                    """,
                    (user_id, limit),
                )
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            await log_error(f"[DB] get_user_bets failed: {e}")
            return []

    async def get_bet_participants(self, prediction_id: str) -> list[dict]:
        if not self.is_connected():
            return []
        try:
            async with _get_conn() as conn:
                cursor = await conn.execute(
                    """
                    SELECT
                        pv.user_id,
                        pv.username,
                        pv.chosen_option,
                        p.option_a,
                        p.option_b,
                        pv.score_awarded,
                        pv.is_correct,
                        pv.placed_at
                    FROM prediction_votes pv
                    JOIN predictions p ON p.prediction_id = pv.prediction_id
                    WHERE pv.prediction_id = ?
                    ORDER BY pv.placed_at ASC
                    """,
                    (prediction_id,),
                )
                rows = await cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            await log_error(f"[DB] get_bet_participants failed: {e}")
            return []

    async def get_max_display_id(self) -> int:
        if not self.is_connected():
            return 0
        try:
            async with _get_conn() as conn:
                cursor = await conn.execute("SELECT COALESCE(MAX(display_id), 0) FROM predictions")
                row = await cursor.fetchone()
                return row[0] if row else 0
        except Exception as e:
            await log_error(f"[DB] get_max_display_id failed: {e}")
            return 0

    async def get_unresolved_predictions(self) -> list[dict]:
        # grabs everything still open/closed plus their votes, used on startup to rebuild state in memory
        if not self.is_connected():
            return []
        try:
            async with _get_conn() as conn:
                cursor = await conn.execute(
                    "SELECT * FROM predictions WHERE status IN ('open', 'closed') ORDER BY created_at ASC"
                )
                preds = [dict(r) for r in await cursor.fetchall()]

                for pred in preds:
                    cursor = await conn.execute(
                        "SELECT user_id, chosen_option FROM prediction_votes WHERE prediction_id = ?",
                        (pred["prediction_id"],),
                    )
                    pred["votes"] = {row["user_id"]: row["chosen_option"] for row in await cursor.fetchall()}

                return preds
        except Exception as e:
            await log_error(f"[DB] get_unresolved_predictions failed: {e}")
            return []


# single shared instance, app_commands and betting both import this
betting_db = BettingDB()
