import cv2
import sys
import os
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_live_test():
    print("Initializing Proctoring System...")
    # Change to False to test the complex suite later if needed
    USE_SIMPLE = False
    
    if USE_SIMPLE:
        try:
            from simple_core import SimpleProctoringSystem
            system = SimpleProctoringSystem()
            print("Using SimpleProctoringSystem")
        except ImportError:
            print("Failed to import SimpleProctoringSystem")
            return
    else:
        try:
            # Import directly from local file
            from core import ProctoringSuite
            system = ProctoringSuite()
            print("Using ProctoringSuite (Complex)")
        except ImportError as e:
            print(f"Import error: {e}")
            return

    print("Select Test Mode:")
    print("1. Face Detection")
    print("2. Gaze Detection")
    print("3. Object Detection")
    print("4. All Features")
    
    try:
        choice = input("Enter choice (1-4): ").strip()
    except KeyboardInterrupt:
        return

    display_mode = 'all'
    if choice == '1': display_mode = 'face'
    elif choice == '2': display_mode = 'gaze'
    elif choice == '3': display_mode = 'object'
    elif choice == '4': display_mode = 'all'
    else:
        print("Invalid choice, defaulting to ALL")
        display_mode = 'all'

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    
    # Track whether test is terminated
    terminated = False
    
    print(f"Starting test in mode: {display_mode.upper()}")
    print("Press 'q' to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to look frame")
                break

            # If terminated, show termination screen
            if terminated:
                # Create red overlay
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), -1)
                cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
                
                cv2.putText(frame, "TEST TERMINATED", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)
                cv2.putText(frame, "Too many violations", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'q' to exit", (200, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
                
                cv2.imshow('Live Proctoring Test', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue

            # Process the frame
            results = system.process_frame(frame)
            
            # Get warning count
            warning_count = 0
            if hasattr(system, 'warning_count'):
                warning_count = system.warning_count
            elif 'total_violations' in results:
                 warning_count = results['total_violations']

            # Check termination condition
            if warning_count >= 3:
                terminated = True
                print("Test Terminated due to excessive warnings.")
                continue

            # Draw results based on display mode
            if display_mode == 'all' and 'annotated_frame' in results and not USE_SIMPLE:
                frame = results['annotated_frame']
            else:
                # Custom feature drawing
                if display_mode == 'face':
                    for (x, y, w, h) in results.get('faces', []):
                         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Faces: {results.get('face_count', 0)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                elif display_mode == 'gaze':
                     gaze_dir = results.get('gaze_direction', 'Unknown')
                     blink = results.get('blink_status', 'Unknown')
                     cv2.putText(frame, f"Gaze: {gaze_dir}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                     cv2.putText(frame, f"Blink: {blink}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                     
                     # Show looking away counter if available
                     if hasattr(system, 'looking_away_frames'):
                         frames_away = system.looking_away_frames
                         color = (0, 255, 0)
                         if frames_away > 5: color = (0, 165, 255)
                         if frames_away > 9: color = (0, 0, 255)
                         cv2.putText(frame, f"Away Frames: {frames_away}/10", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                elif display_mode == 'object':
                    for obj in results.get('objects', []):
                        bbox = obj['bbox']
                        x1, y1, x2, y2 = map(int, bbox)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(frame, f"{obj['class']}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Always show violations
            if 'violations' in results and results['violations']:
                y_text = 120
                for v in results['violations']:
                    cv2.putText(frame, v, (10, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    y_text += 30

            # Draw persistent Warning Counter
            color = (0, 255, 0) # Green
            if warning_count == 1: color = (0, 255, 255) # Yellow
            elif warning_count >= 2: color = (0, 0, 255) # Red
            
            cv2.putText(frame, f"WARNINGS: {warning_count}/3", (frame.shape[1] - 250, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # --- CONSOLE LOGGING ---
            # 1. Log new violations immediately
            if 'violations' in results and results['violations']:
                timestamp = time.strftime("%H:%M:%S")
                for v in results['violations']:
                    print(f"[{timestamp}] ⚠️  {v}")
            
            # 2. Log periodic status (every 30 frames ~ 1 sec)
            current_frame = getattr(system, 'frame_count', 0)
            if current_frame % 30 == 0:
                timestamp = time.strftime("%H:%M:%S")
                faces = results.get('face_count', 0)
                gaze = results.get('gaze_direction', 'N/A')
                blink = results.get('blink_status', 'N/A')
                objects_detected = len(results.get('objects', []))
                
                log_msg = f"[{timestamp}] ℹ️  Faces: {faces} | Gaze: {gaze} | Blink: {blink} | Objects: {objects_detected} | Warnings: {warning_count}/3"
                if display_mode == 'gaze' or True: # Always show Gaze buffer info per user request for detailed logs
                     log_msg += f" | AwayFrames: {getattr(system, 'looking_away_frames', 0)}"
                print(log_msg)
            # -----------------------

            # Mode indicator
            cv2.putText(frame, f"Mode: {display_mode.upper()}", (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow('Live Proctoring Test', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            # Removed keyboard toggles to rely on menu selection as requested
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_live_test()