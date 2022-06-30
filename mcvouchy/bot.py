from calendar import c
import configparser
from typing import Optional
from .config import singleton as config_singleton

import asyncio
import discord
import discord.app_commands


def create_bot(config: Optional[configparser.RawConfigParser]) -> None:
    if config is None:
        config = config_singleton.get_config()

    intents = discord.Intents()

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print("We have logged in as {0.user}".format(client))

        for guild in client.guilds:
            await create_commands(client, guild.id)

    return client.run(config["mcvouchy"]["secret_token"])


async def create_commands(client: discord.Client, guild_id: int) -> None:
    tree = discord.app_commands.CommandTree(client)

    @tree.command(
        guild=discord.Object(id=guild_id),
        name="invite",
        description="Create a single-use invitation for a specific person",
    )
    async def slash_invite(interaction: discord.Interaction, full_name: str) -> None:
        if not isinstance(interaction.channel, discord.TextChannel):
            return None

        await asyncio.gather(
            interaction.response.send_message(f"Test response to `/invite`; full_name={full_name}", ephemeral=True),
            interaction.channel.send(f"<@{interaction.user.id}> generated an invitation for **{full_name}**"),
        )

    @tree.command(
        guild=discord.Object(id=guild_id),
        name="vouch",
        description="Vouch for someone who just joined",
    )
    async def slash_vouch(interaction: discord.Interaction, person: discord.User) -> None:
        await interaction.response.send_message(f"Test response to `/vouch`; person=<@{person.id}>", ephemeral=True)

    @tree.command(
        guild=discord.Object(id=guild_id),
        name="limits",
        description="See how many more invites and vouches you have for today",
    )
    async def slash_limits(interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Test response to `/limits`", ephemeral=True)

    await tree.sync(guild=discord.Object(id=guild_id))
