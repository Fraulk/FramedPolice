## 2025-12-02

- Built logging system with buffering and eeplaced print() statements with async log functions. Logs collect in a deque and flush to Discord every 60 seconds, auto-split on char limit. Logger prints to terminal + sends to Discord channel in parallel
- Fixed HOF DM notifications: added embed validation, safe regex parsing for author extraction, proper error handling for discord.Forbidden

## 2025-12-01

Added checks to make sure the roles exist before trying to assign them and then a tiny pause (0.5 seconds) between removing the Welcome role and adding Padawan, so Discord has time to process both changes properly instead of skipping one. Also added some logs to maybe understand better what's happening
