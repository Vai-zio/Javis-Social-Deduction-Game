using JetBrains.Annotations;
using NUnit.Framework;
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    [System.Serializable]
    public class RolePrefabs
    {
        public GameObject rolePrefab;
        public Role role;
    }
    [Serializable]
    public enum GameState
    {
        Discussion,
        Voting,
        NightStart,
        Night,
        SelectTarget,
    }
    public static GameState state;
    public GameState gameState;
    public static List<Player> players = new List<Player>();
    public static List<Role> roles = new List<Role>();
    public static Dictionary<Player, Role> roleDictionary = new Dictionary<Player, Role>();
    public static Dictionary<Player, Role> rolesAlive = new Dictionary<Player, Role>();
    public static Dictionary<Role, GameObject> roleGameObjectDictionary = new Dictionary<Role, GameObject>();

    public static GameManager instance;

    public List<RolePrefabs> prefabs = new List<RolePrefabs>();

    public static Role activePlayer;
    public Role _activePlayer;
    string dayMessage = "";

    public Transform roleGridParent;

    public List<Player> testPlayers = new List<Player>();
    public List<Role> testRoles = new List<Role>();

    //Both disabled at the start of Skip()
    public static bool votingEnabled = false;
    public static bool selectTargetActive = false;

    


    private void Awake()
    {
        instance = this;
        Role.PlayerTargetSelected.AddListener(OnSelectedTarget);
    }
    private void Start()
    {
        roles.AddRange(testRoles);
        players.AddRange(testPlayers);
        Debug.Log(roles.Count);
        
        StartGame();
    }
    private void Update()
    {
        gameState = state;
        _activePlayer = activePlayer;
    }

    public static void OnTargetSelectionStart(Role selector)
    {
    }


    public void OnSelectedTarget(Role target)
    {
        Debug.Log(target);
        if (target == null)
        {
            Debug.Log("No target lolo");
            if (activePlayer != null)
            {
                activePlayer.visitOver = true;
            }
            state = GameState.Night;
            return;
        }
        if (target.ContainsStatusEffect(Role.StatusEffect.Dead))
        {
            Debug.LogError("Target is dead, cannot select.");
            return;
        }


        if (state == GameState.SelectTarget)
        {
            Debug.Log(activePlayer.connectedPlayer.playerName + " Visited: " + target.connectedPlayer.playerName);
            target.Visited(visitor: activePlayer);
            state = GameState.Night;
        }
        else if (state == GameState.Voting)
        {
            target.Die();
            IncreaseGameState();
        }
        else
        {
            Debug.Log("No valid state to select target in");
        }

            
    }
    private void IncreaseGameState()
    {
        int maxEnum = Enum.GetNames(typeof(GameState)).Length;
        
        int nextState = ((int)state + 1) % maxEnum;
        Debug.Log("State changed to: " + (GameState)nextState);
        state = (GameState)nextState;
    }
    public void Skip()
    {
        votingEnabled = false;
        selectTargetActive = false;

        if (state == GameState.SelectTarget)
        {
            Role.PlayerTargetSelected.Invoke(null);
            
        }
        else
        {
            IncreaseGameState();
        }
            


        switch(state)
        {
            //Should never be able to skip to discussion
            case GameState.Discussion:
                //Start of day, calculates what happened during the night
                
                break;
            case GameState.Voting:
                //Start of voting
                StartVoting();
                break;
            case GameState.NightStart:
                //Start of night
                StartCoroutine(NightLogic());
                break;
        }
    }

    private void StartVoting()
    {
        votingEnabled = true;
    }

    //Runs from UIManager
    public void StartSelectTarget()
    {
        selectTargetActive = true;
        state = GameState.SelectTarget;
    }

    public static void SelectTarget(Role target)
    {
        if (activePlayer == null)
        {
            Debug.LogError("No active player to select target for.");
            return;
        }
        if (!selectTargetActive)
        {
            Debug.LogError("Select target is not active.");
            return;
        }
        
        Role.PlayerTargetSelected.Invoke(target);
        selectTargetActive = false;
    }
    
    public void StartGame()
    {
        //Starts a new game, should only be run once
        Debug.Log("Game started. There should only be one of these messages ever.");

        List<Role> tempRoles = new List<Role>(roles);
        roles.Clear();
        int roleCount = tempRoles.Count;
        Debug.Log("count: " + roleCount);

        for(int i = 0; i<roleCount; i++)
        {
            int rand = UnityEngine.Random.Range(0, tempRoles.Count);
            Role roleAt = tempRoles[rand];

            Role newRole = InstantiateRole(roleAt);
            roleGameObjectDictionary.Add(newRole, newRole.gameObject);
            roles.Add(newRole);
            tempRoles.RemoveAt(rand);

        }

        for (int i = 0; i < players.Count; i++)
        {
            roles[i].name = roles[i].roleName + " (" + players[i].playerName + ")";
            Debug.Log("Player: " + players[i].playerName + " Role: " + roles[i].roleName);
            roles[i].connectedPlayer.playerName = players[i].playerName;
            roles[i].connectedPlayer.UpdateRoleName(roles[i].roleNameText, roles[i].roleName);

            rolesAlive.Add(players[i], roles[i]);
            


        }
        roleDictionary = new Dictionary<Player, Role>(rolesAlive);


        state = GameState.Discussion;
    }

    private Role InstantiateRole(Role role)
    {
        GameObject roleObject = Instantiate(
            prefabs.Find(x => x.role == role).rolePrefab,
            roleGridParent
        );

        return roleObject.GetComponent<Role>();
    }

    public IEnumerator NightLogic()
    {
        state = GameState.Night;
        foreach(var rolePair in rolesAlive)
        {
            activePlayer = rolePair.Value;
            Debug.Log("New active player: " + activePlayer.connectedPlayer.playerName);
            //This is where all roles do their specific tasks at night if any.
            yield return activePlayer.NightAction();
        }
        CalculateNight();
        yield return null;
    }

    public void CalculateNight()
    {
        state = GameState.Discussion;
        dayMessage = "";
        List<Player> playersToRemove = new List<Player>();

        foreach (var role in rolesAlive)
        {
            role.Value.EndOfNight();
            if (role.Value.ContainsStatusEffect(Role.StatusEffect.Dead))
            {
                playersToRemove.Add(role.Key);
                AddToDayMessage(role.Value.connectedPlayer.playerName + " has died.");
            }
        }

        foreach (Player player in playersToRemove)
        {
            rolesAlive.Remove(player);
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
            if (!includeSelf && players.Value == currentRole)
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
        else
        {
            Debug.LogError("No corresponding player");
        }
        return null;
    }
}
