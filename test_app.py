"""
Tests for TalentScout Hiring Assistant
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import ValidationUtils, SecurityUtils, ConversationUtils, TextProcessingUtils
from questions import TechnicalQuestions


class TestValidationUtils(unittest.TestCase):
    """Test validation utilities"""
    
    def test_validate_email(self):
        """Test email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            ""
        ]
        
        for email in valid_emails:
            self.assertTrue(ValidationUtils.validate_email(email), f"Should validate {email}")
        
        for email in invalid_emails:
            self.assertFalse(ValidationUtils.validate_email(email), f"Should not validate {email}")
    
    def test_validate_phone(self):
        """Test phone validation"""
        valid_phones = [
            "+1234567890",
            "1234567890",
            "+44 20 7946 0958",
            "(555) 123-4567"
        ]
        invalid_phones = [
            "123",
            "abc123def",
            "",
            "++1234567890"
        ]
        
        for phone in valid_phones:
            self.assertTrue(ValidationUtils.validate_phone(phone), f"Should validate {phone}")
        
        for phone in invalid_phones:
            self.assertFalse(ValidationUtils.validate_phone(phone), f"Should not validate {phone}")
    
    def test_validate_name(self):
        """Test name validation"""
        valid_names = [
            "John Doe",
            "Jane Smith-Wilson",
            "Mary O'Connor"
        ]
        invalid_names = [
            "A",
            "123",
            "",
            "John123"
        ]
        
        for name in valid_names:
            self.assertTrue(ValidationUtils.validate_name(name), f"Should validate {name}")
        
        for name in invalid_names:
            self.assertFalse(ValidationUtils.validate_name(name), f"Should not validate {name}")
    
    def test_validate_experience(self):
        """Test experience validation"""
        valid_experiences = [
            ("5", 5.0),
            ("3.5", 3.5),
            ("0", 0.0),
            ("25", 25.0)
        ]
        invalid_experiences = [
            "abc",
            "-1",
            "100",
            ""
        ]
        
        for exp_str, expected in valid_experiences:
            is_valid, value = ValidationUtils.validate_experience(exp_str)
            self.assertTrue(is_valid, f"Should validate {exp_str}")
            self.assertEqual(value, expected)
        
        for exp_str in invalid_experiences:
            is_valid, _ = ValidationUtils.validate_experience(exp_str)
            self.assertFalse(is_valid, f"Should not validate {exp_str}")


