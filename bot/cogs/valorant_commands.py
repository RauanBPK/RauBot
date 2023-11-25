import json
import random
from dataclasses import dataclass
from datetime import datetime
from json import JSONDecodeError
from typing import List, Optional

import requests
from discord import InteractionResponded, Member, app_commands
from discord.ext import commands
from utils import GUILDS_LIST, agents, hypes, insults, mapas, nl


@dataclass
class MemberToPlay:
    member: Member
    time_to_play: Optional[datetime] = None

    def __str__(self):
        return str(self.to_dict())

    def __post_init__(self):
        if isinstance(self.time_to_play, str):
            try:
                self.time_to_play = datetime.strptime(self.time_to_play, "%H:%M")
            except (TypeError, ValueError):
                self.time_to_play = None

    @property
    def name_and_time(self):
        formatted_string = f"{self.display_name}"
        if self.time_to_play:
            formatted_string += f" ({self.time_to_play_str})"
        return formatted_string

    @property
    def mention_and_time(self):
        formatted_string = f"{self.mention}"
        if self.time_to_play:
            formatted_string += f" ({self.time_to_play_str})"
        return formatted_string

    @property
    def id(self):
        return self.member.id

    @property
    def name(self):
        return self.member.name

    @property
    def display_name(self):
        return self.member.display_name

    @property
    def mention(self):
        return self.member.mention

    @property
    def voice(self):
        return self.member.voice

    @property
    def move_to(self):
        return self.member.move_to

    @property
    def time_to_play_str(self):
        return self.time_to_play.strftime("%H:%M") if self.time_to_play else ""

    def to_dict(self):
        return {"member": self.member.id, "time_to_play": self.time_to_play_str}

    @classmethod
    def latest_play_hour(cls, members_to_play: List["MemberToPlay"]) -> Optional[str]:
        latest_play_hour = None
        for member_to_play in members_to_play:
            if member_to_play.time_to_play:
                if not latest_play_hour or member_to_play.time_to_play > latest_play_hour:
                    latest_play_hour = member_to_play.time_to_play
        if latest_play_hour:
            latest_play_hour = latest_play_hour.strftime("%H:%M")
        return latest_play_hour

    @classmethod
    def from_dict(cls, data, ctx=None):
        member_id = data["member"]
        member = ctx.get_user(member_id) if ctx and member_id else None
        try:
            time_to_play = datetime.strptime(data["time_to_play"], "%H:%M") if data["time_to_play"] else None
        except ValueError:
            time_to_play = None  # Set to None in case of parsing error
        return cls(member=member, time_to_play=time_to_play)


