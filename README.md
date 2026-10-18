# Town of Javis - Discord bot

A Discord interface for the game. The narrator opens a lobby, players click **Join**, and when the narrator clicks **Start** each player gets their role by DM. The narrator gets the night order.

## Run it

1. Install Python 3.10+ and the packages:
   ```
   pip install -r requirements.txt
   ```
2. Create a bot at https://discord.com/developers/applications (New Application, then the **Bot** tab, then **Reset Token** and copy it).
3. Copy `.env.example` to `.env` and paste the token after `DISCORD_TOKEN=`. Never put the token in code or share `.env`.
4. Invite the bot: **OAuth2 > URL Generator**, tick `bot` and `applications.commands`, permission `Send Messages`, open the link.
5. Start it:
   ```
   python bot.py
   ```

Tip: put your server ID in `GUILD_ID` (right-click the server with Developer Mode on, then Copy Server ID) so the commands appear right away.

## Commands

- `/newgame` opens a lobby in the channel; you become the narrator.
- `/endgame` ends the game and reveals all roles.

## How it works

- **Connecting:** `bot.run(TOKEN)` logs in and keeps a live connection to Discord open.
- **Slash commands:** `setup_hook` tells Discord which commands exist ("sync"). When someone uses one, Discord sends the bot an *interaction* and discord.py calls the matching `@bot.tree.command` function.
- **Buttons:** a `discord.ui.View` holds buttons. A click is also an interaction and runs that button's function.
- **Secret roles:** `member.send(...)` sends a DM. If someone has DMs closed, the **Show my role** button replies with an *ephemeral* message that only they can see.
- **Game logic:** `TownOfJavis2.py` is unchanged in behaviour; the bot just imports `generate_roles`. Game state is kept in memory, so restarting the bot ends running games.
