"""
Discord interface for Town of Javis.

How it fits together:
  1. bot.run(TOKEN) opens a websocket to Discord and keeps it open.
  2. When someone types /newgame, Discord sends an "interaction" down that
     websocket, and discord.py calls the matching function below.
  3. Buttons work the same way: a click is an interaction that calls the
     button's callback.
  4. The game logic (roles, night order) lives in TownOfJavis2.py; we only
     import it here.
"""

import os
import random
from types import SimpleNamespace

import discord
from discord import app_commands
from dotenv import load_dotenv

from TownOfJavis2 import OTHER_NIGHTS, FIRST_NIGHT_ORDER, generate_roles

# Read DISCORD_TOKEN (and optional GUILD_ID) from discordbot.env, which sits
# one folder above this file. __file__ is this script's path, so this works
# no matter which folder you start the bot from.
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "discordbot.env")
load_dotenv(ENV_FILE)
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

MIN_PLAYERS = 6
MAX_PLAYERS = 15


# ---------------------------------------------------------------------------
# Game state (kept in memory; one game per channel)
# ---------------------------------------------------------------------------

class Game:
    def __init__(self, host: discord.Member):
        self.host = host                                # the narrator
        self.players: list[discord.Member] = []
        self.roles: dict[int, str] = {}                 # user id -> role
        self.started = False


games: dict[int, Game] = {}                             # channel id -> Game


def lobby_text(game: Game) -> str:
    names = "\n".join(f"{i}. {p.display_name}" for i, p in enumerate(game.players, 1))
    return (
        f"**Town of Javis** - narrator: {game.host.mention}\n"
        f"Players ({len(game.players)}/{MAX_PLAYERS}):\n{names or '*nobody yet*'}"
    )


def narrator_text(game: Game) -> str:
    """Same output as display_first_night / display_other_nights, but as a string with names."""
    seat = {p.id: i for i, p in enumerate(game.players, 1)}
    order = {role: i for i, role in enumerate(FIRST_NIGHT_ORDER)}
    by_role = sorted(game.players, key=lambda p: order.get(game.roles[p.id], len(order)))

    lines = ["**===== First Night =====**"]
    for p in by_role:
        role = game.roles[p.id]
        lines.append(f"{seat[p.id]} {role} ({p.display_name})")
        if role == "Mafioso":
            lines.append("~ Mafia Identification ~")
        elif role == "Cupid":
            lines.append("~ Lovebirds Identification ~")

    lines.append("\n**===== Other Nights =====**")
    in_game = set(game.roles.values())
    for category, category_roles in OTHER_NIGHTS.items():
        active = [r for r in category_roles if r in in_game]
        if active:
            lines.append(f"__{category}__: " + ", ".join(active))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Buttons
# ---------------------------------------------------------------------------

class LobbyView(discord.ui.View):
    """Join / Leave / Start buttons under the lobby message."""

    def __init__(self, game: Game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = self.game
        if interaction.user == g.host:
            return await interaction.response.send_message("You're the narrator.", ephemeral=True)
        if interaction.user in g.players:
            return await interaction.response.send_message("You already joined.", ephemeral=True)
        if len(g.players) >= MAX_PLAYERS:
            return await interaction.response.send_message("The game is full.", ephemeral=True)
        g.players.append(interaction.user)
        await interaction.response.edit_message(content=lobby_text(g), view=self)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.grey)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.game.players:
            self.game.players.remove(interaction.user)
        await interaction.response.edit_message(content=lobby_text(self.game), view=self)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.blurple)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = self.game
        if interaction.user != g.host:
            return await interaction.response.send_message("Only the narrator can start.", ephemeral=True)
        if len(g.players) < MIN_PLAYERS:
            return await interaction.response.send_message(
                f"Need at least {MIN_PLAYERS} players.", ephemeral=True)

        # Reuse the existing game logic, then hand roles out at random.
        roles = generate_roles(len(g.players))
        random.shuffle(roles)
        g.roles = {p.id: role for p, role in zip(g.players, roles)}
        g.started = True

        # Remove the lobby buttons and post the "reveal" button instead.
        await interaction.response.edit_message(content=lobby_text(g) + "\n\n*Game started!*", view=None)

        # DM each player their role. DMs fail if a player blocks DMs from
        # server members, so we count failures and tell them to use the button.
        failed = []
        for seat, p in enumerate(g.players, 1):
            try:
                await p.send(f"You are player **{seat}**. Your role is **{g.roles[p.id]}**.")
            except discord.Forbidden:
                failed.append(p.display_name)

        # The narrator gets the full night order.
        try:
            await g.host.send(narrator_text(g))
        except discord.Forbidden:
            failed.append(g.host.display_name + " (narrator)")

        note = f"\nCouldn't DM: {', '.join(failed)}. Use the button below." if failed else ""
        await interaction.followup.send(
            "Roles have been sent by DM." + note, view=RevealView(g))


class RevealView(discord.ui.View):
    """Backup way to see your role: an 'ephemeral' reply only the clicker can see."""

    def __init__(self, game: Game):
        super().__init__(timeout=None)
        self.game = game

    @discord.ui.button(label="Show my role", style=discord.ButtonStyle.grey)
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = self.game
        if interaction.user == g.host:
            msg = narrator_text(g)
        elif interaction.user.id in g.roles:
            msg = f"Your role is **{g.roles[interaction.user.id]}**."
        else:
            msg = "You're not in this game."
        await interaction.response.send_message(msg, ephemeral=True)


# ---------------------------------------------------------------------------
# Bot and slash commands
# ---------------------------------------------------------------------------

class JavisBot(discord.Client):
    def __init__(self):
        # Slash commands and buttons need no privileged intents.
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
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


@bot.tree.command(name="newgame", description="Open a lobby. You will be the narrator.")
async def newgame(interaction: discord.Interaction):
    game = games.get(interaction.channel_id)
    if game and not game.started:
        return await interaction.response.send_message("A lobby is already open here.", ephemeral=True)
    game = Game(interaction.user)
    games[interaction.channel_id] = game
    await interaction.response.send_message(lobby_text(game), view=LobbyView(game))


@bot.tree.command(name="gametest", description="Roll a test game with 6-15 fake players.")
async def gametest(interaction: discord.Interaction):
    # Fake players only need the two things narrator_text reads: an id and a name.
    count = random.randint(6, 15)
    game = Game(interaction.user)
    game.players = [SimpleNamespace(id=i, display_name=f"Test{i}") for i in range(1, count + 1)]

    # Same steps as the Start button, minus the DMs.
    roles = generate_roles(count)
    random.shuffle(roles)
    game.roles = {p.id: role for p, role in zip(game.players, roles)}

    # ephemeral=True: only the person who ran the command sees this.
    await interaction.response.send_message(
        f"**Test game with {count} players**\n\n" + narrator_text(game), ephemeral=True)


@bot.tree.command(name="endgame", description="End the game in this channel.")
async def endgame(interaction: discord.Interaction):
    game = games.get(interaction.channel_id)
    if not game:
        return await interaction.response.send_message("No game here.", ephemeral=True)
    if interaction.user != game.host:
        return await interaction.response.send_message("Only the narrator can end it.", ephemeral=True)
    del games[interaction.channel_id]
    reveal = "\n".join(f"{p.display_name}: {game.roles.get(p.id, '-')}" for p in game.players)
    await interaction.response.send_message("**Game over.** Roles were:\n" + reveal)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit(f"Set DISCORD_TOKEN in {os.path.normpath(ENV_FILE)}")
    bot.run(TOKEN)