class Valorant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.comp_cache = {}
        self.players_list: List[MemberToPlay] = []
        self.players_list_5: List[MemberToPlay] = []
        self.teams = {"1": [], "2": []}

    def load_lists(self, ctx):
        self.teams = self.load_teams(ctx)
        self.players_list_5 = self.load_players_list_5(ctx)
        self.players_list = self.load_players_list(ctx)

    def load_teams(self, ctx):
        try:
            with open("bot/cogs/teams/teams.json", "r") as file:
                teams_json = json.load(file)
                teams = {
                    "1": [MemberToPlay.from_dict(user, ctx=ctx) for user in teams_json["1"]],
                    "2": [MemberToPlay.from_dict(user, ctx=ctx) for user in teams_json["2"]],
                }
        except (FileNotFoundError, JSONDecodeError, IndexError):
            teams = {"1": [], "2": []}
        return teams

    def load_players_list(self, ctx):
        try:
            with open("bot/cogs/teams/players_list.json", "r") as file:
                players_list = [MemberToPlay.from_dict(user, ctx=ctx) for user in json.load(file)]
        except (FileNotFoundError, JSONDecodeError):
            players_list = []
        return players_list

    def load_players_list_5(self, ctx):
        try:
            with open("bot/cogs/teams/players_list_5.json", "r") as file:
                players_list_5 = [MemberToPlay.from_dict(user, ctx=ctx) for user in json.load(file)]
        except (FileNotFoundError, JSONDecodeError):
            players_list_5 = []
        return players_list_5

    def save_teams(self):
        with open("bot/cogs/teams/teams.json", "w+") as file:
            teams = {
                "1": [player.to_dict() for player in self.teams["1"]],
                "2": [player.to_dict() for player in self.teams["2"]],
            }
            json.dump(teams, file)

    def save_players_list(self):
        with open("bot/cogs/teams/players_list.json", "w+") as file:
            player_data = [player.to_dict() for player in self.players_list]
            json.dump(player_data, file)

    def save_players_list_5(self):
        with open("bot/cogs/teams/players_list_5.json", "w+") as file:
            player_data = [player.to_dict() for player in self.players_list_5]
            json.dump(player_data, file)

    async def force_send_message(self, ctx, msg):
        try:
            await ctx.response.send_message(msg)
        except InteractionResponded:
            await ctx.channel.send(msg)

    async def reset_teams(self):
        self.teams["1"] = []
        self.teams["2"] = []
        self.save_teams()

    async def shuffle_teams(self):
        if len(self.players_list) == 10:
            random.shuffle(self.players_list)
            team1 = self.players_list[:5]
            team2 = self.players_list[5:10]
            self.teams["1"] = team1
            self.teams["2"] = team2
            self.save_teams()

    async def msg_list_teams(self, ctx, mention=False):
        if not self.teams["1"]:
            insult = random.choice(insults)
            try:
                await self.force_send_message(ctx, f"Os times ainda **não** estão prontos **{insult}.**")
            except Exception as e:
                print(e)
            await self.force_send_message(
                ctx, f"**Falta{'m' if len(self.players_list) < 9 else ''} {10 - len(self.players_list)}!**"
            )
        else:
            if not mention:
                await self.force_send_message(
                    ctx,
                    f"```Time 1 (PINOS): {nl}{nl.join([user.name_and_time for user in self.teams['1']])}{nl}"
                    f"{nl}Time 2 (CONES): {nl}{nl.join([user.name_and_time for user in self.teams['2']])}```",
                )
            else:
                await self.force_send_message(
                    ctx,
                    f"Time 1 (PINOS): {nl}{nl.join([user.mention for user in self.teams['1']])}{nl}"
                    f"Time 2 (CONES): {nl}{nl.join([user.mention for user in self.teams['2']])}",
                )
        return

    async def get_comp_stats(self, ctx, map_code):
        if map_code in self.comp_cache:
            return self.comp_cache[map_code]

        api_url = f"https://api.thespike.gg/stats/compositions?map={map_code}"
        res = requests.get(api_url)

        if res.status_code != 200:
            await self.force_send_message(ctx, "Problema com a API de comps... 😢")
            return

        try:
            res_json = res.json()
            if not res_json:
                await self.force_send_message(
                    ctx, "Não encontrei nenhuma composição pickada no mapa nos últimos 90 dias. 😔"
                )
                return

            most_picked_json = res_json[0]
            most_picked_agents = [agent["title"] for agent in most_picked_json["agents"]]
            pick_rate = most_picked_json["pickRate"]
            times_played = most_picked_json["timesPlayed"]
            win_rate = most_picked_json["winRate"]
            wins = most_picked_json["wins"]
            insult = random.choice(insults)

            result = (most_picked_agents, pick_rate, times_played, win_rate, wins, insult)

            # Cache the result
            self.comp_cache[map_code] = result

            return result
        except (ValueError, KeyError):
            await self.force_send_message(ctx, "Problema com a API de comps... (buguei no json) 😢")

    async def capotei_o_corsa(self, ctx, e):
        await self.force_send_message(ctx, "☠️ERRO☠️ - Capotei o corsa - Chame o Ra1 pra ver oq aconteceu cmg...🫠")
        await self.force_send_message(ctx, f'Log: {" ".join(list(e.args))}')

    async def msg_current_count_call_players(self, ctx, player_list, list_max_size):
        insult = random.choice(insults)
        await self.force_send_message(ctx, f"Estamos em **{len(player_list)}/{list_max_size}**. Bora **{insult}s!**")

    async def print_member_list(self, ctx, user_list: list, user_list_max_size: int):
        current_count = len(user_list)
        await self.force_send_message(
            ctx,
            "```LISTA:\n"
            + nl.join([f"{index + 1} - {user.name_and_time}" for index, user in enumerate(user_list)])
            + "```",
        )
        if current_count >= user_list_max_size:
            msg = "Times fechados!" if user_list_max_size == 10 else "Time fechado!"
            await self.force_send_message(ctx, msg)
        else:
            await self.force_send_message(
                ctx,
                f"{nl}Falta{'m' if current_count < (user_list_max_size - 1) else ''}"
                f" {user_list_max_size - current_count}!",
            )

    def remove_player_from_list(self, player_to_remove, player_list) -> List:
        updated_list = [player for player in player_list if player.member != player_to_remove.member]
        return updated_list

    def valid_time_to_play_str(self, time_to_play: str):
        try:
            datetime.strptime(time_to_play, "%H:%M")
        except ValueError:
            return False
        return True

    @app_commands.command(name="mapa", description="Sorteia um mapa para ser jogado")
    async def random_map(self, ctx):
        mapa = random.choice(mapas)
        await self.force_send_message(ctx, f"O mapa sorteado foi **{mapa}**! 🤪")

    async def role_autocomplete(self, _, current: str) -> List[app_commands.Choice[str]]:
        roles = list(agents.keys())
        return [app_commands.Choice(name=role, value=role) for role in roles if current.lower() in role.lower()]

    @app_commands.autocomplete(role=role_autocomplete)
    @app_commands.command(name="boneco", description="Escolha um boneco pra jogar")
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
                    await self.force_send_message(
                        ctx, f"⚠️ Escolha um dos seguintes roles: **{nl}{nl.join(available_roles)}**"
                    )
                    return
                agent = random.choice(agents[role_formatted])
                await self.force_send_message(ctx, f"{user.mention} vai jogar de **{agent}**! Boa sorte **{insult}** 🤗")
            else:
                all_agents = [item for sublist in [agents[key] for key in agents.keys()] for item in sublist]
                agent = random.choice(all_agents)
                await self.force_send_message(ctx, f"{user.mention} vai jogar de **{agent}**! Boa sorte **{insult}** 🤗")
        except Exception as e:
            await self.capotei_o_corsa(ctx, e)

    @app_commands.command(name="role", description="Escolha um role")
    async def random_role(self, ctx):
        roles = ["Duelista", "Controlador", "Sentinela", "Iniciador"]
        role = random.choice(roles)
        insult = random.choice(insults)
        user = ctx.user
        await self.force_send_message(ctx, f"{user.mention} vai jogar de **{role}**! Boa sorte {insult}! 😊")

    async def toprajogo_autocomplete(self, _, current: str) -> List[app_commands.Choice[str]]:
        options = ["reset", "lista", "remove"]
        return [
            app_commands.Choice(name=option, value=option) for option in options if current.lower() in option.lower()
        ]

    @app_commands.autocomplete(command=toprajogo_autocomplete)
    @app_commands.command(name="toprajogo", description="Adiciona seu nome na lista pra jogar")
    async def toprajogo(self, ctx, command: str = None, extra_member: Member = None, time_to_play: str = None):
        if time_to_play and not self.valid_time_to_play_str(time_to_play):
            await self.force_send_message(ctx, "Hora inválida 😟... É tipo assim ó **21:30**")
            return
        action_user = MemberToPlay(member=ctx.user, time_to_play=time_to_play)
        if extra_member:
            action_user.member = extra_member
        if command == "remove":
            if action_user.id in [user.id for user in self.players_list_5]:
                self.players_list_5 = self.remove_player_from_list(action_user, self.players_list_5)
                self.save_players_list_5()
                await self.force_send_message(ctx, f"O {action_user.display_name} decidiu sair...😟")
                await self.print_member_list(ctx, self.players_list_5, 5)
                return
            else:
                insult = random.choice(insults)
                await self.force_send_message(ctx, f"{action_user.display_name} nem ta na lista **{insult}**")
                return
        if command == "reset":
            self.players_list_5 = []
            self.save_players_list_5()
            await self.force_send_message(ctx, "Contador resetado 😔")
            return
        if command == "lista":
            if len(self.players_list_5) == 0:
                await self.force_send_message(ctx, "Lista vazia... q tistreza 😟")
                return
            await self.print_member_list(ctx, self.players_list_5, 5)
            return

        if action_user.id not in [user.id for user in self.players_list_5]:
            if len(self.players_list_5) >= 5:
                await self.force_send_message(ctx, "Lista cheia... Digite **/toprajogo reset** para limpar")
                return
            self.players_list_5.append(action_user)
            self.save_players_list_5()
            if action_user.time_to_play:
                await self.force_send_message(
                    ctx, f"**{action_user.display_name}** quer jogar só às **{action_user.time_to_play_str}**"
                )
            await self.msg_current_count_call_players(ctx, self.players_list_5, 5)
            if len(self.players_list_5) == 5:
                await self.force_send_message(ctx, "O time está pronto 🌝")

                await self.force_send_message(
                    ctx, f"Time: {nl}{nl.join([user.mention for user in self.players_list_5])}"
                )

                latest_play_hour = MemberToPlay.latest_play_hour(self.players_list_5)
                if latest_play_hour:
                    await self.force_send_message(ctx, f"Hora provável de jogo: **{latest_play_hour}**")
                insult = random.choice(insults)
                await self.force_send_message(ctx, f"Boa sorte pros cinco **{insult.lower()}s**")
        else:
            insult = random.choice(insults)
            await self.force_send_message(ctx, f"{action_user.mention}, você já está na lista **{insult}** 🙄")

    async def fivevsfive_autocomplete(self, _, current: str) -> List[app_commands.Choice[str]]:
        options = ["reset", "lista", "remove", "juntar", "times", "novostimes"]
        return [
            app_commands.Choice(name=option, value=option) for option in options if current.lower() in option.lower()
        ]

    @app_commands.autocomplete(command=fivevsfive_autocomplete)
    @app_commands.command(name="5v5", description="Adiciona seu nome na lista pro 5x5 - Forma 2 times")
    async def five_vs_five(self, ctx, command: str = None, extra_member: Member = None, time_to_play: str = None):
        action_user = MemberToPlay(member=ctx.user, time_to_play=time_to_play)
        if extra_member:
            action_user.member = extra_member
        if command == "novostimes":
            await self.shuffle_teams()
            await self.msg_list_teams(ctx)
            return
        if command == "times":
            await self.msg_list_teams(ctx)
            return
        if command == "remove":
            if action_user.id in [user.id for user in self.players_list]:
                self.players_list = self.remove_player_from_list(action_user, self.players_list)
                self.save_players_list()
                await self.reset_teams()
                await self.force_send_message(ctx, f"{action_user.display_name} decidiu sair...😟")
                await self.print_member_list(ctx, self.players_list, 10)
                return
            else:
                insult = random.choice(insults)
                await self.force_send_message(ctx, f"{action_user.display_name} nem ta na lista **{insult}**")
                return
        if command == "reset":
            self.players_list = []
            self.save_players_list()
            await self.reset_teams()
            await self.force_send_message(ctx, "Contador resetado 😔")
            return
        if command == "lista":
            if len(self.players_list) == 0:
                await self.force_send_message(ctx, "Lista vazia... q tistreza 😟")
                return
            await self.print_member_list(ctx, self.players_list, 10)
            return
        if command == "juntar":
            [self.players_list.append(user) for user in self.players_list_5 if user not in self.players_list]
            self.save_players_list()
            await self.msg_current_count_call_players(ctx, self.players_list, 10)
            return
        if action_user.id not in [user.id for user in self.players_list]:
            if len(self.players_list) >= 10:
                await self.force_send_message(ctx, "Lista cheia... Digite **/5v5 reset** para limpar")
                return
            self.players_list.append(action_user)
            self.save_players_list()
            if action_user.time_to_play:
                await self.force_send_message(
                    ctx, f"**{action_user.display_name}** quer jogar só às **{action_user.time_to_play_str}**"
                )
            await self.msg_current_count_call_players(ctx, self.players_list, 10)

            if len(self.players_list) == 10:
                await self.force_send_message(ctx, "Os times estão prontos 🌝 🆚 🌚")
                await self.shuffle_teams()
                await self.msg_list_teams(ctx, mention=True)

                latest_play_hour = MemberToPlay.latest_play_hour(self.players_list)
                if latest_play_hour:
                    await self.force_send_message(ctx, f"Hora provável de jogo: **{latest_play_hour}**")

                vai_ganhar = random.choice([1, 2])
                insult = random.choice(insults)
                hype = random.choice(hypes)
                await self.force_send_message(
                    ctx,
                    f"Boa sorte pros **{insult.lower()}s**"
                    f" do Time {1 if vai_ganhar == 2 else 2},"
                    f" o Time {vai_ganhar} é **muito {hype}!** 😏",
                )
        else:
            insult = random.choice(insults)
            await self.force_send_message(ctx, f"{action_user.mention}, você já está na lista **{insult}** 🙄")

    async def teams_autocomplete(self, _, current: str) -> List[app_commands.Choice[str]]:
        all_options = [
            app_commands.Choice(name=team, value=team) for team in ["Pinos", "Cones"] if current.lower() in team.lower()
        ]
        return all_options

    async def move_teams_autocomplete(self, ctx, current: str) -> List[app_commands.Choice[str]]:
        voice_channels = ctx.guild.voice_channels
        all_options = [
            app_commands.Choice(name=channel.name, value=channel.name)
            for channel in voice_channels
            if current.lower() in channel.name.lower()
        ]
        return all_options

    @app_commands.autocomplete(channel=move_teams_autocomplete)
    @app_commands.autocomplete(team=teams_autocomplete)
    @app_commands.command(name="moveteam", description="Move um time pra outro canal de voz")
    async def move_teams(self, ctx, team: str, channel: str):
        if team == "1" or "pinos" in team.lower():
            team_members = self.teams["1"]
        elif team == "2" or "cones" in team.lower():
            team_members = self.teams["2"]
        else:
            await self.force_send_message(ctx, "Time inválido 😔. Escolha entre **1-Pinos** ou **2-Cones** ")
            return
        try:
            err = 0
            channels_match = [
                voice_channel for voice_channel in ctx.guild.voice_channels if voice_channel.name == channel
            ]
            to_channel = channels_match[0] if channels_match else None
            if not to_channel:
                await self.force_send_message(ctx, "Não encontrei esse canal 😢")
                return
            if not team_members:
                await self.force_send_message(ctx, "Ninguém pra mover 😢")
                return
            for member in team_members:
                try:
                    if member.voice:
                        await member.move_to(to_channel)
                except Exception:
                    await self.force_send_message(ctx, f"⚠️ Não consegui mover **{member.mention}** 😔")
                    err = 1
                    continue
            if not err:
                await self.force_send_message(ctx, f"Cones movidos para **{to_channel.name}**!")
        except Exception as e:
            await self.capotei_o_corsa(ctx, e)

    async def comp_autocomplete(self, _, current: str) -> List[app_commands.Choice[str]]:
        options = mapas
        all_options = [
            app_commands.Choice(name=mapa, value=mapa) for mapa in options if current.lower() in mapa.lower()
        ]
        all_options.append(app_commands.Choice(name="Random", value="random"))
        return all_options

    @app_commands.autocomplete(mapa=comp_autocomplete)
    @app_commands.command(name="comp", description="Sugere uma comp")
    async def comp_maker(self, ctx, mapa: str = None):
        if mapa == "random":
            all_agents = [item for sublist in [agents[key] for key in agents.keys()] for item in sublist]
            random_comp = random.sample(all_agents, k=5)
            await self.force_send_message(ctx, f"A comp que eu fiz foi: {nl}**{' - '.join(random_comp)}**")
            await self.force_send_message(ctx, "Gostou? 👉👈 🥹")
            return
        if mapa is not None and not mapa.isalpha():
            await self.force_send_message(ctx, "Mano, é pra digitar o nome de um mapa, não uma equação... 😒")
            return
        if not mapa:
            await self.force_send_message(ctx, f"Escolha um dos seguintes mapas:{nl}**{' - '.join(mapas)}**")
            return
        else:
            command = mapa.capitalize()
            if command not in mapas:
                await self.force_send_message(
                    ctx,
                    f"Acho que esse mapa não existe... {nl}Escolha um dos seguintes mapas:{nl}**{' - '.join(mapas)}**",
                )
                return

            map_code = mapas.index(command) + 1  # This is specific for the API that is being used
            try:
                res = await self.get_comp_stats(ctx, map_code)
                if not res:
                    return
                most_picked_agents, pick_rate, times_played, win_rate, wins, insult = res

                await self.force_send_message(
                    ctx,
                    f"A comp mais pickada nos últimos camps na **{command}** "
                    f"foi:{nl}**{' - '.join(most_picked_agents)}**"
                    f"{nl}Frequência: **{pick_rate}%**{nl}Vezes utilizada: **{times_played}**{nl}"
                    f"Taxa de vitória: **{win_rate}%**{nl}Vitórias: **{wins}**",
                )

                await self.force_send_message(ctx, f"{nl}Dei até a Comp, e agora seus **{insult}s**, bora? 😝")
            except ValueError:
                await self.force_send_message(ctx, "Problema com a API de comps... (buguei no json) 😢")


async def setup(bot) -> None:
    await bot.add_cog(Valorant(bot), guilds=GUILDS_LIST)
