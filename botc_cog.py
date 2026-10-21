"""
Blood on the Clocktower as a Cog: every command starts with /botc.

The bot is the table and the cards, not the Storyteller. A human Storyteller
still runs the nights and decides what each player learns; the bot hands
out roles, carries secret messages, shows the grimoire, and runs the votes.

A round of play:
  /newgame botc (or /botc new) -> players Join -> Start (roles by DM)
  /botc night      -> the Storyteller gets tonight's wake order
  /botc ask, /botc tell
                   -> wake a player: ask them to pick players (dropdown by DM)
                      or tell them what they learn
  /botc kill       -> a player dies in the night (role stays secret)
  /botc day        -> a new day; players use /botc nominate
  /botc execute    -> the player "on the block" at the end of the day dies
  ...repeat until the Storyteller calls /botc endgame.
"""

import io
import json
import os
import random

import discord
from discord import app_commands
from discord.ext import commands

from botc import generate_roles
from botc_roles import FIRST_NIGHT_ORDER, OTHER_NIGHTS_ORDER
from common import HERE, get_user
from table_view import draw_table, role_category

SAVE_FILE = os.path.join(HERE, "botc_games.json")

# SETUP_COUNTS in botc_roles has setups for 5 to 15 players.
MIN_PLAYERS = 5
MAX_PLAYERS = 15


# ---------------------------------------------------------------------------
# Game state (one game per channel, saved to botc_games.json after every change)
# ---------------------------------------------------------------------------

class BotcGame:
    def __init__(self, channel_id: int, host_id: int, host_name: str):
        self.channel_id = channel_id
        self.host_id = host_id                      # the Storyteller
        self.host_name = host_name
        self.players: list[int] = []                # seat order, clockwise
        self.names: dict[int, str] = {}             # user id -> display name
        self.roles: dict[int, str] = {}             # user id -> real role
        self.drunk_shown_as: str | None = None      # the Townsfolk the Drunk thinks they are
        self.bluffs: list[str] = []                 # 3 good roles not in play, for the Demon
        self.alive: list[int] = []
        self.dead_vote_used: list[int] = []         # dead players who spent their last vote
        self.started = False
        self.night = 0
        self.day = 0
        self.phase = "setup"                        # "night" or "day" once started
        # Today's nominations. Each player may nominate once and be nominated once a day.
        self.nominators: list[int] = []
        self.nominated: list[int] = []
        self.vote_on: int | None = None             # who is being voted on right now
        self.hands: list[int] = []                  # who has their hand up in that vote
        self.block: int | None = None               # who is "on the block" to be executed
        self.block_votes = 0                        # votes the block needs to beat

    def seat(self, uid: int) -> int:
        return self.players.index(uid) + 1

    def label(self, uid: int) -> str:
        return f"{self.seat(uid)}. {self.names[uid]}"

    def can_vote(self, uid: int) -> bool:
        # The living always vote. The dead get one last vote for the rest of the game.
        return uid in self.alive or (uid in self.players and uid not in self.dead_vote_used)

    # JSON only has string keys, so int keys come back as "123" and need converting.
    def to_dict(self) -> dict:
        return dict(vars(self))

    @classmethod
    def from_dict(cls, data: dict) -> "BotcGame":
        game = cls.__new__(cls)
        game.__dict__.update(data)
        for field in ("names", "roles"):
            setattr(game, field, {int(k): v for k, v in getattr(game, field).items()})
        return game


games: dict[int, BotcGame] = {}                     # channel id -> BotcGame


def save_games() -> None:
    with open(SAVE_FILE, "w") as f:
        json.dump({cid: g.to_dict() for cid, g in games.items()}, f, indent=1)


def load_games() -> None:
    if not os.path.exists(SAVE_FILE):
        return
    with open(SAVE_FILE) as f:
        for cid, data in json.load(f).items():
            games[int(cid)] = BotcGame.from_dict(data)


# ---------------------------------------------------------------------------
# Setup and text
# ---------------------------------------------------------------------------

