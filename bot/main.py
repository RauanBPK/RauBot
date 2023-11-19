import asyncio
import os
import sys
import traceback

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound, ExtensionFailed, ExtensionNotFound
from dotenv import load_dotenv

intents = discord.Intents.all()
load_dotenv()
RAUBOT_TOKEN = os.getenv("RAUBOT_TOKEN")
raubot = commands.Bot(command_prefix="!", intents=intents)
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
    print(f"Logged in as {raubot.user.name}")


@raubot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("⚠️ Comando não encontrado 😔. Digite `!help` para obter a lista de comandos disponíveis.")
    else:
        pass


def run_bot() -> None:
    asyncio.run(raubot.start(RAUBOT_TOKEN))


if __name__ == "__main__":
    run_bot()
