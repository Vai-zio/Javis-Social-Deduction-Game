# The files and how to run the bot

## Running the bot

1. `pip install -r requirements.txt`
2. Put your bot token in `discordbot.env` in the folder **above** the project folder, as `DISCORD_TOKEN=your-token`. It sits outside the project so it never ends up on GitHub.
3. `python bot.py`

The main [README](../README.md) shows how to create the bot on Discord and invite it to a server.

## What each file does

The code is split in two layers. The **game files** know the rules and know nothing about Discord. The **bot files** talk to Discord and ask the game files for answers. That split is why the game can be tested without Discord (see [testing.md](testing.md)).

Game files (pure Python):

| File | What it holds |
|---|---|
| `TownOfJavis2.py` | Town of Javis: role pools, `ROLE_SLOTS`, night order, `generate_roles`, `check_winner`. Run it alone to play in the terminal. |
| `botc_roles.py` | Blood on the Clocktower data only: role pools, `SETUP_COUNTS`, night orders. |
| `botc.py` | Blood on the Clocktower logic: `generate_roles` (Baron, Drunk, bluffs). Run it to roll a setup. |
| `characters.py` | The `Character` base class for homebrew roles. |
| `experimental_roles.py` | Homebrew roles built on `Character`. Run it for a demo. |
| `table_view.py` | Draws the table as a picture with Pillow, and finds a player's living neighbours. |

Bot files (need Discord):

| File | What it holds |
|---|---|
| `bot.py` | Logs in and loads the two Cogs. Start the bot with this. |
| `javis_cog.py` | Town of Javis commands and buttons. Saves running games to `games.json`. |
| `botc_cog.py` | `/botc` commands and buttons. Saves to `botc_games.json`. |
| `common.py` | Small helpers both Cogs use. |

A **Cog** is a class that groups one game's commands. `bot.py` loads each one with `load_extension("javis_cog")`, which imports the file and calls its `setup()` function. That keeps each game in its own file.

Test files:

| File | What it holds |
|---|---|
| `tests/test_game.py` | Tests for the game files. |
| `pytest.ini` | Tells pytest where the tests are and lets them import the game files. |

## Files the bot makes

`games.json`, `botc_games.json` (running games, so a restart keeps them) and `game_log.json` (finished games, for `/stats`). They're in `.gitignore`, so they stay on your PC.

## Where to change things

- Add or rebalance a Town of Javis role: the pools and `ROLE_SLOTS` in `TownOfJavis2.py`, then add it to the night order.
- Change a Clocktower setup: `botc_roles.py`.
- Change what a command says or does: the matching Cog.
