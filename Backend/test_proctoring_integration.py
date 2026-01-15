"""
Proctoring Integration Test
Tests real-time camera integration with interview system
"""

import cv2
import numpy as np
import base64
import requests
import json
import time
from datetime import datetime

def test_proctoring_integration():
    """Test complete proctoring integration"""
    print("🔍 Testing Proctoring System Integration...")
    
    # Test 1: API Endpoints
    print("\n1. Testing API Endpoints...")
    try:
        # Test proctoring test endpoint
        response = requests.get('http://127.0.0.1:5000/api/proctoring/test')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Proctoring API: {data.get('message', 'Working')}")
            print(f"   Models loaded: {data.get('models_loaded', {})}")
        else:
            print(f"❌ Proctoring API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    # Test 2: Frame Processing
    print("\n2. Testing Frame Processing...")
    try:
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_frame, "TEST FRAME", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        # Encode frame
        _, buffer = cv2.imencode('.jpg', test_frame)
        frame_data = base64.b64encode(buffer).decode('utf-8')
        
        # Test frame processing
        response = requests.post('http://127.0.0.1:5000/api/proctoring/process_frame', 
                               json={
                                   'interview_session_id': 999999,  # Test session
                                   'frame': f'data:image/jpeg;base64,{frame_data}'
                               })
        
        if response.status_code == 200:
            print("✅ Frame processing endpoint working")
        else:
            print(f"❌ Frame processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Frame processing test failed: {e}")
    
    # Test 3: Camera Access Simulation
    print("\n3. Testing Camera Access...")
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Camera access working")
                print(f"   Frame size: {frame.shape}")
                
                # Test frame encoding
                _, buffer = cv2.imencode('.jpg', frame)
                frame_data = base64.b64encode(buffer).decode('utf-8')
                print(f"✅ Frame encoding working (size: {len(frame_data)} chars)")
            else:
                print("❌ Failed to read from camera")
            cap.release()
        else:
            print("❌ Cannot access camera")
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
    
    # Test 4: Model Loading
    print("\n4. Testing Model Loading...")
    try:
        from proctoring_system.core import ProctoringSuite
        suite = ProctoringSuite()
        print("✅ ProctoringSuite initialized")
        
        # Test with dummy frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        results = suite.process_frame(test_frame)
        print(f"✅ Frame processing working: {list(results.keys())}")
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
    
    print("\n🏁 Integration test complete!")

def test_live_proctoring():
    """Test live proctoring with real camera"""
    print("\n🎥 Testing Live Proctoring...")
    
    try:
        from proctoring_system.core import ProctoringSuite
        suite = ProctoringSuite()
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot access camera for live test")
            return
        
        print("📹 Live proctoring test started (press 'q' to quit)")
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process every 30th frame (simulate 1 FPS processing)
            if frame_count % 30 == 0:
                start_time = time.time()
                results = suite.process_frame(frame)
                processing_time = time.time() - start_time
                
                print(f"Frame {frame_count}: {processing_time:.3f}s")
                print(f"  Faces: {results.get('face_count', 0)}")
                print(f"  Gaze: {results.get('gaze_direction', 'Unknown')}")
                print(f"  Objects: {len(results.get('objects', []))}")
                print(f"  Violations: {len(results.get('violations', []))}")
                
                if results.get('violations'):
                    for violation in results['violations']:
                        print(f"  🚨 VIOLATION: {violation}")
            
            # Display frame
            cv2.imshow('Live Proctoring Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Live proctoring test completed")
        
    except Exception as e:
        print(f"❌ Live proctoring test failed: {e}")

if __name__ == "__main__":
    test_proctoring_integration()
    
    # Uncomment to test live proctoring
    # test_live_proctoring()