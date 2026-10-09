using TMPro;
using UnityEngine;

[System.Serializable]
public class Player
{
    public string playerName;

    

    public void UpdateRoleName(TextMeshProUGUI UI, string roleName)
    {
        UI.text = roleName;
    }

    public void UpdateInfoText(TextMeshProUGUI UI, string info)
    {
        UI.text = playerName + " - " + info;
    }
}
