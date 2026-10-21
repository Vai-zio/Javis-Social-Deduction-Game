# How to play Town of Javis

Town of Javis is a Mafia game like Town of Salem. One person is the **narrator** and runs the game. Everyone else gets a secret role.

## The teams

- **Town** wants to find and kill every killer.
- **Mafia** knows each other (they share a private "Mafia hideout" thread) and wants to take over the town.
- **Neutrals** each have their own goal.

## A round

1. **Night.** The narrator types `/night`. Every living player with a night ability gets a dropdown by DM and picks a target. The narrator gets one summary once everyone has chosen.
2. The narrator decides what happens. The summary is already sorted in the order things resolve: blocks first, then protections, then kills, then information. So a Doctor's heal is in place before the Mafia's kill lands.
3. **Morning.** The narrator uses `/kill seat` for anyone who died. Their role is revealed.
4. **Day.** Everyone talks and accuses. Then the narrator opens `/vote`. If a majority picks the same person, they go on trial and everyone votes **Guilty** or **Innocent**.
5. Repeat until someone wins.

## Who wins

The bot checks this after every death (`check_winner` in `TownOfJavis2.py`):

- **Town** wins when every Mafia member and every killing neutral is dead.
- **Mafia** wins when no killing neutral is left and the Mafia are at least half of the living players, because then they win every vote.
- A **killing neutral** (Serial Killer, Arsonist) wins when it is alone with at most one other player.
- **Jester** wins by getting voted out. **Executioner** wins if their target gets voted out. The game keeps going after that.

## The roles

| Team | Role | What it does (short) |
|---|---|---|
| Town info | Sheriff, Seer, Spy, Tracker | Learn things about other players at night |
| Town killing | Jailor, Hunter, Veteran | Can kill, but a wrong kill hurts the Town |
| Town support | Doctor, Priest, Guardian Angel, Mayor | Protect players or help the vote |
| Mafia killing | Godfather, Mafioso | Choose who the Mafia kills |
| Mafia support | Poisoner, Framer, Blackmailer, Consigliere | Mess with the Town's information and votes |
| Neutral benign | Amnesiac, Cupid, Survivor | Just want to survive, or help others |
| Neutral evil | Jester, Executioner, Witch | Win by tricking the Town |
| Neutral killing | Serial Killer, Arsonist | Win by being the last one standing |

The narrator is the referee for the details, like what exactly a role learns.

## How many of each

`ROLE_SLOTS` in `TownOfJavis2.py` lists a setup for each player count from 6 to 15. For example, 6 players get 2 Town info, 1 Town support, 1 Mafia killing, 1 Mafia support and 1 Neutral. Change that list to rebalance the game. `/stats` shows how often each side wins so you can tell if it needs it.

Try `/gametest` to roll a fake game and see a setup without real players. Add a number, like `/gametest players:9`, to see the roles for that many players.
