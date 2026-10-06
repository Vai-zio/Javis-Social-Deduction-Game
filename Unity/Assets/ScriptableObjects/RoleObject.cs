using UnityEditor;
using UnityEngine;

[CreateAssetMenu(fileName = "Role")]
public class RoleObject : ScriptableObject
{
    public string roleName;
    public string roleDescription;
    public Sprite roleIcon;

    public GameObject rolePrefab;

    
}
