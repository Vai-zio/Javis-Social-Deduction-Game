using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Seer : Role
{
    
    public override IEnumerator NightAction()
    {
        yield return ChooseTarget(GameManager.GetValidTargets(this, false));
        yield return ChooseTarget(GameManager.GetValidTargets(this, false));

        if (playerVisited.Count == 0)
        {
            yield break;
        }

        Role role1 = playerVisited[0];
        Role role2 = playerVisited[0];

        if (role1.GetRoleType() == RoleType.Werewolf || role2.GetRoleType() == RoleType.Werewolf)
        {
            Debug.Log(playerVisited[0].connectedPlayer.playerName + " or" + playerVisited[1].connectedPlayer.playerName + " is a werewolf!");
        }
    }

    public override IEnumerator ChooseTarget(List<Player> possibleTargets)
    {
        StartVisitEvent.Invoke(possibleTargets);
        yield return new WaitUntil(() => playerVisited.Count > 1);
    }
}
