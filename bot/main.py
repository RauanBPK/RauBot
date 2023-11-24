#!/usr/bin/env python3.9

import asyncio
import os
import random
import sys
import traceback

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, ExtensionFailed, ExtensionNotFound
from dotenv import load_dotenv
from utils import michael_gif

intents = discord.Intents.all()
load_dotenv()
RAUBOT_TOKEN = os.getenv("RAUBOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
raubot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
initial_extensions = ["cogs.misc", "cogs.valorant_commands"]


@raubot.event
async def setup_hook():
    for ext in initial_extensions:
        try:
            await raubot.load_extension(ext)
        except (
            ExtensionNotFound,
            ExtensionFailed,
        ):
            print(f"Failed to load extension {ext}.", file=sys.stderr)
            traceback.print_exc()


@raubot.event
async def on_ready():
    # Gambiarra
    # Da load nos arquivos de listas assim que o bot ta pronto
    # Isso precisa ser refatorado caso o bot seja usado em vários servidores, se naõ, mistura tudo
    if not os.path.exists("bot/cogs/teams"):
        os.makedirs("bot/cogs/teams")
    raubot.cogs["Valorant"].load_lists()
    print(f"Logged in as {raubot.user.name}")


@raubot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("⚠️ Comando não encontrado 😔. Digite `!help` para obter a lista de comandos disponíveis.")
    else:
        pass


@raubot.event
async def on_message(message):
    await raubot.process_commands(message)
    if message.author == raubot.user:
        return

    should_respond = random.choices([True, False], k=1, weights=(1, 150))[0]
    if should_respond:
        await message.reply("That's what she said!")
        await message.channel.send(michael_gif)


@raubot.command()
async def help(ctx):
    help_string = "```        COMANDOS RAUBOT\n"
    cogs = ctx.bot.cogs
    cogs_names = [cog_name for cog_name in cogs]
    for cog_name in cogs_names:
        command_desc_tuple = [(a.name, a.description) for a in vars(ctx.bot.cogs[cog_name])["__cog_app_commands__"]]
        for name_desc in command_desc_tuple:
            name, description = name_desc
            help_string += f"/{name:.<10} -> {description:.>4}\n"
    help_string += "```"
    await ctx.send(help_string)


@raubot.command()
async def sync(ctx):
    if str(ctx.author.id) == OWNER_ID:
        guild = discord.Object(id=ctx.guild.id)
        await ctx.send(f"syncing  to {ctx.guild}...")
        raubot.tree.copy_global_to(guild=guild)
        await raubot.tree.sync(guild=guild)
        await ctx.send("done!")
    else:
        await ctx.response.send_message("Só o papis pode usar esse comando! 🙄")


def run_bot() -> None:
    asyncio.run(raubot.start(RAUBOT_TOKEN))


if __name__ == "__main__":
    run_bot()
