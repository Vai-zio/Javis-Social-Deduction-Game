using System.Collections.Generic;
using UnityEngine;
using System.Collections;
using UnityEngine.Events;
using TMPro;

public class Role : MonoBehaviour
{
    public enum RoleType
    {
        Villager,
        Neutral,
        Werewolf
    }

    public enum StatusEffect
    {
        Framed,
        Silenced,
        Protected,
        Dead,
        Blessed, // priest removes debuffs
        Bonded,
        Doused
    }

    public enum Strength
    {
        None,
        Basic,
        Powerful
    }

    public static UnityEvent<List<Player>> StartVisitEvent = new UnityEvent<List<Player>>();
    public static UnityEvent<Role> PlayerTargetSelected = new UnityEvent<Role>();


    public Player connectedPlayer;
    

    public Strength startDefense;
    public Strength startAttack;
    protected List<StatusEffect> statusEffects = new List<StatusEffect>();

    protected Strength currentDefense;
    protected Strength currentAttack;
    protected RoleType roleType;
    public List<Role> playerVisited = new List<Role>(); // Who this role visited at night

    public int rolePriority; // Roleblock first, then protect, then attack, then information
                             // 1, 2, 3, 4

    
    public List<Role> Attackers = new List<Role>();

    public TextMeshProUGUI playerInfo;
    public TextMeshProUGUI roleName;

    private void Awake()
    {
        
    }
    public RoleType GetRoleType()
    {
               return roleType;
    }
    public virtual void UpdateEffects()
    {
        if (statusEffects.Contains(StatusEffect.Protected) && currentDefense < Strength.Basic)
        {
            currentDefense = Strength.Basic;
        }
    }
    protected virtual void VisitPlayer(Role Visited)
    {
        Debug.Log(connectedPlayer.playerName + " Visited: " + Visited.connectedPlayer.playerName);
        playerVisited.Add(Visited);
    }

    //Called when clicking on the button for a player, which then uses the static active player from gamemanager
    protected virtual void Visited()
    {
        Role roleVisiting = GameManager.activePlayer;
        roleVisiting.VisitPlayer(this);
        PlayerTargetSelected.Invoke(this);
    }

    protected virtual void AttackOtherPlayer(Role defender)
    {
        defender.Attacked(connectedPlayer, this);
    }

    public virtual void Attacked(Player attacker, Role roleAttacker)
    {
        Attackers.Add(roleAttacker);
        
    }

    protected virtual void Die()
    {
        statusEffects.Add(StatusEffect.Dead);
    }

    protected virtual void VotedOut()
    {
        statusEffects.Add(StatusEffect.Dead);
    }
    protected virtual void ResetDay()
    {
        playerVisited = null;
        currentDefense = startDefense;
        currentAttack = startAttack;
    }
    protected virtual void EndOfNight()
    {
        foreach(Role roleAttacker in Attackers)
        {
            if (roleAttacker.currentAttack > currentDefense)
            {
                statusEffects.Add(StatusEffect.Dead);
            }
        }

        playerVisited.Clear();
        
    }

    protected void ClearStatusEffects()
    {
        foreach(StatusEffect effect in statusEffects)
        {
            if (effect != StatusEffect.Doused || effect != StatusEffect.Dead)
            {
                statusEffects.Remove(effect);
            }
        }
    }

    public virtual IEnumerator NightAction()
    {
        yield return null;
        Debug.Log("Visits no one");
    }

    public virtual IEnumerator ChooseTarget(List<Player> possibleTargets)
    {
        StartVisitEvent.Invoke(possibleTargets);
        yield return new WaitUntil(() => playerVisited.Count > 0);
    }

    public virtual bool ContainsStatusEffect(StatusEffect effect)
    {
        return statusEffects.Contains(effect);
    }


}
