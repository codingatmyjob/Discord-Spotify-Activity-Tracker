# Discord Spotify Activity Tracker

A Discord bot that watches a specific user's presence and posts their Spotify activity to a channel whenever they are live on Twitch.

## Setup

**1. Create a bot in the Discord Developer Portal**
- Go to [discord.com/developers/applications](https://discord.com/developers/applications)
- New Application → Bot → Reset Token → copy your token
- Enable all three Privileged Gateway Intents (Presence, Server Members, Message Content)

**2. Configure `config.json`**
```json
{
    "Token": "YOUR_BOT_TOKEN_HERE"
}
```

**3. Set your constants in `bot.py`**
```python
YOUR_USER_ID = 000000000000000000       # your Discord user ID
ACTIVITY_CHANNEL_ID = 000000000000000000 # channel to post updates in
```
Right click your profile in Discord to copy your user ID. Right click the target channel to copy its ID. Developer Mode must be enabled under Settings → Advanced.

**4. Invite the bot to your server**
- OAuth2 → URL Generator → Scopes: `bot` → Permissions: `Administrator`
- Open the generated URL and authorize it to your server

**5. Run**
- Either host the bot on a cheap online hosting service, or run it from your coding environment with
```bash
python bot.py
```

## Behavior
- On startup, posts an online embed to the activity channel
- While streaming on Twitch, posts a new embed each time the Spotify track changes
- When not streaming, or Discord streaming activity is suppressed, all Spotify events are ignored
