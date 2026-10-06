using System.Collections;
using UnityEngine;

public class Werewolf : Role
{
    private void Awake()
    {
        rolePriority = 3;
    }
    public override IEnumerator NightAction()
    {
        yield return ChooseTarget(GameManager.GetValidTargets());

        Role role = GameManager.GetRoleFromPlayer(playerVisited);

        AttackOtherPlayer(role);

        Debug.Log("Attacked " + playerVisited.playerName);
    }
}
