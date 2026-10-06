using NUnit.Framework;
using UnityEngine;
using System.Collections.Generic;
using System.Collections;

public class GameManager : MonoBehaviour
{
    public static Dictionary<Player, Role> roleDictionary = new Dictionary<Player, Role>();
    public static List<Player> players = new List<Player>();
    public static List<Role> roles = new List<Role>();
    public static Dictionary<Role, Player> rolesAlive = new Dictionary<Role, Player>();
    

    string dayMessage = "";


    public void StartGame(Dictionary<Player, Role> playerDict)
    {
        roleDictionary = playerDict;
        players = new List<Player>(playerDict.Keys);
        roles = new List<Role>(playerDict.Values);
        foreach(var players in roleDictionary)
        {
            rolesAlive.Add(players.Value, players.Key);
        }
        // Initialize each player's role
        foreach (var pair in playerDict)
        {
            Player player = pair.Key;
            Role role = pair.Value;
            role.connectedPlayer = player;
            role.UpdateEffects();
        }
    }

    public IEnumerator NightLogic()
    {
        foreach(Role role in roles)
        {
            yield return role.NightAction();
        }
        yield return null;
    }

    public void CalculateNight()
    {
        dayMessage = "";
        foreach(var role in rolesAlive)
        {
            if (role.Key.ContainsStatusEffect(Role.StatusEffect.Dead))
            {
                RemoveRole(role.Key);
            }
        }
    }

    private void AddToDayMessage(string text)
    {
        dayMessage += text + "\n";
    }


    private void RemoveRole(Role role)
    {
        AddToDayMessage(role.connectedPlayer.playerName + " has died.");
        rolesAlive.Remove(role);
    }

    public static List<Player> GetValidTargets()
    {
        List<Player> validTargets = new List<Player>();

        foreach(var players in rolesAlive)
        {
            validTargets.Add(players.Value);
        }
        return validTargets;
    }

    public static Role GetRoleFromPlayer(Player player)
    {
        if (roleDictionary.ContainsKey(player))
        {
            return roleDictionary[player];
        }
        return null;
    }
}
