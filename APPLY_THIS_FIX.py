"""
CRITICAL FIX SCRIPT
Run this to fix all issues at once
"""

import os
import re

def fix_main_py():
    """Fix main.py to use improved feedback generation"""
    file_path = r"ai_interview_system\Backend Files\app\main.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Replace generate_simple_feedback with generate_feedback
    old_code = '''        # Generate detailed student-oriented feedback
        feedback_data = ai_service.generate_simple_feedback(all_responses, "student")'''
    
    new_code = '''        # Generate comprehensive feedback with full conversation history
        feedback_data = ai_service.generate_feedback(questions, responses, session)'''
    
    content = content.replace(old_code, new_code)
    
    # Fix 2: Add problem_solving_score
    old_score_section = '''        session.overall_score = feedback_data.get('overall_score', 75)
        session.technical_score = feedback_data.get('technical_score', 75)
        session.communication_score = feedback_data.get('communication_score', 75)
        session.confidence_score = feedback_data.get('confidence_score', 75)'''
    
    new_score_section = '''        session.overall_score = feedback_data.get('overall_score', 75)
        session.technical_score = feedback_data.get('technical_score', 75)
        session.communication_score = feedback_data.get('communication_score', 75)
        session.confidence_score = feedback_data.get('confidence_score', 75)
        session.problem_solving_score = feedback_data.get('problem_solving_score', 70)'''
    
    content = content.replace(old_score_section, new_score_section)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed main.py - Now using improved feedback generation")

def remove_all_emojis_from_emails():
    """Remove all emojis from email templates"""
    email_dir = r"ai_interview_system\Backend Files\templates\emails"
    
    # Emoji patterns to remove
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    fixed_count = 0
    for root, dirs, files in os.walk(email_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = emoji_pattern.sub('', content)
                
                if content != new_content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    fixed_count += 1
                    print(f"✅ Removed emojis from {file}")
    
    print(f"\n✅ Fixed {fixed_count} email templates")

def create_voice_integration_guide():
    """Create guide for voice integration"""
    guide = """
# Voice Integration Guide

## Add to interview interface template:

1. Add script tag before </body>:
```html
<script src="{{ url_for('static', filename='js/speech.js') }}"></script>
```

2. Add voice controls:
```html
<div class="voice-controls">
    <button id="toggle-voice" class="btn btn-primary">
        <i class="fas fa-volume-up"></i> Enable Voice
    </button>
    <button id="stop-voice" class="btn btn-secondary">
        <i class="fas fa-stop"></i> Stop
    </button>
</div>
<div id="speech-indicator" class="speech-status">
    <i class="fas fa-volume-mute"></i> Silent
</div>
```

3. Add JavaScript to speak questions:
```javascript
// When displaying new question
function displayQuestion(questionText) {
    document.getElementById('question').textContent = questionText;
    
    // Speak the question
    if (speechService && speechService.isEnabled) {
        speechService.speak(questionText, {
            rate: 0.95,
            onEnd: () => {
                console.log('Question read complete');
            }
        });
    }
}

// Voice controls
document.getElementById('toggle-voice').addEventListener('click', function() {
    const enabled = speechService.toggle();
    this.innerHTML = enabled ? 
        '<i class="fas fa-volume-up"></i> Disable Voice' : 
        '<i class="fas fa-volume-mute"></i> Enable Voice';
});

document.getElementById('stop-voice').addEventListener('click', function() {
    speechService.stop();
});
```

4. Add CSS:
```css
.voice-controls {
    position: fixed;
    top: 80px;
    right: 20px;
    z-index: 1000;
    display: flex;
    gap: 10px;
}

.speech-status {
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 10px 20px;
    background: #f3f4f6;
    border-radius: 25px;
    font-size: 14px;
    transition: all 0.3s ease;
    z-index: 1000;
}

.speech-status.speaking {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}
```
"""
    
    with open('VOICE_INTEGRATION_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print("✅ Created voice integration guide")

if __name__ == "__main__":
    print("=" * 60)
    print("APPLYING CRITICAL FIXES")
    print("=" * 60)
    
    try:
        fix_main_py()
        remove_all_emojis_from_emails()
        create_voice_integration_guide()
        
        print("\n" + "=" * 60)
        print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart your Flask server")
        print("2. Test interview completion")
        print("3. Check email sending")
        print("4. Follow VOICE_INTEGRATION_GUIDE.md to add voice")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please run this script from the Main-Copy directory")
