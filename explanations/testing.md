# How the tests work

## What a test is

A test is a tiny function that runs your code and checks the answer.

```python
def test_town_wins_when_no_killers_left():
    assert check_winner(["Sheriff", "Doctor"]) == "Town"
```

`assert` means "this must be true". If it isn't, the test fails and points at the line. A tool called **pytest** finds every function starting with `test_` in files named `test_*.py` and runs them all in under a second.

Why bother: when you add a role or change a rule, you run the tests and instantly see if you broke something, instead of starting a Discord game to find out.

## Test the game, not Discord

The game files (`TownOfJavis2.py`, `botc.py`, `table_view.py`) take a list and give a list back, so they're easy to test. The Cogs talk to Discord, and testing them needs a fake Discord, which is a lot of work for little gain. So keep the rules in the game files, and keep the Cogs thin.

## Testing random code

`generate_roles` is random, so there's no single right answer to check. Instead, check rules that must **always** be true, and run it many times:

```python
@pytest.mark.parametrize("players", range(5, 16))
def test_botc_baron_adds_two_outsiders(players):
    for _ in range(200):
        setup = botc_generate_roles(players)
        assert len(setup["roles"]) == players
```

`parametrize` runs the test once for each player count (5 to 15). The loop rolls 200 games for each. If even one breaks the rule, pytest tells you which player count.

## Running them

In the terminal, from the project folder:

```
pip install -r requirements.txt
python -m pytest
```

In Rider: right-click the `tests` folder and choose **Run 'pytest in tests'**. Green means pass, red means fail.

To see a failure on purpose, change `"Town"` to `"Mafia"` in the first test and run it again. Reading one failure message makes the rest click.

## Good tests to add next

- `sort_roles`: roles come out in night order.
- Drunk: the fake Townsfolk is never a character in play.
- When you add a new role: one test for its special rule.
- Saving: a `Game` written to JSON and read back is the same game.
