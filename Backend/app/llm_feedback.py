import json
from typing import List, Dict

def generate_comprehensive_feedback(ai_service, responses: List[Dict], job_role: str) -> Dict:
    """Generate comprehensive feedback using LLM based on actual conversation"""
    
    # Check for empty or meaningless responses
    if not responses or len(responses) == 0:
        return {
            'overall_score': 0,
            'technical_score': 0,
            'communication_score': 0,
            'confidence_score': 0,
            'strengths': ['No responses provided'],
            'weaknesses': ['Did not participate in interview'],
            'summary': 'No responses were recorded during the interview.'
        }
    
    # Check if responses are meaningful
    meaningful_responses = []
    for resp in responses:
        answer = str(resp.get('answer', '')).strip()
        if len(answer) > 5 and answer.lower() not in ['no', 'yes', 'ok', 'i dont know', 'i don\'t know']:
            meaningful_responses.append(resp)
    
    if len(meaningful_responses) == 0:
        return {
            'overall_score': 0,
            'technical_score': 0,
            'communication_score': 0,
            'confidence_score': 0,
            'strengths': ['Attempted to respond'],
            'weaknesses': ['Responses were too brief or unclear', 'Did not provide meaningful answers'],
            'summary': f'Interview had {len(responses)} responses but none were substantial enough for evaluation.'
        }
    
    # Use meaningful responses for LLM analysis
    conversation_text = ""
    for i, response in enumerate(meaningful_responses):
        conversation_text += f"Q{i+1}: {response.get('question', 'Question')}\n"
        conversation_text += f"A{i+1}: {response.get('answer', 'No answer')}\n"
        conversation_text += f"Response Time: {response.get('response_time', 0)} seconds\n\n"
    
    prompt = f"""Analyze this {job_role} interview conversation and provide detailed feedback.

INTERVIEW CONVERSATION:
{conversation_text}

JOB ROLE: {job_role}
TOTAL RESPONSES: {len(meaningful_responses)} meaningful out of {len(responses)} total

Analyze the candidate's performance based on:
1. Answer quality and depth
2. Technical knowledge demonstrated
3. Communication clarity
4. Problem-solving approach
5. Relevance to the role

Provide scores (0-100) and detailed feedback in this JSON format:
{{
  "overall_score": 75,
  "technical_score": 70,
  "communication_score": 80,
  "confidence_score": 75,
  "strengths": ["Specific strength based on answers", "Another strength"],
  "weaknesses": ["Specific weakness based on answers", "Another weakness"],
  "detailed_analysis": {{
    "communication": "Analysis of communication skills based on responses",
    "technical_skills": "Analysis of technical knowledge shown",
    "problem_solving": "Analysis of problem-solving approach"
  }},
  "recommendations": ["Specific recommendation", "Another recommendation"],
  "summary": "Overall assessment based on the actual conversation"
}}

Base your scores on actual content quality, not just participation."""

    # Try multiple LLM models until one works
    free_models = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.2-1b-instruct:free",
        "google/gemma-2-9b-it:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "huggingfaceh4/zephyr-7b-beta:free",
        "nousresearch/hermes-3-llama-3.1-405b:free",
        "liquid/lfm-40b:free"
    ]
    
    # Only use LLM if we have meaningful responses
    if len(meaningful_responses) < 1:
        return {
            'overall_score': 0,
            'technical_score': 0,
            'communication_score': 0,
            'confidence_score': 0,
            'strengths': ['No meaningful responses'],
            'weaknesses': ['Did not provide substantial answers'],
            'summary': 'Insufficient responses for evaluation.'
        }
    
    # Simplified prompt for better LLM success
    llm_prompt = f"""
Evaluate this {job_role} interview. Candidate gave {len(meaningful_responses)} responses.

Interview Content:
{conversation_text[:800]}

Provide scores and feedback in this EXACT format:
Overall Score: 78
Technical Score: 75
Communication Score: 82
Strengths: Clear answers, Good examples, Professional tone
Weaknesses: Add more details, Include metrics, Practice confidence
Summary: Strong interview performance with clear communication and relevant examples for the role.

Your evaluation:
"""
    
    # Use the same AI service that works for questions
    try:
        print("Using working AI service for feedback...")
        response = ai_service.generate_response(llm_prompt)
        print(f"AI service response: {response[:200]}...")
        
        result = parse_llm_feedback(response, meaningful_responses)
        if result:
            print("✓ AI service feedback generated successfully")
            return result
        else:
            print("AI service response could not be parsed")
            
    except Exception as e:
        print(f"AI service feedback failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Generate intelligent fallback based on response analysis
    print("All LLM models failed, generating intelligent fallback...")
    
    # Analyze response quality
    total_chars = sum(len(str(r.get('answer', ''))) for r in meaningful_responses)
    avg_length = total_chars / max(1, len(meaningful_responses))
    response_count = len(meaningful_responses)
    
    # Calculate realistic scores based on engagement
    if response_count >= 5 and avg_length >= 50:
        base_score = 75
    elif response_count >= 3 and avg_length >= 30:
        base_score = 65
    elif response_count >= 2 and avg_length >= 20:
        base_score = 55
    else:
        base_score = 45
    
    return {
        'overall_score': base_score,
        'technical_score': max(40, base_score - 10),
        'communication_score': min(85, base_score + 5),
        'confidence_score': base_score,
        'strengths': [
            f'Provided {response_count} meaningful responses',
            f'Average response length of {int(avg_length)} characters shows engagement',
            'Completed the full interview process'
        ],
        'weaknesses': [
            'Could provide more detailed technical examples',
            'Practice articulating complex concepts clearly',
            'Prepare specific examples from experience'
        ],
        'summary': f'Interview completed with {response_count} responses averaging {int(avg_length)} characters. Performance shows {"good" if base_score >= 70 else "moderate" if base_score >= 60 else "basic"} engagement level. LLM analysis unavailable - assessment based on response metrics.'
    }

def parse_llm_feedback(llm_text, meaningful_responses):
    """Parse LLM response into structured feedback with flexible parsing"""
    try:
        import re
        
        print(f"Parsing LLM text: {llm_text[:300]}...")
        
        # More flexible score extraction
        score_patterns = [
            r'Overall Score:?\s*(\d+)',
            r'Overall:?\s*(\d+)',
            r'Score:?\s*(\d+)',
            r'(\d+)%?\s*overall',
            r'(\d+)/100'
        ]
        
        overall_score = None
        for pattern in score_patterns:
            match = re.search(pattern, llm_text, re.IGNORECASE)
            if match:
                overall_score = int(match.group(1))
                print(f"Found overall score: {overall_score}")
                break
        
        # If no score found, try to extract any number between 0-100
        if overall_score is None:
            numbers = re.findall(r'\b([0-9]{1,3})\b', llm_text)
            for num in numbers:
                if 0 <= int(num) <= 100:
                    overall_score = int(num)
                    print(f"Using first valid number as score: {overall_score}")
                    break
        
        # Default score if nothing found
        if overall_score is None:
            overall_score = 70
            print("No score found, using default: 70")
        
        # Extract other scores
        technical_match = re.search(r'Technical Score:?\s*(\d+)', llm_text, re.IGNORECASE)
        comm_match = re.search(r'Communication Score:?\s*(\d+)', llm_text, re.IGNORECASE)
        
        technical_score = int(technical_match.group(1)) if technical_match else max(0, overall_score - 5)
        comm_score = int(comm_match.group(1)) if comm_match else min(100, overall_score + 5)
        
        # Extract strengths and weaknesses with flexible parsing
        strengths = ['Participated in interview', 'Provided responses']
        weaknesses = ['Could provide more detail', 'Practice recommended']
        
        strengths_match = re.search(r'Strengths:?\s*(.+?)(?=Weaknesses:|Summary:|$)', llm_text, re.IGNORECASE | re.DOTALL)
        if strengths_match:
            strength_text = strengths_match.group(1).strip()
            if ',' in strength_text:
                strengths = [s.strip() for s in strength_text.split(',') if s.strip()]
            elif '\n' in strength_text:
                strengths = [s.strip() for s in strength_text.split('\n') if s.strip()]
            else:
                strengths = [strength_text]
        
        weaknesses_match = re.search(r'Weaknesses:?\s*(.+?)(?=Summary:|$)', llm_text, re.IGNORECASE | re.DOTALL)
        if weaknesses_match:
            weakness_text = weaknesses_match.group(1).strip()
            if ',' in weakness_text:
                weaknesses = [w.strip() for w in weakness_text.split(',') if w.strip()]
            elif '\n' in weakness_text:
                weaknesses = [w.strip() for w in weakness_text.split('\n') if w.strip()]
            else:
                weaknesses = [weakness_text]
        
        # Extract summary
        summary_match = re.search(r'Summary:?\s*(.+?)$', llm_text, re.IGNORECASE | re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else f'Interview analysis completed with {len(meaningful_responses)} responses.'
        
        result = {
            'overall_score': min(100, max(0, overall_score)),
            'technical_score': min(100, max(0, technical_score)),
            'communication_score': min(100, max(0, comm_score)),
            'confidence_score': overall_score,
            'strengths': strengths[:3],
            'weaknesses': weaknesses[:3],
            'summary': summary[:500]  # Limit summary length
        }
        
        print(f"Successfully parsed feedback: {result}")
        return result
        
    except Exception as e:
        print(f"Parse error: {e}")
        import traceback
        traceback.print_exc()
        return None
        