def assign_roles(game: BotcGame) -> None:
    """Reuse generate_roles from botc.py, then shuffle the roles into the seats."""
    setup = generate_roles(len(game.players))
    roles = setup["roles"]
    random.shuffle(roles)        # generate_roles returns good roles first, evil last
    game.roles = dict(zip(game.players, roles))
    game.drunk_shown_as = setup["drunk_shown_as"]
    game.bluffs = setup["bluffs"]
    game.alive = list(game.players)


def shown_role(game: BotcGame, uid: int) -> str:
    """The role a player *believes* they have. Only the Drunk is lied to."""
    role = game.roles[uid]
    return game.drunk_shown_as if role == "Drunk" else role


def lobby_text(game: BotcGame) -> str:
    names = "\n".join(game.label(u) for u in game.players)
    return (
        f"**Blood on the Clocktower** - Storyteller: <@{game.host_id}>\n"
        f"Players ({len(game.players)}/{MAX_PLAYERS}, need {MIN_PLAYERS}):\n"
        f"{names or '*nobody yet*'}"
    )


def player_text(game: BotcGame, uid: int) -> str:
    """The secret message for one player."""
    role = shown_role(game, uid)
    lines = [
        f"You are player **{game.seat(uid)}**.",
        f"Your character: **{role}** ({role_category(role)})",
    ]
    if game.roles[uid] == "Imp":
        lines.append("These good characters are not in play. You can bluff as them: "
                     + ", ".join(game.bluffs))
    lines.append("The Storyteller will wake you by DM at night when you have something to do.")
    return "\n".join(lines)


def grimoire_text(game: BotcGame) -> str:
    """The Storyteller's view: every real role, who is dead, who has spent their vote."""
    lines = ["**Grimoire**"]
    for u in game.players:
        role = game.roles[u]
        if role == "Drunk":
            role = f"Drunk (thinks {game.drunk_shown_as})"
        status = ""
        if u not in game.alive:
            status = " ~~dead~~" + (" (vote used)" if u in game.dead_vote_used else " (has vote)")
        lines.append(f"{game.label(u)}: {role}{status}")
    lines.append(f"\nDemon bluffs: {', '.join(game.bluffs)}")
    return "\n".join(lines)


def night_order_text(game: BotcGame) -> str:
    """Who to wake tonight, in order. Same idea as display_night in botc.py."""
    first = game.night == 1
    order = FIRST_NIGHT_ORDER if first else OTHER_NIGHTS_ORDER
    lines = [f"**Night {game.night} wake order**"]
    for step in order:
        # Minion and Demon info only happen with 7+ players.
        if step.startswith("~"):
            if len(game.players) >= 7:
                lines.append(step)
            continue
        # The Drunk wakes as the role they think they have.
        for u in game.players:
            if shown_role(game, u) == step:
                dead = " ~~dead~~" if u not in game.alive else ""
                drunk = " (really the Drunk)" if game.roles[u] == "Drunk" else ""
                lines.append(f"{step}: {game.label(u)}{drunk}{dead}")
    if len(lines) == 1:
        lines.append("Nobody wakes tonight.")
    return "\n".join(lines)


def table_file(game: BotcGame, show_roles: bool) -> discord.File:
    """Draw the table with table_view.py and wrap the PNG so Discord can send it."""
    players = [
        {"name": game.names[u], "role": game.roles.get(u, "?"), "alive": u in game.alive}
        for u in game.players
    ]
    image = draw_table(players, show_roles=show_roles)
    buffer = io.BytesIO()            # a "file" that lives in memory, so nothing is saved to disk
    image.save(buffer, "PNG")
    buffer.seek(0)                   # rewind, so Discord reads it from the start
    return discord.File(buffer, filename="table.png")


def votes_needed(game: BotcGame) -> int:
    # At least half the living players, rounded up: 7 alive -> 4, 6 alive -> 3.
    return (len(game.alive) + 1) // 2


def vote_text(game: BotcGame) -> str:
    hands = ", ".join(game.names[u] for u in game.hands) or "nobody yet"
    block = (f"On the block: **{game.label(game.block)}** with {game.block_votes} votes."
             if game.block else "Nobody is on the block yet.")
    return (
        f"**Vote on {game.label(game.vote_on)}**\n"
        f"Needs {max(votes_needed(game), game.block_votes + 1)} votes to go on the block. {block}\n"
        f"Hands up ({len(game.hands)}): {hands}"
    )


