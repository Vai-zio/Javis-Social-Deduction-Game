# Player Manual

This manual covers both games in the bot: **Town of Javis** and **Blood on the Clocktower**. For each game you'll find the goal, the teams, every role, how a round flows, and tips for playing well.

New to the bot commands? The short guides cover those: [Town of Javis](how-to-play-town-of-javis.md) and [Blood on the Clocktower](how-to-play-blood-on-the-clocktower.md).

**Contents**

1. [What a social deduction game is](#1-what-a-social-deduction-game-is)
2. [Town of Javis](#2-town-of-javis)
3. [Blood on the Clocktower](#3-blood-on-the-clocktower)
4. [Experimental roles (homebrew)](#4-experimental-roles-homebrew)
5. [General game sense](#5-general-game-sense)

---

## 1. What a social deduction game is

Everyone gets a secret role. A small **evil** team knows each other. The bigger **good** team doesn't know who anyone is. Evil kills at night; good tries to find evil by talking and voting during the day.

Good has the numbers. Evil has the information. The whole game is good trying to turn its numbers into information before evil runs out the clock.

Both games have a host who doesn't play: the **narrator** in Town of Javis and the **Storyteller** in Clocktower. The bot deals roles, sends DMs and counts votes. The host decides what actually happens at night.

---

## 2. Town of Javis

A Mafia game in the style of Town of Salem. 6 to 15 players. Start it with `/newgame` and pick **1**.

### Goal and win conditions

The bot checks for a winner after every death.

| Who | Wins when |
|---|---|
| **Town** | Every Mafia member and every killing neutral is dead. |
| **Mafia** | No killing neutral is left and the Mafia are at least half of the living players (they can now win every vote). |
| **Serial Killer / Arsonist** | They are alive with at most one other player. |
| **Jester** | They get voted out. The game goes on without them. |
| **Executioner** | Their target gets voted out. The game goes on. |
| **Survivor, Guardian Angel, Amnesiac, Cupid, Witch** | See their role below. |

### The teams

- **Town** is the majority. Nobody in Town knows anyone else's role.
- **Mafia** know each other from the start and talk in a private "Mafia hideout" thread.
- **Neutrals** play for themselves. Some are harmless, some want chaos, some want everyone dead.

### A round

1. **Night.** Every living player with a night ability gets a dropdown by DM and picks a target (or skips). The Witch picks two.
2. **Resolving.** The narrator gets all the choices sorted in the order they happen: **Control** (blocks, poison, frames) → **Killing** → **Buffs** (heals and protection) → **Information**. The narrator decides the results and tells players what they learned.
3. **Morning.** Anyone who died is announced, and **their role is revealed**.
4. **Day.** Everyone talks. Then the vote: if a majority picks the same person, they go on trial. Everyone votes **Guilty** or **Innocent**. More guilty than innocent and they die. A tie means they survive.
5. Repeat.

### How many of each role

Roles are dealt in "slots". For example 6 players get: 2 Town info, 1 Town support, 1 Mafia killing, 1 Mafia support, 1 Neutral. Bigger games add more of each. Below 9 players the Mafia killer is always the Mafioso, and killing neutrals only show up at 9+ players (and at most one per game).

### The roles

The narrator has the final say on details, like exactly what a role learns.

#### Town: Information
Your job is to find evil and share what you learn, at the right time.

| Role | What it does |
|---|---|
| **Sheriff** | Each night, check one player: you learn if they are suspicious (Mafia or a killer) or not. |
| **Seer** | Each night, look at one player and learn a clue about their role. |
| **Spy** | Learns what the Mafia are doing at night (who they visit or target). |
| **Tracker** | Each night, follow one player: you learn who they visited. |

#### Town: Killing
Strong but risky. Killing a Town player by mistake helps the Mafia.

| Role | What it does |
|---|---|
| **Jailor** | Each night, jail one player. They can't act tonight, and you may choose to execute them. |
| **Hunter** | Each night, you may shoot one player. |
| **Veteran** | Some nights, go on alert: anyone who visits you that night dies. |

#### Town: Support
Keep the Town alive and steer the vote.

| Role | What it does |
|---|---|
| **Doctor** | Each night, heal one player. If they're attacked, they survive. |
| **Priest** | Each night, bless one player to protect them. |
| **Guardian Angel** | You get a target. Keep them alive; you win if they do. |
| **Mayor** | Your vote counts for more. A strong voice, so evil wants you dead. |

#### Mafia: Killing
Every night the Mafia choose one player to kill.

| Role | What it does |
|---|---|
| **Godfather** | Leader of the Mafia. Makes the final call on who dies. |
| **Mafioso** | The Mafia's killer. Carries out the kill (and takes over if the Godfather dies). |

#### Mafia: Support
Break the Town's information and votes.

| Role | What it does |
|---|---|
| **Poisoner** | Each night, poison a player. They die later unless healed. |
| **Framer** | Each night, frame a player so they look guilty to Town investigators. |
| **Blackmailer** | Each night, pick a player who can't speak the next day. |
| **Consigliere** | Each night, learn one player's exact role. |

#### Neutral: Benign
Not here to hurt anyone.

| Role | What it does |
|---|---|
| **Amnesiac** | Once, pick a dead player and become their role. |
| **Cupid** | First night, link two players as **Lovebirds**. If one dies, so does the other. |
| **Survivor** | Just stay alive until the end. You win alongside whoever wins. |

#### Neutral: Evil
Win by fooling the Town.

| Role | What it does |
|---|---|
| **Jester** | Get yourself voted out. Act suspicious, but not too obvious. |
| **Executioner** | You get a Town player as your target. Get them voted out. |
| **Witch** | Each night, pick two players: you control the first and choose who they use their ability on. |

#### Neutral: Killing
Against everyone.

| Role | What it does |
|---|---|
| **Serial Killer** | Each night, kill one player. Win by being the last one standing. |
| **Arsonist** | Each night, douse a player in gas, or ignite everyone you've doused at once. |

---

## 3. Blood on the Clocktower

The **Trouble Brewing** script. 5 to 15 players. Start it with `/newgame` and pick **2**.

### What makes it different

- **Dead players keep playing.** They still talk and still help good win. Each gets **one ghost vote** for the rest of the game.
- **Roles stay secret when you die.** Nobody learns your character from your death.
- **Information can be wrong.** The Drunk and poisoned players get false info without knowing. The puzzle is "who is lying, and whose info is broken?"
- The **Storyteller** isn't a neutral referee. They pick what broken players see, and they try to keep the game close and fun.

### Goal and win conditions

| Who | Wins when |
|---|---|
| **Good** | The Demon dies (unless the Scarlet Woman takes over). |
| **Good** | Only 3 players are alive, one is the **Mayor**, and nobody is executed that day. |
| **Evil** | Only 2 players are alive. |
| **Evil** | The **Saint** is executed. |

### The teams

- **Good:** **Townsfolk** (helpful abilities) and **Outsiders** (abilities that get in good's way).
- **Evil:** **Minions** and one **Demon**, the Imp. Minions and the Demon know each other. The Demon also learns 3 **bluffs**: good characters that are *not* in play, safe to pretend to be.

### How many of each

| Players | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Townsfolk | 3 | 3 | 5 | 5 | 5 | 7 | 7 | 7 | 9 | 9 | 9 |
| Outsiders | 0 | 1 | 0 | 1 | 2 | 0 | 1 | 2 | 0 | 1 | 2 |
| Minions | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 3 | 3 | 3 |
| Demon | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

If the **Baron** is in play, 2 Townsfolk become 2 extra Outsiders.

### A round

1. **First night.** Evil learns who is evil. Info roles get their starting info.
2. **Day.** Talk openly, or whisper in private. Anyone can lie.
3. **Nominations.** A living player nominates someone. Everyone raises or lowers their hand. To go "on the block", a nominee needs votes from **at least half the living players** and **more votes** than whoever is on the block now. A tie means nobody is on it.
4. **Execution.** At the end of the day, whoever is on the block dies.
5. **Night.** The Demon kills, and other roles wake in order. Repeat.

Nomination rules: each living player may nominate once per day, and each player may be nominated once per day. Dead players can't nominate.

Example: 7 alive means 4 votes are needed. Alice gets 4, Bob also gets 4. That's a tie, so nobody is on the block unless someone gets 5.

### The characters

"Each night\*" means every night except the first.

#### Townsfolk (good)

| Character | Ability |
|---|---|
| **Washerwoman** | First night: you learn that 1 of 2 players is a particular Townsfolk. |
| **Librarian** | First night: you learn that 1 of 2 players is a particular Outsider (or that there are none). |
| **Investigator** | First night: you learn that 1 of 2 players is a particular Minion. |
| **Chef** | First night: you learn how many pairs of evil players sit next to each other. |
| **Empath** | Each night: you learn how many of your 2 alive neighbours are evil (0, 1 or 2). |
| **Fortune Teller** | Each night: choose 2 players, learn if either is the Demon. One good player is a "red herring" that also shows as the Demon. |
| **Undertaker** | Each night\*: you learn which character was executed today. |
| **Monk** | Each night\*: choose another player. They're safe from the Demon tonight. |
| **Ravenkeeper** | If you die at night, you wake and choose a player: you learn their character. |
| **Virgin** | The first time you're nominated, if the nominator is a Townsfolk, they're executed immediately. |
| **Slayer** | Once per game, during the day, publicly choose a player. If they're the Demon, they die. |
| **Soldier** | You can't be killed by the Demon. |
| **Mayor** | If only 3 players live and nobody is executed, good wins. If you die at night, another player might die instead. |

#### Outsiders (good, but hurt good)

| Character | Ability |
|---|---|
| **Butler** | Each night, choose a "master". Tomorrow you may only vote if they vote too. |
| **Drunk** | You think you're a Townsfolk, but you're not. Your ability does nothing, and your info may be wrong. You never find out. |
| **Recluse** | You might show up as evil, a Minion or the Demon to other abilities, even though you're good. |
| **Saint** | If you're executed, your team loses. |

#### Minions (evil)

| Character | Ability |
|---|---|
| **Poisoner** | Each night, poison a player. Their ability stops working until the next night, and their info may be wrong. |
| **Spy** | Each night, you see the Grimoire (every character). You might show up as good to other abilities. |
| **Scarlet Woman** | If the Demon dies while 5 or more players are alive, you become the Demon. |
| **Baron** | Setup change: there are 2 extra Outsiders in play. |

#### Demon (evil)

| Character | Ability |
|---|---|
| **Imp** | Each night\*, choose a player: they die. If you choose yourself, you die and a Minion becomes the new Imp (the "star pass"). |

---

## 4. Experimental roles (homebrew)

> These are our own custom roles from `experimental_roles.py`. **They are not dealt by the bot yet.** A Storyteller can add them by hand for a test game.

Many of them use **seating**: who sits next to whom. That fits the Discord table picture well.

#### Townsfolk

| Character | Ability | How it plays |
|---|---|---|
| **Truth Speaker** | Each night, you learn 2 statements: 1 true and 1 false. | You never know which one is true, so you compare with others. |
| **Team Watcher** | Each night, choose a player: learn if they're the same character type as both alive neighbours. | Great for spotting evil sitting together. |
| **Pair Seer** | Each night, choose 2 players: learn if they're on the same team. | Builds chains of trust ("A and B are on the same side"). |
| **Shieldbearer** | Each night\*, choose an alive neighbour: if the Demon chooses them, you die instead. | A Monk that sacrifices itself. Where you sit matters. |
| **Tally Clerk** | Each night, learn how many evil players voted today. | Turns votes into clues. Evil has to think before raising a hand. |
| **Bellringer** | Once per game, at night, choose a character type: learn how many of that type are alive. | Strong late ("2 Minions still alive?!"), weak early. |

#### Outsiders

| Character | Ability | How it plays |
|---|---|---|
| **Doubter** | You think you're the Truth Speaker, but both your statements are false. | The Truth Speaker's Drunk. |
| **Lightning Rod** | If the Demon chooses one of your alive neighbours, you die instead. | Protects neighbours, but good loses you early. |
| **Twin** | You start knowing 1 good player. If they die, you die that night. | A confirmed friend, but the Demon gets 2 kills for 1. |

#### Minions

| Character | Ability | How it plays |
|---|---|---|
| **Forger** | Each night, choose a player: if their ability gives info tonight, true becomes false and false becomes true. | Flips info so it's exactly wrong, which smart players can sometimes reverse. |
| **Saboteur** | Each night, choose a player: tomorrow their vote doesn't count. | Quietly flips close executions. |
| **Impersonator** | Each night, choose a Townsfolk not in play: you register as it until tomorrow night. | A Spy-like bluffer that fools info roles. |

#### Demons

| Character | Ability | How it plays |
|---|---|---|
| **Shade** | Each night\*, choose a player: they die. If you're executed while a neighbour is a Minion, that Minion becomes the Shade. | Evil wants to sit together; seating info roles shine. |
| **Rot** | Each night\*, choose a player: they die. Your alive neighbours register as evil. | Frames innocent neighbours. |

---

## 5. General game sense

### For everyone

- **Talk.** Silence is suspicious, and a quiet good player is wasted. Good wins by sharing info.
- **Track claims.** Write down who said what. Lies fall apart when two stories can't both be true.
- **Watch votes.** Who voted for whom, and who changed their vote late, says a lot.
- **Don't tunnel.** Pick a suspect, but update when new info comes in.
- **Think about why.** Ask "why would evil do that?" and "why would good do that?" The answer that makes more sense is usually right.

### Playing good

- **Info roles:** decide when to reveal. Early reveals help the town but make you a target. Sometimes it's worth sharing your info without your role.
- **Protectors:** don't protect the same person every night in a pattern evil can read.
- **Check for broken info** (Clocktower). If your info clashes with everyone else's, you might be Drunk or poisoned.
- **Dead players matter** (Clocktower). Save your ghost vote for the final, important execution.

### Playing evil

- **Have a story ready.** Pick a role to claim before the day starts. In Clocktower, use your 3 bluffs.
- **Blend in.** Vote like a good player would. Don't defend your teammates too hard.
- **Kill smart.** Take out confirmed info roles and protectors, not random players.
- **Sow doubt.** You don't need to be believed, you just need good to stop trusting each other.

### Playing neutral (Town of Javis)

- **Jester:** be suspicious, but leave doubt. If you're too obvious, no one votes you.
- **Executioner:** build a case against your target slowly. Don't look desperate.
- **Killers:** let Town and Mafia fight each other, and clean up at the end.
