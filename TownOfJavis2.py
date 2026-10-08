import random


# ---------------------------------------------------------------------------
# Role pools
# ---------------------------------------------------------------------------

TOWN_INFO = ["Tracker", "Seer", "Spy", "Sheriff"]
TOWN_KILL = ["Jailor", "Hunter", "Veteran"]
TOWN_UTIL = ["Doctor", "Priest", "Guardian Angel", "Mayor"]

MAFIA_KILL = ["Mafioso", "Godfather"]
MAFIA_UTIL = ["Poisoner", "Framer", "Blackmailer", "Consigliere"]

NEUTRAL_BENIGN = ["Amnesiac", "Cupid", "Survivor"]
NEUTRAL_EVIL = ["Jester", "Executioner", "Witch"]
NEUTRAL_KILL = ["Serial Killer", "Arsonist"]


# ---------------------------------------------------------------------------
# Role slots for each player count
# ---------------------------------------------------------------------------

ROLE_SLOTS = {
    6: [
        "town_info", "town_info", "town_util",
        "mafia_kill", "mafia_util",
        "neutral",
    ],
    7: [
        "town_info", "town_info", "town_util", "town_util",
        "mafia_kill", "mafia_util",
        "neutral",
    ],
    8: [
        "town_info", "town_info", "town_util", "town_util",
        "mafia_kill", "mafia_util",
        "neutral", "neutral",
    ],
    9: [
        "town_info", "town_info", "town_info",
        "town_util", "town_util",
        "mafia_kill", "mafia_kill", "mafia_util",
        "neutral",
    ],
    10: [
        "town_info", "town_info", "town_util", "town_util", "town_kill",
        "mafia_kill", "mafia_kill", "mafia_util",
        "neutral", "neutral",
    ],
    11: [
        "town_info", "town_info", "town_info",
        "town_util", "town_util", "town_kill",
        "mafia_kill", "mafia_kill", "mafia_util",
        "neutral", "neutral",
    ],
    12: [
        "town_info", "town_info", "town_info",
        "town_util", "town_util", "town_util", "town_kill",
        "mafia_kill", "mafia_kill", "mafia_util",
        "neutral", "neutral",
    ],
    13: [
        "town_info", "town_info", "town_info",
        "town_util", "town_util", "town_kill",
        "mafia_kill", "mafia_kill", "mafia_util", "mafia_util",
        "neutral", "neutral",
    ],
    14: [
        "town_info", "town_info", "town_info",
        "town_util", "town_util", "town_util", "town_kill",
        "mafia_kill", "mafia_kill", "mafia_util", "mafia_util",
        "neutral", "neutral", "neutral",
    ],
    15: [
        "town_info", "town_info", "town_info",
        "town_util", "town_util", "town_util", "town_kill", "town_kill",
        "mafia_kill", "mafia_kill", "mafia_util", "mafia_util",
        "neutral", "neutral", "neutral",
    ],
}


# ---------------------------------------------------------------------------
# Night order
# ---------------------------------------------------------------------------

FIRST_NIGHT_ORDER = [
    "Godfather",
    "Mafioso",
    "~ Mafia Identification ~",
    "Cupid",
    "~ Lovebirds Identification ~",
    "Poisoner",
    "Framer",
    "Blackmailer",
    "Arsonist",
    "Doctor",
    "Mayor",
    "Jailor",
    "Hunter",
    "Veteran",
    "Amnesiac",
    "Survivor",
    "Serial Killer",
    "Priest",
    "Guardian Angel",
    "Jester",
    "Executioner",
    "Consigliere",
    "Spy",
    "Seer",
    "Sheriff",
    "Tracker",
]

# These are currently unused, but can be used later for subsequent nights.
OTHER_NIGHTS_1 = ["Jailor", "Poisoner", "Framer", "Blackmailer"]
OTHER_NIGHTS_2 = [
    "Godfather / Mafioso",
    "Serial Killer",
    "Arsonist",
    "Hunter",
    "Veteran",
]
OTHER_NIGHTS_3 = [
    "Doctor",
    "Priest",
    "Guardian Angel",
    "Survivor",
    "Amnesiac",
]
OTHER_NIGHTS_4 = [
    "Consigliere",
    "Spy",
    "Seer",
    "Sheriff",
    "Tracker",
]


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

def get_number_of_players() -> int:
    """Ask the user for the number of players."""
    while True:
        try:
            number_of_players = int(input("How many players? (6-15 players) "))
        except ValueError:
            print("Input a whole number from 6 to 15.")
            continue

        if 6 <= number_of_players <= 15:
            return number_of_players

        print("Input a whole number from 6 to 15.")


# ---------------------------------------------------------------------------
# Role generation
# ---------------------------------------------------------------------------

def create_role_pools() -> dict[str, list[str]]:
    """Create fresh role pools for a new game."""
    return {
        "town_info": TOWN_INFO.copy(),
        "town_kill": TOWN_KILL.copy(),
        "town_util": TOWN_UTIL.copy(),
        "mafia_kill": MAFIA_KILL.copy(),
        "mafia_util": MAFIA_UTIL.copy(),
        "neutral_benign": NEUTRAL_BENIGN.copy(),
        "neutral_evil": NEUTRAL_EVIL.copy(),
        "neutral_kill": NEUTRAL_KILL.copy(),
    }


