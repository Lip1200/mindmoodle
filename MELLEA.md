# About Mellea Integration

## What is Mellea?

Mellea is a library for writing generative programs with built-in verification and validation capabilities. It provides structured approaches to ensure LLM outputs meet specific requirements.

## How We Use Mellea Principles

While we don't directly use the full mellea library in this implementation, we've adopted its **validation pattern** and philosophy:

### Mellea-Inspired Safety Architecture

1. **Requirement-Based Validation**
   - Each safety constraint is defined as a `SafetyRequirement`
   - Requirements have clear descriptions and validation functions
   - This mirrors mellea's `Requirement` concept

2. **Structured Safety Checks**
   ```python
   class SafetyRequirement:
       def __init__(self, description: str, check_fn: Callable[[str], bool]):
           self.description = description
           self.check = check_fn
   ```

3. **Validation Pipeline**
   - Generate response
   - Validate against all requirements
   - Collect violations
   - Take action (allow/filter)

### Why Not Full Mellea?

We use a **lightweight, mellea-inspired approach** instead of the full library because:

1. **Simplicity**: Our use case is focused - we only need response validation, not full generative program authoring
2. **Dependencies**: Reduces dependency weight for easier deployment
3. **Customization**: Easier to customize validation logic for mental health context
4. **Transparency**: Clear, readable code that stakeholders can audit

### Key Safety Requirements Implemented

Following mellea's validation philosophy, we implement these requirements:

1. **No Medical Diagnosis**
   - Prevents claiming to diagnose conditions
   - Blocks phrases like "you have [condition]"

2. **No Prescriptions**
   - Prevents recommending medications
   - Blocks dosage and pharmaceutical terms

3. **No Professional Claims**
   - Prevents claiming to be a therapist/doctor
   - Maintains clear AI identity

4. **Grounded Responses**
   - Prevents hallucinated facts
   - Blocks definitive unsupported claims

5. **AI Identity**
   - Prevents claiming human experiences
   - Maintains appropriate boundaries

### Future Enhancement: Full Mellea Integration

For organizations wanting more sophisticated validation, full mellea integration could provide:

1. **Advanced Validation**
   ```python
   from mellea import generative
   from mellea.stdlib.requirement import Requirement
   
   @generative
   def generate_safe_response(user_message: str) -> str:
       """Generate a safe, validated response."""
       response = generate_llm_response(user_message)
       
       # Mellea validation
       requirements = [
           Requirement(
               "No medical advice",
               validation_fn=lambda ctx: validate_no_medical_advice(ctx)
           )
       ]
       
       return response
   ```

2. **Formal Verification**
   - Mathematical guarantees about response properties
   - Compositional validation

3. **Repair Capabilities**
   - Automatic correction of violations
   - Iterative refinement

### References

- Mellea GitHub: https://github.com/ibm-granite/mellea
- Mellea Documentation: Check the repository for latest docs
- Our Implementation: See `app.py` for the safety validation code

### Audit Trail

For organizations requiring compliance:

```python
# All safety checks are logged
violations = validate_response_safety(response)
# Violations include:
# - Which requirement failed
# - Description of the requirement
# - The problematic response (for review)
```

This provides full transparency for mental health professionals and administrators to:
- Review filtered responses
- Adjust requirements
- Ensure student safety

---

## Extending the Safety System

To add new requirements:

```python
def create_safety_requirements() -> List[SafetyRequirement]:
    # Existing requirements...
    
    # Add new requirement
    no_emergency_delay = SafetyRequirement(
        "Does not delay emergency response",
        lambda text: not any(phrase in text.lower() for phrase in [
            "wait until", "try first before calling", 
            "no need to call immediately"
        ])
    )
    
    return [existing_requirements..., no_emergency_delay]
```

Each requirement:
1. Has a clear purpose
2. Uses pattern matching or logic
3. Can be tested independently
4. Provides clear violation messages

This modular approach, inspired by mellea, makes the system:
- **Maintainable**: Easy to update requirements
- **Testable**: Each requirement can be unit tested
- **Auditable**: Clear logic for each safety check
- **Extensible**: New requirements added without breaking existing ones
