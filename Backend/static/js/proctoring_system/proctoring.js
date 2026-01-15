/**
 * Proctoring System Frontend Integration
 * Handles video capture, frame processing, and violation alerts with 3-strike policy
 */

class ProctoringSuite {
    constructor(interviewSessionId) {
        this.interviewSessionId = interviewSessionId;
        this.isActive = false;
        this.videoElement = null;
        this.canvasElement = null;
        this.stream = null;
        this.processInterval = null;
        this.violations = [];
        this.frameProcessingRate = 2000;
        
        this.init();
    }
    
    async init() {
        try {
            this.createVideoElements();
            await this.setupCamera();
            console.log('Proctoring system initialized');
        } catch (error) {
            console.error('Failed to initialize proctoring system:', error);
            this.showError('Camera access required for proctoring');
        }
    }
    
    createVideoElements() {
        this.videoElement = document.createElement('video');
        this.videoElement.id = 'proctoring-video';
        this.videoElement.autoplay = true;
        this.videoElement.muted = true;
        this.videoElement.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 200px;
            height: 150px;
            border: 2px solid #007bff;
            border-radius: 8px;
            z-index: 1000;
            background: #000;
        `;
        
        this.canvasElement = document.createElement('canvas');
        this.canvasElement.style.display = 'none';
        
        document.body.appendChild(this.videoElement);
        document.body.appendChild(this.canvasElement);
        
        this.createStatusIndicator();
    }
    
    createStatusIndicator() {
        const statusDiv = document.createElement('div');
        statusDiv.id = 'proctoring-status';
        statusDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 20px;
            padding: 10px 15px;
            background: #28a745;
            color: white;
            border-radius: 5px;
            font-size: 14px;
            z-index: 1001;
            display: none;
        `;
        statusDiv.innerHTML = '🔒 Proctoring Active';
        document.body.appendChild(statusDiv);
        
        const violationDiv = document.createElement('div');
        violationDiv.id = 'violation-counter';
        violationDiv.style.cssText = `
            position: fixed;
            top: 60px;
            left: 20px;
            padding: 8px 12px;
            background: #28a745;
            color: white;
            border-radius: 5px;
            font-size: 12px;
            z-index: 1001;
            display: none;
        `;
        violationDiv.innerHTML = '⚠️ Warnings: 0/3';
        document.body.appendChild(violationDiv);
    }
    
