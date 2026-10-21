"""
Town of Javis as a Cog.

A Cog is a class that groups one game's slash commands. bot.py loads this
file with load_extension("javis_cog"), which calls setup() at the bottom.
Everything else (Game, the views, the helpers) is the same code that used
to live in bot.py.

A round of play with the bot:
  /newgame javis -> players Join -> Start (roles by DM, Mafia get a private thread)
  /night   -> every living night role gets a dropdown by DM; the narrator
              gets one summary once everyone has chosen
  /kill    -> the narrator announces who died in the night
  /vote    -> players nominate; a majority puts someone on trial,
              then Guilty / Innocent decides
  ...repeat until the bot announces a winner (or /endgame).
"""

import json
import os
import random
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from TownOfJavis2 import (
    OTHER_NIGHTS, FIRST_NIGHT_ORDER, TOWN_ROLES,
    generate_roles, team_of, check_winner,
)
from common import HERE, get_user

SAVE_FILE = os.path.join(HERE, "games.json")     # running games, survives restarts
LOG_FILE = os.path.join(HERE, "game_log.json")   # finished games, for /stats

# ROLE_SLOTS in TownOfJavis2 only has setups for 6 to 15 players.
MIN_PLAYERS = 6
MAX_PLAYERS = 15

# Every role listed in OTHER_NIGHTS acts at night, so it gets a dropdown.
NIGHT_ROLES = {role for roles in OTHER_NIGHTS.values() for role in roles}

# The narrator *wakes* roles in OTHER_NIGHTS order, but *resolves* them in this
# order, like Town of Salem does: blocks first, then protections, then kills,
# then information. That way a Doctor's heal is already in place when the
# Mafia's shot lands, and a Sheriff sees the result of everything else.
RESOLVE_ORDER = ["Control / Setup", "Buffs / Utility", "Killing", "Information"]


# ---------------------------------------------------------------------------
# Game state (one game per channel, saved to games.json after every change)
# ---------------------------------------------------------------------------

class Game:
    def __init__(self, channel_id: int, host_id: int, host_name: str):
        self.channel_id = channel_id
        self.host_id = host_id                      # the narrator
        self.host_name = host_name
        # We store user ids, not discord.Member objects, because ids can be
        # written to a JSON file and Member objects can't.
        self.players: list[int] = []                # seat order
        self.names: dict[int, str] = {}             # user id -> display name
        self.roles: dict[int, str] = {}             # user id -> role
        self.targets: dict[int, int] = {}           # Executioner / Guardian Angel -> target
        self.alive: list[int] = []
        self.started = False
        self.night = 0
        self.night_actions: dict[int, list[int]] = {}   # actor -> chosen ids ([] = skipped)
        self.nominations: dict[int, int] = {}       # voter -> who they want on trial
        self.on_trial: int | None = None
        self.trial_votes: dict[int, str] = {}       # voter -> "guilty" / "innocent"
        self.mafia_thread_id: int | None = None

    def seat(self, uid: int) -> int:
        return self.players.index(uid) + 1

    def label(self, uid: int) -> str:
        return f"{self.seat(uid)}. {self.names[uid]}"

    def night_actors(self) -> list[int]:
        return [u for u in self.alive if self.roles[u] in NIGHT_ROLES]

    # JSON only has string keys, so int keys come back as "123" and need converting.
    def to_dict(self) -> dict:
        return dict(vars(self))

    @classmethod
    def from_dict(cls, data: dict) -> "Game":
        game = cls.__new__(cls)
        game.__dict__.update(data)
        for field in ("names", "roles", "targets", "night_actions", "nominations", "trial_votes"):
            setattr(game, field, {int(k): v for k, v in getattr(game, field).items()})
        return game


games: dict[int, Game] = {}                         # channel id -> Game


def save_games() -> None:
    with open(SAVE_FILE, "w") as f:
        json.dump({cid: g.to_dict() for cid, g in games.items()}, f, indent=1)


def load_games() -> None:
    if not os.path.exists(SAVE_FILE):
        return
    with open(SAVE_FILE) as f:
        for cid, data in json.load(f).items():
            games[int(cid)] = Game.from_dict(data)


