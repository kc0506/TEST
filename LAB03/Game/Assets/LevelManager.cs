using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UI;

public class LevelManager : MonoBehaviour
{

    public GameObject StartFinishLine;
    public GameObject[] CheckPointList;

    private int _gameState = -1;
    private int _checkPointNum;
    private Collider _startLineCollider;

    private float _startTime;
    private bool _isPlaying = false;
    public Text TimerText;


    // Start is called before the first frame update
    void Start()
    {
        _checkPointNum = CheckPointList.Count();
        for (int i = 0; i < _checkPointNum; i++)
            CheckPointList[i].SetActive(false);
        _startLineCollider = StartFinishLine.GetComponent<Collider>();
        _startLineCollider.enabled = true;
    }

    public void LoadCheckPoint()
    {
        if (_gameState == -1)
        {
            _startTime = Time.time;
            _isPlaying = true;
            _startLineCollider.enabled = false;
        }
        else if (_gameState == _checkPointNum)
        {
            _isPlaying = false;
            _startLineCollider.enabled = false;
            return;
        }
        else
        {
            Debug.Log(_gameState);
            CheckPointList[_gameState].SetActive(false);
        }

        _gameState++;

        if (_gameState == _checkPointNum)
        {
            _startLineCollider.enabled = true;
        }
        else
        {
            CheckPointList[_gameState].SetActive(true);
        }

    }

    private void Update()
    {
        if (_isPlaying)
            UpdateTimer();
    }

    private void UpdateTimer()
    {
        float currentTime = Time.time - _startTime;
        currentTime = Mathf.Max(currentTime, 0);
        float minutes = (int)(currentTime / 60);
        float seconds = currentTime % 60;
        TimerText.text = string.Format("{0:0}:{1:00.00}", minutes, seconds);
    }
}
