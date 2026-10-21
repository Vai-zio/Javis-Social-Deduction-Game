"""Small helpers that both games use."""

import os

import discord

# The folder this file is in. Save files go here.
HERE = os.path.dirname(os.path.abspath(__file__))


async def get_user(client: discord.Client, uid: int) -> discord.User:
    # get_user reads the bot's cache; fetch_user asks Discord if it isn't there.
    return client.get_user(uid) or await client.fetch_user(uid)