async def kill_player(channel, game: BotcGame, uid: int, how: str) -> None:
    """A player dies. Unlike Town of Javis, their role stays secret."""
    game.alive.remove(uid)
    save_games()
    await channel.send(f"**{game.label(uid)}** {how}. They keep one vote for the rest of the game.")


# ---------------------------------------------------------------------------
# Persistent buttons (see the comment above LobbyView in javis_cog.py).
# The custom_ids start with "botc:" so they never clash with Town of Javis.
# ---------------------------------------------------------------------------

class LobbyView(discord.ui.View):
    """Join / Leave / Start buttons under the lobby message."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, custom_id="botc:join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        user = interaction.user
        if not g or g.started:
            return await interaction.response.send_message("This lobby is closed.", ephemeral=True)
        if user.id == g.host_id:
            return await interaction.response.send_message("You're the Storyteller.", ephemeral=True)
        if user.id in g.players:
            return await interaction.response.send_message("You already joined.", ephemeral=True)
        if len(g.players) >= MAX_PLAYERS:
            return await interaction.response.send_message("The game is full.", ephemeral=True)
        g.players.append(user.id)
        g.names[user.id] = user.display_name
        save_games()
        await interaction.response.edit_message(content=lobby_text(g), view=self)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.grey, custom_id="botc:leave")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        if not g or g.started:
            return await interaction.response.send_message("This lobby is closed.", ephemeral=True)
        if interaction.user.id in g.players:
            g.players.remove(interaction.user.id)
            save_games()
        await interaction.response.edit_message(content=lobby_text(g), view=self)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.blurple, custom_id="botc:start")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        if not g or g.started:
            return await interaction.response.send_message("This lobby is closed.", ephemeral=True)
        if interaction.user.id != g.host_id:
            return await interaction.response.send_message("Only the Storyteller can start.", ephemeral=True)
        if len(g.players) < MIN_PLAYERS:
            return await interaction.response.send_message(
                f"Need at least {MIN_PLAYERS} players.", ephemeral=True)

        assign_roles(g)
        g.started = True
        save_games()
        await interaction.response.edit_message(content=lobby_text(g) + "\n\n*Game started!*", view=None)

        failed = []
        for uid in g.players:
            try:
                await (await get_user(interaction.client, uid)).send(player_text(g, uid))
            except discord.HTTPException:
                failed.append(g.names[uid])
        try:
            await interaction.user.send(grimoire_text(g), file=table_file(g, show_roles=True))
        except discord.HTTPException:
            failed.append(g.host_name + " (Storyteller)")

        note = f"\nCouldn't DM: {', '.join(failed)}. Use the button below." if failed else ""
        await interaction.followup.send(
            "Characters have been sent by DM. Storyteller, use /botc night to begin." + note,
            file=table_file(g, show_roles=False), view=RevealView())


class RevealView(discord.ui.View):
    """Backup way to see your character, as a reply only you can see."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Show my character", style=discord.ButtonStyle.grey, custom_id="botc:reveal")
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        uid = interaction.user.id
        if not g:
            msg = "There's no game here."
        elif uid == g.host_id:
            msg = grimoire_text(g)
        elif uid in g.roles:
            msg = player_text(g, uid)
        else:
            msg = "You're not in this game."
        await interaction.response.send_message(msg, ephemeral=True)


