using NUnit.Framework;
using TMPro;
using UnityEngine;
using System.Collections.Generic;

public class UIManager : MonoBehaviour
{
    
    public TextMeshProUGUI titleText;
    public TextMeshProUGUI continueButtonText;

    

    private void Awake()
    {
        Role.StartVisitEvent.AddListener(ShowTargetUI);
        Role.PlayerTargetSelected.AddListener(ResetRoleUI);
    }

    private void ShowTargetUI(List<Player> playerTargets)
    {
        HideTargetUI(null);
        foreach (Player target in playerTargets)
        {
            Role role = GameManager.GetRoleFromPlayer(target);

            GameManager.roleGameObjectDictionary[role].gameObject.SetActive(true);
        }
    }

    private void HideTargetUI(Role target)
    {
        foreach(var role in GameManager.roleGameObjectDictionary)
        {
            role.Value.SetActive(false);
        }
    }
    private void ResetRoleUI(Role target)
    {
        foreach (var role in GameManager.roleGameObjectDictionary)
        {
            role.Value.SetActive(true);
        }
    }
    private void Update()
    {
        GameManager.GameState state = GameManager.state;
        switch (state)
        {
            case GameManager.GameState.Discussion:
                titleText.text = "Discussion time";
                continueButtonText.text = "Start voting";
                break;
            case GameManager.GameState.Voting:
                titleText.text = "Select voted target";
                continueButtonText.text = "Abstain";
                break;
            case GameManager.GameState.Night:
                titleText.text = "The town sleeps...";
                continueButtonText.text = "Continue to night";
                break;
            case GameManager.GameState.SelectTarget:
                titleText.text = "Select a target";
                continueButtonText.text = "Abstain";
                break;
        }
    }

    public void SkipButton()
    {

    }

    
}