class TestSecurityUtils(unittest.TestCase):
    """Test security utilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use a test encryption key
        from cryptography.fernet import Fernet
        self.test_key = Fernet.generate_key().decode()
        self.security_utils = SecurityUtils(self.test_key)
    
    def test_encryption_decryption(self):
        """Test data encryption and decryption"""
        test_data = "sensitive information"
        
        # Test encryption
        encrypted = self.security_utils.encrypt_data(test_data)
        self.assertNotEqual(encrypted, test_data)
        
        # Test decryption
        decrypted = self.security_utils.decrypt_data(encrypted)
        self.assertEqual(decrypted, test_data)
    
    def test_generate_session_id(self):
        """Test session ID generation"""
        session_id1 = SecurityUtils.generate_session_id()
        session_id2 = SecurityUtils.generate_session_id()
        
        self.assertNotEqual(session_id1, session_id2)
        self.assertTrue(len(session_id1) > 0)
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = SecurityUtils.sanitize_input(dangerous_input)
        
        self.assertNotIn("<", sanitized)
        self.assertNotIn(">", sanitized)
        self.assertNotIn("'", sanitized)
        self.assertNotIn('"', sanitized)


class TestConversationUtils(unittest.TestCase):
    """Test conversation utilities"""
    
    def test_is_conversation_ending(self):
        """Test conversation ending detection"""
        ending_phrases = [
            "goodbye",
            "thank you for your time",
            "I want to quit",
            "bye bye"
        ]
        continuing_phrases = [
            "hello",
            "I want to continue",
            "tell me more"
        ]
        
        for phrase in ending_phrases:
            self.assertTrue(ConversationUtils.is_conversation_ending(phrase))
        
        for phrase in continuing_phrases:
            self.assertFalse(ConversationUtils.is_conversation_ending(phrase))
    
    def test_is_greeting(self):
        """Test greeting detection"""
        greeting_phrases = [
            "hello",
            "hi there",
            "good morning",
            "hey"
        ]
        non_greeting_phrases = [
            "my name is John",
            "I have experience",
            "goodbye"
        ]
        
        for phrase in greeting_phrases:
            self.assertTrue(ConversationUtils.is_greeting(phrase))
        
        for phrase in non_greeting_phrases:
            self.assertFalse(ConversationUtils.is_greeting(phrase))
    
    def test_format_tech_stack(self):
        """Test tech stack formatting"""
        raw_tech = ["  python  ", "JAVASCRIPT", "", "react", "a"]
        formatted = ConversationUtils.format_tech_stack(raw_tech)
        
        expected = ["Python", "Javascript", "React"]
        self.assertEqual(formatted, expected)
    
    def test_generate_conversation_id(self):
        """Test conversation ID generation"""
        conv_id1 = ConversationUtils.generate_conversation_id()
        conv_id2 = ConversationUtils.generate_conversation_id()
        
        self.assertNotEqual(conv_id1, conv_id2)
        self.assertTrue(conv_id1.startswith("conv_"))


class TestTextProcessingUtils(unittest.TestCase):
    """Test text processing utilities"""
    
    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "  Hello    world!  \n\n  Extra   spaces  "
        cleaned = TextProcessingUtils.clean_text(dirty_text)
        
        self.assertEqual(cleaned, "Hello world! Extra spaces")
    
    def test_extract_tech_stack(self):
        """Test tech stack extraction"""
        tech_text = "Python, JavaScript, React, Node.js and Docker"
        extracted = TextProcessingUtils.extract_tech_stack(tech_text)
        
        expected = ["Python", "JavaScript", "React", "Node.js", "Docker"]
        self.assertEqual(extracted, expected)
    
    def test_truncate_text(self):
        """Test text truncation"""
        long_text = "This is a very long text that should be truncated at some point"
        truncated = TextProcessingUtils.truncate_text(long_text, 30)
        
        self.assertTrue(len(truncated) <= 33)  # 30 + "..."
        self.assertTrue(truncated.endswith("..."))


class TestTechnicalQuestions(unittest.TestCase):
    """Test technical questions functionality"""
    
    def test_get_questions_for_technology(self):
        """Test getting questions for specific technology"""
        python_questions = TechnicalQuestions.get_questions_for_technology("python", "intermediate", 3)
        
        self.assertEqual(len(python_questions), 3)
        self.assertTrue(all(isinstance(q, str) for q in python_questions))
    
    def test_get_experience_level_from_years(self):
        """Test experience level determination"""
        self.assertEqual(TechnicalQuestions.get_experience_level_from_years(1), "beginner")
        self.assertEqual(TechnicalQuestions.get_experience_level_from_years(3), "intermediate")
        self.assertEqual(TechnicalQuestions.get_experience_level_from_years(7), "advanced")
    
    def test_get_all_supported_technologies(self):
        """Test getting all supported technologies"""
        technologies = TechnicalQuestions.get_all_supported_technologies()
        
        self.assertIn("python", technologies)
        self.assertIn("javascript", technologies)
        self.assertIn("sql", technologies)
        self.assertTrue(len(technologies) > 5)
    
    def test_get_questions_for_tech_stack(self):
        """Test getting questions for tech stack"""
        tech_stack = ["python", "javascript", "sql"]
        questions = TechnicalQuestions.get_questions_for_tech_stack(tech_stack, 3.0, 5)
        
        self.assertTrue(len(questions) <= 5)
        self.assertTrue(len(questions) >= 3)  # At least one question per technology


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_complete_workflow(self):
        """Test complete candidate processing workflow"""
        # Simulate candidate data
        candidate_data = {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "experience": 5.0,
            "desired_position": "Software Developer",
            "location": "New York, NY",
            "tech_stack": ["Python", "JavaScript", "SQL"]
        }
        
        # Validate all fields
        self.assertTrue(ValidationUtils.validate_name(candidate_data["full_name"]))
        self.assertTrue(ValidationUtils.validate_email(candidate_data["email"]))
        self.assertTrue(ValidationUtils.validate_phone(candidate_data["phone"]))
        
        is_valid, exp_value = ValidationUtils.validate_experience(str(candidate_data["experience"]))
        self.assertTrue(is_valid)
        self.assertEqual(exp_value, 5.0)
        
        # Generate technical questions
        questions = TechnicalQuestions.get_questions_for_tech_stack(
            candidate_data["tech_stack"], 
            candidate_data["experience"], 
            5
        )
        
        self.assertTrue(len(questions) > 0)
        self.assertTrue(len(questions) <= 5)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
