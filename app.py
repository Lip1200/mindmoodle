"""
Mental Health Support Assistant - Chainlit Copilot Application

This application provides a safe, supportive chatbot for mental health support
embedded in Moodle via a copilot widget. It includes crisis keyword detection
and provides non-medical, supportive responses.

Uses safety filters inspired by mellea library patterns to filter hallucinations 
and medical advice.
"""

import chainlit as cl
from chainlit import user_session
import re
from typing import List, Dict, Tuple, Callable

# Crisis keywords that trigger special handling
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "self-harm", "hurt myself", "cutting", "overdose", "no reason to live",
    "better off dead", "can't go on", "hopeless", "worthless"
]

# Crisis response resources
CRISIS_RESOURCES = """
I'm concerned about what you've shared. Please know that help is available:

🆘 **Immediate Crisis Resources:**
- National Suicide Prevention Lifeline: 988 (US)
- Crisis Text Line: Text HOME to 741741
- International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

**You are not alone.** Please reach out to a mental health professional, counselor, or trusted adult immediately.

Would you like to talk about what's going on? (Remember: I'm an AI assistant, not a therapist, but I'm here to listen and provide support.)
"""

# Safe, supportive response guidelines
SYSTEM_PROMPT = """You are a compassionate mental health support companion for students. Your role is to:

1. Listen actively and provide emotional support
2. Validate feelings and experiences
3. Offer coping strategies and self-care suggestions
4. Encourage professional help when appropriate
5. NEVER provide medical advice or diagnoses
6. NEVER claim to be a therapist or medical professional
7. Always remind users that you're an AI assistant
8. For serious concerns, direct to professional resources

Be warm, empathetic, and supportive while maintaining appropriate boundaries.
Keep responses concise and student-friendly.
"""


def detect_crisis_keywords(message: str) -> bool:
    """
    Detect if the message contains crisis-related keywords.
    
    Args:
        message: User's message text
        
    Returns:
        True if crisis keywords detected, False otherwise
    """
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in CRISIS_KEYWORDS)


class SafetyRequirement:
    """
    A safety requirement for validating LLM responses.
    Inspired by mellea library's approach to response validation.
    """
    
    def __init__(self, description: str, check_fn: Callable[[str], bool]):
        """
        Initialize a safety requirement.
        
        Args:
            description: Description of the requirement
            check_fn: Function that returns True if requirement is satisfied, False otherwise
        """
        self.description = description
        self.check = check_fn


def create_safety_requirements() -> List[SafetyRequirement]:
    """
    Create safety requirements to filter hallucinations and medical advice.
    This approach is inspired by the mellea library's validation patterns.
    
    Returns:
        List of safety requirements for response validation
    """
    # Requirement to ensure no medical diagnosis
    no_diagnosis = SafetyRequirement(
        "The response does not provide medical diagnoses or claim to diagnose any condition",
        lambda text: not any(phrase in text.lower() for phrase in [
            "you have", "you're diagnosed", "this is a diagnosis",
            "you suffer from", "you are bipolar", "you have depression",
            "you have anxiety disorder", "you have ptsd", "you are experiencing",
            "i diagnose", "my diagnosis", "clinically"
        ])
    )
    
    # Requirement to ensure no medical prescriptions
    no_prescriptions = SafetyRequirement(
        "The response does not prescribe medications or specific medical treatments",
        lambda text: not any(phrase in text.lower() for phrase in [
            "take this medication", "you should take", "prescribed",
            "dosage", "mg of", "antidepressant", "ssri", "medication for",
            "prescription", "drug", "pills"
        ])
    )
    
    # Requirement to ensure no claims of being a therapist
    no_therapist_claim = SafetyRequirement(
        "The response does not claim to be a therapist, doctor, or medical professional",
        lambda text: not any(phrase in text.lower() for phrase in [
            "i am a therapist", "i am a doctor", "as your therapist",
            "as your doctor", "i can treat", "i will treat you",
            "my professional opinion", "in my clinical experience"
        ])
    )
    
    # Requirement to ensure grounded responses (no hallucinations)
    grounded_response = SafetyRequirement(
        "The response is grounded in supportive, empathetic language without making up facts",
        lambda text: not any(phrase in text.lower() for phrase in [
            "scientific studies show exactly", "research proves definitively",
            "100% effective", "guaranteed cure", "this will definitely",
            "i know for certain", "medical fact that"
        ])
    )
    
    # Requirement to ensure AI identity is maintained
    ai_identity = SafetyRequirement(
        "The response maintains AI assistant identity without claiming human qualities",
        lambda text: not any(phrase in text.lower() for phrase in [
            "i feel the same way", "i have experienced",
            "when i was", "in my personal life", "i also struggle with",
            "i understand because i", "as a human"
        ])
    )
    
    return [no_diagnosis, no_prescriptions, no_therapist_claim, grounded_response, ai_identity]


