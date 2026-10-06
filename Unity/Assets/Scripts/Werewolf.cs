using System.Collections;
using UnityEngine;

public class Werewolf : Role
{
    
    public override IEnumerator NightAction()
    {
        yield return ChooseTarget(GameManager.GetValidTargets(this, false));

        if (playerVisited.Count == 0)
        {
            yield break;
        }
        Role role = playerVisited[0];

        AttackOtherPlayer(role);

        Debug.Log("Attacked " + playerVisited[0].connectedPlayer.playerName);
    }
}
