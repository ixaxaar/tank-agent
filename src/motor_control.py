#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import yaml
from pathlib import Path


class L298NMotorController:
    def __init__(self, ena_pin, in1_pin, in2_pin, in3_pin=None, in4_pin=None, enb_pin=None):
        """
        Initialize L298N motor controller
        For single motor: use ena, in1, in2
        For dual motor: use all pins
        """
        self.ena_pin = ena_pin
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.in3_pin = in3_pin
        self.in4_pin = in4_pin
        self.enb_pin = enb_pin

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup pins
        GPIO.setup(self.ena_pin, GPIO.OUT)
        GPIO.setup(self.in1_pin, GPIO.OUT)
        GPIO.setup(self.in2_pin, GPIO.OUT)

        if self.in3_pin and self.in4_pin and self.enb_pin:
            GPIO.setup(self.in3_pin, GPIO.OUT)
            GPIO.setup(self.in4_pin, GPIO.OUT)
            GPIO.setup(self.enb_pin, GPIO.OUT)

        # PWM setup
        self.pwm_a = GPIO.PWM(self.ena_pin, 1000)  # 1kHz frequency
        self.pwm_a.start(0)

        if self.enb_pin:
            self.pwm_b = GPIO.PWM(self.enb_pin, 1000)
            self.pwm_b.start(0)

        self.stop_all()

    def motor_a_forward(self, speed=50):
        """Motor A forward with speed (0-100)"""
        GPIO.output(self.in1_pin, GPIO.HIGH)
        GPIO.output(self.in2_pin, GPIO.LOW)
        self.pwm_a.ChangeDutyCycle(speed)

    def motor_a_backward(self, speed=50):
        """Motor A backward with speed (0-100)"""
        GPIO.output(self.in1_pin, GPIO.LOW)
        GPIO.output(self.in2_pin, GPIO.HIGH)
        self.pwm_a.ChangeDutyCycle(speed)

    def motor_b_forward(self, speed=50):
        """Motor B forward with speed (0-100)"""
        if self.in3_pin and self.in4_pin and self.enb_pin:
            GPIO.output(self.in3_pin, GPIO.HIGH)
            GPIO.output(self.in4_pin, GPIO.LOW)
            self.pwm_b.ChangeDutyCycle(speed)

    def motor_b_backward(self, speed=50):
        """Motor B backward with speed (0-100)"""
        if self.in3_pin and self.in4_pin and self.enb_pin:
            GPIO.output(self.in3_pin, GPIO.LOW)
            GPIO.output(self.in4_pin, GPIO.HIGH)
            self.pwm_b.ChangeDutyCycle(speed)

    def stop_motor_a(self):
        """Stop Motor A"""
        GPIO.output(self.in1_pin, GPIO.LOW)
        GPIO.output(self.in2_pin, GPIO.LOW)
        self.pwm_a.ChangeDutyCycle(0)

    def stop_motor_b(self):
        """Stop Motor B"""
        if self.in3_pin and self.in4_pin:
            GPIO.output(self.in3_pin, GPIO.LOW)
            GPIO.output(self.in4_pin, GPIO.LOW)
            if self.enb_pin:
                self.pwm_b.ChangeDutyCycle(0)

    def stop_all(self):
        """Stop all motors"""
        self.stop_motor_a()
        self.stop_motor_b()

    def cleanup(self):
        """Cleanup GPIO"""
        self.stop_all()
        self.pwm_a.stop()
        if hasattr(self, "pwm_b"):
            self.pwm_b.stop()
        GPIO.cleanup()


class StepperMotor:
    def __init__(self, in1, in2, in3, in4, steps_per_rev=200):
        """Initialize stepper motor"""
        self.pins = [in1, in2, in3, in4]
        self.steps_per_rev = steps_per_rev

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # Step sequence for 4-step sequence
        self.step_sequence = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]

        self.current_step = 0

    def step_motor(self, direction=1, delay=0.002):
        """Step motor once (direction: 1=forward, -1=backward)"""
        if direction > 0:
            self.current_step = (self.current_step + 1) % 4
        else:
            self.current_step = (self.current_step - 1) % 4

        sequence = self.step_sequence[self.current_step]
        for i, pin in enumerate(self.pins):
            GPIO.output(pin, sequence[i])

        time.sleep(delay)

    def rotate_degrees(self, degrees, speed=500):
        """Rotate by degrees (positive=clockwise, negative=counterclockwise)"""
        steps = int((abs(degrees) / 360) * self.steps_per_rev)
        direction = 1 if degrees > 0 else -1
        delay = 1.0 / speed

        for _ in range(steps):
            self.step_motor(direction, delay)

    def stop(self):
        """Stop stepper motor"""
        for pin in self.pins:
            GPIO.output(pin, GPIO.LOW)


