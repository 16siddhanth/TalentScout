"""
Utility functions for TalentScout Hiring Assistant
"""
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from cryptography.fernet import Fernet


class ValidationUtils:
    """Utility class for data validation"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove common separators
        clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        pattern = r'^[\+]?[1-9][\d]{7,14}$'
        return re.match(pattern, clean_phone) is not None
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate name format"""
        return len(name.strip()) >= 2 and name.replace(' ', '').replace('-', '').replace("'", '').isalpha()
    
    @staticmethod
    def validate_experience(experience: str) -> tuple[bool, float]:
        """Validate and parse experience"""
        try:
            exp_float = float(experience.strip())
            return 0 <= exp_float <= 50, exp_float
        except ValueError:
            return False, 0.0


class SecurityUtils:
    """Utility class for security operations"""
    
    def __init__(self, encryption_key: str):
        """Initialize with encryption key"""
        self.cipher_suite = Fernet(encryption_key.encode()) if encryption_key else None
    
    def encrypt_data(self, data: Any) -> str:
        """Encrypt data"""
        if not self.cipher_suite:
            return data
        
        json_data = json.dumps(data) if not isinstance(data, str) else data
        return self.cipher_suite.encrypt(json_data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> Any:
        """Decrypt data"""
        if not self.cipher_suite:
            return encrypted_data
        
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data.encode()).decode()
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return decrypted
        except Exception:
            return encrypted_data
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', text)
        return sanitized.strip()


class ConversationUtils:
    """Utility class for conversation management"""
    
    CONVERSATION_ENDING_KEYWORDS = [
        'goodbye', 'bye', 'exit', 'quit', 'thank you', 
        'thanks', 'done', 'finish', 'end', 'stop'
    ]
    
    GREETING_KEYWORDS = [
        'hello', 'hi', 'hey', 'start', 'begin', 'good morning',
        'good afternoon', 'good evening'
    ]
    
    @classmethod
    def is_conversation_ending(cls, text: str) -> bool:
        """Check if user wants to end conversation"""
        text_lower = text.lower().strip()
        return any(keyword in text_lower for keyword in cls.CONVERSATION_ENDING_KEYWORDS)
    
    @classmethod
    def is_greeting(cls, text: str) -> bool:
        """Check if user is greeting"""
        text_lower = text.lower().strip()
        return any(keyword in text_lower for keyword in cls.GREETING_KEYWORDS)
    
    @staticmethod
    def format_tech_stack(tech_list: List[str]) -> List[str]:
        """Format and clean tech stack list"""
        formatted = []
        for tech in tech_list:
            clean_tech = tech.strip()
            if clean_tech and len(clean_tech) > 1:
                formatted.append(clean_tech.title())
        return formatted
    
    @staticmethod
    def generate_conversation_id() -> str:
        """Generate unique conversation ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"conv_{timestamp}_{unique_id}"


class TextProcessingUtils:
    """Utility class for text processing"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s\-.,!?@]', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def extract_tech_stack(text: str) -> List[str]:
        """Extract technology names from text"""
        # Common separators
        separators = [',', ';', '|', '\n', 'and', '&']
        
        # Replace separators with commas
        for sep in separators:
            text = text.replace(sep, ',')
        
        # Split and clean
        tech_items = [item.strip() for item in text.split(',')]
        
        # Filter out empty items and common words
        common_words = ['the', 'and', 'or', 'with', 'using', 'also', 'include', 'includes']
        tech_stack = []
        
        for item in tech_items:
            if item and len(item) > 1 and item.lower() not in common_words:
                tech_stack.append(item)
        
        return tech_stack
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 500) -> str:
        """Truncate text to specified length"""
        if len(text) <= max_length:
            return text
        
        # Try to truncate at word boundary
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:  # If we found a space reasonably close
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."


class DataExportUtils:
    """Utility class for data export operations"""
    
    @staticmethod
    def export_candidate_data(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export candidate data in structured format"""
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_candidates': len(candidates),
            'candidates': []
        }
        
        for candidate in candidates:
            # Remove encrypted fields and internal IDs for export
            clean_candidate = {
                k: v for k, v in candidate.items() 
                if not k.endswith('_encrypted') and k not in ['id']
            }
            export_data['candidates'].append(clean_candidate)
        
        return export_data
    
    @staticmethod
    def generate_summary_stats(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from candidate data"""
        if not candidates:
            return {}
        
        # Experience statistics
        experiences = [c.get('experience', 0) for c in candidates]
        
        # Position distribution
        positions = [c.get('desired_position', 'Unknown') for c in candidates]
        position_counts = {}
        for pos in positions:
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        # Tech stack analysis
        all_tech = []
        for candidate in candidates:
            tech_stack = candidate.get('tech_stack', [])
            all_tech.extend(tech_stack)
        
        tech_counts = {}
        for tech in all_tech:
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        return {
            'total_candidates': len(candidates),
            'avg_experience': sum(experiences) / len(experiences) if experiences else 0,
            'experience_range': {
                'min': min(experiences) if experiences else 0,
                'max': max(experiences) if experiences else 0
            },
            'top_positions': dict(sorted(position_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'top_technologies': dict(sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'completion_rate': len([c for c in candidates if c.get('technical_answers')]) / len(candidates) * 100
        }


class LoggingUtils:
    """Utility class for logging operations"""
    
    @staticmethod
    def log_conversation_event(event_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Log conversation event"""
        return {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
    
    @staticmethod
    def log_error(error: Exception, context: str = "") -> Dict[str, Any]:
        """Log error with context"""
        return {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }


# Factory function for creating utility instances
def create_security_utils(encryption_key: str) -> SecurityUtils:
    """Factory function to create SecurityUtils instance"""
    return SecurityUtils(encryption_key)
