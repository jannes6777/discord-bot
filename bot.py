import discord
from discord import app_commands
import aiohttp
import asyncio

GUILD_ID = 1321257470697668669
GUILD = discord.Object(id=GUILD_ID)

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Debug: zeigt, welche Commands dein Code hat
        print("Lokale Commands:", [c.name for c in self.tree.get_commands()])

        # Sync nur für DEINEN Server (sofort)
        synced = await self.tree.sync(guild=GUILD)
        print("Synced Commands:", [c.name for c in synced])

client = MyClient()

@client.event
async def on_ready():
    print(f"{client.user} ist online!")

@client.tree.command(name="ping", description="Test command", guild=GUILD)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@client.tree.command(name="kick", description="Kickt einen Benutzer", guild=GUILD)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Kein Grund angegeben"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("Keine Berechtigung!", ephemeral=True)
        return
    await member.kick(reason=reason)
    await interaction.response.send_message(f"{member.mention} wurde gekickt. Grund: {reason}")

@client.tree.command(name="ban", description="Bannt einen Benutzer", guild=GUILD)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Kein Grund angegeben"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Keine Berechtigung!", ephemeral=True)
        return
    await member.ban(reason=reason)
    await interaction.response.send_message(f"{member.mention} wurde gebannt. Grund: {reason}")

@client.tree.command(name="clear", description="Löscht Nachrichten", guild=GUILD)
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Keine Berechtigung!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"{len(deleted)} Nachrichten gelöscht.", ephemeral=True)
import asyncio
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent

CHANNEL_ID = 1475124879215952057  # HIER DEINE DISCORD KANAL ID EINSETZEN

tiktok_users = [
    "justrin.379",
    "daniloholzkopf",
    "justinfnjn"
    "sos88194"
]

async def start_tiktok_listener(username):
    tt_client = TikTokLiveClient(unique_id=username)

    @tt_client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(
                f"🔴 {username} ist jetzt LIVE auf TikTok!\n"
                f"https://www.tiktok.com/@{username}/live"
            )

    await tt_client.start()

@client.event
async def on_ready():
    print(f"{client.user} ist online!")

    for user in tiktok_users:
        asyncio.create_task(start_tiktok_listener(user))

import asyncio

DISCORD_CHANNEL_ID = 1475124879215952057

tiktok_users = [
    "justrin.379",
    "daniloholzkopf",
    "justinfnjn"
]

live_status = {}

async def hourly_reminder(username):
    while live_status.get(username, False):
        await asyncio.sleep(3600)  # 1 Stunde
        if live_status.get(username, False):
            channel = client.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                await channel.send(
                    f"⏰ {username} ist immer noch LIVE!\n"
                    f"https://www.tiktok.com/@{username}/live"
                )

async def start_tiktok_listener(username):
    tt_client = TikTokLiveClient(unique_id=username)
    live_status[username] = False

    @tt_client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        if not live_status[username]:
            live_status[username] = True
            channel = client.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                await channel.send(
                    f"🔴 {username} ist jetzt LIVE auf TikTok!\n"
                    f"https://www.tiktok.com/@{username}/live"
                )
            asyncio.create_task(hourly_reminder(username))

    @tt_client.on(DisconnectEvent)
    async def on_disconnect(event: DisconnectEvent):
        if live_status[username]:
            live_status[username] = False
            channel = client.get_channel(DISCORD_CHANNEL_ID)
            if channel:
                await channel.send(
                    f"⚫ Der Stream von {username} ist beendet."
                )

    await tt_client.start()

@client.event
async def on_ready():
    print(f"{client.user} ist online!")

    for user in tiktok_users:
        asyncio.create_task(start_tiktok_listener(user))

import aiohttp
import asyncio
import discord

YOUTUBE_API_KEY = "AIzaSyCmeXg6r6GNVgKamT32cBVlHhawBLrfe5M"  # NICHT öffentlich posten
YOUTUBE_CHANNEL_ID = "UCFC2YQbaGzdKzwHfm9xUTeA"
yt_is_live = False
yt_last_video_id = None
yt_last_upload_id = None

DISCORD_ANNOUNCE_CHANNEL_ID = 1475124879215952057  # dein Discord-Kanal

CHECK_EVERY_SECONDS = 60  # alle 60 Sekunden checken

yt_is_live = False
yt_last_video_id = None


async def fetch_json(session: aiohttp.ClientSession, url: str, params: dict):
    async with session.get(url, params=params, timeout=20) as resp:
        return await resp.json()


