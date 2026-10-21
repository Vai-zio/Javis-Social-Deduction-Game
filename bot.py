"""
Discord bot for Town of Javis and Blood on the Clocktower.

How it fits together:
  1. bot.run(TOKEN) opens a websocket to Discord and keeps it open.
  2. When someone types a slash command, Discord sends an "interaction" down
     that websocket, and discord.py calls the matching function.
  3. Buttons and dropdowns work the same way: a click is an interaction that
     calls the item's callback.
  4. Each game is a Cog in its own file. This file only starts the bot and
     loads them:
       javis_cog.py  Town of Javis: /newgame, /night, /vote, ...
       botc_cog.py   Blood on the Clocktower: /botc new, /botc nominate, ...
"""

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from common import HERE

# Read DISCORD_TOKEN (and optional GUILD_ID) from discordbot.env, which sits
# one folder above this file. __file__ is this script's path, so this works
# no matter which folder you start the bot from.
ENV_FILE = os.path.join(HERE, "..", "discordbot.env")
load_dotenv(ENV_FILE)
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# Each name is a .py file with a setup() function at the bottom.
EXTENSIONS = ["javis_cog", "botc_cog"]


class JavisBot(commands.Bot):
    def __init__(self):
        # commands.Bot is discord.Client plus Cog support. It wants a prefix
        # for old-style text commands; we only use slash commands, so a
        # mention is enough. Slash commands and buttons need no privileged intents.
        super().__init__(command_prefix=commands.when_mentioned,
                         intents=discord.Intents.default())

    async def setup_hook(self):
        for name in EXTENSIONS:
            await self.load_extension(name)

        # Tell Discord which slash commands exist ("syncing").
        # With GUILD_ID set this is instant for that one server; globally it can take a while.
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user}")


bot = JavisBot()


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit(f"Set DISCORD_TOKEN in {os.path.normpath(ENV_FILE)}")
    bot.run(TOKEN)
