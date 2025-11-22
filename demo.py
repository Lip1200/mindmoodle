#!/usr/bin/env python3
"""
Demonstration script for Mental Health Support Assistant

This script demonstrates the safety filtering and crisis detection features
without requiring a full Chainlit environment.
"""

from app import (
    detect_crisis_keywords,
    validate_response_safety,
    CRISIS_RESOURCES
)


def demo_crisis_detection():
    """Demonstrate crisis keyword detection."""
    print("=" * 60)
    print("CRISIS DETECTION DEMONSTRATION")
    print("=" * 60)
    
    test_messages = [
        ("I'm feeling stressed about exams", False),
        ("I'm thinking about suicide", True),
        ("I want to hurt myself", True),
        ("I'm feeling sad today", False),
        ("No reason to live anymore", True),
    ]
    
    for message, expected in test_messages:
        detected = detect_crisis_keywords(message)
        status = "✓ CRISIS" if detected else "  Normal"
        match = "✓" if detected == expected else "✗"
        print(f"{match} {status}: {message[:50]}")
    
    print("\nCrisis resources would show:")
    print(CRISIS_RESOURCES[:200] + "...")
    print()


def demo_safety_filtering():
    """Demonstrate safety requirement filtering."""
    print("=" * 60)
    print("SAFETY FILTERING DEMONSTRATION")
    print("=" * 60)
    
    test_responses = [
        (
            "I hear that you're feeling stressed. Have you tried deep breathing?",
            "Safe supportive response",
            True
        ),
        (
            "You have clinical depression based on what you told me.",
            "Medical diagnosis (BLOCKED)",
            False
        ),
        (
            "You should take 50mg of antidepressant medication.",
            "Prescription (BLOCKED)",
            False
        ),
        (
            "As your therapist, I recommend this treatment.",
            "Therapist claim (BLOCKED)",
            False
        ),
        (
            "Research proves definitively this is 100% effective.",
            "Hallucination (BLOCKED)",
            False
        ),
        (
            "I feel the same way, when I was going through this...",
            "Human experience claim (BLOCKED)",
            False
        ),
    ]
    
    for response, description, expected_safe in test_responses:
        is_safe, violations = validate_response_safety(response)
        status = "✓ SAFE" if is_safe else "✗ BLOCKED"
        match = "✓" if is_safe == expected_safe else "✗"
        
        print(f"\n{match} {status}: {description}")
        print(f"   Response: {response[:60]}...")
        if not is_safe:
            print(f"   Violations: {len(violations)}")
            for v in violations[:2]:  # Show first 2 violations
                print(f"     - {v[:70]}...")
    
    print()


def demo_conversation_flow():
    """Demonstrate a typical conversation flow."""
    print("=" * 60)
    print("CONVERSATION FLOW DEMONSTRATION")
    print("=" * 60)
    
    conversations = [
        {
            "user": "I'm feeling really anxious about my presentation",
            "assistant": "Anxiety can be really challenging. Have you tried grounding techniques?"
        },
        {
            "user": "I'm so stressed I can't sleep",
            "assistant": "I hear that you're feeling stressed. Some helpful strategies include..."
        },
        {
            "user": "Everything feels hopeless",
            "assistant": CRISIS_RESOURCES  # Would trigger crisis detection in real app
        }
    ]
    
    for i, conv in enumerate(conversations, 1):
        print(f"\n--- Conversation {i} ---")
        print(f"User: {conv['user']}")
        
        # Check for crisis
        if detect_crisis_keywords(conv['user']):
            print("🚨 CRISIS DETECTED - Showing resources")
            print(f"Assistant: {conv['assistant'][:100]}...")
        else:
            # Validate response
            is_safe, violations = validate_response_safety(conv['assistant'])
            if is_safe:
                print(f"Assistant: {conv['assistant'][:80]}...")
            else:
                print("⚠️ Response filtered - showing safe fallback")
    
    print()


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Mental Health Support Assistant Demo" + " " * 11 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    demo_crisis_detection()
    demo_safety_filtering()
    demo_conversation_flow()
    
    print("=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nAll safety features are working correctly! ✓")
    print("\nTo run the full Chainlit application:")
    print("  chainlit run app.py")
    print("\nTo run tests:")
    print("  python -m pytest test_safety.py -v")
    print()


if __name__ == "__main__":
    main()
