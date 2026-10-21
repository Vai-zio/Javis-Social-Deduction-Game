"""
Normal Blood on the Clocktower roles (Trouble Brewing).
Only data lives here: role pools, setup counts and night order.
botc.py and experimental_roles.py import from this file.
"""


# ---------------------------------------------------------------------------
# Role pools (Trouble Brewing)
# ---------------------------------------------------------------------------

TOWNSFOLK = [
    "Washerwoman", "Librarian", "Investigator", "Chef", "Empath",
    "Fortune Teller", "Undertaker", "Monk", "Ravenkeeper", "Virgin",
    "Slayer", "Soldier", "Mayor",
]
OUTSIDERS = ["Butler", "Drunk", "Recluse", "Saint"]
MINIONS = ["Poisoner", "Spy", "Scarlet Woman", "Baron"]
DEMONS = ["Imp"]


# ---------------------------------------------------------------------------
# Setup counts for each player count
# (townsfolk, outsiders, minions, demons)
# ---------------------------------------------------------------------------

SETUP_COUNTS = {
    5: (3, 0, 1, 1),
    6: (3, 1, 1, 1),
    7: (5, 0, 1, 1),
    8: (5, 1, 1, 1),
    9: (5, 2, 1, 1),
    10: (7, 0, 2, 1),
    11: (7, 1, 2, 1),
    12: (7, 2, 2, 1),
    13: (9, 0, 3, 1),
    14: (9, 1, 3, 1),
    15: (9, 2, 3, 1),
}


# ---------------------------------------------------------------------------
# Night order
# ---------------------------------------------------------------------------

FIRST_NIGHT_ORDER = [
    "~ Minion Info ~",
    "~ Demon Info ~",
    "Poisoner",
    "Washerwoman",
    "Librarian",
    "Investigator",
    "Chef",
    "Empath",
    "Fortune Teller",
    "Butler",
    "Spy",
]

OTHER_NIGHTS_ORDER = [
    "Poisoner",
    "Monk",
    "Scarlet Woman",
    "Imp",
    "Ravenkeeper",
    "Empath",
    "Fortune Teller",
    "Undertaker",
    "Butler",
    "Spy",
]
