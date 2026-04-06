# PROCTORED INTERVIEW SYSTEM - COMPLETE DOCUMENTATION

## Overview

This is a comprehensive proctored interview system with real-time face detection, violation tracking, deterministic scoring, and evidence-based reporting.

## Key Features

### ✅ Real Scoring System (NO Random Scores)
- **Deterministic**: All scores calculated from tracked metrics
- **Explainable**: Every score component is traceable
- **Weighted Formula**: 
  ```
  Final Score = (Technical × 0.40) + (Problem Solving × 0.25) + 
                (Communication × 0.15) + (Integrity × 0.10) + 
                (Engagement × 0.10)
  ```

### ✅ Face Detection (MediaPipe + TensorFlow.js)
- **1Hz Detection**: Runs once per second (low latency)
- **Pre-loaded Model**: Loaded before interview starts
- **Warm-up**: First frame processed for optimization
- **Instant Violations**: Popup within 1 second of face disappearance
- **Multiple Face Detection**: Immediate violation on detection

### ✅ Violation System
- **7 Violation Types**:
  1. Face not detected
  2. Multiple faces detected
  3. Fullscreen exit
  4. Tab switch
  5. Camera turned off
  6. DevTools attempt
  7. Page reload attempt

- **Auto-End Conditions**:
  - 7 violations reached
  - Camera disabled
  - Page reload

- **Integrity Score**: Starts at 100, -15 points per violation

### ✅ Proper Interview Termination
When interview ends:
- ✓ Face detection loop stopped
- ✓ Question timers stopped
- ✓ AI requests stopped
- ✓ UI locked
- ✓ Termination reason sent to backend
- ✓ Final scores calculated
- ✓ Report generated

### ✅ Comprehensive Report
Report includes:
1. **Candidate & Interview Metadata**
2. **Final Recommendation** (top of report)
3. **Score Breakdown** (with formula)
4. **Technical Assessment**
5. **Problem Solving Analysis**
6. **Communication Evaluation**
7. **Interview Integrity & Proctoring Report**
8. **Assessment Tracking & Engagement Metrics**
9. **Strengths**
10. **Improvement Areas**
11. **AI Decision Trace**
12. **Security & Compliance Disclaimer**

## File Structure

```
Backend Files/
├── static/
│   ├── js/
│   │   └── proctored_interview.js    # Main proctoring logic
│   └── css/
│       └── proctored_interview.css   # Proctoring UI styles
├── app/
│   ├── real_scoring_system.py        # Scoring & report generation
│   └── proctored_routes.py           # Flask API routes
└── templates/
    └── interview/
        └── comprehensive_feedback.html  # Feedback template
```

## Implementation Details

### Frontend (proctored_interview.js)

**Class: ProctoredInterviewSystem**

**Key Methods:**
- `loadFaceDetectionModel()` - Loads MediaPipe detector
- `startFaceDetection()` - Starts 1Hz detection loop
- `detectFace()` - Performs face detection
- `logViolation(type, description)` - Logs and tracks violations
- `endInterview(reason)` - Properly terminates interview
- `calculateFinalScores()` - Computes all score components
- `submitAnswer()` - Evaluates and stores answer
- `sendTerminationToBackend(reason)` - Sends final data

**Metrics Tracked:**
```javascript
{
    totalQuestions: 0,
    attemptedQuestions: 0,
    skippedQuestions: 0,
    totalResponseTime: 0,
    totalResponseLength: 0,
    idleTime: 0,
    abnormalBehaviors: 0,
    startTime: null,
    endTime: null
}
```

**Scores Tracked:**
```javascript
{
    technical: 0,
    problemSolving: 0,
    communication: 0,
    integrity: 100,
    engagement: 0
}
```

### Backend (real_scoring_system.py)

**Class: RealScoringSystem**

**Methods:**
- `calculate_scores(session_data)` - Main scoring function
- `_calculate_technical_score(responses)` - From AI evaluations
- `_calculate_problem_solving_score(responses)` - From AI evaluations
- `_calculate_communication_score(responses)` - From response characteristics
- `_calculate_integrity_score(violations)` - From violation count
- `_calculate_engagement_score(metrics, responses)` - From metrics

**Class: ComprehensiveReportGenerator**

**Methods:**
- `generate_report(session_data)` - Generates complete report
- `_build_metadata(session_data)` - Candidate info
- `_get_recommendation(final_score)` - Hiring recommendation
- `_build_score_breakdown(scores)` - Detailed breakdown
- `_build_integrity_report(session_data)` - Proctoring details
- `_build_engagement_metrics(session_data)` - Tracking metrics
- `_identify_strengths(scores, session_data)` - Evidence-based strengths
- `_identify_improvements(scores, session_data)` - Evidence-based improvements
- `_build_decision_trace(session_data)` - Score evolution

### API Routes (proctored_routes.py)

**Endpoints:**
- `POST /api/log-violation` - Log violation event
- `POST /api/get-next-question` - Get next interview question
- `POST /api/evaluate-answer` - Evaluate candidate answer
- `POST /api/end-interview` - End interview and calculate scores
- `GET /interview/<id>/feedback` - View comprehensive feedback
- `GET /api/session-status/<id>` - Get current session status

## Usage

### 1. Include Required Libraries