class TankController:
    def __init__(self, config_dir="/run/media/ixaxaar/src/code/src/devices/tank/config"):
        """Initialize tank controller from config files"""
        self.config_dir = Path(config_dir)

        # Load configurations
        with open(self.config_dir / "motors.yml", "r") as f:
            self.motors_config = yaml.safe_load(f)

        with open(self.config_dir / "application.yml", "r") as f:
            self.app_config = yaml.safe_load(f)

        with open(self.config_dir / "util.yml", "r") as f:
            self.util_config = yaml.safe_load(f)

        # Initialize motor controllers
        self._init_motors()

    def _init_motors(self):
        """Initialize all motor controllers"""
        # Left wheels (L298N controller)
        left_config = self.motors_config["mobility"]["left_wheels"]["pins"]
        self.left_controller = L298NMotorController(
            ena_pin=left_config["ena"],
            in1_pin=left_config["in1"],
            in2_pin=left_config["in2"],
            in3_pin=left_config["in3"],
            in4_pin=left_config["in4"],
            enb_pin=left_config["enb"],
        )

        # Right wheels (L298N controller)
        right_config = self.motors_config["mobility"]["right_wheels"]["pins"]
        self.right_controller = L298NMotorController(
            ena_pin=right_config["ena"],
            in1_pin=right_config["in1"],
            in2_pin=right_config["in2"],
            in3_pin=right_config["in3"],
            in4_pin=right_config["in4"],
            enb_pin=right_config["enb"],
        )

        # Camera gimbal stepper
        gimbal_config = self.motors_config["motors"]["camera_gimbal"]["pins"]
        self.gimbal = StepperMotor(
            in1=gimbal_config["in1"],
            in2=gimbal_config["in2"],
            in3=gimbal_config["in3"],
            in4=gimbal_config["in4"],
            steps_per_rev=self.motors_config["motors"]["camera_gimbal"]["params"]["steps_per_revolution"],
        )

    def move_forward(self, speed=50, duration=None):
        """Move tank forward"""
        self.left_controller.motor_a_forward(speed)
        self.left_controller.motor_b_forward(speed)
        self.right_controller.motor_a_forward(speed)
        self.right_controller.motor_b_forward(speed)

        if duration:
            time.sleep(duration)
            self.stop_all()

    def move_backward(self, speed=50, duration=None):
        """Move tank backward"""
        self.left_controller.motor_a_backward(speed)
        self.left_controller.motor_b_backward(speed)
        self.right_controller.motor_a_backward(speed)
        self.right_controller.motor_b_backward(speed)

        if duration:
            time.sleep(duration)
            self.stop_all()

    def turn_left(self, speed=50, duration=None):
        """Turn tank left (left wheels backward, right wheels forward)"""
        self.left_controller.motor_a_backward(speed)
        self.left_controller.motor_b_backward(speed)
        self.right_controller.motor_a_forward(speed)
        self.right_controller.motor_b_forward(speed)

        if duration:
            time.sleep(duration)
            self.stop_all()

    def turn_right(self, speed=50, duration=None):
        """Turn tank right (left wheels forward, right wheels backward)"""
        self.left_controller.motor_a_forward(speed)
        self.left_controller.motor_b_forward(speed)
        self.right_controller.motor_a_backward(speed)
        self.right_controller.motor_b_backward(speed)

        if duration:
            time.sleep(duration)
            self.stop_all()

    def stop_all(self):
        """Stop all motors"""
        self.left_controller.stop_all()
        self.right_controller.stop_all()

    def pan_camera(self, degrees):
        """Pan camera gimbal"""
        self.gimbal.rotate_degrees(degrees)

    def cleanup(self):
        """Cleanup all GPIO"""
        self.left_controller.cleanup()
        self.right_controller.cleanup()
        self.gimbal.stop()
        GPIO.cleanup()
