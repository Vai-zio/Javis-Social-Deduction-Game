using NUnit.Framework;
using TMPro;
using UnityEngine;
using System.Collections.Generic;
using System;

public class UIManager : MonoBehaviour
{
    public static UIManager instance;
    public TextMeshProUGUI titleText;
    public TextMeshProUGUI continueButtonText;

    public Color buttonDefaultColor;
    public Color buttonDisabledColor;

    

    private void Awake()
    {
        instance = this;
        Role.StartVisitEvent.AddListener(ShowTargetUI);
        Role.PlayerTargetSelected.AddListener(ResetRoleUI);
    }

    private void ShowTargetUI(List<Player> playerTargets)
    {
        HideTargetUI(null);
        foreach (Player target in playerTargets)
        {
            Role role = GameManager.GetRoleFromPlayer(target);
            role.roleDisabled = false;

            GameManager.instance.StartSelectTarget();
        }
    }

    private void HideTargetUI(Role target)
    {
        foreach(var role in GameManager.roleGameObjectDictionary)
        {
            role.Key.roleDisabled = true;
        }
    }
    private void ResetRoleUI(Role target)
    {
        foreach (var role in GameManager.roleGameObjectDictionary)
        {
            role.Key.roleDisabled = false;
        }
    }
    private void Update()
    {
        GameManager.GameState state = GameManager.state;
        switch (state)
        {
            case GameManager.GameState.Discussion:
                titleText.text = "Discussion time";
                continueButtonText.text = "Continue to voting";
                break;
            case GameManager.GameState.Voting:
                titleText.text = "Select voted target";
                continueButtonText.text = "Abstain";
                break;
            case GameManager.GameState.NightStart:
                titleText.text = "The town sleeps...";
                continueButtonText.text = "Continue to night";
                break;
            case GameManager.GameState.Night:
                titleText.text = "It's a full moon out..";
                continueButtonText.text = "Continue";
                break;
            case GameManager.GameState.SelectTarget:
                titleText.text = "Select a target";
                continueButtonText.text = "No Target";
                break;
        }
    }

    public void SkipButton()
    {
        
    }


    
}