class VoteView(discord.ui.View):
    """Hands up for one nomination. Voting in Clocktower is public, so the
    message shows who has their hand up."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Raise / lower hand", style=discord.ButtonStyle.blurple, custom_id="botc:hand")
    async def hand(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        uid = interaction.user.id
        if not g or g.vote_on is None:
            return await interaction.response.send_message("There's no vote right now.", ephemeral=True)
        if not g.can_vote(uid):
            return await interaction.response.send_message(
                "You can't vote: you are dead and already used your last vote.", ephemeral=True)
        # Clicking again lowers your hand, like in a real game.
        if uid in g.hands:
            g.hands.remove(uid)
        else:
            g.hands.append(uid)
        save_games()
        await interaction.response.edit_message(content=vote_text(g), view=self)

    @discord.ui.button(label="Close vote (Storyteller)", style=discord.ButtonStyle.grey, custom_id="botc:close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        if not g or g.vote_on is None:
            return await interaction.response.send_message("There's no vote right now.", ephemeral=True)
        if interaction.user.id != g.host_id:
            return await interaction.response.send_message("Only the Storyteller can close it.", ephemeral=True)

        nominee, votes = g.vote_on, len(g.hands)
        # A dead player who voted has now spent their one last vote.
        for u in g.hands:
            if u not in g.alive:
                g.dead_vote_used.append(u)

        # The block rule: you need at least half the living players AND more
        # votes than whoever is on the block. A tie with the block means
        # nobody is on it, but the next nominee still has to beat that number.
        if votes < votes_needed(g) or votes < g.block_votes:
            result = "Not enough votes."
        elif votes == g.block_votes:
            g.block = None
            result = "That's a tie, so **nobody** is on the block now."
        else:
            g.block, g.block_votes = nominee, votes
            result = f"**{g.label(nominee)}** is now on the block."

        g.vote_on, g.hands = None, []
        save_games()
        await interaction.response.edit_message(
            content=f"Vote on **{g.label(nominee)}** closed with {votes} votes. {result}", view=None)


# ---------------------------------------------------------------------------
# Dropdown the Storyteller sends with /botc ask (not persistent)
# ---------------------------------------------------------------------------

class AskSelect(discord.ui.Select):
    """A player picks one or two players at night, e.g. the Fortune Teller.
    The answer goes straight to the Storyteller, who decides what happens."""

    def __init__(self, game: BotcGame, actor: int, picks: int):
        self.game, self.actor = game, actor
        options = [discord.SelectOption(label=game.label(u), value=str(u)) for u in game.players]
        super().__init__(placeholder="Choose", options=options, min_values=picks, max_values=picks)

    async def callback(self, interaction: discord.Interaction):
        g = self.game
        if games.get(g.channel_id) is not g:
            return await interaction.response.edit_message(content="This game is over.", view=None)
        chosen = " and ".join(g.label(int(v)) for v in self.values)
        await interaction.response.edit_message(content=f"Got it: you chose **{chosen}**.", view=None)
        try:
            await (await get_user(interaction.client, g.host_id)).send(
                f"{g.label(self.actor)} ({shown_role(g, self.actor)}) chose **{chosen}**.")
        except discord.HTTPException:
            pass


# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------

async def storyteller_game(interaction: discord.Interaction) -> BotcGame | None:
    """The running game in this channel, if the person asking is its Storyteller."""
    game = games.get(interaction.channel_id)
    if not game or not game.started:
        await interaction.response.send_message("No running game here.", ephemeral=True)
    elif interaction.user.id != game.host_id:
        await interaction.response.send_message("Only the Storyteller can do that.", ephemeral=True)
    else:
        return game
    return None


def player_at(game: BotcGame, seat: int) -> int | None:
    return game.players[seat - 1] if 1 <= seat <= len(game.players) else None


async def open_lobby(interaction: discord.Interaction):
    """Open a Clocktower lobby. Used by /botc new and by /newgame botc in bot.py."""
    if interaction.channel_id in games:
        return await interaction.response.send_message(
            "There's already a game here. The Storyteller can /endgame it.", ephemeral=True)
    game = BotcGame(interaction.channel_id, interaction.user.id, interaction.user.display_name)
    games[interaction.channel_id] = game
    save_games()
    await interaction.response.send_message(lobby_text(game), view=LobbyView())


async def stop_game(interaction: discord.Interaction, winner: str = "none"):
    """End the Clocktower game in this channel. Used by /botc endgame and /endgame."""
    game = games[interaction.channel_id]
    if interaction.user.id != game.host_id:
        return await interaction.response.send_message("Only the Storyteller can end it.", ephemeral=True)
    del games[game.channel_id]
    save_games()
    if not game.started:
        return await interaction.response.send_message("Lobby closed.")
    title = f"**{winner} wins!**" if winner != "none" else "**Game over.**"
    await interaction.response.send_message(
        f"{title}\n\n{grimoire_text(game)}", file=table_file(game, show_roles=True))


class BotcCog(commands.GroupCog, name="botc",
              group_description="Blood on the Clocktower commands"):
    """A GroupCog puts every command under one name, so /botc new, /botc day, ...
    That keeps them apart from the Town of Javis commands.

    Without group_description, discord.py sends this docstring to Discord as
    the group's description, and Discord rejects anything over 100 characters."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()

    async def cog_load(self):
        load_games()
        self.bot.add_view(LobbyView())
        self.bot.add_view(RevealView())
        self.bot.add_view(VoteView())

    # --- Setup ------------------------------------------------------------

    @app_commands.command(name="new", description="Open a lobby. You will be the Storyteller.")
    async def new(self, interaction: discord.Interaction):
        await open_lobby(interaction)

    @app_commands.command(name="test", description="Roll a test game with 5-15 fake players.")
    async def test(self, interaction: discord.Interaction):
        count = random.randint(MIN_PLAYERS, MAX_PLAYERS)
        game = BotcGame(interaction.channel_id, interaction.user.id, interaction.user.display_name)
        game.players = list(range(1, count + 1))
        game.names = {i: f"Test{i}" for i in game.players}
        assign_roles(game)
        game.night = 1
        await interaction.response.send_message(
            f"**Test game with {count} players**\n\n{grimoire_text(game)}\n\n{night_order_text(game)}",
            file=table_file(game, show_roles=True), ephemeral=True)

    # --- Storyteller tools ------------------------------------------------

    @app_commands.command(name="grimoire", description="Storyteller: see every character and the table.")
    async def grimoire(self, interaction: discord.Interaction):
        game = await storyteller_game(interaction)
        if game:
            await interaction.response.send_message(
                grimoire_text(game), file=table_file(game, show_roles=True), ephemeral=True)

    @app_commands.command(name="night", description="Storyteller: night falls; you get the wake order.")
    async def night(self, interaction: discord.Interaction):
        game = await storyteller_game(interaction)
        if not game:
            return
        game.night += 1
        game.phase = "night"
        save_games()
        await interaction.response.send_message(night_order_text(game), ephemeral=True)
        await interaction.channel.send(f"**Night {game.night} falls.** Everyone close your eyes.")

    @app_commands.command(name="tell", description="Storyteller: privately tell a player something.")
    @app_commands.describe(seat="The player's seat number", message="What they learn")
    async def tell(self, interaction: discord.Interaction, seat: int, message: str):
        game = await storyteller_game(interaction)
        if not game:
            return
        uid = player_at(game, seat)
        if uid is None:
            return await interaction.response.send_message("No player in that seat.", ephemeral=True)
        try:
            await (await get_user(self.bot, uid)).send(f"**The Storyteller tells you:** {message}")
            await interaction.response.send_message(f"Sent to {game.label(uid)}.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message(f"Couldn't DM {game.label(uid)}.", ephemeral=True)

    @app_commands.command(name="ask", description="Storyteller: wake a player to choose players.")
    @app_commands.describe(seat="The player's seat number", picks="How many players they choose",
                           question="What you ask, e.g. 'Choose a player to protect'")
    async def ask(self, interaction: discord.Interaction, seat: int,
                  question: str, picks: app_commands.Range[int, 1, 2] = 1):
        game = await storyteller_game(interaction)
        if not game:
            return
        uid = player_at(game, seat)
        if uid is None:
            return await interaction.response.send_message("No player in that seat.", ephemeral=True)
        view = discord.ui.View(timeout=None)
        view.add_item(AskSelect(game, uid, picks))
        try:
            await (await get_user(self.bot, uid)).send(f"**The Storyteller wakes you.** {question}", view=view)
            await interaction.response.send_message(
                f"Asked {game.label(uid)}. Their answer will come to you by DM.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message(f"Couldn't DM {game.label(uid)}.", ephemeral=True)

    @app_commands.command(name="kill", description="Storyteller: a player dies (their role stays secret).")
    @app_commands.describe(seat="The player's seat number")
    async def kill(self, interaction: discord.Interaction, seat: int):
        game = await storyteller_game(interaction)
        if not game:
            return
        uid = player_at(game, seat)
        if uid is None or uid not in game.alive:
            return await interaction.response.send_message("That seat isn't a living player.", ephemeral=True)
        await interaction.response.send_message("Done.", ephemeral=True)
        await kill_player(interaction.channel, game, uid, "has died")

    # --- The day and voting -----------------------------------------------

    @app_commands.command(name="day", description="Storyteller: start a new day; nominations open.")
    async def day(self, interaction: discord.Interaction):
        game = await storyteller_game(interaction)
        if not game:
            return
        game.day += 1
        game.phase = "day"
        game.nominators, game.nominated = [], []
        game.vote_on, game.hands = None, []
        game.block, game.block_votes = None, 0
        save_games()
        await interaction.response.send_message(
            f"**Day {game.day}.** Talk, then nominate with `/botc nominate`. "
            f"It takes {votes_needed(game)} votes to put someone on the block.",
            file=table_file(game, show_roles=False))

    @app_commands.command(name="nominate", description="Nominate a player for execution.")
    @app_commands.describe(seat="The seat of the player you nominate")
    async def nominate(self, interaction: discord.Interaction, seat: int):
        game = games.get(interaction.channel_id)
        uid = interaction.user.id
        nominee = player_at(game, seat) if game else None
        # Each check below is one rule of Clocktower nominations.
        if not game or game.phase != "day":
            problem = "You can only nominate during the day."
        elif uid not in game.alive:
            problem = "Only living players can nominate."
        elif uid in game.nominators:
            problem = "You already nominated today."
        elif nominee is None:
            problem = "No player in that seat."
        elif nominee in game.nominated:
            problem = "That player was already nominated today."
        elif game.vote_on is not None:
            problem = "Wait until the current vote is closed."
        else:
            problem = None
        if problem:
            return await interaction.response.send_message(problem, ephemeral=True)

        game.nominators.append(uid)
        game.nominated.append(nominee)
        game.vote_on, game.hands = nominee, []
        save_games()
        await interaction.response.send_message(
            f"**{game.label(uid)}** nominates **{game.label(nominee)}**!\n\n{vote_text(game)}",
            view=VoteView())

    @app_commands.command(name="execute", description="Storyteller: end the day and execute whoever is on the block.")
    async def execute(self, interaction: discord.Interaction):
        game = await storyteller_game(interaction)
        if not game:
            return
        if game.vote_on is not None:
            return await interaction.response.send_message("Close the current vote first.", ephemeral=True)
        target = game.block
        game.phase = "dusk"
        game.block, game.block_votes = None, 0
        save_games()
        if target is None:
            return await interaction.response.send_message("Nobody is on the block. **No execution today.**")
        await interaction.response.send_message("The day ends.")
        if target in game.alive:
            await kill_player(interaction.channel, game, target, "is executed")
        else:
            await interaction.channel.send(f"**{game.label(target)}** is executed, but they were already dead.")

    # --- Everyone ---------------------------------------------------------

    @app_commands.command(name="table", description="Show the table: who sits where and who is dead.")
    async def table(self, interaction: discord.Interaction):
        game = games.get(interaction.channel_id)
        if not game or not game.started:
            return await interaction.response.send_message("No running game here.", ephemeral=True)
        await interaction.response.send_message(file=table_file(game, show_roles=False))

    @app_commands.command(name="endgame", description="Storyteller: end the game and reveal everyone.")
    @app_commands.describe(winner="Which team won (the Storyteller decides)")
    @app_commands.choices(winner=[
        app_commands.Choice(name="Good", value="Good"),
        app_commands.Choice(name="Evil", value="Evil"),
        app_commands.Choice(name="Nobody (stop the game)", value="none"),
    ])
    async def endgame(self, interaction: discord.Interaction, winner: str = "none"):
        if interaction.channel_id not in games:
            return await interaction.response.send_message("No game here.", ephemeral=True)
        await stop_game(interaction, winner)


async def setup(bot: commands.Bot):
    """load_extension("botc_cog") calls this."""
    await bot.add_cog(BotcCog(bot))
