"""
AI-Powered Interview Proctoring System
Integrates face detection, blink detection, mouth tracking, head pose estimation, and object detection
"""

# import cv2
import numpy as np
import mediapipe as mp
import threading
import queue
import time
import json
from datetime import datetime
from math import hypot
from ultralytics import YOLO
import logging

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProctoringSuite:
    """Main proctoring system that combines all detection modules"""
    
    def __init__(self):
        try:
            global cv2, mp, np
            import cv2
            import mediapipe as mp
            import numpy as np
            self.initialize_models()
            self.initialized = True
        except Exception as e:
            print(f"Failed to initialize CV models: {e}")
            logger.error(f"Failed to initialize CV models: {e}")
            self.initialized = False
            # Initialize attributes to None to avoid AttributeError later
            self.face_mesh = None
            self.yolo_model = None
            
        self.reset_session()
        
    def initialize_models(self):
        """Initialize all AI models and detectors"""
        try:
            # Face detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
            
            # MediaPipe Face Mesh
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            # Object detection (YOLOv8)
            try:
                import os
                base_path = os.path.dirname(os.path.abspath(__file__))
                model_path = os.path.join(base_path, 'yolov8n.pt')
                self.yolo_model = YOLO(model_path)
            except:
                logger.warning("YOLOv8 model not found, object detection disabled")
                self.yolo_model = None
            
            # Head pose estimation
            self.setup_head_pose()
            
            logger.info("All proctoring models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    def setup_head_pose(self):
        """Setup head pose estimation parameters"""
        self.model_points = np.array([
            (0.0, 0.0, 0.0),            # Nose tip
            (0.0, -330.0, -65.0),       # Chin
            (-255.0, 170.0, -135.0),    # Left eye left corner
            (225.0, 170.0, -135.0),     # Right eye right corner
            (-150.0, -150.0, -125.0),   # Left mouth corner
            (150.0, -150.0, -125.0)     # Right mouth corner
        ])
        
        # Camera parameters
        self.focal_length = 640
        self.center = (320, 240)
        self.camera_matrix = np.array([
            [self.focal_length, 0, self.center[0]],
            [0, self.focal_length, self.center[1]],
            [0, 0, 1]
        ], dtype="double")
    
    def reset_session(self):
        """Reset session variables"""
        self.violations = []
        self.warnings = []
        self.warning_count = 0
        self.max_warnings = 3
        self.session_start = datetime.now()
        self.frame_count = 0
        self.face_absent_frames = 0
        self.multiple_face_frames = 0
        self.looking_away_frames = 0
        self.mouth_open_frames = 0
        self.suspicious_object_frames = 0
        self.last_warning_time = 0
        self.warning_cooldown = 2  # 2 seconds between warnings
        
        # Thresholds (optimized for interview proctoring)
        self.face_absent_threshold = 60  # 2 seconds
        self.multiple_face_threshold = 30  # 1 second
        self.looking_away_threshold = 10  # 10 frames (approx 0.33s)
        self.mouth_open_threshold = 90  # 3 seconds
        self.suspicious_object_threshold = 15  # 0.5 seconds
    
    def detect_faces(self, frame):
        """Detect faces using Haar Cascade"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Primary detection
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
            )
            
            # Fallback to profile detection
            if len(faces) == 0:
                faces = self.profile_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
                )
            
            # Filter overlapping faces
            faces = self.filter_overlapping_faces(faces)
            
            return faces
            
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []
    
    def filter_overlapping_faces(self, faces):
        """Remove overlapping face detections"""
        if len(faces) <= 1:
            return faces
        
        faces_sorted = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        filtered = []
        
        for (x1, y1, w1, h1) in faces_sorted:
            is_duplicate = False
            for (x2, y2, w2, h2) in filtered:
                # Calculate IoU
                x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                overlap_area = x_overlap * y_overlap
                
                union_area = w1 * h1 + w2 * h2 - overlap_area
                iou = overlap_area / union_area if union_area > 0 else 0
                
                if iou > 0.3:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append((x1, y1, w1, h1))
        
        return filtered
    
    def detect_blinks_and_gaze(self, frame):
        """Detect blinks and gaze direction using MediaPipe"""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(frame_rgb)
            
            if not results.multi_face_landmarks:
                return {"blink": "No face", "gaze": "No face", "mesh_results": None}
            
            h, w, c = frame.shape
            
            for face_landmarks in results.multi_face_landmarks:
                # Blink detection
                blink_status = self.calculate_blink_ratio(face_landmarks, w, h)
                
                # Gaze detection
                gaze_direction, gaze_ratio = self.calculate_gaze_direction(face_landmarks, w, h)
                
                return {
                    "blink": blink_status,
                    "gaze": gaze_direction,
                    "gaze_ratio": gaze_ratio,
                    "mesh_results": results
                }
            
            return {"blink": "No face", "gaze": "No face", "mesh_results": results}
            
        except Exception as e:
            logger.error(f"Blink/Gaze detection error: {e}")
            return {"blink": "Error", "gaze": "Error", "mesh_results": None}
    
    def calculate_blink_ratio(self, face_landmarks, w, h):
        """Calculate eye aspect ratio for blink detection"""
        try:
            # Left eye landmarks
            left_eye_points = [33, 133, 159, 145, 163, 144]
            left_coords = [(int(face_landmarks.landmark[i].x * w), 
                           int(face_landmarks.landmark[i].y * h)) for i in left_eye_points]
            
            # Right eye landmarks
            right_eye_points = [362, 263, 386, 374, 390, 373]
            right_coords = [(int(face_landmarks.landmark[i].x * w), 
                            int(face_landmarks.landmark[i].y * h)) for i in right_eye_points]
            
            # Calculate ratios
            left_ratio = self.eye_aspect_ratio(left_coords)
            right_ratio = self.eye_aspect_ratio(right_coords)
            
            if left_ratio >= 3.6 or right_ratio >= 3.6:
                return "Blink"
            else:
                return "No Blink"
                
        except Exception as e:
            return "Error"
    
    def eye_aspect_ratio(self, eye_coords):
        """Calculate eye aspect ratio"""
        try:
            # Horizontal distance
            horizontal = hypot(eye_coords[0][0] - eye_coords[1][0], 
                             eye_coords[0][1] - eye_coords[1][1])
            
            # Vertical distances
            vertical1 = hypot(eye_coords[2][0] - eye_coords[5][0], 
                             eye_coords[2][1] - eye_coords[5][1])
            vertical2 = hypot(eye_coords[3][0] - eye_coords[4][0], 
                             eye_coords[3][1] - eye_coords[4][1])
            
            vertical = (vertical1 + vertical2) / 2.0
            
            if vertical > 0:
                return horizontal / vertical
            return 0
            
        except:
            return 0
    
    def calculate_gaze_direction(self, face_landmarks, w, h):
        """Calculate gaze direction using eye landmarks"""
        try:
            # Iris landmarks (requires refine_landmarks=True)
            left_iris = face_landmarks.landmark[468]
            right_iris = face_landmarks.landmark[473]
            
            # Get eye corners for specific gaze tracking
            # Left Eye: 33 (Inner), 133 (Outer) - wait, 33 is Right (inner) of left eye, 133 is Left (outer)?
            # MediaPipe Mesh: 33 is query (inner corner of left eye), 133 is outer corner
            
            # Calculate horizontal gaze ratio
            ctr_left, _ = self.get_gaze_ratio(face_landmarks.landmark[33], face_landmarks.landmark[133], left_iris, w, h)
            ctr_right, _ = self.get_gaze_ratio(face_landmarks.landmark[362], face_landmarks.landmark[263], right_iris, w, h)
            
            gaze_ratio = (ctr_left + ctr_right) / 2
            
            # logger.info(f"Gaze Ratio: {gaze_ratio:.2f}")
            
            if gaze_ratio < 0.45:
                direction = "Right"
            elif gaze_ratio > 0.55:
                direction = "Left"
            else:
                direction = "Center"
            
            # Print debug for user
            print(f"DEBUG: Gaze Ratio: {gaze_ratio:.3f} | Direction: {direction}")
            
            return direction, gaze_ratio
        except Exception as e:
            # logger.error(f"Gaze calc error: {e}")
            return "Unknown", 0.5
        except:
            return "Error"
    
    def get_eye_center(self, face_landmarks, eye_points, w, h):
        """Get center point of eye"""
        try:
            coords = [(int(face_landmarks.landmark[i].x * w), 
                      int(face_landmarks.landmark[i].y * h)) for i in eye_points]
            
            center_x = sum(coord[0] for coord in coords) // len(coords)
            center_y = sum(coord[1] for coord in coords) // len(coords)
            
            return (center_x, center_y)
        except:
            return None
    

            
    def get_gaze_ratio(self, inner_point, outer_point, iris_point, w, h):
        """Calculate relative position of iris between eye corners"""
        try:
            # Convert to pixels
            in_p = np.array([int(inner_point.x * w), int(inner_point.y * h)])
            out_p = np.array([int(outer_point.x * w), int(outer_point.y * h)])
            iris_p = np.array([int(iris_point.x * w), int(iris_point.y * h)])
            
            # Distance of eye width
            eye_width = np.linalg.norm(in_p - out_p)
            if eye_width == 0: return 0.5, 0.5
            
            # Distance of iris from inner corner
            iris_dist = np.linalg.norm(in_p - iris_p)
            
            # Ratio
            ratio = iris_dist / eye_width
            return ratio, 0  # Only returning horizontal for now
        except Exception as e:
            # logger.error(f"Gaze ratio error: {e}")
            return 0.5, 0.5

    def detect_objects(self, frame):
        """Detect objects using YOLO"""
        if not self.yolo_model:
            return [], []
        
        try:
            results = self.yolo_model(frame, verbose=False, conf=0.2)
            objects = []
            suspicious_objects = []
            
            # Suspicious items that should trigger immediate warnings
            phone_keywords = ['cell phone', 'mobile phone', 'smartphone', 'phone', 'iphone', 'android']
            device_keywords = ['laptop', 'computer', 'tablet', 'ipad', 'book', 'notebook']
            
            # Track person count from YOLO
            person_count = 0
            
            for result in results:
                if result.boxes is not None:
                    # logger.info(f"YOLO detections: {len(result.boxes)}")
                    for box in result.boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = self.yolo_model.names[class_id].lower()
                        print(f"DEBUG: Detected {class_name} with confidence {confidence:.2f}")
                        
                        # Filter low confidence general objects
                        if confidence > 0.2: 
                            objects.append({
                                'class': class_name,
                                'confidence': confidence,
                                'bbox': box.xyxy[0].tolist()
                            })
                            
                            # Check for phones (highest priority)
                            if any(keyword in class_name for keyword in phone_keywords):
                                suspicious_objects.append(f"Mobile phone detected (confidence: {confidence:.2f})")
                            
                            # Check for other devices
                            elif any(keyword in class_name for keyword in device_keywords):
                                suspicious_objects.append(f"{class_name.title()} detected (confidence: {confidence:.2f})")
                            
                            # Count people (Strict threshold to avoid hands/phones/clothes being detected as people)
                            elif class_name == 'person' and confidence > 0.6:
                                person_count += 1
            
            # Only flag additional person if we see MORE THAN ONE person
            # Note: This might be tricky if the user is close and YOLO detects 1 person (the user).
            # Safety margin: if person_count > 1, then flag.
            if person_count > 1:
                 suspicious_objects.append(f"Multiple people detected ({person_count})")
            
            return objects, suspicious_objects
        except Exception as e:
            logger.error(f"Object detection error: {e}")
            return [], []
    
    def process_frame(self, frame):
        """Process a single frame for all detections"""
        if not getattr(self, 'initialized', False):
            return {'error': 'Proctoring system failed to initialize. Check logs.'}

        try:
            self.frame_count += 1
            # Face detection
            faces = self.detect_faces(frame)
            face_count = len(faces)
            
            # Blink and gaze detection
            blink_gaze = self.detect_blinks_and_gaze(frame)
            
            # Object detection
            objects, suspicious_objects = self.detect_objects(frame)
            
            # Analyze violations
            violations = self.analyze_violations(face_count, blink_gaze, suspicious_objects)
            
            # Create annotated frame
            annotated_frame = self.annotate_frame(frame, faces, blink_gaze, objects)
            
            return {
                'face_count': face_count,
                'faces': faces,
                'blink_status': blink_gaze['blink'],
                'gaze_direction': blink_gaze['gaze'],
                'gaze_ratio': blink_gaze.get('gaze_ratio', 0.5),
                'objects': objects,
                'suspicious_objects': suspicious_objects,
                'violations': violations,
                'annotated_frame': annotated_frame,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return {'error': str(e)}
    
    def analyze_violations(self, face_count, blink_gaze, suspicious_objects):
        """Analyze frame for violations"""
        violations = []
        current_time = time.time()
        
        # Face count violations
        if face_count == 0:
            self.face_absent_frames += 1
            if self.face_absent_frames > self.face_absent_threshold:
                violations.append("⚠️ VIOLATION: No face detected - please stay in camera view")
        else:
            self.face_absent_frames = 0
        
        if face_count > 1:
            self.multiple_face_frames += 1
            if self.multiple_face_frames > self.multiple_face_threshold:
                violations.append("⚠️ VIOLATION: Multiple people detected - ensure you're alone")
        else:
            self.multiple_face_frames = 0
        
        # Gaze violations
        if blink_gaze['gaze'] in ['Left', 'Right']:
            self.looking_away_frames += 1
            if self.looking_away_frames > self.looking_away_threshold:
                violations.append("⚠️ VIOLATION: Looking away from camera - maintain eye contact")
        else:
            self.looking_away_frames = 0
        
        if suspicious_objects:
            for obj in suspicious_objects:
                if 'phone' in obj.lower():
                    # Immediate violation for phones
                    violations.append(f"🚨 CRITICAL VIOLATION: {obj} - Remove device immediately!")
                    # Warning count handled below
                else:
                    # Regular threshold for other objects
                    self.suspicious_object_frames += 1
                    if self.suspicious_object_frames > 3:
                        violations.append(f"⚠️ VIOLATION: {obj}")
        else:
            self.suspicious_object_frames = 0
            
        # General Warning Handling (Unified for "3 strikes" rule)
        if violations:
            # Check cooldown
            if (current_time - self.last_warning_time) > self.warning_cooldown:
                self.warning_count += 1  # Increment by 1 regardless of number of simultaneous violations
                self.last_warning_time = current_time
                self.warnings.extend(violations)
                
                # Log violations internally
                for violation in violations:
                   logger.warning(f"PROCTORING VIOLATION: {violation}")
                logger.warning(f"PROCTORING VIOLATION: {violation}")
        
        return violations
    
    def annotate_frame(self, frame, faces, blink_gaze, objects):
        """Annotate frame with detection results"""
        try:
            annotated = frame.copy()
            
            # Draw face rectangles
            for (x, y, w, h) in faces:
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(annotated, 'Face', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Draw object bounding boxes
            for obj in objects:
                bbox = obj['bbox']
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(annotated, f"{obj['class']} {obj['confidence']:.2f}", 
                           (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            # Add status text
            cv2.putText(annotated, f"Gaze: {blink_gaze['gaze']}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(annotated, f"Faces: {len(faces)}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            return annotated
        except Exception as e:
            logger.error(f"Frame annotation error: {e}")
            return frame
    
    def get_session_summary(self):
        """Get summary of proctoring session"""
        duration = (datetime.now() - self.session_start).total_seconds()
        
        return {
            'session_duration': duration,
            'total_violations': len(self.violations),
            'warning_count': self.warning_count,
            'violations': self.violations,
            'session_start': self.session_start.isoformat(),
            'session_end': datetime.now().isoformat()
        }