```html
<!-- TensorFlow.js -->
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs"></script>

<!-- MediaPipe Face Detection -->
<script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/face-detection"></script>

<!-- Proctoring System -->
<link rel="stylesheet" href="/static/css/proctored_interview.css">
<script src="/static/js/proctored_interview.js"></script>
```

### 2. Initialize System

```javascript
// In your HTML
<input type="hidden" id="sessionId" value="{{ session.id }}">
<input type="hidden" id="candidateId" value="{{ candidate.id }}">

// System auto-initializes on page load
// Access via global: proctoredInterview
```

### 3. Start Interview

```javascript
// Request fullscreen and start
await proctoredInterview.startInterview();
```

### 4. Handle Answers

```javascript
// Submit answer
proctoredInterview.submitAnswer();

// Skip question
proctoredInterview.skipQuestion();
```

### 5. End Interview

```javascript
// Manual end
proctoredInterview.endInterview('USER_ENDED');

// Auto-end on violations
// Handled automatically by system
```

## Scoring Logic

### Technical Score (40% weight)
- Calculated from AI evaluation of answers
- Based on technical accuracy and depth
- Range: 0-100

### Problem Solving Score (25% weight)
- Calculated from AI evaluation
- Based on analytical approach
- Range: 0-100

### Communication Score (15% weight)
- Length score (optimal: 100-500 chars)
- Structure score (sentences, punctuation)
- Clarity score (from AI)
- Formula: `(length × 0.3) + (structure × 0.2) + (clarity × 0.5)`
- Range: 0-100

### Integrity Score (10% weight)
- Starts at 100
- Deducts 15 points per violation
- Formula: `max(0, 100 - (violations × 15))`
- Range: 0-100

### Engagement Score (10% weight)
- Completion rate (50%)
- Response quality (30%)
- Behavior score (20%)
- Formula: `(completion × 0.5) + (quality × 0.3) + (behavior × 0.2)`
- Range: 0-100

## Performance Optimizations

1. **Model Pre-loading**: TensorFlow model loaded before interview
2. **Warm-up Detection**: First frame processed during initialization
3. **1Hz Detection**: Reduces CPU usage while maintaining accuracy
4. **Async Operations**: Non-blocking detection and API calls
5. **Throttled Updates**: UI updates batched to prevent reflows

## Security Features

1. **Fullscreen Enforcement**: Interview must run in fullscreen
2. **DevTools Prevention**: Blocks F12, Ctrl+Shift+I, etc.
3. **Right-click Disabled**: Prevents context menu
4. **Page Unload Warning**: Warns before leaving page
5. **Tab Switch Detection**: Tracks visibility changes
6. **No PII Storage**: No raw face images stored

## Testing

### Test Face Detection
```javascript
// Check if detector loaded
console.log(proctoredInterview.faceDetector);

// Check detection status
console.log(proctoredInterview.faceDetectionActive);

// View violations
console.log(proctoredInterview.violations);
```

### Test Scoring
```javascript
// View current scores
console.log(proctoredInterview.scores);

// View metrics
console.log(proctoredInterview.metrics);

// Calculate final scores
proctoredInterview.calculateFinalScores();
console.log(proctoredInterview.scores.final);
```

### Test Violations
```javascript
// Manually trigger violation
proctoredInterview.logViolation('TEST', 'Test violation');

// Check violation count
console.log(proctoredInterview.violationCount);

// Check integrity score
console.log(proctoredInterview.scores.integrity);
```

## Troubleshooting

### Face Detection Not Working
1. Check TensorFlow.js loaded: `console.log(tf)`
2. Check MediaPipe loaded: `console.log(faceDetection)`
3. Check camera permissions
4. Check video element: `document.getElementById('candidateVideo')`

### Violations Not Logging
1. Check `interviewActive` flag
2. Check backend route: `/api/log-violation`
3. Check network tab for API calls
4. Check console for errors

### Scores Not Calculating
1. Check responses array: `proctoredInterview.responses`
2. Check metrics object: `proctoredInterview.metrics`
3. Call `calculateFinalScores()` manually
4. Check backend scoring logic

### Interview Not Ending
1. Check `interviewEnded` flag
2. Check `endInterview()` called
3. Check backend route: `/api/end-interview`
4. Check for JavaScript errors

## Browser Compatibility

**Fully Supported:**
- Chrome 90+
- Edge 90+
- Firefox 88+

**Partially Supported:**
- Safari 14+ (face detection may be slower)

**Not Supported:**
- Internet Explorer
- Browsers without WebRTC support

## Performance Benchmarks

- **Model Load Time**: < 2 seconds
- **Detection Latency**: < 100ms per frame
- **Violation Popup**: < 1 second
- **Score Calculation**: < 500ms
- **Report Generation**: < 2 seconds

## Future Enhancements

1. **Eye Tracking**: Detect if candidate looking away
2. **Audio Analysis**: Detect background voices
3. **Screen Recording**: Optional video recording
4. **Advanced AI**: GPT-4 for answer evaluation
5. **Mobile Support**: Responsive proctoring for mobile devices

## License

Proprietary - TalentSync Interview System

## Support

For issues or questions, contact: support@talentsync.com

---

**Last Updated**: January 2025
**Version**: 1.0.0
**Status**: Production Ready ✅
