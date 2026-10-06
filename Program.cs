using System;
using System.Collections.Generic;
using System.Linq;

// ---------- ENUMS: the "vocabulary" of the game ----------
enum Faction  { Town, Mafia, Coven, Neutral }

enum Category
{
    TownInvestigative, TownProtective, TownKilling, TownSupport,
    MafiaKilling, MafiaDeception, MafiaSupport,
    CovenEvil,
    NeutralBenign, NeutralEvil, NeutralKilling, NeutralChaos
}

enum GameMode { Classic = 1, Coven = 2 }

enum Role
{
    // Town
    Investigator, Lookout, Psychic, Sheriff, Spy, Tracker,
    Bodyguard, Crusader, Doctor, Trapper,
    Jailor, VampireHunter, Veteran, Vigilante,
    Escort, Mayor, Medium, Retributionist, Transporter,
    // Mafia
    Godfather, Mafioso, Ambusher,
    Disguiser, Forger, Framer, Hypnotist, Janitor,
    Blackmailer, Consigliere, Consort,
    // Coven
    CovenLeader, HexMaster, Medusa, Necromancer, Poisoner, PotionMaster,
    // Neutral
    Amnesiac, GuardianAngel, Survivor,
    Executioner, Jester, Witch,
    Arsonist, Juggernaut, SerialKiller, Werewolf,
    Pirate, Plaguebearer, Vampire
}

class Program
{
    static Random rng = new Random();
    static GameMode mode;
    static List<Role> used = new List<Role>();

    // ---------- DATA: which category each role belongs to ----------
    static Dictionary<Role, Category> categoryOf = new Dictionary<Role, Category>();

    static void Add(Category c, params Role[] roles)
    {
        foreach (var r in roles) categoryOf[r] = c;
    }

    // A static constructor runs once, before Main. It fills the dictionary.
    static Program()
    {
        Add(Category.TownInvestigative, Role.Investigator, Role.Lookout, Role.Psychic, Role.Sheriff, Role.Spy, Role.Tracker);
        Add(Category.TownProtective,    Role.Bodyguard, Role.Crusader, Role.Doctor, Role.Trapper);
        Add(Category.TownKilling,       Role.Jailor, Role.VampireHunter, Role.Veteran, Role.Vigilante);
        Add(Category.TownSupport,       Role.Escort, Role.Mayor, Role.Medium, Role.Retributionist, Role.Transporter);
        Add(Category.MafiaKilling,      Role.Godfather, Role.Mafioso, Role.Ambusher);
        Add(Category.MafiaDeception,    Role.Disguiser, Role.Forger, Role.Framer, Role.Hypnotist, Role.Janitor);
        Add(Category.MafiaSupport,      Role.Blackmailer, Role.Consigliere, Role.Consort);
        Add(Category.CovenEvil,         Role.CovenLeader, Role.HexMaster, Role.Medusa, Role.Necromancer, Role.Poisoner, Role.PotionMaster);
        Add(Category.NeutralBenign,     Role.Amnesiac, Role.GuardianAngel, Role.Survivor);
        Add(Category.NeutralEvil,       Role.Executioner, Role.Jester, Role.Witch);
        Add(Category.NeutralKilling,    Role.Arsonist, Role.Juggernaut, Role.SerialKiller, Role.Werewolf);
        Add(Category.NeutralChaos,      Role.Pirate, Role.Plaguebearer, Role.Vampire);
    }

    // Roles that can only appear once per game.
    static readonly HashSet<Role> Unique = new HashSet<Role>
    {
        Role.Jailor, Role.Mayor, Role.Retributionist, Role.Veteran,
        Role.Godfather, Role.Mafioso, Role.Ambusher,
        Role.Werewolf, Role.Juggernaut, Role.Pirate, Role.Plaguebearer,
        Role.CovenLeader, Role.HexMaster, Role.Medusa, Role.Necromancer, Role.Poisoner, Role.PotionMaster
    };

    // Roles added in the Coven expansion. Classic mode ignores them.
    static readonly HashSet<Role> ExpansionRoles = new HashSet<Role>
    {
        Role.Psychic, Role.Tracker, Role.Crusader, Role.Trapper, Role.Ambusher,
        Role.Hypnotist, Role.GuardianAngel, Role.Juggernaut, Role.Pirate, Role.Plaguebearer
    };

    // Team sizes as fractions of the player count. Change these to rebalance.
    const double EvilShare    = 0.33;
    const double NeutralShare = 0.10;
    const double InfoShare    = 0.20;   // Town information roles (Sheriff, Spy, Investigator...)

    // ---------- RULES ----------
    static Faction FactionOf(Role r) => categoryOf[r] switch
    {
        Category.TownInvestigative or Category.TownProtective
            or Category.TownKilling or Category.TownSupport => Faction.Town,
        Category.MafiaKilling or Category.MafiaDeception or Category.MafiaSupport => Faction.Mafia,
        Category.CovenEvil => Faction.Coven,
        _ => Faction.Neutral
    };

    // In Coven mode the Coven replaces the Mafia.
    static Faction EvilFaction => mode == GameMode.Coven ? Faction.Coven : Faction.Mafia;

