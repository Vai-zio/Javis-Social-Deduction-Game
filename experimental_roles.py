import random

from botc_roles import TOWNSFOLK, OUTSIDERS, MINIONS, DEMONS
from characters import Character


# ---------------------------------------------------------------------------
# Experimental homebrew roles
# Not wired into botc.py or bot.py yet. Run this file to see example info.
# ---------------------------------------------------------------------------

def character_type(role: str) -> str:
    """Return a role's type: Townsfolk, Outsider, Minion or Demon."""
    if role in TOWNSFOLK or role in EXPERIMENTAL_TOWNSFOLK:
        return "Townsfolk"
    if role in OUTSIDERS or role in EXPERIMENTAL_OUTSIDERS:
        return "Outsider"
    if role in MINIONS or role in EXPERIMENTAL_MINIONS:
        return "Minion"
    return "Demon"


def alive_neighbours(seats: list[str], dead: set[int], i: int) -> tuple[int, int]:
    """Closest alive seat to the left and right of seat i (skips the dead)."""
    n = len(seats)

    left = (i - 1) % n
    while left in dead:
        left = (left - 1) % n

    right = (i + 1) % n
    while right in dead:
        right = (right + 1) % n

    return left, right


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

class TruthSpeaker(Character):
    name = "Truth Speaker"
    category = "Townsfolk"
    ability = "Each night, you learn 2 statements: 1 is true and 1 is false."
    triggers = "Each night"


class TeamWatcher(Character):
    name = "Team Watcher"
    category = "Townsfolk"
    ability = (
        "Each night, choose a player: you learn if they are the same "
        "character type as both of their alive neighbours."
    )
    triggers = "Each night"


# Ideas in the same spirit (see the thread for how they play)
class PairSeer(Character):
    name = "Pair Seer"
    category = "Townsfolk"
    ability = "Each night, choose 2 players: you learn if they are on the same team."
    triggers = "Each night"


class Doubter(Character):
    # No name, so __init_subclass__ sets it to "Doubter"
    category = "Outsider"
    ability = (
        "You think you are the Truth Speaker, but both of your "
        "statements are false."
    )
    triggers = "Each night"


class Forger(Character):
    category = "Minion"
    ability = (
        "Each night, choose a player: if their ability gives them "
        "information tonight, true becomes false and false becomes true."
    )
    triggers = "Each night"


# --- Batch 2 ---------------------------------------------------------------
# Each role has a short note on how it plays.

class Shieldbearer(Character):
    category = "Townsfolk"
    ability = (
        "Each night*, choose an alive neighbour: if the Demon chooses them "
        "tonight, you die instead."
    )
    triggers = "Each night except the first"
    # Plays: a Monk that sacrifices itself. Uses seating, so where you sit matters.


class TallyClerk(Character):
    name = "Tally Clerk"
    category = "Townsfolk"
    ability = "Each night, you learn how many evil players voted today."
    triggers = "Each night"
    # Plays: turns /vote into clues. Evil must think about every hand they raise.


class Bellringer(Character):
    category = "Townsfolk"
    ability = (
        "Once per game, at night, choose a character type: you learn how "
        "many players of that type are alive."
    )
    triggers = "Once per game"
    # Plays: great late game ("2 Minions still alive?!"). Weak if used early.


class LightningRod(Character):
    name = "Lightning Rod"
    category = "Outsider"
    ability = "If the Demon chooses one of your alive neighbours, you die instead."
    triggers = "Passive"
    # Plays: you protect neighbours, but good loses its Outsider early.


class Twin(Character):
    category = "Outsider"
    ability = "You start knowing 1 good player. If they die, you die tonight."
    triggers = "First night"
    # Plays: a confirmed good friend, but the Demon gets 2 kills for 1.


class Saboteur(Character):
    category = "Minion"
    ability = "Each night, choose a player: tomorrow, their vote does not count."
    triggers = "Each night"
    # Plays: quietly flips close executions. Good players notice odd vote counts.


class Impersonator(Character):
    category = "Minion"
    ability = (
        "Each night, choose a Townsfolk not in play: you register as that "
        "character until tomorrow night."
    )
    triggers = "Each night"
    # Plays: a Spy-like bluffer. Breaks info roles like Team Watcher on purpose.


