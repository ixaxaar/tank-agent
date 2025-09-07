# Robot Tank Project - Claude Documentation

## Project Overview
**Agentic AI controlled robotic tank project** - 4-wheel drive robot tank with camera gimbal, built on Raspberry Pi with L298N motor drivers. Designed for autonomous operation with AI decision-making capabilities.

## Hardware Configuration

### Motors & Drivers
- **Left Wheels**: L298N driver controlling 2 DC motors (front + rear)
  - Front Left: GPIO 12 (PWM), 10 (forward), 22 (reverse)  
  - Rear Left: GPIO 2 (speed), 27 (forward), 17 (reverse)

- **Right Wheels**: L298N driver controlling 2 DC motors (front + rear)  
  - Front Right: GPIO 13 (PWM), 26 (forward), 21 (reverse)
  - Rear Right: GPIO 6 (speed), 20 (forward), 16 (reverse)

- **Camera Gimbal**: Stepper motor (4-phase)
  - GPIO pins: 14, 15, 18, 23
  - 200 steps/revolution, 360� pan range

### Camera
- Pi Camera v2/v3 compatible
- 1920x1080 @ 10fps default
- Stream server on port 5000 (Flask-based)

## Software Architecture

### Core Modules
- **`src/motor_control.py`**: Main motor control library
  - `L298NMotorController`: Controls L298N drivers (single/dual motor)
  - `StepperMotor`: 4-phase stepper motor control  
  - `TankController`: High-level tank movement & integration

### Configuration Files  
- **`config/motors.yml`**: Motor pin assignments & parameters
- **`config/application.yml`**: Movement patterns & camera config
- **`config/util.yml`**: Wheel position enums

### Testing Utilities
- **`utils/test_mobility.py`**: Comprehensive hardware test suite
- **`utils/quick_test.py`**: Quick individual component testing
- **`utils/camera_stream.py`**: Camera streaming server

## Key Commands

### Testing Hardware
```bash
# Full hardware test suite
python3 utils/test_mobility.py

# Quick individual tests
python3 utils/quick_test.py

# Camera stream test
python3 utils/camera_stream.py
```

### Installation (TODO)
```bash
make install  # Copy files to Pi & setup systemd services
```

## Development Notes

### Motor Control Design
- L298N controllers support dual motors per IC  
- PWM speed control (0-100%)
- Tank steering: opposite wheel directions for turns
- Emergency stop functionality in all test scripts

### GPIO Safety
- Always call `cleanup()` in try/finally blocks
- GPIO.setwarnings(False) to avoid conflicts
- Use BCM pin numbering consistently

### Configuration Structure
- YAML-based modular config system
- Separate concerns: hardware pins, movement patterns, utilities
- Easy to modify without code changes

## Known Issues & Fixes
- Fixed typo: `moror_a` � `motor_a` in motors.yml:30
- Path fix: moved motor_control.py from lib/ to src/
- Import paths use relative src/ directory

## Future Enhancements
- [ ] Remote control via web interface
- [ ] Autonomous navigation features  
- [ ] Sensor integration (ultrasonic, IMU)
- [ ] Video recording capabilities
- [ ] Battery monitoring
- [ ] LED status indicators

## Dependencies
```bash
pip install RPi.GPIO PyYAML flask picamera2
```

## Test Results Tracking
The test suite provides detailed pass/fail reporting for:
- Individual motor functionality (4 motors)
- Movement patterns (forward, backward, left turn, right turn)
- Gimbal functionality (pan left/right/center)
- System integration (complex movement sequences)

## Troubleshooting

### Motor Not Moving
1. Check wiring connections to L298N
2. Verify power supply to motors
3. Test individual GPIO pins with multimeter
4. Check motor driver enable pins (ENA/ENB)

### GPIO Permission Issues  
```bash
sudo usermod -a -G gpio $USER
# Logout/login or reboot
```

### Camera Issues
```bash
# Enable camera interface
sudo raspi-config
# Interface Options > Camera > Enable
```