    // The game mode filter: returns false for roles that should be ignored.
    static bool Allowed(Role r)
    {
        Faction f = FactionOf(r);
        if ((f == Faction.Mafia || f == Faction.Coven) && f != EvilFaction) return false;
        if (mode == GameMode.Classic && ExpansionRoles.Contains(r)) return false;
        if (mode == GameMode.Coven && r == Role.Witch) return false;   // Coven replaces the Witch
        if (Unique.Contains(r) && used.Contains(r)) return false;
        return true;
    }

    // Pick a random allowed role that matches a condition ("fits").
    static Role Pick(Func<Role, bool> fits)
    {
        var options = categoryOf.Keys.Where(r => Allowed(r) && fits(r)).ToList();
        if (options.Count == 0)   // safety net: fall back to any Town role
            options = categoryOf.Keys.Where(r => Allowed(r) && FactionOf(r) == Faction.Town).ToList();
        return options[rng.Next(options.Count)];
    }

    // Round to the nearest whole player (0.5 rounds up, not to the nearest even number).
    static int Share(int players, double share) =>
        (int)Math.Round(players * share, MidpointRounding.AwayFromZero);

    // ---------- PROGRAM ----------
    static void Main()
    {
        Console.WriteLine("Choose game mode:");
        Console.WriteLine("1 - Classic  (original roles, Mafia)");
        Console.WriteLine("2 - Coven    (all roles, Coven replaces Mafia)");
        Console.Write("> ");
        if (!int.TryParse(Console.ReadLine(), out int m) || !Enum.IsDefined(typeof(GameMode), m))
        {
            Console.WriteLine("Pick 1 or 2.");
            return;
        }
        mode = (GameMode)m;   // casting a number to an enum

        Console.Write("Number of players (5-15): ");
        if (!int.TryParse(Console.ReadLine(), out int players) || players < 5 || players > 15)
        {
            Console.WriteLine("Please enter a number from 5 to 15.");
            return;
        }

        // 1) Work out team sizes from the percentages
        int evilCount    = Math.Max(1, Share(players, EvilShare));   // always at least 1 evil
        int neutralCount = Share(players, NeutralShare);
        int townCount    = players - evilCount - neutralCount;       // town gets the rest
        int infoCount    = Math.Clamp(Share(players, InfoShare), 1, townCount); // at least 1, never more than Town

        // 2) Guaranteed killing roles: Mafioso always, Godfather too if 3+ Mafia
        //    (in Coven mode: Medusa always, Coven Leader too if 3+ Coven)
        Role killer = mode == GameMode.Coven ? Role.Medusa      : Role.Mafioso;
        Role leader = mode == GameMode.Coven ? Role.CovenLeader : Role.Godfather;
        used.Add(killer);
        if (evilCount >= 3) used.Add(leader);

        // 3) Fill the remaining spots with fully random roles from each faction.
        //    The leader is never picked at random: it was either added above,
        //    or the team is too small to have one.
        while (used.Count < evilCount)         used.Add(Pick(r => FactionOf(r) == EvilFaction && r != leader));
        for (int i = 0; i < neutralCount; i++) used.Add(Pick(r => FactionOf(r) == Faction.Neutral));

        // 4) Town: first the information roles, then the rest from the other Town categories
        for (int i = 0; i < infoCount; i++)
            used.Add(Pick(r => categoryOf[r] == Category.TownInvestigative));
        for (int i = 0; i < townCount - infoCount; i++)
            used.Add(Pick(r => FactionOf(r) == Faction.Town && categoryOf[r] != Category.TownInvestigative));

        Console.WriteLine($"\n=== {mode}: {evilCount} {EvilFaction}, {neutralCount} Neutral, {townCount} Town ({infoCount} info) ===");

        List<Role> roles = new List<Role>(used);
        Shuffle(roles);

        Console.WriteLine("\n=== Players ===");
        Console.WriteLine("Guide: * dead, D dying, + safe, P poisoned, F framed, T tracked\n");
        for (int i = 0; i < roles.Count; i++)
            Console.WriteLine($"{i + 1,2} - {roles[i],-15} ({categoryOf[roles[i]]})");

        // Executioner: target is a Town player, but never the Jailor
        PrintTarget(roles, Role.Executioner,
            i => FactionOf(roles[i]) == Faction.Town && roles[i] != Role.Jailor);
        // Guardian Angel: target is anyone except the Guardian Angel itself
        PrintTarget(roles, Role.GuardianAngel, i => roles[i] != Role.GuardianAngel);
    }

    static void PrintTarget(List<Role> roles, Role who, Func<int, bool> valid)
    {
        int seat = roles.IndexOf(who);
        if (seat < 0) return;
        var options = Enumerable.Range(0, roles.Count).Where(i => i != seat && valid(i)).ToList();
        if (options.Count == 0) return;
        int target = options[rng.Next(options.Count)];
        Console.WriteLine($"\n{who} (player {seat + 1}) target: player {target + 1}");
    }

    // Fisher-Yates shuffle
    static void Shuffle<T>(List<T> list)
    {
        for (int i = list.Count - 1; i > 0; i--)
        {
            int j = rng.Next(i + 1);
            (list[i], list[j]) = (list[j], list[i]);
        }
    }
}