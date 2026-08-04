## 2026-08-04

Added a prediction market / betting system. A mod posts a question with `/bet_create` (two options, a duration like `2h`, `1d`, `30m`, whatever), it goes up as an embed with vote buttons, and people click to bet on one side or the other - can switch their vote until it closes. Voting auto-closes when the timer runs out, then a mod resolves it with `/bet_close` and picks the winning side. Everyone who called it right splits points based on how many people bet the other way (so calling the underdog pays off more), wrong picks eat a flat -10. Everything's stored in a local sqlite db (`betting.db`) so scores and open bets survive a bot restart. `/my_bets` shows your own history and score, `/leaderboard` shows the server ranking (or the ranking for one specific bet).

## 2025-12-04

- Fix: sixth shot is now reliably deleted and counter no longer drifts (bot-marked deletes are ignored by `on_message_delete`). added delete error handling and clearer logs.

## 2025-12-03

Got the per-user shot limit behaving properly: the sixth post in a two-hour window is now deleted every time. The check looks at the next count (count+1) before touching the message, we return immediately on delete so the counter doesn’t drift, and when the window rolls over we start at 1 for the first shot. The DM includes the exact next allowed time. Swapped the prints in this path for the async logger so you can see the flow in the terminal and the logs channel.

## 2025-12-02

- Built logging system with buffering and eeplaced print() statements with async log functions. Logs collect in a deque and flush to Discord every 60 seconds, auto-split on char limit. Logger prints to terminal + sends to Discord channel in parallel
- Fixed HOF DM notifications: added embed validation, safe regex parsing for author extraction, proper error handling for discord.Forbidden

## 2025-12-01

Added checks to make sure the roles exist before trying to assign them and then a tiny pause (0.5 seconds) between removing the Welcome role and adding Padawan, so Discord has time to process both changes properly instead of skipping one. Also added some logs to maybe understand better what's happening
