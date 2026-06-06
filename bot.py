import asyncio
import discord
import os
import json

# ---- CONFIG ----
if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": ""}
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f)

token = configData["Token"]

# ---- CONSTANTS ----
YOUR_USER_ID = 123456789012345678  # REPLACE WITH YOUR DISCORD USER ID
ACTIVITY_CHANNEL_ID = 123456789012345678  # REPLACE WITH THE CHANNEL ID WHERE YOU WANT EMBEDS POSTED

# ---- BOT SETUP ----
intents = discord.Intents.all()
bot = discord.Client(intents=intents) # WE DON'T NEED COMMANDS, SO NO BOT, JUST THE CLIENT

# ---- CHANNEL HELPER ----
async def get_channel():
    for guild in bot.guilds:
        channel = guild.get_channel(ACTIVITY_CHANNEL_ID)
        if channel:
            return channel
    try:
        return await bot.fetch_channel(ACTIVITY_CHANNEL_ID)
    except discord.NotFound:
        print("ERROR: Channel not found — check ACTIVITY_CHANNEL_ID.")
        return None
    except discord.Forbidden:
        print("ERROR: Bot does not have access to that channel.")
        return None
    except discord.HTTPException as e:
        print(f"ERROR: Failed to fetch channel — {e}")
        return None


# ---- MEMBER HELPER ----
def get_member():
    for guild in bot.guilds:
        member = guild.get_member(YOUR_USER_ID)
        if member:
            return member
    return None


# ---- TWITCH HELPER ----
def is_streaming(activities):
    return any(isinstance(a, discord.Streaming) for a in activities)


# ---- STARTUP ----
@bot.event
async def on_ready():
    print(f"Bot is ready.")
    for guild in bot.guilds:
        print(f"Connected to: {guild.name} — {guild.id}")

    channel = await get_channel()
    if channel is None:
        print("ERROR: Could not find activity channel on startup.")
        return

    try:
        embed = discord.Embed(
            title="🟢 Bot Online",
            description="Activity tracking is active and listening for presence updates.",
            color=0x00ff00
        )
        embed.set_footer(text=f"Watching user ID: {YOUR_USER_ID}")
        await channel.send(embed=embed)
        print("Startup embed posted successfully.")
    except discord.HTTPException as e:
        print(f"ERROR: Failed to post startup embed — {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error on startup — {e}")


# ---- PRESENCE TRACKING ----
@bot.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    if after.id != YOUR_USER_ID:
        return

    before_spotify = next((a for a in before.activities if isinstance(a, discord.Spotify)), None)
    after_spotify = next((a for a in after.activities if isinstance(a, discord.Spotify)), None)

    # ---- DEBUG ----
    print(f"Presence update received.")
    print(f"All activities: {[(type(a).__name__, a.name if hasattr(a, 'name') else '') for a in after.activities]}")

    # ---- SPOTIFY (only active during Twitch stream) ----
    member = get_member()
    live_streaming = is_streaming(member.activities if member else [])
    print(f"is_streaming (live check): {live_streaming}")

    if not live_streaming:
        return

    if not after_spotify:
        return
    if before_spotify and before_spotify.track_id == after_spotify.track_id:
        return

    channel = await get_channel()
    if channel is None:
        print("ERROR: Could not find activity channel.")
        return

    try:
        embed = discord.Embed(
            title="**NOW PLAYING:**",
            description=f"Listening to {after_spotify.title}",
            color=0xa22b20
        )
        embed.set_thumbnail(url=after_spotify.album_cover_url)
        embed.add_field(name="Artist", value=after_spotify.artist)
        embed.add_field(
            name="Track Link",
            value=f"[{after_spotify.title}](https://open.spotify.com/track/{after_spotify.track_id})"
        )
        embed.set_footer(text=f"Song started at {after_spotify.created_at.strftime('%H:%M')}")
        await channel.send(embed=embed)
        print(f"Spotify embed posted: {after_spotify.title} by {after_spotify.artist}")

    except discord.HTTPException as e:
        print(f"ERROR: Failed to post Spotify embed — {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error in Spotify tracking — {e}")


bot.run(token)
