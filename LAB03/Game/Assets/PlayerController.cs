using System;
using UnityEngine;

public class PlayerController : MonoBehaviour
{

    private Rigidbody _rb;
    private WirelessMotionController _controller;

    private float _currentSpeed = 0f;
    public float MinSpeed;
    [Tooltip("Max speed")]
    public float MaxSpeed;
    [Tooltip("Acceleration")]
    public float Acceleration;

    public float MaxRotationAngle;
    public float RotationSpeed;
    public Transform Hands;
    // These two object contains the rigid body of wheels
    public Transform FrontLeftWheel;
    public Transform FrontRightWheel;

    void Start()
    {
        _rb = GetComponent<Rigidbody>();
        _controller = GetComponent<WirelessMotionController>();
    }

    // Update is called once per frame
    void FixedUpdate()
    {
        Steer();
        Move();
    }

    private void ControllerSteer()
    {
        RotateVisual(_controller.yaw, 1 / Time.fixedDeltaTime);
    }
    private void ControllerMove()
    {
        if (_controller.isTrigger)
            _currentSpeed = Mathf.Lerp(_currentSpeed, MaxSpeed, Time.fixedDeltaTime * Acceleration * 1f);
        else
            _currentSpeed = Mathf.Lerp(_currentSpeed, 0, Time.deltaTime * Acceleration * 6f);

        RotateRigidBody();

        Vector3 vel = transform.forward * _currentSpeed;  // transform object has forward, up, right for three axis in world space
        vel.y = _rb.velocity.y;  // transform may slightly tilted due to shape of wheel etc.
        _rb.velocity = vel;
    }


    void Move()
    {
        // interpolate current speed to target speed
        if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow))
            _currentSpeed = Mathf.Lerp(_currentSpeed, MaxSpeed, Time.fixedDeltaTime * Acceleration * 1f);
        else if (Input.GetKey(KeyCode.S))
            _currentSpeed = Mathf.Lerp(_currentSpeed, MinSpeed, Time.fixedDeltaTime * Acceleration * 2f);
        else
            _currentSpeed = Mathf.Lerp(_currentSpeed, 0, Time.fixedDeltaTime * Acceleration * 6f);


        RotateRigidBody();

        // Quaternion Q = FrontLeftWheel.parent.rotation * FrontLeftWheel.localRotation;
        // Debug.Log(Q == FrontLeftWheel.rotation);  // always True

        Vector3 vel = transform.forward * _currentSpeed;  // transform object has forward, up, right for three axis in world space
        vel.y = _rb.velocity.y;  // transform may slightly tilted due to shape of wheel etc.
        _rb.velocity = vel;
    }

    void Steer()
    {
        if (Input.GetKey(KeyCode.A))
            RotateVisual(MaxRotationAngle, RotationSpeed * 1f);
        else if (Input.GetKey(KeyCode.D))
            RotateVisual(-MaxRotationAngle, RotationSpeed * 1f);
        else
            RotateVisual(0, RotationSpeed * 3f);

    }

    private float RegularizeAngle(float angle)
    {
        angle -= (angle > 180 ? 1 : 0) * 360;
        angle += (angle < -180 ? 1 : 0) * 360;
        return angle;
    }

    private void RotateVisual(float targetAngle, float rotateSpeed)
    {

        // Unity is left-handed (both axis and rotation)
        // The order of euler angles is Z-X-Y

        // transform.localEulerAngles: the rotation between obj and parent
        // transform.eulerAngles: the rotation between obj in world
        // We can verify as following:

        // Quaternion Q = Quaternion.Euler(Hands.eulerAngles);
        // Debug.Log(Q * Vector3.forward == Hands.forward);
        // Debug.Log(Q * Vector3.right == Hands.right);
        // Debug.Log(Q * Vector3.up == Hands.up);


        // note that Z is rotated before X
        float handAngle = RegularizeAngle(Hands.localEulerAngles.z);
        float wheelAngle = RegularizeAngle(FrontLeftWheel.localEulerAngles.y);

        float deltaHandAngle = (targetAngle - handAngle) * Time.fixedDeltaTime * rotateSpeed;
        float deltaWheelAngle = (-targetAngle - wheelAngle) * Time.fixedDeltaTime * rotateSpeed;
        // The above is equivalent to lerp:
        // float afterAngle = handAngle + deltaHandAngle;
        // Debug.Log(afterAngle == Mathf.Lerp(handAngle, targetAngle, Time.fixedDeltaTime * rotateSpeed));

        Hands.Rotate(0, 0, deltaHandAngle, Space.Self);  // relative to parent
        FrontLeftWheel.Rotate(0, deltaWheelAngle, 0, Space.Self);
        FrontRightWheel.Rotate(0, deltaWheelAngle, 0, Space.Self);
    }

    private void RotateRigidBody()
    {
        float deltaAngleY = FrontLeftWheel.eulerAngles.y - transform.eulerAngles.y;
        deltaAngleY = RegularizeAngle(deltaAngleY);

        Quaternion deltaRotation = Quaternion.Euler(0, Mathf.Sign(_currentSpeed) * Time.fixedDeltaTime * deltaAngleY, 0);
        _rb.MoveRotation(deltaRotation * _rb.rotation);  // instantly take effect
    }
}