def log_game(game: Game, winner: str) -> None:
    """Add a finished game to game_log.json so /stats can count wins per side."""
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            log = json.load(f)
    log.append({
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "players": len(game.players),
        "winner": winner,
        "roles": [game.roles[u] for u in game.players],
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=1)



# ---------------------------------------------------------------------------
# Setup and text
# ---------------------------------------------------------------------------

def assign_roles(game: Game) -> None:
    """Reuse the existing game logic, hand roles out at random, then pick targets."""
    roles = generate_roles(len(game.players))
    random.shuffle(roles)
    game.roles = dict(zip(game.players, roles))
    game.alive = list(game.players)

    for uid, role in game.roles.items():
        others = [u for u in game.players if u != uid]
        if role == "Executioner":
            # Must get a Town player voted out; fall back to anyone if there's no Town.
            town = [u for u in others if game.roles[u] in TOWN_ROLES]
            game.targets[uid] = random.choice(town or others)
        elif role == "Guardian Angel":
            game.targets[uid] = random.choice(others)


def lobby_text(game: Game) -> str:
    names = "\n".join(game.label(u) for u in game.players)
    return (
        f"**Town of Javis** - narrator: <@{game.host_id}>\n"
        f"Players ({len(game.players)}/{MAX_PLAYERS}, need {MIN_PLAYERS}):\n"
        f"{names or '*nobody yet*'}"
    )


def player_text(game: Game, uid: int) -> str:
    """The secret message for one player: seat, role, team, teammates, target."""
    role = game.roles[uid]
    team = team_of(role)
    lines = [
        f"You are player **{game.seat(uid)}**.",
        f"Your role: **{role}**",
        f"Your team: **{team}**",
    ]
    # Only the Mafia know who their teammates are.
    if team == "Mafia":
        mates = [
            f"{game.label(u)} ({game.roles[u]})"
            for u in game.players
            if u != uid and team_of(game.roles[u]) == "Mafia"
        ]
        lines.append("Your Mafia teammates:\n" + ("\n".join(mates) or "none"))
    if role == "Executioner":
        lines.append(f"Your target: **{game.label(game.targets[uid])}**. Get them voted out to win.")
    elif role == "Guardian Angel":
        lines.append(f"Your target: **{game.label(game.targets[uid])}**. Keep them alive.")
    return "\n".join(lines)


def narrator_text(game: Game) -> str:
    """Same output as display_first_night / display_other_nights, but with names."""
    order = {role: i for i, role in enumerate(FIRST_NIGHT_ORDER)}
    by_role = sorted(game.players, key=lambda u: order.get(game.roles[u], len(order)))

    lines = ["**===== First Night =====**"]
    for u in by_role:
        role = game.roles[u]
        dead = "" if u in game.alive else " ~~dead~~"
        lines.append(f"{game.seat(u)} {role} ({game.names[u]}){dead}")
        if role == "Mafioso":
            lines.append("~ Mafia Identification ~")
        elif role == "Cupid":
            lines.append("~ Lovebirds Identification ~")

    if game.targets:
        lines.append("\n**Targets**")
        for u, t in game.targets.items():
            lines.append(f"{game.roles[u]} ({game.names[u]}) -> {game.label(t)}")

    lines.append("\n**===== Other Nights =====**")
    in_game = set(game.roles.values())
    for category, category_roles in OTHER_NIGHTS.items():
        active = [r for r in category_roles if r in in_game]
        if active:
            lines.append(f"__{category}__: " + ", ".join(active))
    return "\n".join(lines)


def night_summary(game: Game) -> str:
    """Every night choice so far, grouped in the order the narrator resolves them."""
    lines = [f"**Night {game.night} actions** (resolve top to bottom)"]
    for category in RESOLVE_ORDER:
        actors = [u for u in game.night_actors() if game.roles[u] in OTHER_NIGHTS[category]]
        if not actors:
            continue
        lines.append(f"\n__{category}__")
        for u in actors:
            if u not in game.night_actions:
                choice = "*waiting...*"
            elif not game.night_actions[u]:
                choice = "skipped"
            else:
                choice = " and ".join(game.label(t) for t in game.night_actions[u])
            lines.append(f"{game.roles[u]} ({game.label(u)}) -> {choice}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Deaths and the end of the game
# ---------------------------------------------------------------------------

async def kill_player(channel, game: Game, uid: int, by_vote: bool = False) -> None:
    """Remove a player, reveal their role, then check whether anyone has won."""
    game.alive.remove(uid)
    role = game.roles[uid]
    lines = [f"**{game.label(uid)}** has died. They were the **{role}**."]

    # Jester and Executioner win *by* a vote, and the game carries on without them.
    if by_vote:
        if role == "Jester":
            lines.append("The Jester wanted this. **The Jester wins!**")
        for ex, target in game.targets.items():
            if target == uid and game.roles[ex] == "Executioner":
                lines.append(f"{game.names[ex]} was the Executioner. **The Executioner wins!**")
    save_games()
    await channel.send("\n".join(lines))

    winner = check_winner([game.roles[u] for u in game.alive])
    if winner:
        await end_game(channel, game, winner)


async def end_game(channel, game: Game, winner: str | None) -> None:
    if winner:
        log_game(game, winner)
    del games[game.channel_id]
    save_games()

    reveal = "\n".join(f"{game.label(u)}: {game.roles[u]}" for u in game.players)
    title = f"**{winner} wins!**" if winner else "**Game over.**"
    await channel.send(f"{title} Roles were:\n{reveal}")

    # Remove the Mafia's private thread. Deleting needs "Manage Threads";
    # without it we lock and archive it instead.
    if game.mafia_thread_id:
        try:
            guild = channel.guild
            thread = guild.get_thread(game.mafia_thread_id) or await guild.fetch_channel(game.mafia_thread_id)
            try:
                await thread.delete()
            except discord.Forbidden:
                await thread.edit(archived=True, locked=True)
        except discord.HTTPException:
            pass


# ---------------------------------------------------------------------------
# Persistent buttons
#
# A "persistent" view keeps working after the bot restarts. Two rules make
# that possible: timeout=None, and a fixed custom_id on every button. Discord
# sends the custom_id back with each click, and setup_hook registers one copy
# of each view so discord.py knows which function that id belongs to. The view
# holds no game itself; it looks the game up from the channel that was clicked.
# ---------------------------------------------------------------------------

class LobbyView(discord.ui.View):
    """Join / Leave / Start buttons under the lobby message."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join", style=discord.ButtonStyle.green, custom_id="lobby:join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        user = interaction.user
        if not g or g.started:
            return await interaction.response.send_message("This lobby is closed.", ephemeral=True)
        if user.id == g.host_id:
            return await interaction.response.send_message("You're the narrator.", ephemeral=True)
        if user.id in g.players:
            return await interaction.response.send_message("You already joined.", ephemeral=True)
        if len(g.players) >= MAX_PLAYERS:
            return await interaction.response.send_message("The game is full.", ephemeral=True)
        g.players.append(user.id)
        g.names[user.id] = user.display_name
        save_games()
        await interaction.response.edit_message(content=lobby_text(g), view=self)

    @discord.ui.button(label="Leave", style=discord.ButtonStyle.grey, custom_id="lobby:leave")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        if not g or g.started:
            return await interaction.response.send_message("This lobby is closed.", ephemeral=True)
        if interaction.user.id in g.players:
            g.players.remove(interaction.user.id)
            save_games()
        await interaction.response.edit_message(content=lobby_text(g), view=self)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.blurple, custom_id="lobby:start")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        if not g or g.started:
            return await interaction.response.send_message("This lobby is closed.", ephemeral=True)
        if interaction.user.id != g.host_id:
            return await interaction.response.send_message("Only the narrator can start.", ephemeral=True)
        if len(g.players) < MIN_PLAYERS:
            return await interaction.response.send_message(
                f"Need at least {MIN_PLAYERS} players.", ephemeral=True)

        assign_roles(g)
        g.started = True
        save_games()

        # Remove the lobby buttons first. Discord wants an answer within 3
        # seconds, and sending all the DMs below can take longer than that.
        await interaction.response.edit_message(content=lobby_text(g) + "\n\n*Game started!*", view=None)

        # DM each player their role. DMs fail if a player blocks DMs from
        # server members, so we count failures and tell them to use the button.
        failed = []
        for uid in g.players:
            try:
                await (await get_user(interaction.client, uid)).send(player_text(g, uid))
            except discord.HTTPException:
                failed.append(g.names[uid])
        try:
            await interaction.user.send(narrator_text(g))
        except discord.HTTPException:
            failed.append(g.host_name + " (narrator)")

        note = await make_mafia_thread(interaction.channel, g)
        if failed:
            note += f"\nCouldn't DM: {', '.join(failed)}. Use the button below."
        await interaction.followup.send("Roles have been sent by DM." + note, view=RevealView())


async def make_mafia_thread(channel, game: Game) -> str:
    """A private thread only the Mafia and the narrator can see, for night talk."""
    mafia = [u for u in game.players if team_of(game.roles[u]) == "Mafia"]
    if not isinstance(channel, discord.TextChannel):
        return ""
    try:
        thread = await channel.create_thread(
            name="Mafia hideout", type=discord.ChannelType.private_thread, invitable=False)
        for uid in mafia + [game.host_id]:
            await thread.add_user(discord.Object(id=uid))
    except discord.HTTPException:
        return "\n(I couldn't make the Mafia thread. Give me the Create Private Threads permission.)"
    game.mafia_thread_id = thread.id
    save_games()
    await thread.send("Mafia, plan your kill here. Only you and the narrator can see this.")
    return ""


class RevealView(discord.ui.View):
    """Backup way to see your role: an 'ephemeral' reply only the clicker can see."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Show my role", style=discord.ButtonStyle.grey, custom_id="reveal:show")
    async def reveal(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        uid = interaction.user.id
        if not g:
            msg = "There's no game here."
        elif uid == g.host_id:
            msg = narrator_text(g)
        elif uid in g.roles:
            msg = player_text(g, uid)
        else:
            msg = "You're not in this game."
        await interaction.response.send_message(msg, ephemeral=True)


class TrialView(discord.ui.View):
    """Guilty / Innocent for the player on trial. Votes stay secret until Close."""

    def __init__(self):
        super().__init__(timeout=None)

    async def cast(self, interaction: discord.Interaction, verdict: str):
        g = games.get(interaction.channel_id)
        uid = interaction.user.id
        if not g or g.on_trial is None:
            return await interaction.response.send_message("There's no trial right now.", ephemeral=True)
        if uid not in g.alive or uid == g.on_trial:
            return await interaction.response.send_message("You can't vote in this trial.", ephemeral=True)
        g.trial_votes[uid] = verdict          # clicking again just changes your vote
        save_games()
        await interaction.response.send_message(
            f"You voted **{verdict}**. You can change it until the narrator closes the trial.",
            ephemeral=True)

    @discord.ui.button(label="Guilty", style=discord.ButtonStyle.red, custom_id="trial:guilty")
    async def guilty(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cast(interaction, "guilty")

    @discord.ui.button(label="Innocent", style=discord.ButtonStyle.green, custom_id="trial:innocent")
    async def innocent(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cast(interaction, "innocent")

    @discord.ui.button(label="Close trial (narrator)", style=discord.ButtonStyle.grey, custom_id="trial:close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = games.get(interaction.channel_id)
        if not g or g.on_trial is None:
            return await interaction.response.send_message("There's no trial right now.", ephemeral=True)
        if interaction.user.id != g.host_id:
            return await interaction.response.send_message("Only the narrator can close it.", ephemeral=True)

        accused = g.on_trial
        guilty = list(g.trial_votes.values()).count("guilty")
        innocent = list(g.trial_votes.values()).count("innocent")
        g.on_trial, g.trial_votes = None, {}
        save_games()

        # A tie is not a majority, so the accused survives it.
        result = "guilty" if guilty > innocent else "innocent"
        await interaction.response.edit_message(
            content=f"Trial of **{g.label(accused)}**: {guilty} guilty, {innocent} innocent. "
                    f"Found **{result}**.",
            view=None)
        if result == "guilty":
            await kill_player(interaction.channel, g, accused, by_vote=True)


# ---------------------------------------------------------------------------
# Dropdowns (not persistent: after a restart, run /night or /vote again)
# ---------------------------------------------------------------------------

def player_options(game: Game) -> list[discord.SelectOption]:
    return [discord.SelectOption(label=game.label(u), value=str(u)) for u in game.alive]


class NightSelect(discord.ui.Select):
    """Sent by DM to one night role. The pick is stored, not acted on: the
    narrator still decides what happens, using the summary."""

    def __init__(self, game: Game, actor: int):
        self.game, self.actor, self.night = game, actor, game.night
        options = player_options(game) + [discord.SelectOption(label="Skip (do nothing)", value="skip")]
        # The Witch controls one player and picks who they hit, so she picks two.
        picks = 2 if game.roles[actor] == "Witch" else 1
        super().__init__(placeholder="Choose your target", options=options,
                         min_values=1, max_values=picks)

    async def callback(self, interaction: discord.Interaction):
        g = self.game
        if games.get(g.channel_id) is not g or g.night != self.night or self.actor not in g.alive:
            return await interaction.response.edit_message(content="This night is over.", view=None)

        chosen = [] if "skip" in self.values else [int(v) for v in self.values]
        g.night_actions[self.actor] = chosen
        save_games()
        text = "skip tonight" if not chosen else " and ".join(g.label(t) for t in chosen)
        await interaction.response.edit_message(content=f"Got it: you chose **{text}**.", view=None)

        # Once the last actor has chosen, the narrator gets the full summary.
        if all(u in g.night_actions for u in g.night_actors()):
            try:
                await (await get_user(interaction.client, g.host_id)).send(night_summary(g))
            except discord.HTTPException:
                pass


class NominateSelect(discord.ui.Select):
    """Day vote: pick who you want on trial. A majority of the living starts it."""

    def __init__(self, game: Game):
        self.game = game
        super().__init__(placeholder="Who should go on trial?", options=player_options(game))

    async def callback(self, interaction: discord.Interaction):
        g = self.game
        uid = interaction.user.id
        if games.get(g.channel_id) is not g or g.on_trial is not None:
            return await interaction.response.send_message("This vote is closed.", ephemeral=True)
        if uid not in g.alive:
            return await interaction.response.send_message("Only living players can vote.", ephemeral=True)

        g.nominations[uid] = int(self.values[0])
        save_games()

        # Majority = more than half of the living, e.g. 7 alive -> 4 votes.
        needed = len(g.alive) // 2 + 1
        counts = {}
        for target in g.nominations.values():
            counts[target] = counts.get(target, 0) + 1
        tally = "\n".join(f"{g.label(t)}: {n}" for t, n in sorted(counts.items(), key=lambda x: -x[1]))
        top, votes = max(counts.items(), key=lambda x: x[1])

        if votes < needed:
            return await interaction.response.edit_message(
                content=f"**Day vote** ({needed} votes put someone on trial)\n{tally}")

        g.on_trial, g.trial_votes, g.nominations = top, {}, {}
        save_games()
        await interaction.response.edit_message(content=f"**Day vote**\n{tally}", view=None)
        await interaction.followup.send(
            f"**{g.label(top)}** is on trial! They may defend themselves, then everyone else votes.",
            view=TrialView())


# ---------------------------------------------------------------------------
# Slash commands
# ---------------------------------------------------------------------------

async def narrator_game(interaction: discord.Interaction) -> Game | None:
    """The running game in this channel, if the person asking is its narrator."""
    game = games.get(interaction.channel_id)
    if not game or not game.started:
        await interaction.response.send_message("No running game here.", ephemeral=True)
    elif interaction.user.id != game.host_id:
        await interaction.response.send_message("Only the narrator can do that.", ephemeral=True)
    else:
        return game
    return None



async def open_lobby(interaction: discord.Interaction):
    """Open a Town of Javis lobby. /newgame in bot.py calls this."""
    if interaction.channel_id in games:
        return await interaction.response.send_message(
            "There's already a game here. The narrator can /endgame it.", ephemeral=True)
    game = Game(interaction.channel_id, interaction.user.id, interaction.user.display_name)
    games[interaction.channel_id] = game
    save_games()
    await interaction.response.send_message(lobby_text(game), view=LobbyView())


class JavisCog(commands.Cog):
    """All Town of Javis commands. Inside a Cog, @app_commands.command
    replaces @bot.tree.command, and each command gets `self` first."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Runs once when the Cog is added: load saved games and register the
        # persistent views so old buttons still work after a restart.
        load_games()
        self.bot.add_view(LobbyView())
        self.bot.add_view(RevealView())
        self.bot.add_view(TrialView())

    @app_commands.command(name="gametest", description="Roll a test game with 6-15 fake players.")
    async def gametest(self, interaction: discord.Interaction):
        # Fake players are just ids 1..count with made-up names. It isn't saved.
        count = random.randint(MIN_PLAYERS, MAX_PLAYERS)
        game = Game(interaction.channel_id, interaction.user.id, interaction.user.display_name)
        game.players = list(range(1, count + 1))
        game.names = {i: f"Test{i}" for i in game.players}
        assign_roles(game)

        # ephemeral=True: only the person who ran the command sees this.
        await interaction.response.send_message(
            f"**Test game with {count} players**\n\n" + narrator_text(game), ephemeral=True)


    @app_commands.command(name="night", description="Start the next night: night roles get a dropdown by DM.")
    async def night(self, interaction: discord.Interaction):
        game = await narrator_game(interaction)
        if not game:
            return
        game.night += 1
        game.night_actions = {}
        save_games()

        # DMs take time, so "defer" tells Discord we'll answer in a moment.
        await interaction.response.defer(ephemeral=True)
        failed = []
        for uid in game.night_actors():
            view = discord.ui.View(timeout=None)
            view.add_item(NightSelect(game, uid))
            try:
                await (await get_user(self.bot, uid)).send(
                    f"**Night {game.night}.** You are the **{game.roles[uid]}**. Who do you visit?",
                    view=view)
            except discord.HTTPException:
                failed.append(game.label(uid))

        note = f"\nCouldn't DM {', '.join(failed)}; ask them in person." if failed else ""
        await interaction.followup.send(
            f"Night {game.night} has started. I'll DM you a summary once everyone has chosen. "
            f"Use /nightsummary to peek before then.{note}", ephemeral=True)
        await interaction.channel.send(f"**Night {game.night} falls.** Check your DMs.")


    @app_commands.command(name="nightsummary", description="Narrator: see tonight's choices so far.")
    async def nightsummary(self, interaction: discord.Interaction):
        game = await narrator_game(interaction)
        if game:
            await interaction.response.send_message(night_summary(game), ephemeral=True)


    @app_commands.command(name="kill", description="Narrator: a player dies (their role is revealed).")
    @app_commands.describe(seat="The player's seat number")
    async def kill(self, interaction: discord.Interaction, seat: int):
        game = await narrator_game(interaction)
        if not game:
            return
        if not 1 <= seat <= len(game.players) or game.players[seat - 1] not in game.alive:
            return await interaction.response.send_message("That seat isn't a living player.", ephemeral=True)
        await interaction.response.send_message("Done.", ephemeral=True)
        await kill_player(interaction.channel, game, game.players[seat - 1])


    @app_commands.command(name="vote", description="Narrator: open the day vote.")
    async def vote(self, interaction: discord.Interaction):
        game = await narrator_game(interaction)
        if not game:
            return
        game.nominations, game.on_trial = {}, None
        save_games()
        view = discord.ui.View(timeout=None)
        view.add_item(NominateSelect(game))
        needed = len(game.alive) // 2 + 1
        await interaction.response.send_message(
            f"**Day vote** ({needed} votes put someone on trial)", view=view)


    @app_commands.command(name="alive", description="List who is still alive.")
    async def alive(self, interaction: discord.Interaction):
        game = games.get(interaction.channel_id)
        if not game or not game.started:
            return await interaction.response.send_message("No running game here.", ephemeral=True)
        names = "\n".join(game.label(u) for u in game.alive)
        await interaction.response.send_message(f"**Alive ({len(game.alive)}):**\n{names}")


    @app_commands.command(name="stats", description="Win counts for each side from finished games.")
    async def stats(self, interaction: discord.Interaction):
        if not os.path.exists(LOG_FILE):
            return await interaction.response.send_message("No finished games yet.", ephemeral=True)
        with open(LOG_FILE) as f:
            log = json.load(f)
        wins = {}
        for entry in log:
            wins[entry["winner"]] = wins.get(entry["winner"], 0) + 1
        lines = [f"{side}: {n} ({n * 100 // len(log)}%)" for side, n in sorted(wins.items(), key=lambda x: -x[1])]
        await interaction.response.send_message(
            f"**{len(log)} finished games**\n" + "\n".join(lines))


    @app_commands.command(name="endgame", description="End the game in this channel.")
    async def endgame(self, interaction: discord.Interaction):
        game = games.get(interaction.channel_id)
        if not game:
            return await interaction.response.send_message("No game here.", ephemeral=True)
        if interaction.user.id != game.host_id:
            return await interaction.response.send_message("Only the narrator can end it.", ephemeral=True)
        await interaction.response.send_message("Ending the game.", ephemeral=True)
        if not game.started:
            del games[game.channel_id]
            save_games()
            return await interaction.channel.send("Lobby closed.")
        await end_game(interaction.channel, game, None)


async def setup(bot: commands.Bot):
    """load_extension("javis_cog") calls this."""
    await bot.add_cog(JavisCog(bot))
