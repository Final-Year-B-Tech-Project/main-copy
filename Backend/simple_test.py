#!/usr/bin/env python3
"""
Simple Proctoring Test - Basic OpenCV and YOLO only
"""

import cv2
import numpy as np
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_opencv():
    """Test OpenCV face detection"""
    logger.info("Testing OpenCV face detection...")
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    if face_cascade.empty():
        logger.error("❌ Failed to load face cascade")
        return False
    
    logger.info("✅ Face cascade loaded")
    
    # Test camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("❌ Cannot access camera")
        return False
    
    logger.info("✅ Camera accessible")
    
    # Capture and test detection
    ret, frame = cap.read()
    if not ret:
        logger.error("❌ Cannot read frame")
        cap.release()
        return False
    
    logger.info(f"✅ Frame captured: {frame.shape}")
    
    # Test face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
    
    logger.info(f"✅ Face detection result: {len(faces)} faces found")
    
    # Draw faces and save
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        logger.info(f"  Face at: x={x}, y={y}, w={w}, h={h}")
    
    cv2.imwrite('opencv_test.jpg', frame)
    logger.info("✅ Test image saved as opencv_test.jpg")
    
    cap.release()
    return True

def test_yolo():
    """Test YOLO object detection"""
    logger.info("Testing YOLO object detection...")
    
    try:
        from ultralytics import YOLO
        
        # Check if model exists
        model_path = 'proctoring_system/yolov8n.pt'
        if not os.path.exists(model_path):
            logger.error(f"❌ YOLO model not found at {model_path}")
            return False
        
        logger.info("✅ YOLO model file found")
        
        # Load model
        model = YOLO(model_path)
        logger.info("✅ YOLO model loaded")
        
        # Test camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("❌ Cannot access camera")
            return False
        
        # Capture frame
        ret, frame = cap.read()
        if not ret:
            logger.error("❌ Cannot read frame")
            cap.release()
            return False
        
        logger.info(f"✅ Frame captured for YOLO: {frame.shape}")
        
        # Run detection
        results = model(frame, verbose=False, conf=0.3)
        
        objects_found = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    label = model.names[class_id]
                    objects_found.append((label, confidence))
                    logger.info(f"  Object: {label} (confidence: {confidence:.2f})")
        
        logger.info(f"✅ YOLO detection result: {len(objects_found)} objects found")
        
        cap.release()
        return True
        
    except Exception as e:
        logger.error(f"❌ YOLO test failed: {e}")
        return False

def test_live_detection():
    """Test live detection with OpenCV only"""
    logger.info("Starting live detection test (OpenCV only)...")
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Load YOLO if available
    yolo_model = None
    try:
        from ultralytics import YOLO
        if os.path.exists('proctoring_system/yolov8n.pt'):
            yolo_model = YOLO('proctoring_system/yolov8n.pt')
            logger.info("✅ YOLO model loaded for live test")
    except:
        logger.warning("⚠️ YOLO not available for live test")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("❌ Cannot access camera for live test")
        return
    
    logger.info("🎥 Live detection started. Press 'q' to quit, 'm' to test mobile detection")
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Process every 30th frame
        if frame_count % 30 == 0:
            logger.info(f"\n--- Processing Frame {frame_count} ---")
            
            # Face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
            
            logger.info(f"Faces detected: {len(faces)}")
            
            # Draw faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Face", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Object detection
            if yolo_model:
                try:
                    results = yolo_model(frame, verbose=False, conf=0.3)
                    objects = []
                    suspicious = []
                    
                    for result in results:
                        boxes = result.boxes
                        if boxes is not None:
                            for box in boxes:
                                class_id = int(box.cls[0])
                                confidence = float(box.conf[0])
                                label = yolo_model.names[class_id]
                                objects.append((label, confidence))
                                
                                # Check for mobile/phone
                                if 'phone' in label.lower() or 'cell' in label.lower():
                                    suspicious.append((label, confidence))
                                    logger.warning(f"🚨 MOBILE DETECTED: {label} (confidence: {confidence:.2f})")
                    
                    logger.info(f"Objects: {len(objects)}, Suspicious: {len(suspicious)}")
                    
                    if suspicious:
                        cv2.putText(frame, "MOBILE DETECTED!", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                except Exception as e:
                    logger.error(f"YOLO error: {e}")
        
        # Add status text
        cv2.putText(frame, f"Faces: {len(faces) if 'faces' in locals() else 0}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, "Press 'q' to quit, 'm' for mobile test", (10, frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show frame
        cv2.imshow('Simple Proctoring Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('m'):
            logger.info("📱 Hold up a mobile phone to test detection...")
    
    cap.release()
    cv2.destroyAllWindows()
    logger.info("Live test completed")

def main():
    logger.info("🚀 Starting Simple Proctoring Test")
    logger.info("=" * 50)
    
    # Test 1: OpenCV
    if not test_opencv():
        logger.error("OpenCV test failed")
        return
    
    # Test 2: YOLO
    if not test_yolo():
        logger.warning("YOLO test failed, but continuing...")
    
    # Test 3: Live detection
    print("\nChoose test:")
    print("1. Live detection test")
    print("2. Exit")
    
    choice = input("Enter choice (1-2): ").strip()
    
    if choice == '1':
        test_live_detection()
    
    logger.info("🏁 Simple test completed")

if __name__ == "__main__":
    main()