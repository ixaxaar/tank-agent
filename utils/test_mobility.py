#!/usr/bin/env python3
"""
Tank Mobility and Hardware Test Script
Tests all mechanical components of the robot tank:
- Individual motor functionality  
- Tank movement patterns (forward, backward, turns)
- Camera gimbal stepper motor
- System integration
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from motor_control import TankController, L298NMotorController, StepperMotor
    import RPi.GPIO as GPIO
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running on a Raspberry Pi with RPi.GPIO installed")
    sys.exit(1)

class TankTester:
    def __init__(self):
        """Initialize the tank tester"""
        self.tank = None
        self.test_results = {
            'individual_motors': {},
            'movement_patterns': {},
            'gimbal': {},
            'overall': 'pending'
        }
    
    def setup(self):
        """Setup the tank controller"""
        try:
            print("🤖 Initializing Tank Controller...")
            self.tank = TankController()
            print("✅ Tank Controller initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize tank: {e}")
            traceback.print_exc()
            return False
    
    def test_individual_motors(self):
        """Test each motor individually"""
        print("\n🔧 Testing Individual Motors...")
        
        tests = [
            ("Front Left Motor (Motor A - Left Controller)", self._test_front_left),
            ("Rear Left Motor (Motor B - Left Controller)", self._test_rear_left),
            ("Front Right Motor (Motor A - Right Controller)", self._test_front_right), 
            ("Rear Right Motor (Motor B - Right Controller)", self._test_rear_right),
        ]
        
        for motor_name, test_func in tests:
            print(f"\n  Testing {motor_name}...")
            try:
                test_func()
                self.test_results['individual_motors'][motor_name] = 'pass'
                print(f"  ✅ {motor_name} test passed")
            except Exception as e:
                self.test_results['individual_motors'][motor_name] = f'fail: {e}'
                print(f"  ❌ {motor_name} test failed: {e}")
                input("  Press Enter to continue to next test...")
    
    def _test_front_left(self):
        """Test front left motor"""
        print("    Forward direction...")
        self.tank.left_controller.motor_a_forward(30)
        time.sleep(1.5)
        self.tank.left_controller.stop_motor_a()
        time.sleep(0.5)
        
        print("    Backward direction...")
        self.tank.left_controller.motor_a_backward(30)
        time.sleep(1.5)
        self.tank.left_controller.stop_motor_a()
    
    def _test_rear_left(self):
        """Test rear left motor"""
        print("    Forward direction...")
        self.tank.left_controller.motor_b_forward(30)
        time.sleep(1.5)
        self.tank.left_controller.stop_motor_b()
        time.sleep(0.5)
        
        print("    Backward direction...")
        self.tank.left_controller.motor_b_backward(30)
        time.sleep(1.5)
        self.tank.left_controller.stop_motor_b()
    
    def _test_front_right(self):
        """Test front right motor"""
        print("    Forward direction...")
        self.tank.right_controller.motor_a_forward(30)
        time.sleep(1.5)
        self.tank.right_controller.stop_motor_a()
        time.sleep(0.5)
        
        print("    Backward direction...")
        self.tank.right_controller.motor_a_backward(30)
        time.sleep(1.5)
        self.tank.right_controller.stop_motor_a()
    
    def _test_rear_right(self):
        """Test rear right motor"""
        print("    Forward direction...")
        self.tank.right_controller.motor_b_forward(30)
        time.sleep(1.5)
        self.tank.right_controller.stop_motor_b()
        time.sleep(0.5)
        
        print("    Backward direction...")
        self.tank.right_controller.motor_b_backward(30)
        time.sleep(1.5)
        self.tank.right_controller.stop_motor_b()
    
    def test_movement_patterns(self):
        """Test tank movement patterns"""
        print("\n🚗 Testing Movement Patterns...")
        
        movements = [
            ("Forward Movement", lambda: self.tank.move_forward(40, 2)),
            ("Backward Movement", lambda: self.tank.move_backward(40, 2)),
            ("Left Turn", lambda: self.tank.turn_left(35, 1.5)),
            ("Right Turn", lambda: self.tank.turn_right(35, 1.5)),
        ]
        
        for movement_name, movement_func in movements:
            print(f"\n  Testing {movement_name}...")
            try:
                input(f"  Press Enter to start {movement_name}...")
                movement_func()
                time.sleep(0.5)  # Brief pause between movements
                self.test_results['movement_patterns'][movement_name] = 'pass'
                print(f"  ✅ {movement_name} completed")
            except Exception as e:
                self.test_results['movement_patterns'][movement_name] = f'fail: {e}'
                print(f"  ❌ {movement_name} failed: {e}")
                self.tank.stop_all()  # Emergency stop
    
    def test_gimbal(self):
        """Test camera gimbal stepper motor"""
        print("\n📷 Testing Camera Gimbal...")
        
        gimbal_tests = [
            ("Pan Right 45°", lambda: self.tank.pan_camera(45)),
            ("Pan Left 90° (back to -45°)", lambda: self.tank.pan_camera(-90)),
            ("Return to Center", lambda: self.tank.pan_camera(45)),
        ]
        
        for test_name, test_func in gimbal_tests:
            print(f"\n  Testing {test_name}...")
            try:
                input(f"  Press Enter to start {test_name}...")
                test_func()
                time.sleep(1)
                self.test_results['gimbal'][test_name] = 'pass'
                print(f"  ✅ {test_name} completed")
            except Exception as e:
                self.test_results['gimbal'][test_name] = f'fail: {e}'
                print(f"  ❌ {test_name} failed: {e}")
    
    def test_integration(self):
        """Test system integration - complex movement"""
        print("\n🎯 Testing System Integration...")
        print("  This will test a complex movement pattern combining multiple systems")
        
        try:
            input("  Press Enter to start integration test...")
            
            print("  → Moving forward...")
            self.tank.move_forward(40, 2)
            
            print("  → Panning camera right while turning left...")
            self.tank.turn_left(35, 1)
            time.sleep(0.5)
            self.tank.pan_camera(30)
            
            print("  → Moving backward...")
            self.tank.move_backward(40, 2)
            
            print("  → Returning camera to center while turning right...")
            self.tank.turn_right(35, 1)
            time.sleep(0.5)
            self.tank.pan_camera(-30)
            
            self.test_results['overall'] = 'pass'
            print("  ✅ Integration test completed successfully")
            
        except Exception as e:
            self.test_results['overall'] = f'fail: {e}'
            print(f"  ❌ Integration test failed: {e}")
            self.tank.stop_all()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🧾 TEST SUMMARY")
        print("="*60)
        
        # Individual motors
        print("\nIndividual Motor Tests:")
        for motor, result in self.test_results['individual_motors'].items():
            status = "✅ PASS" if result == 'pass' else f"❌ FAIL ({result})"
            print(f"  {motor}: {status}")
        
        # Movement patterns  
        print("\nMovement Pattern Tests:")
        for movement, result in self.test_results['movement_patterns'].items():
            status = "✅ PASS" if result == 'pass' else f"❌ FAIL ({result})"
            print(f"  {movement}: {status}")
        
        # Gimbal tests
        print("\nGimbal Tests:")
        for test, result in self.test_results['gimbal'].items():
            status = "✅ PASS" if result == 'pass' else f"❌ FAIL ({result})"
            print(f"  {test}: {status}")
        
        # Overall result
        print(f"\nOverall Integration: {self.test_results['overall']}")
        
        # Count results
        total_tests = (len(self.test_results['individual_motors']) + 
                      len(self.test_results['movement_patterns']) + 
                      len(self.test_results['gimbal']) + 1)
        
        passed_tests = sum([
            sum(1 for r in self.test_results['individual_motors'].values() if r == 'pass'),
            sum(1 for r in self.test_results['movement_patterns'].values() if r == 'pass'), 
            sum(1 for r in self.test_results['gimbal'].values() if r == 'pass'),
            1 if self.test_results['overall'] == 'pass' else 0
        ])
        
        print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Your tank is ready for action!")
        else:
            print("⚠️  Some tests failed. Check connections and configurations.")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.tank:
            try:
                self.tank.cleanup()
                print("🧹 GPIO cleanup completed")
            except:
                pass

def main():
    """Main test function"""
    print("🤖 Robot Tank Hardware Test Suite")
    print("="*50)
    print("This script will test all mechanical components of your tank:")
    print("• Individual motor functionality")
    print("• Movement patterns (forward, backward, turns)")  
    print("• Camera gimbal stepper motor")
    print("• System integration")
    print("\n⚠️  Make sure your tank has clearance to move safely!")
    
    input("\nPress Enter to begin testing...")
    
    tester = TankTester()
    
    try:
        # Setup
        if not tester.setup():
            return 1
        
        # Run tests
        tester.test_individual_motors()
        tester.test_movement_patterns()
        tester.test_gimbal()
        tester.test_integration()
        
        # Show results
        tester.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
    finally:
        tester.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
