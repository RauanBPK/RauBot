import os

import requests
from discord.ext import commands

DADJOKE_API_KEY = os.getenv("DADJOKE_API_KEY")


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dadjoke", help="Conta uma piadinha tosca")
    async def dad_joke(self, ctx):
        api_url = "https://api.api-ninjas.com/v1/dadjokes?limit=1"
        headers = {"Accept": "application/json", "X-Api-Key": DADJOKE_API_KEY}
        res = requests.get(api_url, headers=headers)
        if res.status_code == 200:
            await ctx.send(res.json()[0]["joke"])
        else:
            await ctx.send("⚠️ Problema com a API de piadinhas... 😢")

    @commands.command(name="oi", help="Diga oi para RauBot!")
    async def hello(self, ctx):
        await ctx.send("Oi, cara de boi 🐮!")


async def setup(bot) -> None:
    await bot.add_cog(Misc(bot))
