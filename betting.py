from __future__ import annotations

import re
import uuid
import asyncio
import datetime
import discord

from logger import log_info, log_error
from db_connector import betting_db

_DURATION_RE = re.compile(r"(\d+(?:\.\d+)?)\s*([a-z]*)")

_DURATION_UNITS = {
    "": 1, "m": 1, "min": 1, "mins": 1, "minute": 1, "minutes": 1,
    "h": 60, "hr": 60, "hrs": 60, "hour": 60, "hours": 60,
    "d": 1440, "day": 1440, "days": 1440,
}


def parse_duration(raw: str) -> int:
    # takes stuff like "2h", "2 hours", "1d", "2 days", "90m", or a bare number (minutes)
    # and turns it into minutes. raises ValueError if it can't make sense of it
    raw = raw.strip().lower()
    match = _DURATION_RE.fullmatch(raw)
    if not match:
        raise ValueError(f"can't parse duration '{raw}'")

    amount = float(match.group(1))
    unit = match.group(2)
    if unit not in _DURATION_UNITS:
        raise ValueError(f"unknown duration unit '{unit}'")

    minutes = round(amount * _DURATION_UNITS[unit])
    if minutes <= 0:
        raise ValueError("duration has to be positive")
    return minutes


# In-memory store: prediction_id -> Prediction
activePredictions: dict[str, "Prediction"] = {}

# Pending embed update tasks (debounced): prediction_id -> asyncio.Task
_pendingUpdates: dict[str, asyncio.Task] = {}

# Sequential display ID counter (1, 2, 3, ...)
_display_id_counter: int = 0
EMBED_UPDATE_DELAY = 8  # seconds to wait before updating embed after a vote


async def initialize_display_id_counter(db):
    # pulls the last used bet number from the DB so we don't reset to #1 on restart
    global _display_id_counter
    if db is not None:
        max_id = await db.get_max_display_id()
        _display_id_counter = max_id
        await log_info(f"[BETTING] Initialized display_id counter to {_display_id_counter}")
    else:
        _display_id_counter = 0


async def restore_active_predictions(client: discord.Client, db):
    # bot restarted, so activePredictions is empty - load whatever was still open/closed from the DB
    if db is None:
        return
    rows = await db.get_unresolved_predictions()
    if not rows:
        await log_info("[BETTING] No active predictions to restore")
        return

    for row in rows:
        pred = Prediction.__new__(Prediction)
        pred.prediction_id = row["prediction_id"]
        pred.display_id = row["display_id"]
        pred.question = row["question"]
        pred.description = row["description"]
        pred.option_a = row["option_a"]
        pred.option_b = row["option_b"]
        pred.creator_id = row["creator_id"]
        pred.creator_name = row["creator_name"]
        pred.created_at = datetime.datetime.fromisoformat(row["created_at"])
        pred.closes_at = datetime.datetime.fromisoformat(row["closes_at"])
        pred.duration_minutes = row["duration_minutes"]
        pred.status = row["status"]
        pred.winner = row["winner"]
        pred.message_id = row["message_id"]
        pred.channel_id = row["channel_id"]
        pred.guild_id = row["guild_id"]
        pred.votes = row.get("votes", {})

        activePredictions[pred.prediction_id] = pred

        # Re-register persistent view so buttons still work
        view = PredictionView(pred.prediction_id)
        view.vote_a.label = pred.option_a
        view.vote_b.label = pred.option_b
        client.add_view(view)

        # Re-arm auto-close if still open
        if pred.status == "open":
            asyncio.create_task(auto_close_prediction(client, pred, db))

    await log_info(f"[BETTING] Restored {len(rows)} active prediction(s) from DB")


