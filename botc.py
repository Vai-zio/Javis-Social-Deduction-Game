import random

from botc_roles import (
    TOWNSFOLK, OUTSIDERS, MINIONS, DEMONS,
    SETUP_COUNTS, FIRST_NIGHT_ORDER, OTHER_NIGHTS_ORDER,
)


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

def get_number_of_players() -> int:
    """Ask the user for the number of players."""
    while True:
        try:
            number_of_players = int(input("How many players? (5-15 players) "))
        except ValueError:
            print("Input a whole number from 5 to 15.")
            continue

        if 5 <= number_of_players <= 15:
            return number_of_players

        print("Input a whole number from 5 to 15.")


# ---------------------------------------------------------------------------
# Role generation
# ---------------------------------------------------------------------------

def pick(pool: list[str], amount: int) -> list[str]:
    """Pick some different roles from a pool."""
    return random.sample(pool, amount)


def generate_roles(number_of_players: int) -> dict:
    """
    Generate a complete setup for a game.

    Returns a dict with:
        - "roles": the real role of every player
        - "drunk_shown_as": the Townsfolk the Drunk thinks they are (or None)
        - "bluffs": 3 good roles not in play, shown to the Demon
    """
    townsfolk, outsiders, minions, demons = SETUP_COUNTS[number_of_players]

    # Evil first, because the Baron changes the good counts.
    evil_roles = pick(DEMONS, demons) + pick(MINIONS, minions)

    if "Baron" in evil_roles:
        townsfolk -= 2
        outsiders += 2

    good_roles = pick(TOWNSFOLK, townsfolk) + pick(OUTSIDERS, outsiders)
    roles = good_roles + evil_roles

    # Roles nobody has. The Drunk's fake role and the bluffs come from here.
    not_in_play = [
        role for role in TOWNSFOLK + OUTSIDERS
        if role not in roles
    ]

    drunk_shown_as = None
    if "Drunk" in roles:
        fake_townsfolk = [role for role in not_in_play if role in TOWNSFOLK]
        drunk_shown_as = random.choice(fake_townsfolk)
        not_in_play.remove(drunk_shown_as)

    bluffs = pick(not_in_play, 3)

    return {
        "roles": roles,
        "drunk_shown_as": drunk_shown_as,
        "bluffs": bluffs,
    }


# ---------------------------------------------------------------------------
# Sorting and player numbers
# ---------------------------------------------------------------------------

def sort_roles(roles: list[str], night_order: list[str]) -> list[str]:
    """Sort roles according to a night order."""
    order = {
        role: index
        for index, role in enumerate(night_order)
    }

    return sorted(
        roles,
        key=lambda role: order.get(role, len(night_order)),
    )


def get_random_player_numbers(number_of_players: int) -> list[int]:
    """Return player numbers in a random order."""
    player_numbers = list(range(1, number_of_players + 1))
    random.shuffle(player_numbers)
    return player_numbers


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def display_setup(setup: dict, player_numbers: list[int]) -> None:
    """Display every player's role, plus the Drunk and the bluffs."""
    print("\n===== Grimoire =====")

    for player_number, role in zip(player_numbers, setup["roles"]):
        if role == "Drunk":
            print(f"{player_number} Drunk (thinks: {setup['drunk_shown_as']})")
        else:
            print(f"{player_number} {role}")

    print(f"\nDemon bluffs: {', '.join(setup['bluffs'])}")


def display_night(
    title: str,
    roles: list[str],
    night_order: list[str],
    number_of_players: int,
) -> None:
    """Display the roles that wake up, in night order."""
    print(f"\n===== {title} =====")

    for step in night_order:
        # Minion and Demon info only happen with 7+ players.
        if step.startswith("~"):
            if number_of_players >= 7:
                print(step)
        elif step in roles:
            print(step)


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------

def play_game() -> None:
    """Generate and display a game of Blood on the Clocktower."""
    while True:
        number_of_players = get_number_of_players()

        setup = generate_roles(number_of_players)
        player_numbers = get_random_player_numbers(number_of_players)

        # The Drunk wakes up as the role they think they are.
        waking_roles = setup["roles"] + [setup["drunk_shown_as"]]

        display_setup(setup, player_numbers)
        display_night(
            "First Night", waking_roles, FIRST_NIGHT_ORDER, number_of_players
        )
        display_night(
            "Other Nights", waking_roles, OTHER_NIGHTS_ORDER, number_of_players
        )

        play_again = input("\nReroll? Enter 'y' to play again: ")

        if play_again.lower() != "y":
            break


if __name__ == "__main__":
    play_game()
