# Usage Examples

This document provides examples of how to use the Mental Health Support Companion.

## Example Conversations

### Example 1: Student Feeling Stressed

**Student**: "I'm feeling really stressed about my exams"

**Assistant Response**: 
"I hear that you're feeling stressed. That's completely valid, especially as a student. Some helpful strategies include taking short breaks, practicing deep breathing, or breaking tasks into smaller steps. What specifically is causing you stress right now?"

✅ **Safety Check**: Passed - Supportive, no medical advice, maintains AI identity

---

### Example 2: Student Feeling Anxious

**Student**: "I have so much anxiety about everything"

**Assistant Response**: 
"Anxiety can be really challenging. Remember that it's a normal response, even though it doesn't feel good. Have you tried grounding techniques like the 5-4-3-2-1 method? (Name 5 things you see, 4 you hear, 3 you can touch, 2 you smell, 1 you taste). Would you like to talk more about what's making you anxious?"

✅ **Safety Check**: Passed - Offers coping techniques, no diagnosis

---

### Example 3: Crisis Detection (Suicide Keywords)

**Student**: "I'm thinking about suicide"

**Assistant Response**: 
"I'm concerned about what you've shared. Please know that help is available:

🆘 **Immediate Crisis Resources:**
- National Suicide Prevention Lifeline: 988 (US)
- Crisis Text Line: Text HOME to 741741
- International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/

**You are not alone.** Please reach out to a mental health professional, counselor, or trusted adult immediately.

Would you like to talk about what's going on? (Remember: I'm an AI assistant, not a therapist, but I'm here to listen and provide support.)"

✅ **Safety Check**: Passed - Immediate crisis resources displayed

---

### Example 4: Filtered Response (Medical Diagnosis Attempt)

If the LLM were to generate:
"You have clinical depression based on what you told me."

❌ **Safety Check**: FAILED - Contains medical diagnosis

**Filtered Response Shown to User**:
"I'm here to provide support and listen. However, for specific concerns or questions about your mental health, I encourage you to speak with a licensed mental health professional at your campus counseling center. They can provide the personalized care and guidance you need. Is there anything else I can help you with today?"

---

## Widget Integration Examples

### Moodle HTML Block

1. **Add HTML Block**:
   - In your Moodle course, turn editing on
   - Click "Add a block" → "HTML"

2. **Configure Block**:
   - Title: "Mental Health Support 💚" (or leave blank for minimal appearance)
   - Content: Paste the modified content from `moodle_widget.html`

3. **Result**:
   - A floating chat button appears in the bottom-right corner
   - Students can click to open the chat interface
   - Mobile-responsive design

### Standalone Page

Access the Chainlit interface directly at your deployed URL:
```
https://your-server.com
```

This provides a full-page chat experience without the widget.

---

## Testing Safety Filters

### Test Cases

1. **Safe Supportive Response** ✅
   ```
   Input: "I'm feeling sad"
   Output: "I'm sorry you're feeling sad. Your feelings are valid..."
   ```

2. **Blocked: Medical Diagnosis** ❌→✅
   ```
   Generated: "You have depression"
   Filtered Output: Safe fallback message directing to professionals
   ```

3. **Blocked: Prescription** ❌→✅
   ```
   Generated: "You should take 50mg of antidepressant"
   Filtered Output: Safe fallback message
   ```

4. **Blocked: Therapist Claim** ❌→✅
   ```
   Generated: "As your therapist, I recommend..."
   Filtered Output: Safe fallback message
   ```

5. **Blocked: Hallucination** ❌→✅
   ```
   Generated: "Research proves definitively that this is 100% effective"
   Filtered Output: Safe fallback message
   ```

6. **Blocked: Human Experience Claim** ❌→✅
   ```
   Generated: "I feel the same way, when I was going through this..."
   Filtered Output: Safe fallback message
   ```

---

## Running Tests

```bash
# Run all safety tests
python -m pytest test_safety.py -v

# Run specific test class
python -m pytest test_safety.py::TestCrisisDetection -v

# Run with coverage
pytest test_safety.py --cov=app --cov-report=html
```

### Expected Output