class Prediction:
    def __init__(
        self,
        question: str,
        description: str,
        option_a: str,
        option_b: str,
        creator_id: int,
        creator_name: str,
        closes_at: datetime.datetime,
        guild_id: int,
        channel_id: int,
        duration_minutes: int = 1440,
    ):
        global _display_id_counter
        _display_id_counter += 1
        
        self.prediction_id: str = str(uuid.uuid4())[:8]  # internal id, not shown to users
        self.display_id: int = _display_id_counter  # this is the "Bet #N" number people actually see
        self.question = question
        self.description = description
        self.option_a = option_a  # YES equivalent
        self.option_b = option_b  # NO equivalent
        self.creator_id = creator_id
        self.creator_name = creator_name
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
        self.closes_at = closes_at
        self.duration_minutes = duration_minutes
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.status = "open"  # open | closed | resolved
        self.winner: str | None = None  # "A" | "B" | None
        self.message_id: int | None = None
        # votes: {user_id: "A" | "B"}
        self.votes: dict[int, str] = {}

    @property
    def votes_a(self) -> int:
        return sum(1 for v in self.votes.values() if v == "A")

    @property
    def votes_b(self) -> int:
        return sum(1 for v in self.votes.values() if v == "B")

    @property
    def total_votes(self) -> int:
        return len(self.votes)

    def percent_a(self) -> float:
        if self.total_votes == 0:
            return 50.0
        return round(self.votes_a / self.total_votes * 100, 1)

    def percent_b(self) -> float:
        if self.total_votes == 0:
            return 50.0
        return round(self.votes_b / self.total_votes * 100, 1)

    def odds_a(self) -> float:
        # decimal odds, just 1 / implied probability
        prob_a = self.percent_a() / 100
        if prob_a <= 0:
            return float('inf')
        return round(1 / prob_a, 2)

    def odds_b(self) -> float:
        prob_b = self.percent_b() / 100
        if prob_b <= 0:
            return float('inf')
        return round(1 / prob_b, 2)

    def is_open(self) -> bool:
        return self.status == "open" and datetime.datetime.now(datetime.timezone.utc) < self.closes_at

    def time_remaining_str(self) -> str:
        if self.status != "open":
            return "Closed"
        # going off duration_minutes instead of closes_at directly so this doesn't drift with server timezone weirdness
        elapsed = datetime.datetime.now(datetime.timezone.utc) - self.created_at
        total_duration = datetime.timedelta(minutes=self.duration_minutes)
        delta = total_duration - elapsed
        if delta.total_seconds() <= 0:
            return "Expired"
        hours, rem = divmod(int(delta.total_seconds()), 3600)
        minutes = rem // 60
        if hours >= 24:
            days = hours // 24
            return f"{days}d {hours % 24}h"
        return f"{hours}h {minutes}m"

    def calculate_scores(self) -> dict[int, float]:
        # kinda like Polymarket - correct side splits (losing_pool / total) * 100 pts between them,
        # wrong side just eats a flat -10. so picking the underdog and being right pays off more,
        # it's not some crazy exponential curve, just proportional to how many people you beat
        if self.winner is None:
            return {}

        scores: dict[int, float] = {}
        total = self.total_votes
        if total == 0:
            return {}

        winning_pool = self.votes_a if self.winner == "A" else self.votes_b
        losing_pool = self.votes_b if self.winner == "A" else self.votes_a

        for user_id, choice in self.votes.items():
            if choice == self.winner:
                if winning_pool > 0:
                    score = round((losing_pool / total) * 100, 1)
                else:
                    score = 0.0
                scores[user_id] = max(score, 1.0)  # at least 1pt for correct
            else:
                scores[user_id] = -10.0  # flat penalty for wrong

        return scores


