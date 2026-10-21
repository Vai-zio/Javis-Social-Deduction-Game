import pytest

from TownOfJavis2 import ROLE_SLOTS, check_winner, generate_roles
from botc import generate_roles as botc_generate_roles


# check_winner: no randomness, so we can check exact answers.

def test_town_wins_when_no_killers_left():
    assert check_winner(["Sheriff", "Doctor"]) == "Town"


def test_mafia_wins_at_half_the_table():
    assert check_winner(["Mafioso", "Sheriff"]) == "Mafia"


def test_nobody_wins_yet():
    assert check_winner(["Mafioso", "Sheriff", "Doctor"]) is None


# generate_roles is random, so we check rules that must ALWAYS hold,
# for every player count, many times.

@pytest.mark.parametrize("players", sorted(ROLE_SLOTS))
def test_one_role_per_player(players):
    for _ in range(200):
        assert len(generate_roles(players)) == players


@pytest.mark.parametrize("players", range(5, 16))
def test_botc_baron_adds_two_outsiders(players):
    from botc_roles import OUTSIDERS, SETUP_COUNTS
    for _ in range(200):
        setup = botc_generate_roles(players)
        outsiders = sum(1 for r in setup["roles"] if r in OUTSIDERS)
        expected = SETUP_COUNTS[players][1]
        if "Baron" in setup["roles"]:
            expected += 2
        assert outsiders == expected
        assert len(setup["roles"]) == players
        assert not set(setup["bluffs"]) & set(setup["roles"])


def test_killing_neutral_wins_alone_with_one_player():
    assert check_winner(["Serial Killer", "Sheriff"]) == "Serial Killer"


# alive_neighbours: dead players are skipped, and the table wraps around.

def test_neighbours_skip_the_dead_and_wrap_around():
    from table_view import alive_neighbours
    players = [
        {"alive": True},   # seat 0
        {"alive": False},  # seat 1 (dead)
        {"alive": True},   # seat 2
        {"alive": True},   # seat 3
    ]
    # Seat 0's left is seat 3 (wraps), its right skips dead seat 1.
    assert alive_neighbours(players, 0) == (3, 2)