    async setupCamera() {
        try {
            const constraints = {
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                },
                audio: false
            };
            
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.videoElement.srcObject = this.stream;
            
            return new Promise((resolve) => {
                this.videoElement.onloadedmetadata = () => {
                    this.canvasElement.width = this.videoElement.videoWidth;
                    this.canvasElement.height = this.videoElement.videoHeight;
                    resolve();
                };
            });
            
        } catch (error) {
            throw new Error('Camera access denied or not available');
        }
    }
    
    async startProctoring() {
        try {
            const response = await fetch('/api/proctoring/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    interview_session_id: this.interviewSessionId
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to start proctoring');
            }
            
            this.isActive = true;
            
            document.getElementById('proctoring-status').style.display = 'block';
            document.getElementById('violation-counter').style.display = 'block';
            
            this.startFrameProcessing();
            
            console.log('Proctoring started successfully');
            
        } catch (error) {
            console.error('Failed to start proctoring:', error);
            this.showError('Failed to start proctoring: ' + error.message);
        }
    }
    
    async stopProctoring() {
        try {
            if (!this.isActive) return;
            
            if (this.processInterval) {
                clearInterval(this.processInterval);
                this.processInterval = null;
            }
            
            const response = await fetch('/api/proctoring/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    interview_session_id: this.interviewSessionId
                })
            });
            
            const data = await response.json();
            
            this.isActive = false;
            
            document.getElementById('proctoring-status').style.display = 'none';
            document.getElementById('violation-counter').style.display = 'none';
            
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
            }
            
            if (this.videoElement) {
                this.videoElement.remove();
            }
            if (this.canvasElement) {
                this.canvasElement.remove();
            }
            
            console.log('Proctoring stopped successfully');
            
            if (data.success && data.summary) {
                this.showSummary(data.summary);
            }
            
        } catch (error) {
            console.error('Failed to stop proctoring:', error);
        }
    }
    
    startFrameProcessing() {
        this.processInterval = setInterval(() => {
            if (this.isActive && this.videoElement && this.videoElement.readyState === 4) {
                this.captureAndProcessFrame();
            }
        }, this.frameProcessingRate);
    }
    
    async captureAndProcessFrame() {
        try {
            const context = this.canvasElement.getContext('2d');
            context.drawImage(this.videoElement, 0, 0);
            
            const frameData = this.canvasElement.toDataURL('image/jpeg', 0.8);
            
            const response = await fetch('/api/proctoring/process_frame', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    interview_session_id: this.interviewSessionId,
                    frame: frameData
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.results) {
                this.handleProcessingResults(data.results);
            }
            
        } catch (error) {
            console.error('Frame processing error:', error);
        }
    }
    
    handleProcessingResults(results) {
        // Handle termination
        if (results.should_terminate) {
            this.showTerminationAlert();
            setTimeout(() => {
                if (window.submitInterview) {
                    window.submitInterview(true, 'Proctoring violations exceeded limit');
                }
            }, 5000);
            return;
        }
        
        // Update violation counter and show warnings
        if (results.violations && results.violations.length > 0) {
            this.violations.push(...results.violations);
            this.updateViolationCounter(results.warning_count, results.max_warnings);
            
            results.violations.forEach(violation => {
                this.showViolationAlert(violation, results.warning_count, results.max_warnings);
            });
        }
        
        this.updateStatusDisplay(results);
    }
    
    updateViolationCounter(warningCount, maxWarnings) {
        const counter = document.getElementById('violation-counter');
        if (counter) {
            counter.innerHTML = `⚠️ Warnings: ${warningCount || 0}/${maxWarnings || 3}`;
            
            if (warningCount >= 2) {
                counter.style.background = '#dc3545'; // Red
            } else if (warningCount >= 1) {
                counter.style.background = '#ffc107'; // Yellow
                counter.style.color = '#000';
            }
        }
    }
    
    updateStatusDisplay(results) {
        const overlay = document.getElementById('detection-overlay');
        if (!overlay) {
            const newOverlay = document.createElement('div');
            newOverlay.id = 'detection-overlay';
            newOverlay.style.cssText = `
                position: fixed;
                top: 180px;
                right: 20px;
                width: 200px;
                background: rgba(0,0,0,0.7);
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 12px;
                z-index: 1002;
                display: none;
            `;
            document.body.appendChild(newOverlay);
        }
        
        const overlayElement = document.getElementById('detection-overlay');
        if (overlayElement && results) {
            overlayElement.innerHTML = `
                <div>Faces: ${results.face_count || 0}</div>
                <div>Gaze: ${results.gaze_direction || 'Unknown'}</div>
                <div>Head: ${results.head_pose || 'Unknown'}</div>
                <div>Objects: ${results.objects ? results.objects.length : 0}</div>
            `;
            overlayElement.style.display = 'block';
        }
    }
    
    showViolationAlert(violation, warningCount, maxWarnings) {
        const alert = document.createElement('div');
        alert.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #dc3545;
            color: white;
            padding: 20px;
            border-radius: 10px;
            z-index: 2000;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            max-width: 400px;
        `;
        
        alert.innerHTML = `
            <h4>⚠️ Warning ${warningCount}/${maxWarnings}</h4>
            <p>${violation}</p>
            <small>Interview will be terminated after ${maxWarnings} warnings</small>
        `;
        
        document.body.appendChild(alert);
        
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 4000);
        
        this.playAlertSound();
    }
    
    showTerminationAlert() {
        const alert = document.createElement('div');
        alert.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #dc3545;
            color: white;
            padding: 30px;
            border-radius: 10px;
            z-index: 2001;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            max-width: 500px;
        `;
        
        alert.innerHTML = `
            <h3>🚫 Interview Terminated</h3>
            <p>Maximum violations exceeded. Your interview will be automatically submitted in 5 seconds.</p>
            <div id="countdown">5</div>
        `;
        
        document.body.appendChild(alert);
        
        let countdown = 5;
        const countdownInterval = setInterval(() => {
            countdown--;
            const countdownElement = document.getElementById('countdown');
            if (countdownElement) {
                countdownElement.textContent = countdown;
            }
            if (countdown <= 0) {
                clearInterval(countdownInterval);
            }
        }, 1000);
    }
    
    playAlertSound() {
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.log('Could not play alert sound:', error);
        }
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #dc3545;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 2000;
            text-align: center;
        `;
        errorDiv.innerHTML = `❌ ${message}`;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    showSummary(summary) {
        const summaryDiv = document.createElement('div');
        summaryDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            color: #333;
            padding: 30px;
            border-radius: 10px;
            z-index: 2000;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            max-width: 500px;
            border: 2px solid #007bff;
        `;
        
        const duration = Math.round(summary.session_duration / 60);
        
        summaryDiv.innerHTML = `
            <h3>🔒 Proctoring Session Complete</h3>
            <div style="margin: 20px 0;">
                <p><strong>Duration:</strong> ${duration} minutes</p>
                <p><strong>Total Violations:</strong> ${summary.total_violations}</p>
            </div>
            <button onclick="this.parentElement.remove()" 
                    style="background: #007bff; color: white; border: none; 
                           padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                Close
            </button>
        `;
        
        document.body.appendChild(summaryDiv);
    }
    
    isProctoring() {
        return this.isActive;
    }
    
    getViolationCount() {
        return this.violations.length;
    }
}

window.ProctoringSuite = ProctoringSuite;