def build_prediction_embed(pred: Prediction) -> discord.Embed:
    is_open = pred.is_open()

    if is_open:
        color = 0x5865F2  # blurple
        status_str = f"Closes <t:{int(pred.closes_at.timestamp())}:R>"
    elif pred.status == "resolved":
        color = 0x57F287
        winner_label = pred.option_a if pred.winner == "A" else pred.option_b
        status_str = f"Resolved — Winner: **{winner_label}**"
    else:
        color = 0xFEE75C  # yellow = closed, awaiting resolution
        status_str = "Voting closed — awaiting resolution"

    embed = discord.Embed(
        title=f"{pred.question}",
        description=pred.description or "",
        color=color,
    )

    pct_a = pred.percent_a()
    pct_b = pred.percent_b()

    # bar stays all white with no votes, otherwise fills green for whichever side is ahead
    if pred.total_votes == 0:
        bar = "⬜" * 20
    else:
        bar_filled = int(max(pct_a, pct_b) / 100 * 20)
        bar = "🟩" * bar_filled + "⬜" * (20 - bar_filled)

    odds_a = pred.odds_a()
    odds_b = pred.odds_b()
    odds_a_str = f"{odds_a}x" if odds_a != float('inf') else "∞"
    odds_b_str = f"{odds_b}x" if odds_b != float('inf') else "∞"
    
    embed.add_field(
        name=f"{pred.option_a}",
        value=f"{pct_a}% • Odds: {odds_a_str}\n{pred.votes_a} votes",
        inline=True,
    )
    embed.add_field(
        name=f"{pred.option_b}",
        value=f"{pct_b}% • Odds: {odds_b_str}\n{pred.votes_b} votes",
        inline=True,
    )
    embed.add_field(name="\u200b", value=bar, inline=False)

    embed.set_footer(
        text=f"Bet #{pred.display_id} • Created by {pred.creator_name} • {pred.total_votes} total votes"
    )

    embed.add_field(name="Status", value=status_str, inline=False)

    return embed


class PredictionView(discord.ui.View):
    # the two vote buttons attached under a prediction embed

    def __init__(self, prediction_id: str):
        super().__init__(timeout=None)
        self.prediction_id = prediction_id
        # custom_id needs to be fixed per-prediction, that's what lets the buttons still work after a restart
        self.vote_a.custom_id = f"bet_vote_a_{prediction_id}"
        self.vote_b.custom_id = f"bet_vote_b_{prediction_id}"

    def _get_pred(self) -> Prediction | None:
        return activePredictions.get(self.prediction_id)

    async def _handle_vote(self, interaction: discord.Interaction, choice: str):
        pred = self._get_pred()
        if pred is None:
            await interaction.response.send_message(
                "This prediction no longer exists.", ephemeral=True
            )
            return

        if not pred.is_open():
            await interaction.response.send_message(
                "⚠️ Voting is closed for this prediction.", ephemeral=True
            )
            return

        user_id = interaction.user.id
        previous = pred.votes.get(user_id)

        if previous == choice:
            await interaction.response.send_message(
                f"You already voted **{pred.option_a if choice == 'A' else pred.option_b}**.",
                ephemeral=True,
            )
            return

        pred.votes[user_id] = choice
        option_label = pred.option_a if choice == "A" else pred.option_b

        if previous is not None:
            msg = f"You switched your vote to **{option_label}**."
        else:
            msg = f"You voted **{option_label}**!"

        await interaction.response.send_message(msg, ephemeral=True)
        await log_info(
            f"[BETTING] {interaction.user.name} voted {choice} on prediction {pred.prediction_id}"
        )

        if betting_db.is_connected():
            await betting_db.record_vote(
                pred.prediction_id,
                user_id,
                interaction.user.display_name,
                choice,
            )

        await _schedule_embed_update(interaction.client, pred)

    @discord.ui.button(
        label="Option A", style=discord.ButtonStyle.secondary, custom_id="bet_vote_a_placeholder"
    )
    async def vote_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_vote(interaction, "A")

    @discord.ui.button(
        label="Option B", style=discord.ButtonStyle.secondary, custom_id="bet_vote_b_placeholder"
    )
    async def vote_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_vote(interaction, "B")