def validate_response_safety(response_text: str) -> Tuple[bool, List[str]]:
    """
    Validate response using safety requirements to ensure safety.
    This implements a validation pattern inspired by mellea library.
    
    Args:
        response_text: Generated response to validate
        
    Returns:
        Tuple of (is_safe, list_of_violations)
    """
    requirements = create_safety_requirements()
    violations = []
    
    for requirement in requirements:
        try:
            # Check if requirement is satisfied
            is_satisfied = requirement.check(response_text)
            if not is_satisfied:
                violations.append(requirement.description)
        except Exception as e:
            # If check fails, consider it a violation and log for monitoring
            error_msg = f"Safety check error in '{requirement.description}': {str(e)}"
            print(f"⚠️ {error_msg}")  # Log for monitoring
            violations.append(error_msg)
    
    is_safe = len(violations) == 0
    return is_safe, violations


async def generate_response(message: str, history: List[Dict]) -> str:
    """
    Generate a safe, supportive response to the user's message.
    
    This is a placeholder that should be replaced with your LLM integration
    (e.g., OpenAI, Anthropic, etc.) in production.
    
    Args:
        message: User's current message
        history: Conversation history
        
    Returns:
        Generated response text, validated by safety requirements
    """
    # Check for crisis keywords in user message first
    if detect_crisis_keywords(message):
        return CRISIS_RESOURCES
    
    # Placeholder responses for demonstration
    # In production, replace this with actual LLM API calls
    default_responses = {
        "stress": "I hear that you're feeling stressed. That's completely valid, especially as a student. Some helpful strategies include taking short breaks, practicing deep breathing, or breaking tasks into smaller steps. What specifically is causing you stress right now?",
        "anxiety": "Anxiety can be really challenging. Remember that it's a normal response, even though it doesn't feel good. Have you tried grounding techniques like the 5-4-3-2-1 method? (Name 5 things you see, 4 you hear, 3 you can touch, 2 you smell, 1 you taste). Would you like to talk more about what's making you anxious?",
        "overwhelmed": "Feeling overwhelmed is tough. Let's take a moment - you don't have to handle everything at once. What's the most pressing thing on your mind right now? Sometimes just identifying one thing to focus on can help.",
        "lonely": "Feeling lonely can be really hard. Thank you for sharing that with me. Connection is important - have you considered reaching out to campus groups, clubs, or student support services? Even small interactions can help.",
        "sad": "I'm sorry you're feeling sad. Your feelings are valid. Is there something specific that's bothering you, or is it more of a general feeling? Sometimes talking about it can help.",
    }
    
    # Simple keyword matching for demo (replace with LLM in production)
    message_lower = message.lower()
    response_text = None
    for keyword, response in default_responses.items():
        if keyword in message_lower:
            response_text = response
            break
    
    # Default supportive response
    if not response_text:
        response_text = "Thank you for sharing that with me. I'm here to listen and support you. Can you tell me more about what's on your mind? Remember, if you need professional support, your campus counseling center is a great resource."
    
    # Check generated response for crisis indicators as well
    # (User might express crisis thoughts in response to assistant questions)
    if detect_crisis_keywords(response_text):
        # This should rarely happen with good responses, but check anyway
        print("⚠️ Warning: Generated response contains crisis keywords - replacing with resources")
        return CRISIS_RESOURCES
    
    # Validate response using safety requirements
    is_safe, violations = validate_response_safety(response_text)
    
    if not is_safe:
        # If validation fails, return a safe fallback response
        # Log violations for debugging
        print(f"⚠️ Response failed safety checks: {violations}")
        return ("I'm here to provide support and listen. However, for specific concerns or questions "
                "about your mental health, I encourage you to speak with a licensed mental health "
                "professional at your campus counseling center. They can provide the personalized "
                "care and guidance you need. Is there anything else I can help you with today?")
    
    return response_text


@cl.on_chat_start
async def start():
    """Initialize the chat session."""
    await cl.Message(
        content="👋 Hi! I'm your mental health support companion. I'm here to listen and provide support.\n\n"
                "**Important:** I'm an AI assistant, not a therapist. For serious concerns or emergencies, "
                "please contact your campus counseling center or call 988.\n\n"
                "How are you feeling today?"
    ).send()
    
    # Initialize conversation history
    cl.user_session.set("history", [])


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages."""
    # Get conversation history
    history = cl.user_session.get("history", [])
    
    # Add user message to history
    history.append({
        "role": "user",
        "content": message.content
    })
    
    # Generate response
    response_text = await generate_response(message.content, history)
    
    # Add assistant response to history
    history.append({
        "role": "assistant",
        "content": response_text
    })
    
    # Update history (keep last 10 messages to manage memory)
    cl.user_session.set("history", history[-10:])
    
    # Send response
    await cl.Message(content=response_text).send()
