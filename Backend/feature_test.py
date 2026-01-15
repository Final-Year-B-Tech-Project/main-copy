#!/usr/bin/env python3
"""
Comprehensive Proctoring Features Test
Tests each detection feature individually with detailed logging
"""

import cv2
import numpy as np
import sys
import os
import logging
from datetime import datetime

# Setup detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_face_detection():
    """Test Face Detection - detect_faces() method"""
    logger.info("=" * 50)
    logger.info("TESTING FACE DETECTION")
    logger.info("=" * 50)
    
    try:
        # Load face cascades
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        
        if face_cascade.empty() or profile_cascade.empty():
            logger.error("❌ Failed to load face cascades")
            return False
        
        logger.info("✅ Face cascades loaded successfully")
        
        # Test with camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("❌ Cannot access camera")
            return False
        
        logger.info("📷 Camera opened. Testing face detection...")
        logger.info("Instructions: Look at camera, then turn left/right to test profile detection")
        
        frame_count = 0
        while frame_count < 100:  # Test for ~3 seconds at 30fps
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Test every 10th frame
            if frame_count % 10 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Frontal face detection
                frontal_faces = face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
                )
                
                # Profile face detection
                profile_faces = profile_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
                )
                
                total_faces = len(frontal_faces) + len(profile_faces)
                
                logger.info(f"Frame {frame_count}: Frontal={len(frontal_faces)}, Profile={len(profile_faces)}, Total={total_faces}")
                
                # Draw detections
                for (x, y, w, h) in frontal_faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, "Frontal", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                for (x, y, w, h) in profile_faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(frame, "Profile", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                
                # Status text
                cv2.putText(frame, f"Faces: {total_faces}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "Face Detection Test", (10, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Face Detection Test', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        logger.info("✅ Face detection test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Face detection test failed: {e}")
        return False

def test_object_detection():
    """Test Object Detection for mobile phones"""
    logger.info("=" * 50)
    logger.info("TESTING OBJECT DETECTION")
    logger.info("=" * 50)
    
    try:
        from ultralytics import YOLO
        
        # Check model
        model_path = 'proctoring_system/yolov8n.pt'
        if not os.path.exists(model_path):
            logger.error(f"❌ YOLO model not found at {model_path}")
            return False
        
        model = YOLO(model_path)
        logger.info("✅ YOLO model loaded")
        
        # Test with camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("❌ Cannot access camera")
            return False
        
        logger.info("📱 Camera opened. Testing object detection...")
        logger.info("Instructions: Hold up a mobile phone, book, or other objects")
        
        frame_count = 0
        mobile_detected = False
        
        while frame_count < 150:  # Test for ~5 seconds
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Test every 15th frame (every 0.5 seconds)
            if frame_count % 15 == 0:
                logger.info(f"Processing frame {frame_count}...")
                
                # Run YOLO detection
                results = model(frame, verbose=False, conf=0.3, imgsz=320)
                
                objects_found = []
                suspicious_objects = []
                
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            class_id = int(box.cls[0])
                            confidence = float(box.conf[0])
                            label = model.names[class_id]
                            
                            objects_found.append((label, confidence))
                            
                            # Check for suspicious objects
                            suspicious_keywords = ['phone', 'cell', 'mobile', 'book', 'laptop', 'tablet']
                            if any(keyword in label.lower() for keyword in suspicious_keywords):
                                suspicious_objects.append((label, confidence))
                                if 'phone' in label.lower() or 'cell' in label.lower():
                                    mobile_detected = True
                                    logger.warning(f"🚨 MOBILE PHONE DETECTED: {label} (confidence: {confidence:.2f})")
                
                logger.info(f"Objects found: {len(objects_found)}")
                for obj, conf in objects_found:
                    logger.info(f"  - {obj}: {conf:.2f}")
                
                if suspicious_objects:
                    logger.warning(f"⚠️ Suspicious objects: {len(suspicious_objects)}")
                
                # Draw results on frame
                cv2.putText(frame, f"Objects: {len(objects_found)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                if suspicious_objects:
                    cv2.putText(frame, "SUSPICIOUS OBJECT!", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(frame, f"Count: {len(suspicious_objects)}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                cv2.putText(frame, "Object Detection Test", (10, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Object Detection Test', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if mobile_detected:
            logger.info("✅ Object detection test completed - Mobile phone detected!")
        else:
            logger.info("✅ Object detection test completed - No mobile phone detected")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Object detection test failed: {e}")
        return False

def test_basic_gaze_detection():
    """Test basic gaze detection using simple eye position"""
    logger.info("=" * 50)
    logger.info("TESTING BASIC GAZE DETECTION")
    logger.info("=" * 50)
    
    try:
        # Load face and eye cascades
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        if face_cascade.empty() or eye_cascade.empty():
            logger.error("❌ Failed to load cascades")
            return False
        
        logger.info("✅ Face and eye cascades loaded")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("❌ Cannot access camera")
            return False
        
        logger.info("👀 Camera opened. Testing gaze detection...")
        logger.info("Instructions: Look left, right, and center")
        
        frame_count = 0
        while frame_count < 100:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            if frame_count % 10 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                gaze_direction = "Unknown"
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    # Detect eyes within face region
                    roi_gray = gray[y:y+h, x:x+w]
                    eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                    
                    if len(eyes) >= 2:
                        # Sort eyes by x position
                        eyes = sorted(eyes, key=lambda e: e[0])
                        
                        # Get eye centers
                        left_eye = eyes[0]
                        right_eye = eyes[1] if len(eyes) > 1 else eyes[0]
                        
                        left_center = (x + left_eye[0] + left_eye[2]//2, y + left_eye[1] + left_eye[3]//2)
                        right_center = (x + right_eye[0] + right_eye[2]//2, y + right_eye[1] + right_eye[3]//2)
                        
                        # Simple gaze estimation based on eye position relative to face
                        face_center_x = x + w//2
                        eyes_center_x = (left_center[0] + right_center[0]) // 2
                        
                        if eyes_center_x < face_center_x - 10:
                            gaze_direction = "Looking Left"
                        elif eyes_center_x > face_center_x + 10:
                            gaze_direction = "Looking Right"
                        else:
                            gaze_direction = "Looking Forward"
                        
                        # Draw eyes
                        cv2.circle(frame, left_center, 5, (0, 255, 0), -1)
                        cv2.circle(frame, right_center, 5, (0, 255, 0), -1)
                    
                    logger.info(f"Frame {frame_count}: Gaze = {gaze_direction}")
                
                cv2.putText(frame, f"Gaze: {gaze_direction}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "Gaze Detection Test", (10, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Gaze Detection Test', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        logger.info("✅ Basic gaze detection test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Gaze detection test failed: {e}")
        return False

def test_violation_system():
    """Test violation detection and warning system"""
    logger.info("=" * 50)
    logger.info("TESTING VIOLATION SYSTEM")
    logger.info("=" * 50)
    
    # Simulate violations
    violations = []
    warning_count = 0
    max_warnings = 3
    
    # Test scenarios
    test_scenarios = [
        "Multiple people detected",
        "Mobile phone detected", 
        "Looking away from screen"
    ]
    
    for scenario in test_scenarios:
        warning_count += 1
        violation_data = {
            'timestamp': datetime.now().isoformat(),
            'violation': scenario,
            'warning_number': warning_count,
            'severity': 'high' if 'phone' in scenario or 'Multiple' in scenario else 'medium'
        }
        violations.append(violation_data)
        
        logger.warning(f"⚠️ WARNING {warning_count}/{max_warnings}: {scenario}")
        
        if warning_count >= max_warnings:
            logger.error("🚫 MAXIMUM WARNINGS REACHED - INTERVIEW WOULD BE TERMINATED")
            break
    
    logger.info(f"✅ Violation system test completed. Total violations: {len(violations)}")
    return True

def main():
    logger.info("🚀 Starting Comprehensive Proctoring Features Test")
    logger.info("=" * 60)
    
    print("\nSelect test to run:")
    print("1. Face Detection Test")
    print("2. Object Detection Test (Mobile/Phone)")
    print("3. Basic Gaze Detection Test")
    print("4. Violation System Test")
    print("5. Run All Tests")
    print("6. Exit")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == '1':
        test_face_detection()
    elif choice == '2':
        test_object_detection()
    elif choice == '3':
        test_basic_gaze_detection()
    elif choice == '4':
        test_violation_system()
    elif choice == '5':
        logger.info("Running all tests...")
        test_face_detection()
        test_object_detection()
        test_basic_gaze_detection()
        test_violation_system()
    elif choice == '6':
        logger.info("Exiting...")
        return
    else:
        logger.error("Invalid choice")
    
    logger.info("🏁 Test completed")

if __name__ == "__main__":
    main()