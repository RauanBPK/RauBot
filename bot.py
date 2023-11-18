import discord
import random
import os
import requests
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from utils import get_id_from_mention, nl, insults, hypes, mapas, agents

intents = discord.Intents.all()
load_dotenv()
RAUBOT_TOKEN = os.getenv('RAUBOT_TOKEN')
DADJOKE_API_KEY = os.getenv('DADJOKE_API_KEY')
bot = commands.Bot(command_prefix='!', intents=intents)
players_queue = []
players_queue_5 = []


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command(name='oi', help="Diga oi para RauBot!")
async def hello(ctx):
    await ctx.send('Oi, cara de boi 🐮!')


@bot.command(name="mapa", help="Sorteia um mapa para ser jogado")
async def random_map(ctx):
    mapa = random.choice(mapas)
    await ctx.send(f"O mapa sorteado foi **{mapa}**! 🤪")


@bot.command(name='boneco', help="Escolha um boneco pra jogar. <role> opcional")
async def random_char(ctx, role=None):
    try:
        user = ctx.message.author
        insult = random.choice(insults)
        if role:
            role_formatted = role.lower()
            role_formatted = f"{role_formatted}es" if role_formatted[-1] == "r" else role_formatted
            role_formatted = f"{role_formatted}s" if role_formatted[-1] != "s" else role_formatted
            available_roles = list(agents.keys())
            if role_formatted not in available_roles:
                await ctx.send(f"⚠️ Escolha um dos seguintes roles: **{nl}{nl.join(available_roles)}**")
                return
            agent = random.choice(agents[role_formatted])
            await ctx.send(f"{user.mention} vai jogar de **{agent}**! Boa sorte **{insult}** 🤗")
        else:
            all_agents = [item for sublist in [agents[key] for key in agents.keys()] for item in sublist]
            agent = random.choice(all_agents)
            await ctx.send(f"{user.mention} vai jogar de **{agent}**! Boa sorte **{insult}** 🤗")
    except Exception as e:
        await ctx.send('☠️ERRO☠️ - Capotei o corsa - Chame o Ra1 pra ver oq aconteceu cmg...🫠')
        await ctx.send(f'Log: {" ".join(list(e.args))}')


@bot.command(name='role', help="Escolha um role")
async def random_role(ctx):
    roles = ["Duelista", "Controlador", "Sentinela", "Iniciador"]
    role = random.choice(roles)
    insult = random.choice(insults)
    user = ctx.message.author
    await ctx.send(f"{user.mention} vai jogar de **{role}**! Boa sorte {insult}! 😊")


@bot.command(name='times', help="!times @<user1> @<user2>... para formar times ")
async def random_teams(ctx, *member_mentions):
    try:
        # Check if there are enough members for teams
        if len(member_mentions) < 2:
            await ctx.send("⚠️ Escolha menos dois cones pra formar times né...")
            return

        # Shuffle the list of members to randomize the teams
        member_mentions = list(member_mentions)
        random.shuffle(member_mentions)

        # Calculate the midpoint to split the list into two teams
        midpoint = len(member_mentions) // 2
        # Divide the list into two teams
        team1 = member_mentions[:midpoint]
        team1 = [get_id_from_mention(member) for member in team1]
        team2 = member_mentions[midpoint:]
        team2 = [get_id_from_mention(member) for member in team2]
        # Display the teams
        await ctx.send("Times criados! 😎")
        # appends the names that resolved to a valid ID ( like in @ra1 )
        team1_names = [await bot.fetch_user(user_id) for user_id in team1 if isinstance(user_id, int)]
        # transforms the names in valid mentions, so that the user is notified
        team1_names = [user.mention for user in team1_names]
        # appends the rest of names that did not resolve to a valid ID ( like a simple string 'player1' )
        team1_names += [user for user in team1 if not isinstance(user, int)]

        team2_names = [await bot.fetch_user(user_id) for user_id in team2 if isinstance(user_id, int)]
        team2_names = [user.mention for user in team2_names]
        team2_names += [user for user in team2 if not isinstance(user, int)]

        await ctx.send(f'Time 1: **{nl}{nl.join([user for user in team1_names])}**')
        await ctx.send(f'Time 2: **{nl}{nl.join([user for user in team2_names])}**')

        vai_ganhar = random.choice([1, 2])
        insult = random.choice(insults)
        hype = random.choice(hypes)
        await ctx.send(f'Boa sorte pros **{insult.lower()}s** do Time{1 if vai_ganhar == 2 else 2}, o Time{vai_ganhar} é **muito** {hype}! 😏')
    except Exception as e:
        await ctx.send('☠️ERRO☠️ - Capotei o corsa - Chame o Ra1 pra ver oq aconteceu cmg...🫠')
        await ctx.send(f'Log: {" ".join(list(e.args))}')


