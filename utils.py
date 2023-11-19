def get_id_from_mention(mention) -> int:
    try:
        return int(mention.replace("<@", "").replace(">", "").replace("&", ""))
    except ValueError:
        return mention


nl = "\n"
insults = [
    "Pino",
    "Ruim",
    "Horroroso",
    "Cone",
    "Bot",
    "Bunda mole",
    "Camelo",
    "Despreparado",
    "Esmilinguido",
    "Bizonho",
    "Jamanta",
    "Energúmeno",
    "Estrupício",
    "Mentecapto",
    "Lerdo",
]
hypes = [
    "superior",
    "melhor",
    "mais forte",
    "mais baludo",
    "mais cheiroso",
    "mais preparado",
    "supimpa",
    "brabo",
    "fodelástico",
    "mais gabaritado",
]
mapas = [
    "Split",
    "Bind",
    "Haven",
    "Ascent",
    "Icebox",
    "Breeze",
    "Fracture",
    "Pearl",
    "Lotus",
    "Sunset",
]
agents = {
    "duelistas": ["Phoenix", "Neon", "Jett", "Raze", "Yoru", "Iso", "Reyna"],
    "sentinelas": ["Killjoy", "Cypher", "Deadlock", "Chamber", "Sage"],
    "controladores": ["Omen", "Brimstone", "Viper", "Astra", "Harbor"],
    "iniciadores": ["Sova", "Fade", "Skye", "Breach", "Kay/o", "Gekko"],
}
