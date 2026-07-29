def get_prefix(persona: str) -> str:
    if persona == "valkyrie":
        return "[bold #00A8FF]Amadeus // Valkyrie: [/bold #00A8FF] "
    elif persona == "skuld":
        return "[bold #00FF66]Amadeus // Skuld: [/bold #00FF66] "
    elif persona == "gold":
        return "[bold #ffc300]Amadeus // GOLD: [/bold #ffc300] "
    return "[bold #FF003C]Amadeus // Kurisu: [/bold #FF003C]"