@bot.command(name='dadjoke', help="Conta uma piadinha tosca")
async def dad_joke(ctx):
    api_url = "https://api.api-ninjas.com/v1/dadjokes?limit=1"
    headers = {'Accept': 'application/json', 'X-Api-Key': DADJOKE_API_KEY}
    res = requests.get(api_url, headers=headers)
    if res.status_code == 200:
        await ctx.send(res.json()[0]['joke'])
    else:
        await ctx.send("⚠️ Problema com a API de piadinhas... 😢")


@bot.command(name='mover', help="!mover <canal_de_voz> @<user1> @<user2> para mover os times para outro canal de voz")
async def move_to_voice_channel(ctx, to_channel: str, *member_mentions):
    try:
        # Check if the command was used in a guild
        if ctx.guild:
            # Get the target voice channel to move users to
            to_channel = await commands.VoiceChannelConverter().convert(ctx, to_channel)
            # Check if the target voice channel exists
            if to_channel:
                # Move each mentioned member to the target channel
                moved = 0
                for member_mention in member_mentions:
                    try:
                        member_id = int(member_mention.replace('<@', '').replace('>', ''))  # Extract member ID from mention
                        member = ctx.guild.get_member(member_id)
                    except ValueError:
                        await ctx.send(f"⚠️ Não consegui mover **{member_mention}** 😔")
                        continue
                    if member and member.voice:
                        await member.move_to(to_channel)
                        moved += 1

                if moved:
                    await ctx.send(f'{"Cones movidos" if moved > 1 else "Cone movido"} para {to_channel.name}!')
            else:
                await ctx.send('⚠️Canal inválido⚠️')
        else:
            await ctx.send('⚠️ Esse comando só pode ser usado dentro de um servidor!')

    except commands.ChannelNotFound as e:
        await ctx.send(f'☠️ERRO☠️ - Não encontrei o canal {e.argument} 😢')
    except Exception as e:
        await ctx.send('☠️ERRO☠️ - Capotei o corsa - Chame o Ra1 pra ver oq aconteceu cmg...🫠')
        await ctx.send(f'Log: {" ".join(list(e.args))}')


@bot.command(name='toprajogo', help="!toprajogo - !toprajogo reset || lista || remove")
async def toprajogo(ctx, command=None):
    global players_queue_5
    if command == "remove":
        if ctx.author.id in [user.id for user in players_queue_5]:
            players_queue_5.remove(ctx.author)
            current_count = len(players_queue_5)
            await ctx.send(f"O {ctx.author.display_name} decidiu sair...😟")
            await ctx.send("```LISTA:\n" + nl.join([f"{index + 1} - {user.display_name}" for index, user in enumerate(players_queue_5)]) + "```")
            await ctx.send(f"Falta{'m' if current_count < 4 else ''} {5 - current_count}!")
            return
        else:
            insult = random.choice(insults)
            await ctx.send(f"Vc nem ta na lista **{insult}**")
            return
    if command == "reset":
        players_queue_5 = []
        await ctx.send("Contador resetado 😔")
        return
    if command == "lista":
        if len(players_queue_5) == 0:
            await ctx.send("Lista vazia... q tistreza 😟")
            return
        await ctx.send("```LISTA:\n" + nl.join([f"{index + 1} - {user.display_name}" for index, user in enumerate(players_queue_5)]) + "```")
        current_count = len(players_queue_5)
        if current_count < 5:
            await ctx.send(f"Falta{'m' if current_count < 4 else ''} {5-current_count}!")
        return
    if ctx.author.id not in [user.id for user in players_queue_5]:
        if len(players_queue_5) >= 5:
            await ctx.send("Lista cheia... Digite **!toprajogo reset** para limpar")
            return
        players_queue_5.append(ctx.author)
        insult = random.choice(insults)
        await ctx.send(f"Estamos em **{len(players_queue_5)}/5**. Bora **{insult}s!**")

        if len(players_queue_5) == 5:
            await ctx.send("O time está pronto 🌝")

            await ctx.send(f"Time: {nl}{nl.join([user.mention for user in players_queue_5])}")

            insult = random.choice(insults)
            await ctx.send(f'Boa sorte pros cinco **{insult.lower()}s**')
    else:
        insult = random.choice(insults)
        await ctx.send(f"{ctx.author.mention}, você já está na lista **{insult}** 🙄")