async def _schedule_embed_update(client: discord.Client, pred: Prediction):
    pred_id = pred.prediction_id

    # if someone spam-votes we don't want to hammer the Discord API, so cancel and reschedule
    existing = _pendingUpdates.get(pred_id)
    if existing and not existing.done():
        existing.cancel()

    async def _do_update():
        await asyncio.sleep(EMBED_UPDATE_DELAY)
        try:
            channel = client.get_channel(pred.channel_id)
            if channel is None:
                return
            message = await channel.fetch_message(pred.message_id)
            embed = build_prediction_embed(pred)
            view = PredictionView(pred.prediction_id)
            if pred.is_open():
                view.vote_a.label = pred.option_a
                view.vote_b.label = pred.option_b
            else:
                view = discord.ui.View()  # empty view disables buttons
            await message.edit(embed=embed, view=view)
            await log_info(f"[BETTING] Updated embed for prediction {pred.prediction_id}")
        except discord.NotFound:
            await log_error(f"[BETTING] Message not found for prediction {pred.prediction_id}")
        except Exception as e:
            await log_error(f"[BETTING] Failed to update embed for {pred.prediction_id}: {e}")
        finally:
            _pendingUpdates.pop(pred.prediction_id, None)

    task = asyncio.create_task(_do_update())
    _pendingUpdates[pred.prediction_id] = task


async def close_prediction(
    client: discord.Client, pred: Prediction, winner: str, db
) -> str:
    # resolves the bet, hands out scores, edits the embed one last time, returns a summary to post
    if pred.status == "resolved":
        return "This prediction has already been resolved."

    pred.status = "resolved"
    pred.winner = winner

    scores = pred.calculate_scores()
    winner_label = pred.option_a if winner == "A" else pred.option_b

    if db is not None:
        try:
            await db.resolve_prediction(pred.prediction_id, winner, scores)
        except Exception as e:
            await log_error(f"[BETTING] DB error on resolve: {e}")

    # no debounce here, closing should reflect right away
    try:
        channel = client.get_channel(pred.channel_id)
        if channel and pred.message_id:
            message = await channel.fetch_message(pred.message_id)
            embed = build_prediction_embed(pred)
            await message.edit(embed=embed, view=discord.ui.View())  # remove buttons
    except Exception as e:
        await log_error(f"[BETTING] Failed to update embed on close: {e}")

    correct_count = sum(1 for v in pred.votes.values() if v == winner)
    wrong_count = pred.total_votes - correct_count

    summary = (
        f"Prediction resolved!\n"
        f"**{pred.question}**\n"
        f"Winner: **{winner_label}**\n\n"
        f"**{correct_count}** correct predictions, **{wrong_count}** incorrect.\n"
    )

    if scores:
        best_score = max(scores.values())
        summary += f"Top score this round: **{best_score} pts**"

    return summary


async def auto_close_prediction(client: discord.Client, pred: Prediction, db):
    # sleeps until closes_at, then flips status to closed so it's awaiting a mod to resolve it
    now = datetime.datetime.now(datetime.timezone.utc)
    wait_secs = (pred.closes_at - now).total_seconds()
    if wait_secs > 0:
        await asyncio.sleep(wait_secs)

    if pred.status != "open":
        return  # already resolved or closed manually

    pred.status = "closed"
    await log_info(f"[BETTING] Prediction {pred.prediction_id} voting window expired")

    try:
        channel = client.get_channel(pred.channel_id)
        if channel and pred.message_id:
            message = await channel.fetch_message(pred.message_id)
            embed = build_prediction_embed(pred)
            # Keep buttons disabled but visible
            await message.edit(embed=embed, view=discord.ui.View())
    except Exception as e:
        await log_error(f"[BETTING] Failed to update embed on auto-close: {e}")

    if db is not None:
        try:
            await db.close_prediction(pred.prediction_id)
        except Exception as e:
            await log_error(f"[BETTING] DB error on auto-close: {e}")
