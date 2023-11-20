import random
from typing import List

import requests
from discord import app_commands
from discord.ext import commands

from bot.utils import GUILDS_LIST, agents, hypes, insults, mapas, nl

players_queue = []
players_queue_5 = []


class Valorant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mapa", description="Sorteia um mapa para ser jogado")
    async def random_map(self, ctx):
        mapa = random.choice(mapas)
        await ctx.response.send_message(f"O mapa sorteado foi **{mapa}**! 🤪")

    async def role_autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
        roles = list(agents.keys())
        return [app_commands.Choice(name=role, value=role) for role in roles if current.lower() in role.lower()]

    @app_commands.autocomplete(role=role_autocomplete)
    @app_commands.command(name="boneco", description="Escolha um boneco pra jogar. <role> opcional")
    async def random_char(self, ctx, role: str = None):
        try:
            user = ctx.user
            insult = random.choice(insults)
            if role:
                role_formatted = role.lower()
                role_formatted = f"{role_formatted}es" if role_formatted[-1] == "r" else role_formatted
                role_formatted = f"{role_formatted}s" if role_formatted[-1] != "s" else role_formatted
                available_roles = list(agents.keys())
                if role_formatted not in available_roles:
                    await ctx.response.send_message(
                        f"⚠️ Escolha um dos seguintes roles: **{nl}{nl.join(available_roles)}**"
                    )
                    return
                agent = random.choice(agents[role_formatted])
                await ctx.response.send_message(f"{user.mention} vai jogar de **{agent}**! Boa sorte **{insult}** 🤗")
            else:
                all_agents = [item for sublist in [agents[key] for key in agents.keys()] for item in sublist]
                agent = random.choice(all_agents)
                await ctx.response.send_message(f"{user.mention} vai jogar de **{agent}**! Boa sorte **{insult}** 🤗")
        except Exception as e:
            await ctx.response.send_message("☠️ERRO☠️ - Capotei o corsa - Chame o Ra1 pra ver oq aconteceu cmg...🫠")
            await ctx.channel.send(f'Log: {" ".join(list(e.args))}')

    @app_commands.command(name="role", description="Escolha um role")
    async def random_role(self, ctx):
        roles = ["Duelista", "Controlador", "Sentinela", "Iniciador"]
        role = random.choice(roles)
        insult = random.choice(insults)
        user = ctx.user
        await ctx.response.send_message(f"{user.mention} vai jogar de **{role}**! Boa sorte {insult}! 😊")

    async def toprajogo_autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
        options = ["reset", "lista", "remove"]
        return [
            app_commands.Choice(name=option, value=option) for option in options if current.lower() in option.lower()
        ]

    @app_commands.autocomplete(command=toprajogo_autocomplete)
    @app_commands.command(name="toprajogo", description="!toprajogo - !toprajogo reset || lista || remove")
    async def toprajogo(self, ctx, command: str = None):
        global players_queue_5
        if command == "remove":
            if ctx.user.id in [user.id for user in players_queue_5]:
                players_queue_5.remove(ctx.user)
                current_count = len(players_queue_5)
                await ctx.response.send_message(f"O {ctx.user.display_name} decidiu sair...😟")
                await ctx.channel.send(
                    "```LISTA:\n"
                    + nl.join([f"{index + 1} - {user.display_name}" for index, user in enumerate(players_queue_5)])
                    + "```"
                )
                await ctx.channel.send(f"{nl}Falta{'m' if current_count < 4 else ''} {5 - current_count}!")
                return
            else:
                insult = random.choice(insults)
                await ctx.response.send_message(f"Vc nem ta na lista **{insult}**")
                return
        if command == "reset":
            players_queue_5 = []
            await ctx.response.send_message("Contador resetado 😔")
            return
        if command == "lista":
            if len(players_queue_5) == 0:
                await ctx.response.send_message("Lista vazia... q tistreza 😟")
                return
            await ctx.response.send_message(
                "```LISTA:\n"
                + nl.join([f"{index + 1} - {user.display_name}" for index, user in enumerate(players_queue_5)])
                + "```"
            )
            current_count = len(players_queue_5)
            if current_count < 5:
                await ctx.channel.send(f"Falta{'m' if current_count < 4 else ''} {5 - current_count}!")
            return

        if ctx.user.id not in [user.id for user in players_queue_5]:
            if len(players_queue_5) >= 5:
                await ctx.response.send_message("Lista cheia... Digite **!toprajogo reset** para limpar")
                return
            players_queue_5.append(ctx.user)
            insult = random.choice(insults)
            await ctx.response.send_message(f"Estamos em **{len(players_queue_5)}/5**. Bora **{insult}s!**")

            if len(players_queue_5) == 5:
                await ctx.channel.send("O time está pronto 🌝")

                await ctx.channel.send(f"Time: {nl}{nl.join([user.mention for user in players_queue_5])}")

                insult = random.choice(insults)
                await ctx.channel.send(f"Boa sorte pros cinco **{insult.lower()}s**")
        else:
            insult = random.choice(insults)
            await ctx.response.send_message(f"{ctx.user.mention}, você já está na lista **{insult}** 🙄")

    async def fivevsfive_autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
        options = ["reset", "lista", "remove", "juntar"]
        return [
            app_commands.Choice(name=option, value=option) for option in options if current.lower() in option.lower()
        ]

    @app_commands.autocomplete(command=fivevsfive_autocomplete)
    @app_commands.command(name="5v5", description="!5v5 - !5v5 reset || lista || remove || juntar")
    async def five_vs_five(self, ctx, command: str = None):
        global players_queue
        if command == "remove":
            if ctx.user.id in [user.id for user in players_queue]:
                players_queue.remove(ctx.user)
                current_count = len(players_queue)
                await ctx.response.send_message(f"O {ctx.user.display_name} decidiu sair...😟")
                await ctx.channel.send(
                    "```LISTA:\n"
                    + nl.join([f"{index + 1} - {user.display_name}" for index, user in enumerate(players_queue)])
                    + "```"
                )
                await ctx.channel.send(f"{nl}Falta{'m' if current_count < 10 else ''} {10 - current_count}!")
                return
            else:
                insult = random.choice(insults)
                await ctx.response.send_message(f"Vc nem ta na lista **{insult}**")
                return
        if command == "reset":
            players_queue = []
            await ctx.response.send_message("Contador resetado 😔")
            return
        if command == "lista":
            if len(players_queue) == 0:
                await ctx.response.send_message("Lista vazia... q tistreza 😟")
                return
            current_count = len(players_queue)
            await ctx.response.send_message(
                "```LISTA:\n"
                + nl.join([f"{index + 1} - {user.display_name}" for index, user in enumerate(players_queue)])
                + "```"
            )
            await ctx.channel.send(f"Falta{'m' if current_count < 9 else ''} {10 - current_count}!")
            return
        if command == "juntar":
            [players_queue.append(user) for user in players_queue_5 if user not in players_queue]
            insult = random.choice(insults)
            await ctx.response.send_message(f"Estamos em **{len(players_queue)}/10**. Bora **{insult}s!**")
            return
        if ctx.user.id not in [user.id for user in players_queue]:
            if len(players_queue) >= 10:
                await ctx.response.send_message("Lista cheia... Digite **!5v5 reset** para limpar")
                return
            players_queue.append(ctx.user)
            insult = random.choice(insults)
            await ctx.response.send_message(f"Estamos em **{len(players_queue)}/10**. Bora **{insult}s!**")

            if len(players_queue) == 10:
                await ctx.channel.send("Os times estão prontos 🌝 🆚 🌚")

                random.shuffle(players_queue)
                team1 = players_queue[:5]
                team2 = players_queue[5:10]

                vai_ganhar = random.choice([1, 2])
                insult = random.choice(insults)
                hype = random.choice(hypes)

                await ctx.channel.send(f"Time 1: {nl}{nl.join([user.mention for user in team1])}")
                await ctx.channel.send(f"Time 2: {nl}{nl.join([user.mention for user in team2])}")
                await ctx.channel.send(
                    f"Boa sorte pros **{insult.lower()}s**"
                    f" do Time{1 if vai_ganhar == 2 else 2},"
                    f" o Time{vai_ganhar} é **muito** {hype}! 😏"
                )
        else:
            insult = random.choice(insults)
            await ctx.response.send_message(f"{ctx.user.mention}, você já está na lista **{insult}** 🙄")

    async def comp_autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
        options = mapas
        all_options = [
            app_commands.Choice(name=mapa, value=mapa) for mapa in options if current.lower() in mapa.lower()
        ]
        all_options.append(app_commands.Choice(name="random", value="random"))
        return all_options

    @app_commands.autocomplete(mapa=comp_autocomplete)
    @app_commands.command(name="comp", description="!comp <mapa> || random")
    async def comp_maker(self, ctx, mapa: str = None):
        api_url = "https://api.thespike.gg/stats/compositions?"
        if mapa == "random":
            all_agents = [item for sublist in [agents[key] for key in agents.keys()] for item in sublist]
            random_comp = random.sample(all_agents, k=5)
            await ctx.response.send_message(f"A comp que eu fiz foi: {nl}**{' - '.join(random_comp)}**")
            await ctx.channel.send("Gostou? 👉👈 🥹")
            return

        if mapa is not None and not mapa.isalpha():
            await ctx.response.send_message("Mano, é pra digitar o nome de um mapa, não uma equação... 😒")
            return
        if not mapa:
            await ctx.response.send_message(f"Escolha um dos seguintes mapas:{nl}**{' - '.join(mapas)}**")
            return
        else:
            command = mapa.capitalize()
            if command not in mapas:
                await ctx.response.send_message(
                    f"Acho que esse mapa não existe... {nl}Escolha um dos seguintes mapas:{nl}**{' - '.join(mapas)}**"
                )
                return

            map_code = mapas.index(command) + 1  # This is specific for the API that is being used
            api_url_formatted = f"{api_url}map={map_code}"
            res = requests.get(api_url_formatted)
            if res.status_code != 200:
                await ctx.response.send_message("⚠️ Problema com a API de comps... 😢")
                return
            try:
                res_json = res.json()
                if not res_json:
                    await ctx.response.send_message(
                        f"Não encontrei nenhuma composição pickada na **{command}** nos últimos 90 dias. 😔"
                    )
                    return
                most_picked_json = res_json[0]
                most_picked_agents = [agent["title"] for agent in most_picked_json["agents"]]
                pick_rate = most_picked_json["pickRate"]
                times_played = most_picked_json["timesPlayed"]
                win_rate = most_picked_json["winRate"]
                wins = most_picked_json["wins"]
                insult = random.choice(insults)
                await ctx.response.send_message(
                    f"A comp mais pickada nos últimos camps na **{command}** foi:{nl}**{' - '.join(most_picked_agents)}**"
                    f"{nl}Frequência: **{pick_rate}%**{nl}Vezes utilizada: **{times_played}**{nl}"
                    f"Taxa de vitória: **{win_rate}%**{nl}Vitórias: **{wins}**"
                )
                await ctx.channel.send(f"{nl}Dei até a Comp, e agora seus **{insult}s**, bora? 😝")
            except (ValueError, KeyError):
                await ctx.response.send_message("⚠️ Problema com a API de comps... (buguei no json) 😢")


async def setup(bot) -> None:
    await bot.add_cog(Valorant(bot), guilds=GUILDS_LIST)
