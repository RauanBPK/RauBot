import os

import requests
from discord import app_commands
from discord.ext import commands

from bot.utils import GUILDS_LIST

DADJOKE_API_KEY = os.getenv("DADJOKE_API_KEY")


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dadjoke", description="Conta uma piadinha tosca")
    async def dad_joke(self, ctx):
        api_url = "https://api.api-ninjas.com/v1/dadjokes?limit=1"
        headers = {"Accept": "application/json", "X-Api-Key": DADJOKE_API_KEY}
        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            await ctx.response.send_message(res.json()[0]["joke"])
        else:
            await ctx.response.send_message("⚠️ Problema com a API de piadinhas... 😢")

    @app_commands.command(name="oi", description="Diga oi para RauBot!")
    async def hello(self, ctx):
        await ctx.response.send_message("Oi, cara de boi 🐮!")


async def setup(bot) -> None:
    await bot.add_cog(Misc(bot), guilds=GUILDS_LIST)