```
test_safety.py::TestCrisisDetection::test_suicide_keyword PASSED
test_safety.py::TestCrisisDetection::test_self_harm_keyword PASSED
test_safety.py::TestSafetyRequirements::test_safe_response PASSED
test_safety.py::TestSafetyRequirements::test_medical_diagnosis_blocked PASSED
...
16 passed in 1.20s
```

---

## Customization Examples

### Customize Crisis Keywords

```python
# In app.py
CRISIS_KEYWORDS = [
    "suicide", "suicidal", 
    # Add more keywords
    "self-harm", "hurt myself",
    # Add region-specific terms
]
```

### Customize Crisis Resources

```python
# In app.py
CRISIS_RESOURCES = """
🆘 **UK Crisis Resources:**
- Samaritans: 116 123
- Crisis Text Line: Text SHOUT to 85258

**Australia Crisis Resources:**
- Lifeline: 13 11 14
...
"""
```

### Customize Widget Colors

```css
/* In moodle_widget.html */
#mh-chat-button {
    background: linear-gradient(135deg, #your-color-1, #your-color-2);
}
```

---

## Integration with LLM Providers

### OpenAI Example

```python
import openai

async def generate_response(message: str, history: List[Dict]) -> str:
    if detect_crisis_keywords(message):
        return CRISIS_RESOURCES
    
    # Call OpenAI API
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": message}
        ]
    )
    
    response_text = response.choices[0].message.content
    
    # Validate with safety filters
    is_safe, violations = validate_response_safety(response_text)
    
    if not is_safe:
        return SAFE_FALLBACK_MESSAGE
    
    return response_text
```

### Anthropic Example

```python
from anthropic import Anthropic

async def generate_response(message: str, history: List[Dict]) -> str:
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    if detect_crisis_keywords(message):
        return CRISIS_RESOURCES
    
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        system=SYSTEM_PROMPT,
        messages=[*history, {"role": "user", "content": message}]
    )
    
    response_text = response.content[0].text
    
    # Validate with safety filters
    is_safe, violations = validate_response_safety(response_text)
    
    if not is_safe:
        return SAFE_FALLBACK_MESSAGE
    
    return response_text
```

---

## Monitoring and Analytics

### Log Analysis

Monitor logs for:

```bash
# Count safety filter violations
grep "Response failed safety checks" logs/app.log | wc -l

# View crisis detections
grep "crisis_detected" logs/app.log

# Count total conversations
grep "Chat session started" logs/app.log | wc -l
```

### Metrics to Track

- Total conversations started
- Crisis keyword detections
- Safety filter violations (by type)
- Average conversation length
- Most common topics (stress, anxiety, etc.)

---

## Best Practices

1. **Regular Updates**: Keep crisis resources up-to-date for your region
2. **Monitor Logs**: Review filtered responses to improve safety filters
3. **Test Changes**: Always run tests after modifying safety requirements
4. **Professional Partnership**: Work with campus counseling services
5. **Privacy**: Don't log sensitive conversation details
6. **HTTPS**: Always use HTTPS in production
7. **Rate Limiting**: Implement to prevent abuse
8. **Regular Maintenance**: Update dependencies and review safety filters

---

## Troubleshooting

### Too Many Responses Being Filtered

**Problem**: Most responses are being blocked by safety filters

**Solution**: Review the safety requirements and adjust patterns:
```python
# Be more specific with patterns to reduce false positives
# Instead of blocking "you have", use "you have [condition]"
```

### Crisis Resources Not Displaying

**Problem**: Crisis keywords not triggering resource display

**Solution**: 
1. Check CRISIS_KEYWORDS list includes the terms
2. Verify case-insensitive matching
3. Test with `detect_crisis_keywords("test message")`

### Widget Not Appearing in Moodle

**Problem**: Widget doesn't show on Moodle page

**Solution**:
1. Check browser console for errors
2. Verify CHAINLIT_SERVER_URL is correct
3. Check Moodle allows iframe embedding
4. Verify CORS settings on server

---

## Support and Feedback

For questions, issues, or feedback:
- GitHub Issues: https://github.com/Lip1200/mindmoodle/issues
- Documentation: See README.md and DEPLOYMENT.md