class Shade(Character):
    category = "Demon"
    ability = (
        "Each night*, choose a player: they die. If you are executed while "
        "a neighbour is a Minion, that Minion becomes the Shade."
    )
    triggers = "Each night except the first"
    # Plays: evil wants to sit next to each other. Seating info roles shine here.


class Rot(Character):
    category = "Demon"
    ability = "Each night*, choose a player: they die. Your alive neighbours register as evil."
    triggers = "Each night except the first"
    # Plays: framing. Pair Seer and Team Watcher point at innocent neighbours.


# Every experimental role. The name lists below are built from it,
# so a new role only has to be added here.
EXPERIMENTAL_ROLES = [
    TruthSpeaker, TeamWatcher, PairSeer, Doubter, Forger,
    Shieldbearer, TallyClerk, Bellringer, LightningRod, Twin,
    Saboteur, Impersonator, Shade, Rot,
]


def names_in(category: str) -> list[str]:
    """Names of the experimental roles in one category."""
    return [role.name for role in EXPERIMENTAL_ROLES if role.category == category]


EXPERIMENTAL_TOWNSFOLK = names_in("Townsfolk")
EXPERIMENTAL_OUTSIDERS = names_in("Outsider")
EXPERIMENTAL_MINIONS = names_in("Minion")
EXPERIMENTAL_DEMONS = names_in("Demon")


# ---------------------------------------------------------------------------
# Truth Speaker
# ---------------------------------------------------------------------------

def all_statements(seats: list[str], dead: set[int], me: int) -> list[tuple[str, bool]]:
    """
    Every statement the Storyteller could say, paired with whether it is true.
    The trick: build each statement from a real fact, so the truth is
    computed, not guessed.
    """
    statements = []

    # "X is in play" for a few interesting roles.
    for role in ["Baron", "Drunk", "Scarlet Woman", "Saint", "Poisoner"]:
        statements.append((f"The {role} is in play.", role in seats))

    # "Your left/right neighbour is an Outsider/Minion."
    left, right = alive_neighbours(seats, dead, me)
    for side, seat in [("left", left), ("right", right)]:
        for kind in ["Outsider", "Minion"]:
            is_true = character_type(seats[seat]) == kind
            statements.append((f"Your {side} neighbour is a {kind}.", is_true))

    # "There are exactly N Outsiders."
    outsiders = sum(1 for role in seats if character_type(role) == "Outsider")
    guess = random.choice([outsiders, outsiders + 1, max(0, outsiders - 1)])
    statements.append((f"There are exactly {guess} Outsiders.", guess == outsiders))

    return statements


def truth_speaker_info(seats: list[str], dead: set[int], me: int, broken: bool = False) -> list[str]:
    """
    Pick 1 true and 1 false statement, in random order.
    broken = drunk, poisoned or the Doubter: give 2 false ones instead.
    """
    statements = all_statements(seats, dead, me)
    true_ones = [text for text, is_true in statements if is_true]
    false_ones = [text for text, is_true in statements if not is_true]

    if broken:
        info = random.sample(false_ones, 2)
    else:
        info = [random.choice(true_ones), random.choice(false_ones)]

    random.shuffle(info)
    return info


# ---------------------------------------------------------------------------
# Team Watcher
# ---------------------------------------------------------------------------

def team_watcher_info(seats: list[str], dead: set[int], target: int) -> bool:
    """True if the target has the same type as both alive neighbours."""
    left, right = alive_neighbours(seats, dead, target)
    my_type = character_type(seats[target])
    return character_type(seats[left]) == my_type == character_type(seats[right])


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    seats = ["Truth Speaker", "Empath", "Baron", "Imp", "Saint", "Chef", "Team Watcher"]
    dead = {5}  # the Chef is dead

    print("Seats:", seats, "| dead:", [seats[i] for i in dead])
    print("Truth Speaker learns:", truth_speaker_info(seats, dead, me=0))
    print("Team Watcher picks the Empath:", team_watcher_info(seats, dead, target=1))
    print("Team Watcher picks the Imp:", team_watcher_info(seats, dead, target=3))

    print("\nAll experimental roles:")
    for role in EXPERIMENTAL_ROLES:
        role().printinfo()

    # One player's Doubter, who has died and used their dead vote
    doubter = Doubter(state="dead", deadvote=False)
    doubter.printinfo()
