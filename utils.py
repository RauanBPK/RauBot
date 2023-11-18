def get_id_from_mention(mention) -> int:
    try:
        return int(mention.replace('<@', '').replace('>', '').replace('&', ''))
    except ValueError as e:
        return mention

nl = "\n"
insults = ["Pino", "Ruim", "Horroroso", "Cone", "Bot", "Bunda mole", "Camelo"]
hypes = ["superior", "melhor", "mais forte", "mais baludo", "mais cheiroso", "mais preparado"]
mapas = ["Split", "Bind", "Haven", "Ascent", "Icebox", "Breeze", "Fracture", "Pearl", "Lotus", "Sunset"]