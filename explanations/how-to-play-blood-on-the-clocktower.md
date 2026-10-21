# How to play Blood on the Clocktower

This is the Trouble Brewing script. One person is the **Storyteller**. Everyone else gets a secret character. All commands start with `/botc`.

## How it's different from Mafia

- **Dead players keep playing.** They still talk, and they get one last vote.
- **Information can be wrong.** The Drunk and poisoned players get false info without knowing. So the puzzle is "who is lying, and whose info is broken?".
- The Storyteller isn't a neutral referee. They choose what drunk or poisoned players see, and try to keep the game close.

## The teams

- **Good:** Townsfolk (useful abilities) and Outsiders (abilities that hurt good).
- **Evil:** Minions and one Demon, the Imp. The Demon learns 3 "bluffs", good characters not in play, so it can pretend to be one.

## A round

1. **Night.** `/botc night` shows the Storyteller the wake order. The Storyteller wakes characters one by one: `/botc ask` sends a player a dropdown to choose players, and `/botc tell` DMs them what they learn. Anyone who dies gets `/botc kill seat`. Their character stays secret.
2. **Day.** `/botc day` opens nominations. People talk, whisper and lie.
3. **Nominations.** A living player uses `/botc nominate seat`. Everyone clicks **Raise / lower hand**, and the Storyteller clicks **Close vote**.
4. `/botc execute` ends the day and executes whoever is on the block.

## Voting rules

- Only living players nominate, once each per day. Each player can be nominated once per day.
- Dead players have **one ghost vote** for the rest of the game.
- To go on the block, a nominee needs votes from at least **half the living players**, and **more** votes than whoever is on it now. A tie means nobody.

Example: 7 alive, so 4 votes are needed. Alice gets 4. Bob gets 4 too, a tie, so nobody is on the block unless someone else gets 5.

## Who wins

- **Good** wins when the Demon dies (unless the Scarlet Woman takes over).
- **Evil** wins when only 2 players are alive.
- **Evil** wins if the **Saint** is executed.
- **Good** wins if 3 players are alive, the **Mayor** is one of them, and nobody is executed that day.

The Storyteller ends it with `/botc endgame winner`, which reveals everyone.

## Setup

`SETUP_COUNTS` in `botc_roles.py` says how many of each type each player count gets (5 to 15). Two characters change the setup, and `botc.py` handles both:

- **Baron:** 2 Townsfolk are swapped for 2 Outsiders.
- **Drunk:** the player is told a Townsfolk character that is not in play, and never learns the truth.

Try `/botc test` to roll a fake game.

## The characters

| Type | Role | What it does (short) |
|---|---|---|
| Townsfolk | Washerwoman | Night 1: learns 1 of 2 players is a specific Townsfolk |
| | Librarian | Night 1: same, but for an Outsider (or "none in play") |
| | Investigator | Night 1: same, but for a Minion |
| | Chef | Night 1: learns how many pairs of evil players sit next to each other |
| | Empath | Each night: how many of their 2 alive neighbours are evil (0, 1, 2) |
| | Fortune Teller | Each night: picks 2 players, learns "yes" if either is the Demon. One good player is a "red herring" that also reads "yes" |
| | Undertaker | Each night (not 1st): learns the role of today's executed player |
| | Monk | Each night (not 1st): protects one other player from the Demon |
| | Ravenkeeper | If killed at night: picks a player and learns their role |
| | Virgin | First time nominated: if the nominator is a Townsfolk, the nominator is executed instantly |
| | Slayer | Once per game, by day: publicly shoots a player. If it's the Demon, it dies |
| | Soldier | Safe from the Demon |
| | Mayor | If 3 players are alive and no one is executed, good wins. If killed at night, the Storyteller may make someone else die instead |
| Outsider | Butler | Each night picks a "master"; can only vote if the master votes |
| | Drunk | Thinks they're a Townsfolk, but isn't. Their ability does nothing and their info can be wrong |
| | Recluse | May "register" as evil, a Minion or a Demon to other abilities |
| | Saint | If executed, **evil wins** |
| Minion | Poisoner | Each night poisons one player: their ability stops working until next dusk (info can be wrong) |
| | Spy | Sees the whole Grimoire each night. May register as good |
| | Scarlet Woman | If the Demon dies while 5+ players are alive, she becomes the Demon |
| | Baron | Setup change: +2 Outsiders (and 2 fewer Townsfolk) |
| Demon | Imp | Each night (not 1st) kills one player. Can kill itself: then a Minion becomes the new Imp ("star pass") |
