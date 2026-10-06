using System.Collections.Generic;
using UnityEngine;
using System.Collections;
using UnityEngine.Events;

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


    public Player connectedPlayer;
    

    public Strength startDefense;
    public Strength startAttack;
    protected List<StatusEffect> statusEffects;

    protected Strength currentDefense;
    protected Strength currentAttack;
    protected RoleType roleType;
    protected Player playerVisited; // Who this role visited at night

    public int rolePriority; // Roleblock first, then protect, then attack, then information
                             // 1, 2, 3, 4

    public static UnityEvent<Role> StartVisitEvent = new UnityEvent<Role>();
    public virtual void UpdateEffects()
    {
        if (statusEffects.Contains(StatusEffect.Protected) && currentDefense < Strength.Basic)
        {
            currentDefense = Strength.Basic;
        }
    }
    protected virtual void VisitPlayer(Player otherPlayer, Role otherRole)
    {
        Debug.Log(connectedPlayer.playerName + " visited " + otherPlayer.playerName);
    }

    protected virtual void Visited(Player playerVisiting, Role roleVisiting)
    {

    }

    protected virtual void AttackOtherPlayer(Role defender)
    {
        defender.Attacked(connectedPlayer, this);
    }

    public virtual void Attacked(Player attacker, Role roleAttacker)
    {
        if (roleAttacker.currentAttack > currentDefense)
        {
            statusEffects.Add(StatusEffect.Dead);
        }
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
        yield return null;
        Debug.Log("Chooses no one");
    }

    public virtual bool ContainsStatusEffect(StatusEffect effect)
    {
        return statusEffects.Contains(effect);
    }


}
