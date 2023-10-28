using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CheckPoint : MonoBehaviour
{

    public AudioClip CheckPointES;

    private void OnTriggerEnter(Collider other)
    {
        AudioSource.PlayClipAtPoint(CheckPointES, other.gameObject.transform.position);
        transform.parent.GetComponent<LevelManager>().LoadCheckPoint();
    }

}
