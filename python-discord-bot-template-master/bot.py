import logging
import os
import sys

import discord
from discord.ext import commands
import dotenv

# Load variables from .env file
dotenv.load_dotenv()


# Configure logging
LOG_LVL = os.getenv('LOG_LVL')
log = logging.getLogger(__name__)
if not LOG_LVL:
    LOG_LVL = 'DEBUG'

log = logging.getLogger(__name__)
h = logging.StreamHandler(sys.stdout)
h.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(h)
log.setLevel(LOG_LVL)


# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    log.error('`DISCORD_TOKEN` must be set in .env file')
    sys.exit()


# Create bot
intents = discord.Intents.none()
intents.messages = True
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)
#bot.remove_command('help')


@bot.event
async def on_ready():
    log.info('Bot logged in as `%s` (id %s)', bot.user, bot.user.id)
    log.info('Member of the following servers/guilds:')
    for guild in bot.guilds:
        log.info('  %s', guild.name)


@bot.command(name='hello', aliases=['yo'], help='hello world test command')
async def helloworld(ctx):
    await ctx.send(f"Hello {ctx.author.name}!")




#@bot.command(name='help')
#async def help(ctx):
#
#    about_text = ('A Python Discord template-bot, '
#                 'demonstrating how to write a bot.')
#
#    embed = discord.Embed(colour = discord.Colour.blue())
#    embed.set_author(name='Help')
#    embed.add_field(name='About', value=about_text, inline=False)
#                          
#    embed.add_field(name='`!hello` | `!yo`',
#                    value=('hello world test command.',
#                    inline=False)
#
#    await ctx.send(embed=embed)

# Start bot
try:
    bot.run(TOKEN)
except discord.errors.LoginFailure:
    log.error('Bot login failed, improper/invalid token')
    sys.exit()
