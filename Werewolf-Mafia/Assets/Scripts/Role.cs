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
    public TextMeshProUGUI playerInfoText;
    public TextMeshProUGUI roleNameText;
    public string roleName;
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
    public bool visitOver;

    public int rolePriority; // Roleblock first, then protect, then attack, then information
                             // 1, 2, 3, 4

    
    public List<Role> Attackers = new List<Role>();


    private void Awake()
    {
        
    }
    private void Update()
    {
        UpdateEffects();
    }
    public RoleType GetRoleType()
    {
               return roleType;
    }

    public void OnClicked()
    {
        GameManager.instance.OnSelectedTarget(this);
    }
    public virtual void UpdateEffects()
    {
        if (connectedPlayer == null)
        {
            Debug.Log("Player is null");
            return;
        }
        string playerInfo = "";
        foreach(StatusEffect effect in statusEffects)
        {
            playerInfo += effect.ToString() + ", ";
        }
        connectedPlayer.UpdateInfoText(playerInfoText, playerInfo);
        if (statusEffects.Contains(StatusEffect.Protected) && currentDefense < Strength.Basic)
        {
            currentDefense = Strength.Basic;
        }
    }
    protected virtual void VisitPlayer(Role Visited)
    {
        playerVisited.Add(Visited);
    }

    
    public virtual void Visited(Role visitor)
    {
        
        visitor.VisitPlayer(this);
    }

    protected virtual void AttackOtherPlayer(Role defender)
    {
        defender.Attacked(connectedPlayer, this);
    }

    public virtual void Attacked(Player attacker, Role roleAttacker)
    {
        Attackers.Add(roleAttacker);
        
    }

    public virtual void Die()
    {
        statusEffects.Add(StatusEffect.Dead);
        Debug.Log(connectedPlayer.playerName + " Has died.");
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
                Die();
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
        yield return new WaitForEndOfFrame();

    }

    public virtual IEnumerator ChooseTarget(List<Player> possibleTargets)
    {
        GameManager.OnTargetSelectionStart(this);
        StartVisitEvent.Invoke(possibleTargets);
        yield return new WaitUntil(() => visitOver);
        visitOver = false;
    }

    public virtual bool ContainsStatusEffect(StatusEffect effect)
    {
        return statusEffects.Contains(effect);
    }


}
