"""
Simplified Real-Time Proctoring System
Focuses on reliable integration with live camera feed
"""

# import cv2
import numpy as np
import time
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SimpleProctoringSystem:
    """Simplified proctoring system for reliable real-time processing"""
    
    def __init__(self):
        self.violations = []
        self.session_start = datetime.now()
        self.frame_count = 0
        self.violation_count = 0
        
        # Initialize face detection
        try:
            global cv2
            import cv2
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.initialized = True
            logger.info("Simple proctoring system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            self.initialized = False
    
    def process_frame(self, frame):
        """Process frame for violations"""
        if not self.initialized:
            return {'error': 'System not initialized'}
        
        self.frame_count += 1
        violations = []
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=3, minSize=(40, 40)
            )
            
            face_count = len(faces)
            
            # Check violations - more sensitive
            if face_count == 0:
                violations.append("🚨 CRITICAL: No face detected - Stay in camera view")
            elif face_count > 1:
                violations.append("🚨 VIOLATION: Multiple people detected - You must be alone")
            
            # Enhanced phone detection using multiple methods
            phone_detected = self.detect_phones_enhanced(frame, gray)
            if phone_detected:
                violations.append("🚨 CRITICAL VIOLATION: PHONE/DEVICE DETECTED - Remove immediately")
            
            # Simple object detection using color detection
            suspicious_objects = self.detect_rectangular_objects(frame)
            if suspicious_objects > 2:  # More than 2 rectangular objects
                violations.append(f"⚠️ Multiple suspicious objects detected - Remove unauthorized items")
            
            # Store violations
            if violations:
                self.violation_count += len(violations)
                self.violations.extend([{
                    'timestamp': datetime.now().isoformat(),
                    'frame': self.frame_count,
                    'violation': v
                } for v in violations])
            
            return {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'frame_count': self.frame_count,
                'face_count': face_count,
                'faces': [{'x': x, 'y': y, 'w': w, 'h': h} for x, y, w, h in faces],
                'violations': violations,
                'total_violations': self.violation_count,
                'processing_time': time.time(),
                'phone_detected': phone_detected,
                'suspicious_objects': suspicious_objects
            }
            
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return {'error': str(e)}
    
    def detect_phones_enhanced(self, frame, gray):
        """Enhanced phone detection using multiple techniques"""
        try:
            import cv2
            # Method 1: Dark rectangular objects (phones are usually dark)
            _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                area = w * h
                
                # Phone-like characteristics: rectangular, medium size, dark
                if (0.3 < aspect_ratio < 3.0) and (2000 < area < 80000):
                    # Additional check: is it in hand region (lower part of frame)
                    frame_height = frame.shape[0]
                    if y > frame_height * 0.3:  # Lower 70% of frame
                        return True
            
            # Method 2: Edge detection for phone outlines
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                if cv2.contourArea(contour) > 1500:
                    # Approximate contour to polygon
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # Rectangular objects with 4 corners (phones/tablets)
                    if len(approx) == 4:
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h if h > 0 else 0
                        if 0.4 < aspect_ratio < 2.5:  # Phone aspect ratios
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Enhanced phone detection error: {e}")
            return False
    def detect_rectangular_objects(self, frame):
        """Simple rectangular object detection (phones, tablets)"""
        try:
            import cv2
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            rectangular_objects = 0
            
            for contour in contours:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if it's rectangular and of reasonable size (possible phone/device)
                aspect_ratio = w / h if h > 0 else 0
                area = w * h
                
                # Phone-like dimensions and size
                if (0.4 < aspect_ratio < 2.5) and (1000 < area < 50000):
                    rectangular_objects += 1
            
            return rectangular_objects
            
        except Exception as e:
            logger.error(f"Object detection error: {e}")
            return 0
    
    def get_session_summary(self):
        """Get session summary"""
        duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            'session_duration': duration,
            'total_frames': self.frame_count,
            'total_violations': self.violation_count,
            'violations': self.violations[-10:],  # Last 10 violations
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat()
        }