async def check_youtube_live_loop():
    global yt_is_live, yt_last_video_id

    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_ANNOUNCE_CHANNEL_ID)
    if channel is None:
        print("❌ Discord-Kanal nicht gefunden (prüf DISCORD_ANNOUNCE_CHANNEL_ID).")
        return

    async with aiohttp.ClientSession() as session:
        while not client.is_closed():
            try:
                # 1) Check: gibt es gerade einen LIVE Stream auf dem Kanal?
                search_url = "https://www.googleapis.com/youtube/v3/search"
                search_params = {
                    "part": "snippet",
                    "channelId": YOUTUBE_CHANNEL_ID,
                    "eventType": "live",
                    "type": "video",
                    "maxResults": 1,
                    "key": YOUTUBE_API_KEY,
                }

                data = await fetch_json(session, search_url, search_params)
                items = data.get("items", [])

                if items:
                    video_id = items[0]["id"]["videoId"]
                    title = items[0]["snippet"].get("title", "LIVE")
                    live_url = f"https://www.youtube.com/watch?v={video_id}"

                    if not yt_is_live or yt_last_video_id != video_id:
                        yt_is_live = True
                        yt_last_video_id = video_id
                        await channel.send(
                            f"🔴 **YouTube LIVE** ist gestartet!\n"
                            f"**Titel:** {title}\n"
                            f"{live_url}"
                        )
                else:
                    # kein Live gefunden -> wenn vorher live war, dann Ende melden
                    if yt_is_live:
                        yt_is_live = False
                        await channel.send("⚫ **YouTube Stream ist beendet.**")
                        yt_last_video_id = None

            except Exception as e:
                print("YouTube Check Fehler:", e)

            await asyncio.sleep(CHECK_EVERY_SECONDS)


# Starte den Loop automatisch, wenn der Bot online ist:
@client.event
async def on_ready():
    print(f"{client.user} ist online!")
    asyncio.create_task(check_youtube_loop())
    # nur 1x starten (falls on_ready mehrfach feuert)
    if not hasattr(client, "yt_task_started"):
        client.yt_task_started = True
        asyncio.create_task(check_youtube_live_loop())

async def check_youtube_loop():
    global yt_is_live, yt_last_video_id, yt_last_upload_id

    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_ANNOUNCE_CHANNEL_ID)

    async with aiohttp.ClientSession() as session:
        while not client.is_closed():
            try:
                url = "https://www.googleapis.com/youtube/v3/search"

                # 🔴 LIVE CHECK
                live_params = {
                    "part": "snippet",
                    "channelId": YOUTUBE_CHANNEL_ID,
                    "eventType": "live",
                    "type": "video",
                    "maxResults": 1,
                    "key": YOUTUBE_API_KEY,
                }

                async with session.get(url, params=live_params) as resp:
                    live_data = await resp.json()

                live_items = live_data.get("items", [])

                if live_items:
                    video_id = live_items[0]["id"]["videoId"]
                    title = live_items[0]["snippet"]["title"]
                    link = f"https://www.youtube.com/watch?v={video_id}"

                    if not yt_is_live:
                        yt_is_live = True
                        yt_last_video_id = video_id
                        await channel.send(f"🔴 YouTube LIVE gestartet!\n**{title}**\n{link}")
                else:
                    if yt_is_live:
                        yt_is_live = False
                        await channel.send("⚫ YouTube Stream beendet.")

                # 📹 UPLOAD CHECK
                upload_params = {
                    "part": "snippet",
                    "channelId": YOUTUBE_CHANNEL_ID,
                    "order": "date",
                    "type": "video",
                    "maxResults": 1,
                    "key": YOUTUBE_API_KEY,
                }

                async with session.get(url, params=upload_params) as resp:
                    upload_data = await resp.json()

                upload_items = upload_data.get("items", [])

                if upload_items:
                    upload_id = upload_items[0]["id"]["videoId"]
                    title = upload_items[0]["snippet"]["title"]
                    link = f"https://www.youtube.com/watch?v={upload_id}"

                    if yt_last_upload_id != upload_id and not yt_is_live:
                        yt_last_upload_id = upload_id
                        await channel.send(f"📹 Neues YouTube Video!\n**{title}**\n{link}")

            except Exception as e:
                print("YouTube Fehler:", e)

            await asyncio.sleep(60)

@client.tree.command(name="ticket", description="Erstelle ein Support-Ticket")
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user

    # Kategorie suchen oder erstellen
    category = discord.utils.get(guild.categories, name="Tickets")
    if category is None:
        category = await guild.create_category("Tickets")

    # Rechte setzen
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        category=category,
        overwrites=overwrites
    )

    await channel.send(
        f"{user.mention} 🎫 Dein Ticket wurde erstellt!\n"
        f"Ein Teammitglied wird dir bald helfen."
    )

    await interaction.response.send_message(
        f"✅ Dein Ticket wurde erstellt: {channel.mention}",
        ephemeral=True
    )


@client.tree.command(name="close", description="Schließt dieses Ticket")
async def close(interaction: discord.Interaction):
    if interaction.channel.name.startswith("ticket-"):
        await interaction.response.send_message("🔒 Ticket wird geschlossen...")
        await interaction.channel.delete()
    else:
        await interaction.response.send_message(
            "❌ Das ist kein Ticket-Kanal.",
            ephemeral=True
        )

@client.event
async def on_ready():
    guild = discord.Object(id=1321257470697668669)
    await client.tree.sync(guild=guild)
    print("Commands synchronisiert.")

import os
client.run(os.getenv("DISCORD_TOKEN"))
