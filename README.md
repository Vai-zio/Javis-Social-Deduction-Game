# Town of Javis + Blood on the Clocktower - Discord bot

A Discord interface for the game. The narrator opens a lobby, players click **Join**, and when the narrator clicks **Start** each player gets their role by DM. The narrator gets the night order.

## Run it

1. Install Python 3.10+ and the packages:
   ```
   pip install -r requirements.txt
   ```
2. Create a bot at https://discord.com/developers/applications (New Application, then the **Bot** tab, then **Reset Token** and copy it).
3. Put the token in `discordbot.env` in the folder **above** this one (`Claude projects`), written as `DISCORD_TOKEN=your-token`. See `.env.example` for the format. Never put the token in code or share that file.
4. Invite the bot: **OAuth2 > URL Generator**, tick `bot` and `applications.commands`, permissions `Send Messages`, `Create Private Threads`, `Send Messages in Threads` and `Manage Threads`, then open the link. The thread permissions are for the Mafia's private chat.
5. Start it:
   ```
   python bot.py
   ```

Tip: put your server ID in `GUILD_ID` (right-click the server with Developer Mode on, then Copy Server ID) so the commands appear right away.

## Commands

Narrator:
- `/newgame` opens a lobby (6 to 15 players); you become the narrator.
- `/night` starts a night. Every living night role gets a dropdown by DM, and you get one summary when all have chosen.
- `/nightsummary` shows tonight's choices so far.
- `/kill seat` kills a player and reveals their role.
- `/vote` opens the day vote. A majority puts someone on trial, then everyone votes Guilty or Innocent and you press **Close trial**.
- `/endgame` ends the game and reveals all roles.

Everyone:
- `/alive` lists living players.
- `/stats` shows how often each side has won.
- `/gametest` rolls a fake game so you can check the role setup alone.

## How it works

- **Connecting:** `bot.run(TOKEN)` logs in and keeps a live connection to Discord open.
- **Slash commands:** `setup_hook` tells Discord which commands exist ("sync"). When someone uses one, Discord sends the bot an *interaction* and discord.py calls the matching `@bot.tree.command` function.
- **Buttons and dropdowns:** a `discord.ui.View` holds them. A click is also an interaction and runs that item's function.
- **Secret roles:** roles go out by DM. If someone has DMs closed, the **Show my role** button replies with an *ephemeral* message that only they can see.
- **Night actions:** the bot only collects choices. The summary lists them in resolve order (blocks, protections, kills, information), like Town of Salem, so a Doctor's heal is in place before the kill lands. You still decide what happens.
- **Winning:** after every death, `check_winner` in `TownOfJavis2.py` looks at who is alive. Town wins when all killers are dead; Mafia wins when they are at least half the living. Jester and Executioner win by a vote and the game goes on.
- **Saving:** running games are written to `games.json` after every change, so a restart keeps them. Lobby, role and trial buttons keep working after a restart; dropdowns don't, so rerun `/night` or `/vote`.
- **Balance:** every finished game is added to `game_log.json`. After a few dozen games, `/stats` shows if one side wins too often, and you can adjust `ROLE_SLOTS`.

## Blood on the Clocktower commands

All under `/botc`. The bot is the table and the cards; the Storyteller still runs the night.

Storyteller:
- `/botc new` opens a lobby (5 to 15 players). **Start** DMs each player their character (the Drunk is told a fake Townsfolk, the Imp gets 3 bluffs) and DMs you the grimoire with the table picture.
- `/botc night` announces night and shows you tonight's wake order.
- `/botc ask seat question picks` DMs a player a dropdown (for the Fortune Teller, Monk, Imp, ...). Their answer comes back to you by DM.
- `/botc tell seat message` DMs a player what they learn.
- `/botc kill seat` a player dies. Their character stays secret.
- `/botc day` starts the day and opens nominations.
- `/botc execute` ends the day and executes whoever is on the block.
- `/botc grimoire` shows you every character again.
- `/botc endgame winner` reveals everyone.

Everyone:
- `/botc nominate seat` nominates a player. Then everyone clicks **Raise / lower hand**, and the Storyteller clicks **Close vote**.
- `/botc table` shows who sits where and who is dead.
- `/botc test` rolls a fake game so you can check the setup alone.

Voting rules the bot checks: only the living nominate; each player nominates once and is nominated once per day; dead players keep one last vote; to go on the block you need at least half the living players *and* more votes than whoever is on it (a tie means nobody).

## How the files fit together

- `bot.py`: starts the bot and loads the two Cogs. A Cog is a class holding one game's commands; `load_extension("javis_cog")` imports the file and calls its `setup()`.
- `javis_cog.py`: Town of Javis commands, buttons and saving (`games.json`).
- `botc_cog.py`: Blood on the Clocktower commands, buttons and saving (`botc_games.json`).
- `common.py`: small helpers both games use.

## Blood on the Clocktower files

- `botc_roles.py`: the normal Trouble Brewing roles (pools, setup counts, night order). Data only.
- `experimental_roles.py`: homebrew roles (Truth Speaker, Team Watcher, Pair Seer, Doubter, Forger). Run it for a demo.
- `botc.py`: the game logic (generate roles, show the grimoire). Run it to roll a setup.

Both `botc.py` and `experimental_roles.py` import the normal roles from `botc_roles.py`.
