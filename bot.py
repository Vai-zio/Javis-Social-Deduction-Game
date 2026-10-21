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
       javis_cog.py  Town of Javis: /night, /vote, ...
       botc_cog.py   Blood on the Clocktower: /botc nominate, ...
     /newgame and /endgame live here because they work for either game.
"""

import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import botc_cog
import javis_cog
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


# @app_commands.choices turns the option into a fixed list. Discord shows each
# choice's *name*, and filters the list as you type, so typing "2" or "botc"
# both find the Clocktower entry. The function receives the choice's *value*.
@bot.tree.command(name="newgame", description="Open a lobby for a game. You run it.")
@app_commands.describe(game="Which game to play")
@app_commands.choices(game=[
    app_commands.Choice(name="1 - Town of Javis (javis)", value="javis"),
    app_commands.Choice(name="2 - Blood on the Clocktower (botc)", value="botc"),
])
async def newgame(interaction: discord.Interaction, game: str):
    # One game per channel, whichever game it is.
    if interaction.channel_id in botc_cog.games or interaction.channel_id in javis_cog.games:
        return await interaction.response.send_message(
            "There's already a game here. Its host can /endgame it.", ephemeral=True)
    # Routing: each game keeps its own open_lobby; this only picks which one.
    if game == "botc":
        await botc_cog.open_lobby(interaction)
    else:
        await javis_cog.open_lobby(interaction)


# Each game keeps its own dict of running games (channel id -> game), so
# /endgame checks which dict has this channel and asks that game to stop.
@bot.tree.command(name="endgame", description="End the game in this channel.")
@app_commands.describe(winner="Clocktower only: which team won (Town of Javis finds its own winner)")
@app_commands.choices(winner=[
    app_commands.Choice(name="Good", value="Good"),
    app_commands.Choice(name="Evil", value="Evil"),
    app_commands.Choice(name="Nobody (stop the game)", value="none"),
])
async def endgame(interaction: discord.Interaction, winner: str = "none"):
    if interaction.channel_id in botc_cog.games:
        await botc_cog.stop_game(interaction, winner)
    elif interaction.channel_id in javis_cog.games:
        await javis_cog.stop_game(interaction)
    else:
        await interaction.response.send_message("No game here.", ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit(f"Set DISCORD_TOKEN in {os.path.normpath(ENV_FILE)}")
    bot.run(TOKEN)
