# Proctoring System Integration Setup Guide

## Overview
This guide will help you set up the integrated AI-powered proctoring system in your interview platform. The system includes:

- **Face Detection**: Monitors candidate presence and identity
- **Blink Detection**: Tracks natural eye movement patterns
- **Gaze Tracking**: Detects if candidate is looking away
- **Mouth Movement**: Identifies talking/communication attempts
- **Head Pose Estimation**: Monitors head orientation
- **Object Detection**: Identifies suspicious objects (phones, books, etc.)

## Prerequisites

1. **Python 3.8+** installed
2. **Camera access** for testing
3. **Sufficient system resources** (recommended: 8GB RAM, modern CPU)

## Installation Steps

### 1. Install Dependencies

```bash
# Navigate to your project directory
cd /Users/deepakshinde/Desktop/mock/main-copy/Backend

# Install the updated requirements
pip install -r requirements.txt
```

### 2. Download Required Models

The system will automatically download required models on first run:
- **YOLOv8n model**: Already copied to your project
- **MediaPipe models**: Downloaded automatically
- **OpenCV Haar Cascades**: Included with OpenCV

### 3. Verify Installation

1. **Start your Flask application**:
   ```bash
   python app.py
   ```

2. **Test the proctoring system**:
   - Visit: `http://localhost:5000/api/proctoring/test_page`
   - Click "Test API" to verify all models are loaded
   - Click "Start Test" to test camera and detection

3. **Check the API endpoint**:
   - Visit: `http://localhost:5000/api/proctoring/test`
   - Should return JSON with success status and model information

## How It Works

### During Interview Flow

1. **Interview Start**:
   - Camera permission requested
   - Proctoring session initialized
   - Real-time monitoring begins

2. **Continuous Monitoring**:
   - Processes video frames every 2 seconds
   - Detects violations in real-time
   - Shows live camera feed to candidate

3. **Violation Detection**:
   - Face absent for >3 seconds
   - Multiple people detected
   - Looking away for >5 seconds
   - Talking detected for >3 seconds
   - Suspicious objects present for >2 seconds

4. **Interview End**:
   - Proctoring session stopped
   - Violation summary generated
   - Results stored in interview session

### Technical Architecture

```
Frontend (JavaScript)          Backend (Python)
├── Camera capture            ├── ProctoringSuite class
├── Frame processing          ├── Face detection (OpenCV)
├── Real-time alerts          ├── MediaPipe integration
└── Violation display         ├── YOLO object detection
                             └── Violation tracking
```

## Configuration Options

### Violation Thresholds (in `proctoring_system.py`)

```python
# Adjust these values based on your requirements
self.face_absent_threshold = 90      # 3 seconds at 30fps
self.multiple_face_threshold = 30    # 1 second
self.looking_away_threshold = 150    # 5 seconds
self.mouth_open_threshold = 90       # 3 seconds
self.suspicious_object_threshold = 60 # 2 seconds
```

### Frame Processing Rate (in `proctoring.js`)

```javascript
// Process frames every N milliseconds
this.frameProcessingRate = 2000; // 2 seconds
```

## Troubleshooting

### Common Issues

1. **Camera Not Working**:
   - Ensure browser has camera permissions
   - Check if camera is being used by another application
   - Try refreshing the page

2. **Models Not Loading**:
   - Check internet connection (for initial downloads)
   - Verify all dependencies are installed
   - Check console for specific error messages

3. **High CPU Usage**:
   - Reduce frame processing rate
   - Lower video resolution
   - Disable object detection if not needed

4. **False Positives**:
   - Adjust violation thresholds
   - Improve lighting conditions
   - Ensure stable camera position

### Performance Optimization

1. **For Lower-End Systems**:
   ```python
   # In proctoring_system.py, disable YOLO if needed
   self.yolo_model = None  # Disables object detection
   ```

2. **Reduce Processing Load**:
   ```javascript
   // In proctoring.js, increase interval
   this.frameProcessingRate = 5000; // Process every 5 seconds
   ```

## Security Features

### Data Privacy
- Video frames are processed locally
- No video data is permanently stored
- Only violation metadata is saved
- Camera feed visible only to candidate

### Violation Logging
- All violations timestamped
- Stored in interview session notes
- Available for HR review
- Exportable for compliance

## Testing Checklist

Before going live, test these scenarios:

- [ ] Camera permission granted/denied
- [ ] Single person detection works
- [ ] Multiple people trigger violation
- [ ] Looking away detection
- [ ] Object detection (hold up phone/book)
- [ ] Interview completion with proctoring data
- [ ] System works on different browsers
- [ ] Performance acceptable on target hardware

## Browser Compatibility

### Fully Supported
- Chrome 80+
- Edge 80+
- Safari 14+
- Firefox 75+

### Limited Support
- Older browsers may lack WebRTC support
- Mobile browsers have limited camera access

## API Endpoints

### Proctoring Routes
- `POST /api/proctoring/start` - Start proctoring session
- `POST /api/proctoring/stop` - Stop proctoring session
- `POST /api/proctoring/process_frame` - Process video frame
- `GET /api/proctoring/status` - Get session status
- `GET /api/proctoring/violations` - Get violations list
- `GET /api/proctoring/test` - Test system health
- `GET /api/proctoring/test_page` - Test interface

## Integration Points

### Database
- Violation data stored in `InterviewSession.notes`
- JSON format for easy parsing
- Includes session summary and violation list

### Frontend
- `proctoring.js` handles all client-side logic
- Integrates with existing interview interface
- Minimal changes to existing templates

### Backend
- `proctoring_system.py` - Core detection logic
- `proctoring_routes.py` - Flask API endpoints
- Registered in main Flask app

## Next Steps

1. **Test thoroughly** with the test page
2. **Adjust thresholds** based on your requirements
3. **Train your team** on the new features
4. **Monitor performance** in production
5. **Gather feedback** from users

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review console logs for errors
3. Test with the provided test page
4. Verify all dependencies are installed

The system is designed to be robust and fail gracefully - interviews will continue even if proctoring encounters issues.