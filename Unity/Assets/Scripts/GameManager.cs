using NUnit.Framework;
using UnityEngine;
using System.Collections.Generic;
using System.Collections;

public class GameManager : MonoBehaviour
{
    [System.Serializable]
    public class RolePrefabs
    {
        public GameObject rolePrefab;
        public Role role;
    }
    public enum GameState
    {
        Discussion,
        Voting,
        Night,
        SelectTarget,
    }
    public static GameState state;
    public static List<Player> players = new List<Player>();
    public static List<Role> roles = new List<Role>();
    public static Dictionary<Player, Role> roleDictionary = new Dictionary<Player, Role>();
    public static Dictionary<Player, Role> rolesAlive = new Dictionary<Player, Role>();
    public static Dictionary<Role, GameObject> roleGameObjectDictionary = new Dictionary<Role, GameObject>();

    public List<RolePrefabs> prefabs = new List<RolePrefabs>();

    public static Role activePlayer;
    string dayMessage = "";

    public Transform roleGridParent;

    public List<Player> testPlayers = new List<Player>();
    public List<Role> testRoles = new List<Role>();
    


    private void Start()
    {
        roles.AddRange(testRoles);
        players.AddRange(testPlayers);
        Debug.Log(roles.Count);
        for(int i = 0; i<roles.Count; i++)
        {
            roleDictionary.Add(players[i], roles[i]);
        }
        StartGame();
    }
    public void StartGame()
    {
        
        List<Role> tempRoles = new List<Role>(roles);
        roles.Clear();
        int roleCount = tempRoles.Count;
        Debug.Log("count: " + roleCount);
        for(int i = 0; i<roleCount; i++)
        {
            int rand = Random.Range(0, tempRoles.Count);
            Role roleAt = tempRoles[rand];
            roles.Add(roleAt);
            tempRoles.RemoveAt(rand);
            InstantiateRole(roleAt);
            Debug.Log(roles[i]);
        }
        for (int i = 0; i < players.Count; i++)
        {
            Debug.Log(i);
            roles[i].connectedPlayer = players[i];

            rolesAlive.Add(players[i], roles[i]);


        }


        state = GameState.Discussion;
    }

    private void InstantiateRole(Role role)
    {
        GameObject roleObject = Instantiate(prefabs.Find(x => x.role == role).rolePrefab, roleGridParent);
    }

    public IEnumerator NightLogic()
    {
        foreach(Role role in roles)
        {
            activePlayer = role;
            yield return role.NightAction();
        }
        yield return null;
    }

    public void CalculateNight()
    {
        dayMessage = "";
        foreach(var role in rolesAlive)
        {
            if (role.Value.ContainsStatusEffect(Role.StatusEffect.Dead))
            {
                RemoveRole(role.Value);
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
        rolesAlive.Remove(role.connectedPlayer);
    }

    public static List<Player> GetValidTargets(Role currentRole, bool includeSelf)
    {
        List<Player> validTargets = new List<Player>();

        foreach(var players in rolesAlive)
        {
            if (players.Value.playerVisited.Contains(players.Value))
            {
                continue;
            }
            if (!includeSelf && players.Key == currentRole.connectedPlayer)
            {
                continue;
            }
            validTargets.Add(players.Key);
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
