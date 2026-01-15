/**
 * Free Text-to-Speech Service using Web Speech API
 * Provides human-like voice for interview questions
 */

class SpeechService {
    constructor() {
        this.synth = window.speechSynthesis;
        this.currentUtterance = null;
        this.voices = [];
        this.selectedVoice = null;
        this.isEnabled = true;
        
        // Load voices
        this.loadVoices();
        
        // Handle voice list changes
        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = () => this.loadVoices();
        }
    }
    
    loadVoices() {
        this.voices = this.synth.getVoices();
        
        // Select best human-like voice
        this.selectedVoice = this.selectBestVoice();
        
        console.log(`Loaded ${this.voices.length} voices`);
        if (this.selectedVoice) {
            console.log(`Selected voice: ${this.selectedVoice.name}`);
        }
    }
    
    selectBestVoice() {
        // Priority order for natural-sounding voices
        const preferredVoices = [
            // Google voices (most natural)
            'Google US English',
            'Google UK English Female',
            'Google UK English Male',
            
            // Microsoft voices
            'Microsoft Zira Desktop',
            'Microsoft David Desktop',
            
            // Apple voices
            'Samantha',
            'Alex',
            
            // Other quality voices
            'Karen',
            'Daniel',
            'Fiona'
        ];
        
        // Try to find preferred voice
        for (const preferred of preferredVoices) {
            const voice = this.voices.find(v => v.name.includes(preferred));
            if (voice) return voice;
        }
        
        // Fallback: Find any English voice
        const englishVoice = this.voices.find(v => v.lang.startsWith('en'));
        if (englishVoice) return englishVoice;
        
        // Last resort: Use first available voice
        return this.voices[0] || null;
    }
    
    speak(text, options = {}) {
        if (!this.isEnabled || !text) return;
        
        // Stop any ongoing speech
        this.stop();
        
        // Create utterance
        this.currentUtterance = new SpeechSynthesisUtterance(text);
        
        // Configure voice settings for natural sound
        if (this.selectedVoice) {
            this.currentUtterance.voice = this.selectedVoice;
        }
        
        // Natural speech parameters
        this.currentUtterance.rate = options.rate || 0.95;  // Slightly slower for clarity
        this.currentUtterance.pitch = options.pitch || 1.0;  // Normal pitch
        this.currentUtterance.volume = options.volume || 1.0;  // Full volume
        
        // Event handlers
        this.currentUtterance.onstart = () => {
            if (options.onStart) options.onStart();
            this.highlightSpeaking(true);
        };
        
        this.currentUtterance.onend = () => {
            if (options.onEnd) options.onEnd();
            this.highlightSpeaking(false);
        };
        
        this.currentUtterance.onerror = (event) => {
            console.error('Speech error:', event);
            this.highlightSpeaking(false);
        };
        
        // Speak
        this.synth.speak(this.currentUtterance);
    }
    
    stop() {
        if (this.synth.speaking) {
            this.synth.cancel();
        }
        this.highlightSpeaking(false);
    }
    
    pause() {
        if (this.synth.speaking) {
            this.synth.pause();
        }
    }
    
    resume() {
        if (this.synth.paused) {
            this.synth.resume();
        }
    }
    
    toggle() {
        this.isEnabled = !this.isEnabled;
        if (!this.isEnabled) {
            this.stop();
        }
        return this.isEnabled;
    }
    
    highlightSpeaking(isSpeaking) {
        const indicator = document.getElementById('speech-indicator');
        if (indicator) {
            if (isSpeaking) {
                indicator.classList.add('speaking');
                indicator.innerHTML = '<i class="fas fa-volume-up"></i> Speaking...';
            } else {
                indicator.classList.remove('speaking');
                indicator.innerHTML = '<i class="fas fa-volume-mute"></i> Silent';
            }
        }
    }
    
    getAvailableVoices() {
        return this.voices.map(v => ({
            name: v.name,
            lang: v.lang,
            default: v.default
        }));
    }
    
    setVoice(voiceName) {
        const voice = this.voices.find(v => v.name === voiceName);
        if (voice) {
            this.selectedVoice = voice;
            return true;
        }
        return false;
    }
    
    isSupported() {
        return 'speechSynthesis' in window;
    }
}

// Create global instance
const speechService = new SpeechService();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = speechService;
}
