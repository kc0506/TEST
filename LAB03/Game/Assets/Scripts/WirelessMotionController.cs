using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using Unity.VisualScripting;
using UnityEngine;

public class WirelessMotionController : MonoBehaviour
{

    const string hostIP = "192.168.43.121";
    const int port = 80;

    private SocketClient socketClient;
    public bool isTrigger;
    public Quaternion quaternion;
    public float yaw;

    private void Awake()
    {
        socketClient = new SocketClient(hostIP, port);
    }

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        isTrigger = socketClient.isTrigger;
        quaternion = new Quaternion(socketClient.x, socketClient.y, socketClient.z, socketClient.w);
        yaw = quaternion.eulerAngles.z;
    }

    void OnDestroy()
    {
        socketClient.Close();
    }
}
