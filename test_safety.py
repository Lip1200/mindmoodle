"""
Test suite for Mental Health Support Assistant safety features.

Tests crisis detection and mellea-based filtering of hallucinations
and medical advice.
"""

import pytest
from app import (
    detect_crisis_keywords,
    create_safety_requirements,
    validate_response_safety
)


class TestCrisisDetection:
    """Test crisis keyword detection."""
    
    def test_suicide_keyword(self):
        """Test detection of suicide-related keywords."""
        assert detect_crisis_keywords("I'm thinking about suicide") == True
        assert detect_crisis_keywords("feeling suicidal") == True
        
    def test_self_harm_keyword(self):
        """Test detection of self-harm keywords."""
        assert detect_crisis_keywords("I want to hurt myself") == True
        assert detect_crisis_keywords("self-harm thoughts") == True
        
    def test_hopeless_keyword(self):
        """Test detection of hopelessness keywords."""
        assert detect_crisis_keywords("I feel hopeless") == True
        assert detect_crisis_keywords("no reason to live") == True
        
    def test_no_crisis_keywords(self):
        """Test that normal messages don't trigger crisis detection."""
        assert detect_crisis_keywords("I'm feeling stressed") == False
        assert detect_crisis_keywords("I'm sad today") == False
        assert detect_crisis_keywords("I need help with anxiety") == False
        
    def test_case_insensitive(self):
        """Test that detection is case-insensitive."""
        assert detect_crisis_keywords("I want to KILL MYSELF") == True
        assert detect_crisis_keywords("Suicidal thoughts") == True


class TestSafetyRequirements:
    """Test mellea safety requirement filtering."""
    
    def test_safe_response(self):
        """Test that safe responses pass validation."""
        safe_response = (
            "I hear that you're feeling stressed. That's completely valid. "
            "Have you tried taking a short break or practicing deep breathing?"
        )
        is_safe, violations = validate_response_safety(safe_response)
        assert is_safe == True
        assert len(violations) == 0
        
    def test_medical_diagnosis_blocked(self):
        """Test that medical diagnoses are blocked."""
        unsafe_response = "You have clinical depression based on what you told me."
        is_safe, violations = validate_response_safety(unsafe_response)
        assert is_safe == False
        assert any("diagnos" in v.lower() for v in violations)
        
    def test_prescription_blocked(self):
        """Test that medication prescriptions are blocked."""
        unsafe_response = "You should take 50mg of this antidepressant medication."
        is_safe, violations = validate_response_safety(unsafe_response)
        assert is_safe == False
        assert any("prescri" in v.lower() or "medication" in v.lower() for v in violations)
        
    def test_therapist_claim_blocked(self):
        """Test that claiming to be a therapist is blocked."""
        unsafe_response = "As your therapist, I can tell you that..."
        is_safe, violations = validate_response_safety(unsafe_response)
        assert is_safe == False
        assert any("therapist" in v.lower() or "professional" in v.lower() for v in violations)
        
    def test_hallucination_blocked(self):
        """Test that hallucinated facts are blocked."""
        unsafe_response = "Research proves definitively that this is 100% effective."
        is_safe, violations = validate_response_safety(unsafe_response)
        assert is_safe == False
        assert any("grounded" in v.lower() or "fact" in v.lower() for v in violations)
        
    def test_human_claim_blocked(self):
        """Test that claiming human experiences is blocked."""
        unsafe_response = "I feel the same way, when I was going through this..."
        is_safe, violations = validate_response_safety(unsafe_response)
        assert is_safe == False
        assert any("identity" in v.lower() or "human" in v.lower() for v in violations)
        
    def test_supportive_response(self):
        """Test that genuinely supportive responses pass."""
        safe_response = (
            "Thank you for sharing that with me. Your feelings are valid. "
            "It sounds like you're going through a challenging time. "
            "Have you considered talking to a counselor about this?"
        )
        is_safe, violations = validate_response_safety(safe_response)
        assert is_safe == True
        
    def test_resource_referral(self):
        """Test that referrals to professional resources pass."""
        safe_response = (
            "For professional support, I encourage you to contact "
            "your campus counseling center. They can provide personalized care."
        )
        is_safe, violations = validate_response_safety(safe_response)
        assert is_safe == True


class TestSafetyRequirementCreation:
    """Test that safety requirements are properly created."""
    
    def test_requirements_list_created(self):
        """Test that requirements list is created."""
        requirements = create_safety_requirements()
        assert isinstance(requirements, list)
        assert len(requirements) > 0
        
    def test_all_requirements_have_checks(self):
        """Test that all requirements have check functions."""
        requirements = create_safety_requirements()
        for req in requirements:
            assert hasattr(req, 'check')
            assert callable(req.check)
            
    def test_all_requirements_have_descriptions(self):
        """Test that all requirements have descriptions."""
        requirements = create_safety_requirements()
        for req in requirements:
            assert hasattr(req, 'description')
            assert isinstance(req.description, str)
            assert len(req.description) > 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
