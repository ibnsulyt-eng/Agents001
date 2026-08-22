# TikTok Live Monitoring

`monitor_main.py` watches a list of TikTok accounts' live rooms in real time — comments,
gifts, joins, and likes — for moderation/safety monitoring purposes: catching spam,
scam links, harassment, or suspicious accounts as they happen.

## How it works

```
RoomWatcher (per account) ──► shared queue ──► batch flusher
     │                                              │
     uses TikTokLive (unofficial client,             ├─► SQLite: every event logged
     websocket feed of the public live room)          │
                                                       ├─► rule filter (free, instant):
                                                       │     banned keywords, links,
                                                       │     spammy repeated text
                                                       │
                                                       └─► LLM Monitor agent (batched,
                                                             every N seconds/comments):
                                                             catches nuanced cases the
                                                             rules miss
                                                                   │
                                                             flagged → alert (Discord/
                                                             Telegram) + marked in SQLite
```

Rules run first and are free/instant — only comments that pass the rule filter get
batched up and sent to the LLM, which keeps free-tier API usage low even on busy chats.

## Important caveats

- **Unofficial client**: `TikTokLive` (https://github.com/isaackogan/TikTokLive) is a
  reverse-engineered client, not an official TikTok API. TikTok can change their
  protocol at any time and break it — if events stop coming in, check that project for
  an update. It reads only what's already publicly visible to anyone watching the live
  (no login, no private data).
- **Use within TikTok's Terms of Service** for whatever you're monitoring — e.g.
  monitoring your own account/community for moderation, or a public room with a
  legitimate safety purpose. This is a data-reading tool, not a bypass of any account
  security.

## Setup

In `.env` (see `.env.example`):

```
TIKTOK_WATCHLIST=someaccount,anotheraccount
MONITOR_BANNED_KEYWORDS=scam,giveaway link,dm me for
ALERT_PROVIDER=discord
ALERT_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

Discord webhook: Server Settings → Integrations → Webhooks → New Webhook → Copy URL.
Telegram: message [@BotFather](https://t.me/BotFather) to create a bot and get a token,
then message your bot once and fetch your chat ID from
`https://api.telegram.org/bot<token>/getUpdates`.

## Run

```
python monitor_main.py
```

Runs until stopped (Ctrl+C), reconnecting automatically if a room drops. Intended to run
on the VPS long-term — see [DEPLOY_VPS.md](DEPLOY_VPS.md) for `tmux`/`cron`-style options
to keep it running unattended.

## Reviewing logged events

Every event (flagged or not) is in the SQLite file (`monitor.sqlite3` by default):

```
sqlite3 monitor.sqlite3 "SELECT room, event_type, nickname, text, flag_reason FROM events WHERE flagged=1 ORDER BY timestamp DESC LIMIT 20;"
```