@bot.command(name='5v5', help="!5v5 - !5v5 reset || lista || remove || juntar")
async def five_vs_five(ctx, command=None):
    global players_queue
    if command == "remove":
        if ctx.author.id in [user.id for user in players_queue]:
            players_queue.remove(ctx.author)
            current_count = len(players_queue)
            await ctx.send(f"O {ctx.author.display_name} decidiu sair...😟")
            await ctx.send("```LISTA:\n" + nl.join([f"{index + 1} - {user.display_name}" for index, user in enumerate(players_queue)]) + "```")
            await ctx.send(f"Falta{'m' if current_count < 10 else ''} {10 - current_count}!")
            return
        else:
            insult = random.choice(insults)
            await ctx.send(f"Vc nem ta na lista **{insult}**")
            return
    if command == "reset":
        players_queue = []
        await ctx.send("Contador resetado 😔")
        return
    if command == "lista":
        if len(players_queue) == 0:
            await ctx.send("Lista vazia... q tistreza 😟")
            return
        await ctx.send("```LISTA:\n" + nl.join([f"{index + 1} - {user.display_name}" for index, user in enumerate(players_queue)]) + "```")
        current_count = len(players_queue)
        if current_count < 10:
            await ctx.send(f"Falta{'m' if current_count < 9 else ''} {10-current_count}!")
        return
    if command == "juntar":
        [players_queue.append(user) for user in players_queue_5 if user not in players_queue]
        insult = random.choice(insults)
        await ctx.send(f"Estamos em **{len(players_queue)}/10**. Bora **{insult}s!**")
        return
    if ctx.author.id not in [user.id for user in players_queue]:
        if len(players_queue) >= 10:
            await ctx.send("Lista cheia... Digite **!5v5 reset** para limpar")
            return
        players_queue.append(ctx.author)
        insult = random.choice(insults)
        await ctx.send(f"Estamos em **{len(players_queue)}/10**. Bora **{insult}s!**")

        if len(players_queue) == 10:
            await ctx.send("Os times estão prontos 🌝 🆚 🌚")

            random.shuffle(players_queue)
            team1 = players_queue[:5]
            team2 = players_queue[5:10]

            await ctx.send(f"Time 1: {nl}{nl.join([user.mention for user in team1])}")
            await ctx.send(f"Time 2: {nl}{nl.join([user.mention for user in team2])}")

            vai_ganhar = random.choice([1, 2])
            insult = random.choice(insults)
            hype = random.choice(hypes)
            await ctx.send(f'Boa sorte pros **{insult.lower()}s** do Time{1 if vai_ganhar == 2 else 2}, o Time{vai_ganhar} é **muito** {hype}! 😏')
    else:
        insult = random.choice(insults)
        await ctx.send(f"{ctx.author.mention}, você já está na lista **{insult}** 🙄")


@bot.command(name='comp', help="!comp <mapa> || random")
async def comp_maker(ctx, command=None):
    api_url = "https://api.thespike.gg/stats/compositions?"
    if command == "random":
        all_agents = [item for sublist in [agents[key] for key in agents.keys()] for item in sublist]
        random_comp = random.sample(all_agents, k=5)
        await ctx.send(f"A comp que eu fiz foi: {nl}**{' - '.join(random_comp)}**")
        await ctx.send("Gostou? 👉👈 🥹")
        return

    if command is not None and not command.isalpha():
        await ctx.send("Mano, é pra digitar o nome de um mapa, não uma equação... 😒")
        return
    if not command:
        await ctx.send(f"Escolha um dos seguintes mapas:{nl}**{' - '.join(mapas)}**")
        return
    else:
        command = command.capitalize()
        if command not in mapas:
            await ctx.send(f"Acho que esse mapa não existe... {nl}Escolha um dos seguintes mapas:{nl}**{' - '.join(mapas)}**")
            return

        map_code = mapas.index(command) + 1  # This is specific for the API that is being used
        api_url_formatted = f"{api_url}map={map_code}"
        res = requests.get(api_url_formatted)
        if res.status_code != 200:
            await ctx.send("⚠️ Problema com a API de comps... 😢")
            return
        try:
            res_json = res.json()
            if not res_json:
                await ctx.send(f"Não encontrei nenhuma composição pickada na **{command}** nos últimos 90 dias. 😔")
                return
            most_picked_json = res_json[0]
            most_picked_agents = [agent['title'] for agent in most_picked_json['agents']]
            pick_rate = most_picked_json['pickRate']
            times_played = most_picked_json['timesPlayed']
            win_rate = most_picked_json['winRate']
            wins = most_picked_json['wins']
            await ctx.send(f"A comp mais pickada nos últimos camps na **{command}** foi:{nl}**{' - '.join(most_picked_agents)}**")
            await ctx.send(f"Frequência: **{pick_rate}%**{nl}Vezes utilizada: **{times_played}**{nl}"
                           f"Taxa de vitória: **{win_rate}%**{nl}Vitórias: **{wins}**")
            insult = random.choice(insults)
            await ctx.send(f"Dei até a Comp, e agora seus **{insult}s**, bora? 😝")
        except (ValueError, KeyError):
            await ctx.send("⚠️ Problema com a API de comps... (buguei no json) 😢")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.send("⚠️ Comando não encontrado 😔. Digite `!help` para obter a lista de comandos disponíveis.")
    else:
        pass

bot.run(RAUBOT_TOKEN)