def choose_role(
    role_type: str,
    number_of_players: int,
    role_pools: dict[str, list[str]],
    killing_neutral_present: bool,
) -> tuple[str, bool]:
    """
    Replace a role category with an actual role.

    Returns:
        A tuple containing:
        - the selected role
        - whether a killing neutral is now present
    """

    if role_type == "town_info":
        pool = role_pools["town_info"]
        role = random.choice(pool)
        pool.remove(role)

    elif role_type == "town_util":
        pool = role_pools["town_util"]
        role = random.choice(pool)
        pool.remove(role)

    elif role_type == "town_kill":
        pool = role_pools["town_kill"]
        role = random.choice(pool)
        pool.remove(role)

    elif role_type == "mafia_kill":
        # Games with fewer than 9 players always get Mafioso here.
        if number_of_players < 9:
            role = "Mafioso"
        else:
            pool = role_pools["mafia_kill"]
            role = pool.pop(0)

    elif role_type == "mafia_util":
        pool = role_pools["mafia_util"]
        role = random.choice(pool)
        pool.remove(role)

    elif role_type == "neutral":
        if number_of_players < 9 or killing_neutral_present:
            neutral_type = random.randint(1, 2)
        else:
            neutral_type = random.randint(1, 3)

        if neutral_type == 1:
            pool = role_pools["neutral_benign"]
            role = random.choice(pool)
            pool.remove(role)

        elif neutral_type == 2:
            pool = role_pools["neutral_evil"]
            role = random.choice(pool)
            pool.remove(role)

        else:
            pool = role_pools["neutral_kill"]
            role = random.choice(pool)
            pool.remove(role)
            killing_neutral_present = True

    else:
        raise ValueError(f"Unknown role type: {role_type}")

    return role, killing_neutral_present


def generate_roles(number_of_players: int) -> list[str]:
    """Generate a complete role list for a game."""
    role_pools = create_role_pools()
    role_slots = ROLE_SLOTS[number_of_players]

    roles = []
    killing_neutral_present = False

    for role_type in role_slots:
        role, killing_neutral_present = choose_role(
            role_type,
            number_of_players,
            role_pools,
            killing_neutral_present,
        )
        roles.append(role)

    return roles


# ---------------------------------------------------------------------------
# Sorting and player numbers
# ---------------------------------------------------------------------------

def sort_roles(roles: list[str]) -> list[str]:
    """Sort roles according to the first-night order."""
    order = {
        role: index
        for index, role in enumerate(FIRST_NIGHT_ORDER)
    }

    return sorted(
        roles,
        key=lambda role: order.get(role, len(FIRST_NIGHT_ORDER)),
    )


def get_random_player_numbers(number_of_players: int) -> list[int]:
    """Return player numbers in a random order."""
    player_numbers = list(range(1, number_of_players + 1))
    random.shuffle(player_numbers)
    return player_numbers


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def display_first_night(
    roles: list[str],
    player_numbers: list[int],
) -> None:
    """Display the first-night role order."""
    print("\n===== First Night =====")

    for player_number, role in zip(player_numbers, roles):
        print(f"{player_number} {role}")

        if role == "Mafioso":
            print("~ Mafia Identification ~")

        elif role == "Cupid":
            print("~ Lovebirds Identification ~")

# Other night categories
OTHER_NIGHTS = {
    "Control / Setup": [
        "Jailor",
        "Poisoner",
        "Framer",
        "Blackmailer",
    ],
    "Killing": [
        "Mafioso",
        "Godfather"
        "Serial Killer",
        "Arsonist",
        "Hunter",
        "Veteran",
    ],
    "Buffs / Utility": [
        "Doctor",
        "Priest",
        "Guardian Angel",
        "Survivor",
        "Amnesiac",
    ],
    "Information": [
        "Consigliere",
        "Spy",
        "Seer",
        "Sheriff",
        "Tracker",
    ],
}

def display_other_nights(roles: list[str]) -> None:
    """Display the roles that act during nights after the first night."""

    print("\n===== Other Nights =====")

    for category, category_roles in OTHER_NIGHTS.items():
        # Only show roles that are actually in the current game.
        active_roles = [
            role for role in category_roles
            if role in roles
        ]

        if not active_roles:
            continue

        print(f"\n--- {category} ---")

        for role in active_roles:
            print(role)


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------

def play_game() -> None:
    """Generate and display a game of Javis' Social Deduction."""
    while True:
        number_of_players = get_number_of_players()

        roles = generate_roles(number_of_players)
        roles = sort_roles(roles)

        player_numbers = get_random_player_numbers(number_of_players)

        display_first_night(roles, player_numbers)
        display_other_nights(roles)
        

        play_again = input("\nReroll? Enter 'y' to play again: ")

        if play_again.lower() != "y":
            break


if __name__ == "__main__":
    play_game()

