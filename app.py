import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import re
import time
from cryptography.fernet import Fernet
from textblob import TextBlob
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()

class DataHandler:
    """Handle secure data storage and retrieval with enhanced features"""
    
    def __init__(self):
        self.encryption_key = os.getenv('ENCRYPTION_KEY')
        if self.encryption_key:
            self.cipher_suite = Fernet(self.encryption_key.encode())
        else:
            self.cipher_suite = None
        
        # Initialize data storage
        if 'candidates_data' not in st.session_state:
            st.session_state.candidates_data = []
        
        if 'conversation_analytics' not in st.session_state:
            st.session_state.conversation_analytics = {
                'total_conversations': 0,
                'completed_assessments': 0,
                'average_completion_time': 0,
                'drop_off_points': {},
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0}
            }
    
    def encrypt_data(self, data):
        """Encrypt sensitive data with error handling"""
        if self.cipher_suite:
            try:
                return self.cipher_suite.encrypt(json.dumps(data).encode()).decode()
            except Exception as e:
                st.error(f"Encryption error: {str(e)}")
                return data
        return data
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data with error handling"""
        if self.cipher_suite and isinstance(encrypted_data, str):
            try:
                return json.loads(self.cipher_suite.decrypt(encrypted_data.encode()).decode())
            except Exception as e:
                st.error(f"Decryption error: {str(e)}")
                return encrypted_data
        return encrypted_data
    
    def save_candidate_data(self, candidate_info):
        """Save candidate data securely with enhanced metadata"""
        candidate_info['id'] = str(uuid.uuid4())
        candidate_info['timestamp'] = datetime.now().isoformat()
        candidate_info['session_duration'] = self.calculate_session_duration()
        candidate_info['completion_status'] = self.get_completion_status()
        
        # Encrypt sensitive information
        sensitive_fields = ['email', 'phone', 'full_name']
        for field in sensitive_fields:
            if field in candidate_info:
                candidate_info[f'{field}_encrypted'] = self.encrypt_data(candidate_info[field])
                # Keep original for session display, remove before storage
                candidate_info[f'{field}_original'] = candidate_info[field]
                del candidate_info[field]
        
        st.session_state.candidates_data.append(candidate_info)
        self.update_analytics()
        return candidate_info['id']
    
    def calculate_session_duration(self):
        """Calculate session duration"""
        if 'session_start_time' not in st.session_state:
            st.session_state.session_start_time = datetime.now()
            return 0
        
        duration = (datetime.now() - st.session_state.session_start_time).total_seconds() / 60
        return round(duration, 2)
    
    def get_completion_status(self):
        """Get current completion status"""
        stage = st.session_state.get('conversation_stage', 'greeting')
        completion_map = {
            'greeting': 0,
            'collecting_name': 10,
            'collecting_email': 20,
            'collecting_phone': 30,
            'collecting_experience': 40,
            'collecting_position': 50,
            'collecting_location': 60,
            'collecting_tech_stack': 70,
            'technical_questions': 80,
            'completed': 100
        }
        return completion_map.get(stage, 0)
    
    def update_analytics(self):
        """Update conversation analytics"""
        analytics = st.session_state.conversation_analytics
        analytics['total_conversations'] += 1
        
        if st.session_state.get('conversation_stage') == 'completed':
            analytics['completed_assessments'] += 1
        
        # Update average completion time
        durations = [c.get('session_duration', 0) for c in st.session_state.candidates_data if c.get('session_duration')]
        if durations:
            analytics['average_completion_time'] = round(sum(durations) / len(durations), 2)
    
    def export_data(self, format_type='json'):
        """Export candidate data in various formats"""
        if not st.session_state.candidates_data:
            return None
        
        if format_type == 'json':
            return json.dumps(st.session_state.candidates_data, indent=2)
        elif format_type == 'csv':
            df = pd.DataFrame(st.session_state.candidates_data)
            return df.to_csv(index=False)
        elif format_type == 'excel':
            df = pd.DataFrame(st.session_state.candidates_data)
            return df.to_excel(index=False)
        
        return None

class TechStackQuestionGenerator:
    """Generate technical questions based on tech stack"""
    
    TECH_QUESTIONS = {
        'python': [
            "Explain the difference between list and tuple in Python",
            "What is a decorator in Python and how would you implement one?",
            "How does Python's garbage collection work?",
            "Explain the concept of generators and yield keyword",
            "What are Python's data structures and when would you use each?"
        ],
        'javascript': [
            "Explain the difference between var, let, and const",
            "What is closure in JavaScript and provide an example",
            "How does the event loop work in JavaScript?",
            "Explain promises and async/await",
            "What is the difference between == and === in JavaScript?"
        ],
        'react': [
            "Explain the virtual DOM and how React uses it",
            "What are React hooks and why were they introduced?",
            "Describe the component lifecycle in React",
            "How would you optimize a React application's performance?",
            "Explain the difference between controlled and uncontrolled components"
        ],
        'django': [
            "Explain Django's MTV architecture",
            "What are Django models and how do they relate to databases?",
            "How does Django's ORM work?",
            "Explain Django's middleware and provide an example",
            "What is Django's admin interface and how do you customize it?"
        ],
        'sql': [
            "Explain the difference between INNER JOIN and LEFT JOIN",
            "What are database indexes and how do they improve performance?",
            "Describe ACID properties in database transactions",
            "How would you optimize a slow SQL query?",
            "Explain normalization and denormalization in databases"
        ],
        'java': [
            "Explain the concept of Object-Oriented Programming in Java",
            "What is the difference between abstract class and interface?",
            "How does Java's garbage collection work?",
            "Explain the concept of multithreading in Java",
            "What are Java Collections and when would you use each type?"
        ],
        'aws': [
            "Explain the difference between EC2 and Lambda",
            "What is S3 and what are its use cases?",
            "How does auto-scaling work in AWS?",
            "Explain VPC and its components",
            "What are the different types of load balancers in AWS?"
        ],
        'docker': [
            "Explain the difference between containers and virtual machines",
            "What is a Dockerfile and how do you write one?",
            "How do you manage persistent data in Docker containers?",
            "Explain Docker networking and different network types",
            "What is Docker Compose and when would you use it?"
        ]
    }
    
    @classmethod
    def get_questions_for_tech(cls, tech_stack):
        """Generate questions based on tech stack"""
        questions = []
        for tech in tech_stack:
            tech_lower = tech.lower().strip()
            if tech_lower in cls.TECH_QUESTIONS:
                questions.extend(cls.TECH_QUESTIONS[tech_lower][:3])
        
        # If no specific questions found, generate generic ones
        if not questions:
            questions = [
                f"Describe your experience with {tech_stack[0] if tech_stack else 'your primary technology'}",
                "What project are you most proud of and what technologies did you use?",
                "How do you stay updated with the latest technology trends?",
                "Describe a challenging technical problem you solved recently",
                "What are your preferred development tools and why?"
            ]
        
        return questions[:5]  # Return maximum 5 questions

class AdvancedSentimentAnalyzer:
    """Advanced sentiment and emotion analysis"""
    
    def __init__(self):
        # Initialize emotion keywords
        self.emotion_keywords = {
            'confident': ['confident', 'sure', 'certain', 'experienced', 'skilled', 'expert'],
            'nervous': ['nervous', 'worried', 'anxious', 'uncertain', 'unsure', 'confused'],
            'excited': ['excited', 'enthusiastic', 'passionate', 'motivated', 'eager'],
            'frustrated': ['frustrated', 'annoyed', 'difficult', 'challenging', 'stuck'],
            'satisfied': ['good', 'great', 'excellent', 'perfect', 'wonderful', 'amazing']
        }
    
    @staticmethod
    def analyze_sentiment(text):
        """Analyze sentiment using TextBlob with enhanced categorization"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Enhanced sentiment classification
            if polarity > 0.3:
                sentiment = "very_positive"
            elif polarity > 0.1:
                sentiment = "positive"
            elif polarity > -0.1:
                sentiment = "neutral"
            elif polarity > -0.3:
                sentiment = "negative"
            else:
                sentiment = "very_negative"
            
            return {
                'sentiment': sentiment,
                'polarity': round(polarity, 2),
                'subjectivity': round(subjectivity, 2),
                'confidence': abs(polarity)
            }
        except Exception:
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.0,
                'confidence': 0.0
            }
    
    def detect_emotion(self, text):
        """Detect specific emotions in text"""
        text_lower = text.lower()
        detected_emotions = []
        
        for emotion, keywords in self.emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions if detected_emotions else ['neutral']
    
    def get_sentiment_emoji(self, sentiment):
        """Get emoji based on sentiment with more variety"""
        emoji_map = {
            "very_positive": "🌟",
            "positive": "😊",
            "neutral": "😐",
            "negative": "😟",
            "very_negative": "😔"
        }
        return emoji_map.get(sentiment, "😐")
    
    def get_emotion_emoji(self, emotions):
        """Get emoji based on detected emotions"""
        emotion_emojis = {
            'confident': '💪',
            'nervous': '😰',
            'excited': '🎉',
            'frustrated': '😤',
            'satisfied': '✨',
            'neutral': '😐'
        }
        
        if emotions:
            return emotion_emojis.get(emotions[0], '😐')
        return '😐'
    
    def analyze_response_quality(self, text, min_length=10):
        """Analyze the quality of user response"""
        word_count = len(text.split())
        char_count = len(text.strip())
        
        # Basic quality metrics
        quality_score = 0
        feedback = []
        
        if char_count >= min_length:
            quality_score += 30
        else:
            feedback.append("Try to provide more detailed answers")
        
        if word_count >= 5:
            quality_score += 25
        
        if any(char.isupper() for char in text):
            quality_score += 10  # Proper capitalization
        
        if '.' in text or '!' in text or '?' in text:
            quality_score += 15  # Proper punctuation
        
        # Technical terms bonus
        tech_terms = ['algorithm', 'database', 'framework', 'api', 'function', 'class', 'object']
        if any(term in text.lower() for term in tech_terms):
            quality_score += 20
            feedback.append("Great use of technical terminology!")
        
        # Determine quality level
        if quality_score >= 80:
            quality = "excellent"
        elif quality_score >= 60:
            quality = "good"
        elif quality_score >= 40:
            quality = "fair"
        else:
            quality = "needs_improvement"
        
        return {
            'quality': quality,
            'score': quality_score,
            'word_count': word_count,
            'feedback': feedback
        }

class EnhancedLanguageDetector:
    """Enhanced language detection and multilingual support"""
    
    SUPPORTED_LANGUAGES = {
        'en': {'name': 'English', 'flag': '🇺🇸'},
        'es': {'name': 'Spanish', 'flag': '🇪🇸'},
        'fr': {'name': 'French', 'flag': '🇫🇷'},
        'de': {'name': 'German', 'flag': '🇩🇪'},
        'hi': {'name': 'Hindi', 'flag': '🇮🇳'},
        'zh': {'name': 'Chinese', 'flag': '🇨🇳'},
        'ja': {'name': 'Japanese', 'flag': '🇯🇵'},
        'ko': {'name': 'Korean', 'flag': '🇰🇷'},
        'pt': {'name': 'Portuguese', 'flag': '🇵🇹'},
        'it': {'name': 'Italian', 'flag': '🇮🇹'}
    }
    
    # Enhanced translations for key phrases
    TRANSLATIONS = {
        'greeting': {
            'en': "Hello! Welcome to TalentScout's Hiring Assistant! 👋",
            'es': "¡Hola! ¡Bienvenido al Asistente de Contratación de TalentScout! 👋",
            'fr': "Bonjour! Bienvenue à l'Assistant d'Embauche de TalentScout! 👋",
            'de': "Hallo! Willkommen bei TalentScouts Einstellungsassistent! 👋",
            'hi': "नमस्ते! TalentScout के हायरिंग असिस्टेंट में आपका स्वागत है! 👋",
            'zh': "你好！欢迎使用TalentScout招聘助手！👋",
            'ja': "こんにちは！TalentScoutの採用アシスタントへようこそ！👋",
            'ko': "안녕하세요! TalentScout 채용 도우미에 오신 것을 환영합니다! 👋",
            'pt': "Olá! Bem-vindo ao Assistente de Contratação da TalentScout! 👋",
            'it': "Ciao! Benvenuto nell'Assistente per le Assunzioni di TalentScout! 👋"
        },
        'name_request': {
            'en': "What's your full name?",
            'es': "¿Cuál es tu nombre completo?",
            'fr': "Quel est votre nom complet?",
            'de': "Wie ist Ihr vollständiger Name?",
            'hi': "आपका पूरा नाम क्या है?",
            'zh': "您的全名是什么？",
            'ja': "お名前をフルネームで教えてください。",
            'ko': "성함을 알려주세요.",
            'pt': "Qual é o seu nome completo?",
            'it': "Qual è il suo nome completo?"
        },
        'email_request': {
            'en': "Could you please provide your email address?",
            'es': "¿Podrías proporcionar tu dirección de correo electrónico?",
            'fr': "Pourriez-vous fournir votre adresse e-mail?",
            'de': "Könnten Sie bitte Ihre E-Mail-Adresse angeben?",
            'hi': "कृपया अपना ईमेल पता बताएं?",
            'zh': "请提供您的电子邮件地址？",
            'ja': "メールアドレスを教えてください。",
            'ko': "이메일 주소를 알려주세요.",
            'pt': "Você poderia fornecer seu endereço de e-mail?",
            'it': "Potresti fornire il tuo indirizzo email?"
        },
        'thank_you': {
            'en': "Thank you for using TalentScout's Hiring Assistant!",
            'es': "¡Gracias por usar el Asistente de Contratación de TalentScout!",
            'fr': "Merci d'avoir utilisé l'Assistant d'Embauche de TalentScout!",
            'de': "Vielen Dank für die Nutzung von TalentScouts Einstellungsassistent!",
            'hi': "TalentScout के हायरिंग असिस्टेंट का उपयोग करने के लिए धन्यवाद!",
            'zh': "感谢您使用TalentScout招聘助手！",
            'ja': "TalentScoutの採用アシスタントをご利用いただきありがとうございます！",
            'ko': "TalentScout 채용 도우미를 이용해 주셔서 감사합니다!",
            'pt': "Obrigado por usar o Assistente de Contratação da TalentScout!",
            'it': "Grazie per aver utilizzato l'Assistente per le Assunzioni di TalentScout!"
        }
    }
    
    @staticmethod
    def detect_language(text):
        """Detect language of input text with fallback"""
        try:
            detected = detect(text)
            return detected if detected in EnhancedLanguageDetector.SUPPORTED_LANGUAGES else 'en'
        except LangDetectException:
            return 'en'  # Default to English
    
    @classmethod
    def get_translation(cls, key, lang='en'):
        """Get translation for a key in specified language"""
        return cls.TRANSLATIONS.get(key, {}).get(lang, cls.TRANSLATIONS.get(key, {}).get('en', ''))
    
    @classmethod
    def get_language_info(cls, lang_code):
        """Get language information"""
        return cls.SUPPORTED_LANGUAGES.get(lang_code, {'name': 'English', 'flag': '🇺🇸'})
    
    @classmethod
    def auto_translate_response(cls, text, target_lang='en'):
        """Simple keyword-based translation for common responses"""
        if target_lang == 'en':
            return text
        
        # Simple translation patterns
        translation_patterns = {
            'es': {
                'Hello': 'Hola',
                'Thank you': 'Gracias',
                'Please': 'Por favor',
                'Good': 'Bueno',
                'Yes': 'Sí',
                'No': 'No'
            },
            'fr': {
                'Hello': 'Bonjour',
                'Thank you': 'Merci',
                'Please': 'S\'il vous plaît',
                'Good': 'Bon',
                'Yes': 'Oui',
                'No': 'Non'
            }
        }
        
        patterns = translation_patterns.get(target_lang, {})
        for english, translation in patterns.items():
            text = text.replace(english, translation)
        
        return text

class HiringAssistant:
    """Main Hiring Assistant chatbot class"""
    
    def __init__(self):
        self.setup_gemini()
        self.data_handler = DataHandler()
        self.question_generator = TechStackQuestionGenerator()
        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
        self.language_detector = EnhancedLanguageDetector()
        
        # Initialize session state
        self.init_session_state()
    
    def setup_gemini(self):
        """Configure Gemini AI"""
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            st.error("GEMINI_API_KEY not found in environment variables")
            self.model = None
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'conversation_stage' not in st.session_state:
            st.session_state.conversation_stage = 'greeting'
        
        if 'candidate_info' not in st.session_state:
            st.session_state.candidate_info = {}
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'tech_questions' not in st.session_state:
            st.session_state.tech_questions = []
        
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        
        if 'conversation_ended' not in st.session_state:
            st.session_state.conversation_ended = False
        
        if 'user_language' not in st.session_state:
            st.session_state.user_language = 'en'
    
    def generate_ai_response(self, prompt, context=""):
        """Generate response using Gemini AI"""
        if not self.model:
            return "I'm sorry, but I'm currently unable to process your request. Please try again later."
        
        try:
            full_prompt = f"""
            You are a professional hiring assistant for TalentScout, a technology recruitment agency.
            Your role is to:
            1. Gather candidate information professionally
            2. Generate relevant technical questions based on their tech stack
            3. Maintain a professional but friendly tone
            4. Stay focused on recruitment-related topics
            
            Context: {context}
            User input: {prompt}
            
            Respond professionally and keep the conversation focused on the hiring process.
            """
            
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error. Please try again. Error: {str(e)}"
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone):
        """Validate phone number format"""
        pattern = r'^[\+]?[1-9][\d]{3,14}$'
        return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None
    
    def check_conversation_ending(self, user_input):
        """Check if user wants to end conversation"""
        ending_keywords = ['goodbye', 'bye', 'exit', 'quit', 'thank you', 'thanks', 'done', 'finish']
        return any(keyword in user_input.lower() for keyword in ending_keywords)
    
    def process_user_input(self, user_input):
        """Process user input based on conversation stage with enhanced analysis"""
        if self.check_conversation_ending(user_input):
            st.session_state.conversation_ended = True
            return self.end_conversation()
        
        # Detect language
        detected_lang = self.language_detector.detect_language(user_input)
        if detected_lang in self.language_detector.SUPPORTED_LANGUAGES:
            st.session_state.user_language = detected_lang
        
        # Enhanced sentiment and emotion analysis
        sentiment_analysis = self.sentiment_analyzer.analyze_sentiment(user_input)
        emotions = self.sentiment_analyzer.detect_emotion(user_input)
        quality_analysis = self.sentiment_analyzer.analyze_response_quality(user_input)
        
        # Store analysis for later use
        st.session_state.last_analysis = {
            'sentiment': sentiment_analysis,
            'emotions': emotions,
            'quality': quality_analysis
        }
        
        stage = st.session_state.conversation_stage
        
        if stage == 'greeting':
            return self.handle_greeting(user_input)
        elif stage == 'collecting_name':
            return self.collect_name(user_input)
        elif stage == 'collecting_email':
            return self.collect_email(user_input)
        elif stage == 'collecting_phone':
            return self.collect_phone(user_input)
        elif stage == 'collecting_experience':
            return self.collect_experience(user_input)
        elif stage == 'collecting_position':
            return self.collect_position(user_input)
        elif stage == 'collecting_location':
            return self.collect_location(user_input)
        elif stage == 'collecting_tech_stack':
            return self.collect_tech_stack(user_input)
        elif stage == 'technical_questions':
            return self.handle_technical_questions(user_input, sentiment_analysis)
        else:
            return self.generate_fallback_response(user_input)
    
    def handle_greeting(self, user_input):
        """Handle initial greeting with enhanced multilingual support"""
        greeting = self.language_detector.get_translation('greeting', st.session_state.user_language)
        name_request = self.language_detector.get_translation('name_request', st.session_state.user_language)
        st.session_state.conversation_stage = 'collecting_name'
        
        return f"""{greeting}
        
I'm here to help you with your job application process. I'll gather some information about you and ask relevant technical questions based on your expertise.

Let's start! {name_request}"""
    
    def collect_name(self, user_input):
        """Collect candidate's name"""
        if len(user_input.strip()) < 2:
            return "Please provide your full name (at least 2 characters)."
        
        st.session_state.candidate_info['full_name'] = user_input.strip()
        st.session_state.conversation_stage = 'collecting_email'
        
        email_request = self.language_detector.get_translation('email_request', st.session_state.user_language)
        return f"Nice to meet you, {user_input.strip()}! 😊\n\n{email_request}"
    
    def collect_email(self, user_input):
        """Collect candidate's email with enhanced validation"""
        if not self.validate_email(user_input.strip()):
            return "Please provide a valid email address (e.g., john@example.com)."
        
        st.session_state.candidate_info['email'] = user_input.strip()
        st.session_state.conversation_stage = 'collecting_phone'
        
        return "Great! Now, could you please provide your phone number?"
    
    def collect_phone(self, user_input):
        """Collect candidate's phone"""
        if not self.validate_phone(user_input.strip()):
            return "Please provide a valid phone number (e.g., +1234567890 or 1234567890)."
        
        st.session_state.candidate_info['phone'] = user_input.strip()
        st.session_state.conversation_stage = 'collecting_experience'
        
        return "Perfect! How many years of professional experience do you have?"
    
    def collect_experience(self, user_input):
        """Collect candidate's experience"""
        try:
            experience = float(user_input.strip())
            if experience < 0 or experience > 50:
                return "Please provide a valid number of years (0-50)."
        except ValueError:
            return "Please provide your experience as a number (e.g., 3.5 for 3.5 years)."
        
        st.session_state.candidate_info['experience'] = experience
        st.session_state.conversation_stage = 'collecting_position'
        
        return "Excellent! What position(s) are you interested in? (e.g., Software Developer, Data Scientist, etc.)"
    
    def collect_position(self, user_input):
        """Collect desired position"""
        if len(user_input.strip()) < 3:
            return "Please provide the position you're interested in (at least 3 characters)."
        
        st.session_state.candidate_info['desired_position'] = user_input.strip()
        st.session_state.conversation_stage = 'collecting_location'
        
        return "Great choice! What's your current location? (City, State/Country)"
    
    def collect_location(self, user_input):
        """Collect candidate's location"""
        if len(user_input.strip()) < 2:
            return "Please provide your current location."
        
        st.session_state.candidate_info['location'] = user_input.strip()
        st.session_state.conversation_stage = 'collecting_tech_stack'
        
        return """Perfect! Now, let's talk about your technical skills. 

Please list your tech stack including:
- Programming languages (e.g., Python, JavaScript, Java)
- Frameworks (e.g., React, Django, Spring)
- Databases (e.g., PostgreSQL, MongoDB)
- Tools & Technologies (e.g., Docker, AWS, Git)

Separate each technology with commas."""
    
    def collect_tech_stack(self, user_input):
        """Collect and process tech stack"""
        if len(user_input.strip()) < 3:
            return "Please provide at least one technology from your tech stack."
        
        tech_stack = [tech.strip() for tech in user_input.split(',')]
        st.session_state.candidate_info['tech_stack'] = tech_stack
        
        # Generate technical questions
        questions = self.question_generator.get_questions_for_tech(tech_stack)
        st.session_state.tech_questions = questions
        st.session_state.current_question_index = 0
        st.session_state.conversation_stage = 'technical_questions'
        
        # Save candidate data
        candidate_id = self.data_handler.save_candidate_data(st.session_state.candidate_info.copy())
        
        return f"""Excellent! I can see you have experience with: {', '.join(tech_stack)} 💻

Now I'll ask you {len(questions)} technical questions to assess your skills. Don't worry, just answer to the best of your ability!

**Question 1/{len(questions)}:**
{questions[0]}"""
    
    def handle_technical_questions(self, user_input, sentiment_analysis):
        """Handle technical Q&A session with enhanced feedback"""
        quality_analysis = st.session_state.get('last_analysis', {}).get('quality', {})
        
        # Enhanced quality check
        if quality_analysis.get('quality') == 'needs_improvement':
            feedback_msg = "Please provide a more detailed answer. " + "; ".join(quality_analysis.get('feedback', []))
            return feedback_msg
        
        current_index = st.session_state.current_question_index
        questions = st.session_state.tech_questions
        
        # Store the answer with enhanced metadata
        if 'technical_answers' not in st.session_state.candidate_info:
            st.session_state.candidate_info['technical_answers'] = []
        
        answer_data = {
            'question': questions[current_index],
            'answer': user_input.strip(),
            'timestamp': datetime.now().isoformat(),
            'sentiment_analysis': sentiment_analysis,
            'quality_score': quality_analysis.get('score', 0),
            'word_count': quality_analysis.get('word_count', 0)
        }
        
        st.session_state.candidate_info['technical_answers'].append(answer_data)
        
        # Move to next question or end
        st.session_state.current_question_index += 1
        
        # Generate response with quality feedback
        sentiment_emoji = self.sentiment_analyzer.get_sentiment_emoji(sentiment_analysis.get('sentiment', 'neutral'))
        quality_emoji = '⭐' if quality_analysis.get('quality') == 'excellent' else '👍' if quality_analysis.get('quality') == 'good' else '👌'
        
        if st.session_state.current_question_index >= len(questions):
            return self.complete_technical_assessment()
        else:
            next_index = st.session_state.current_question_index
            quality_feedback = ""
            if quality_analysis.get('feedback'):
                quality_feedback = f"\n💡 {quality_analysis['feedback'][0]}"
            
            return f"""Thank you for your answer! {sentiment_emoji} {quality_emoji}
{quality_feedback}

**Question {next_index + 1}/{len(questions)}:**
{questions[next_index]}"""
    
    def complete_technical_assessment(self):
        """Complete the technical assessment"""
        st.session_state.conversation_stage = 'completed'
        
        return """🎉 Congratulations! You've completed the technical assessment!

Thank you for taking the time to answer all our questions. Here's what happens next:

✅ **Your Information Summary:**
- We have collected your contact details and professional information
- Your technical answers have been recorded for review
- Our recruitment team will evaluate your responses

📞 **Next Steps:**
1. Our technical team will review your answers within 2-3 business days
2. If there's a good match, you'll receive a call/email for the next round
3. We may schedule a detailed technical interview or coding challenge

Thank you for your interest in opportunities with TalentScout! We'll be in touch soon. 

Is there anything else you'd like to know about our process?"""
    
    def end_conversation(self):
        """End conversation gracefully with multilingual support"""
        thank_you = self.language_detector.get_translation('thank_you', st.session_state.user_language)
        
        return f"""{thank_you} 👋

We appreciate your time and interest. If you'd like to start a new session or have any questions, feel free to refresh the page.

Have a great day! 🌟"""
    
    def generate_fallback_response(self, user_input):
        """Generate fallback response for unexpected inputs"""
        fallback_responses = [
            "I understand you're trying to communicate with me, but I need to focus on gathering your information for the hiring process.",
            "Let's stay focused on the interview process. Could you please answer the current question?",
            "I'm here to help with your job application. Please provide the requested information.",
            "I want to make sure I collect all necessary details for your application. Let's continue with the current step."
        ]
        
        import random
        return random.choice(fallback_responses)

def create_advanced_analytics_dashboard():
    """Create comprehensive analytics dashboard with enhanced visualizations"""
    if 'candidates_data' not in st.session_state or not st.session_state.candidates_data:
        st.info("🔍 No candidate data available yet. Complete some assessments to see analytics!")
        
        # Show sample analytics for demonstration
        st.subheader("📊 Sample Analytics Preview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Candidates", "0", "+0")
        with col2:
            st.metric("Completion Rate", "0%", "+0%")
        with col3:
            st.metric("Avg. Experience", "0 years", "+0")
        with col4:
            st.metric("Active Sessions", "1", "+1")
        
        return
    
    st.subheader("📊 Advanced Recruitment Analytics Dashboard")
    
    # Calculate comprehensive metrics
    candidates = st.session_state.candidates_data
    analytics = st.session_state.conversation_analytics
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    total_candidates = len(candidates)
    completed = analytics.get('completed_assessments', 0)
    completion_rate = (completed / total_candidates * 100) if total_candidates > 0 else 0
    
    # Safely calculate average experience
    experience_values = [c.get('experience', 0) for c in candidates if c.get('experience') is not None and c.get('experience') != '']
    avg_experience = np.mean(experience_values) if experience_values else 0
    
    avg_duration = analytics.get('average_completion_time', 0)
    
    with col1:
        st.metric("Total Candidates", total_candidates, "+1" if total_candidates > 0 else "0")
    with col2:
        st.metric("Completion Rate", f"{completion_rate:.1f}%", f"+{completion_rate:.1f}%")
    with col3:
        st.metric("Avg. Experience", f"{avg_experience:.1f} years", "+0.5")
    with col4:
        st.metric("Avg. Duration", f"{avg_duration:.1f} min", "+2.3")
    
    # Create comprehensive DataFrame
    df_data = []
    for candidate in candidates:
        row = {
            'Experience': max(candidate.get('experience', 0), 0),  # Ensure non-negative
            'Position': candidate.get('desired_position', 'Unknown'),
            'Location': candidate.get('location', 'Unknown'),
            'Tech Stack Count': max(len(candidate.get('tech_stack', [])), 0),
            'Completion Status': max(candidate.get('completion_status', 0), 0),
            'Session Duration': max(candidate.get('session_duration', 0), 0),
            'Timestamp': candidate.get('timestamp', ''),
            'Tech Stack': ', '.join(candidate.get('tech_stack', [])),
            'ID': candidate.get('id', '')
        }
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Add safety check for empty dataframe
    if len(df) > 0 and not df.empty:
        # Create tabs for different analytics views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Overview", "👥 Demographics", "💻 Technical Skills", "⏱️ Performance", "📋 Detailed Data"
        ])
        
        with tab1:
            # Overview Analytics
            col1, col2 = st.columns(2)
            
            with col1:
                # Experience distribution with custom colors
                fig1 = px.histogram(df, x='Experience', nbins=15, 
                                  title='📊 Experience Distribution',
                                  color_discrete_sequence=['#667eea'])
                fig1.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig1, use_container_width=True)
                
                # Completion status
                completion_data = df['Completion Status'].value_counts()
                fig3 = px.bar(x=completion_data.index, y=completion_data.values,
                             title='📈 Completion Status Distribution',
                             color=completion_data.values,
                             color_continuous_scale='Viridis')
                fig3.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                # Position distribution with better styling
                position_counts = df['Position'].value_counts().head(8)
                fig2 = px.pie(values=position_counts.values, names=position_counts.index,
                             title='🎯 Desired Positions Distribution',
                             color_discrete_sequence=px.colors.qualitative.Set3)
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)
                
                # Tech stack complexity
                fig4 = px.histogram(df, x='Tech Stack Count', nbins=10,
                                  title='💻 Tech Stack Complexity',
                                  color_discrete_sequence=['#764ba2'])
                fig4.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig4, use_container_width=True)
        
        with tab2:
            # Demographics Analysis
            col1, col2 = st.columns(2)
            
            with col1:
                # Location analysis
                location_counts = df['Location'].value_counts().head(10)
                fig5 = px.bar(x=location_counts.values, y=location_counts.index,
                             title='🌍 Top Candidate Locations',
                             orientation='h',
                             color=location_counts.values,
                             color_continuous_scale='Blues')
                fig5.update_layout(height=500)
                st.plotly_chart(fig5, use_container_width=True)
            
            with col2:
                # Experience vs Position scatter plot
                fig6 = px.scatter(df, x='Experience', y='Position', 
                                size='Tech Stack Count',
                                title='👥 Experience vs Position Analysis',
                                color='Position',
                                hover_data=['Location'])
                fig6.update_layout(height=500)
                st.plotly_chart(fig6, use_container_width=True)
        
        with tab3:
            # Technical Skills Analysis
            # Extract all technologies
            all_tech = []
            for candidate in candidates:
                tech_stack = candidate.get('tech_stack', [])
                all_tech.extend(tech_stack)
            
            if all_tech:
                tech_counts = pd.Series(all_tech).value_counts().head(15)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Most popular technologies
                    fig7 = px.bar(x=tech_counts.values, y=tech_counts.index,
                                 title='🔥 Most Popular Technologies',
                                 orientation='h',
                                 color=tech_counts.values,
                                 color_continuous_scale='Plasma')
                    fig7.update_layout(height=600)
                    st.plotly_chart(fig7, use_container_width=True)
                
                with col2:
                    # Technology categories (simplified)
                    categories = {
                        'Languages': ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust'],
                        'Frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring'],
                        'Databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis'],
                        'Cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes']
                    }
                    
                    category_counts = {}
                    for category, techs in categories.items():
                        count = sum(1 for tech in all_tech if tech.lower() in techs)
                        category_counts[category] = count
                    
                    fig8 = px.pie(values=list(category_counts.values()), 
                                 names=list(category_counts.keys()),
                                 title='📈 Technology Categories',
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig8.update_layout(height=400)
                    st.plotly_chart(fig8, use_container_width=True)
                    
                    # Tech stack size distribution
                    stack_size_dist = df['Tech Stack Count'].value_counts().sort_index()
                    fig9 = px.line(x=stack_size_dist.index, y=stack_size_dist.values,
                                  title='📊 Tech Stack Size Trend',
                                  markers=True)
                    fig9.update_layout(height=300)
                    st.plotly_chart(fig9, use_container_width=True)
        
        with tab4:
            # Performance Analytics
            col1, col2 = st.columns(2)
            
            with col1:
                # Session duration analysis
                if 'Session Duration' in df.columns and df['Session Duration'].sum() > 0:
                    fig10 = px.histogram(df, x='Session Duration', nbins=15,
                                       title='⏱️ Session Duration Distribution',
                                       color_discrete_sequence=['#f093fb'])
                    fig10.update_layout(height=400)
                    st.plotly_chart(fig10, use_container_width=True)
                else:
                    st.info("Session duration data not available")
                
                # Completion rate by position
                completion_by_position = df.groupby('Position')['Completion Status'].mean().sort_values(ascending=False)
                fig12 = px.bar(x=completion_by_position.values, y=completion_by_position.index,
                             title='📈 Completion Rate by Position',
                             orientation='h',
                             color=completion_by_position.values,
                             color_continuous_scale='Greens')
                fig12.update_layout(height=400)
                st.plotly_chart(fig12, use_container_width=True)
            
            with col2:
                # Time series of applications
                df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
                daily_apps = df.groupby('Date').size().reset_index(name='Applications')
                
                fig11 = px.line(daily_apps, x='Date', y='Applications',
                               title='📅 Applications Over Time',
                               markers=True)
                fig11.update_layout(height=400)
                st.plotly_chart(fig11, use_container_width=True)
                
                # Experience vs Tech Stack correlation
                correlation = df['Experience'].corr(df['Tech Stack Count'])
                st.metric("Experience-Tech Stack Correlation", f"{correlation:.3f}")
                
                # Performance summary
                st.subheader("📊 Performance Summary")
                performance_metrics = {
                    "Average Session Duration": f"{df['Session Duration'].mean():.1f} minutes",
                    "Quickest Completion": f"{df['Session Duration'].min():.1f} minutes",
                    "Most Popular Position": df['Position'].mode().iloc[0] if not df['Position'].mode().empty else "N/A",
                    "Average Tech Stack Size": f"{df['Tech Stack Count'].mean():.1f} technologies"
                }
                
                for metric, value in performance_metrics.items():
                    st.write(f"**{metric}:** {value}")
        
        with tab5:
            # Detailed Data View
            st.subheader("📋 Detailed Candidate Data")
            
            # Search and filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_term = st.text_input("🔍 Search candidates", "")
            with col2:
                position_filter = st.selectbox("Filter by Position", 
                                             ['All'] + list(df['Position'].unique()))
            with col3:
                # Safe slider implementation with validation
                min_exp = float(df['Experience'].min())
                max_exp = float(df['Experience'].max())
                
                # Ensure min and max are different for slider
                if min_exp == max_exp:
                    if min_exp == 0:
                        max_exp = 10  # Default range if all are 0
                        experience_range = st.slider("Experience Range", 
                                                   0.0, 
                                                   10.0,
                                                   (0.0, 10.0))
                    else:
                        # If all candidates have same non-zero experience
                        range_extension = max(1.0, min_exp * 0.1)  # 10% extension or minimum 1
                        exp_min = max(0.0, min_exp - range_extension)
                        exp_max = min_exp + range_extension
                        experience_range = st.slider("Experience Range", 
                                                   exp_min, 
                                                   exp_max,
                                                   (exp_min, exp_max))
                else:
                    # Normal case with different min/max values
                    experience_range = st.slider("Experience Range", 
                                               min_exp, 
                                               max_exp,
                                               (min_exp, max_exp))
            
            # Apply filters with safety checks
            filtered_df = df.copy()
            
            if search_term and len(search_term.strip()) > 0:
                try:
                    filtered_df = filtered_df[
                        filtered_df['Position'].str.contains(search_term, case=False, na=False) |
                        filtered_df['Location'].str.contains(search_term, case=False, na=False) |
                        filtered_df['Tech Stack'].str.contains(search_term, case=False, na=False)
                    ]
                except Exception:
                    st.warning("Search term caused an error. Showing all data.")
            
            if position_filter != 'All':
                filtered_df = filtered_df[filtered_df['Position'] == position_filter]
            
            # Apply experience range filter with safety checks
            try:
                filtered_df = filtered_df[
                    (filtered_df['Experience'] >= experience_range[0]) & 
                    (filtered_df['Experience'] <= experience_range[1])
                ]
            except Exception:
                st.warning("Experience filter caused an error. Showing all data.")
            
            # Display filtered data
            st.dataframe(
                filtered_df[['Position', 'Experience', 'Location', 'Tech Stack', 'Completion Status', 'Session Duration']],
                use_container_width=True
            )
            
            # Export options
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 Export to CSV"):
                    csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"talentscout_candidates_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📈 Generate Report"):
                    st.success("Report generation feature coming soon!")
            
            with col3:
                if st.button("🔄 Refresh Data"):
                    st.rerun()

def create_enhanced_ui():
    """Create enhanced UI with better styling and animations"""
    # Custom CSS for enhanced UI
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cg fill-opacity='0.1'%3E%3Cpolygon fill='%23ffffff' points='50 0 60 40 100 50 60 60 50 100 40 60 0 50 40 40'/%3E%3C/g%3E%3C/svg%3E") repeat;
        opacity: 0.1;
    }
    
    .main-header h1, .main-header p {
        position: relative;
        z-index: 1;
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s ease-in-out;
        color: #1a1a1a !important;
        font-weight: 500;
    }
    
    .chat-message:hover {
        transform: translateY(-2px);
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 5px solid #2196f3;
        margin-left: 20%;
        color: #0d47a1 !important;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left: 5px solid #9c27b0;
        margin-right: 20%;
        color: #4a148c !important;
    }
    
    .success-box {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        border: 2px solid #4caf50;
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.2);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .sidebar-info {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
        color: #e65100 !important;
        font-weight: 600;
    }
    
    .progress-container {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #2c2c2c !important;
        font-weight: 500;
        border: 2px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Enhanced progress bar styling */
    .progress-container .stProgress > div {
        background-color: #e8e8e8 !important;
        border-radius: 10px !important;
        height: 1rem !important;
        overflow: hidden !important;
    }
    
    .progress-container .stProgress > div > div {
        background: linear-gradient(90deg, #4caf50 0%, #45a049 100%) !important;
        border-radius: 10px !important;
        height: 100% !important;
        transition: all 0.3s ease !important;
    }
    
    /* Fix for Streamlit progress bar classes */
    .progress-container [data-testid="stProgress"] > div {
        background-color: #e8e8e8 !important;
        border-radius: 10px !important;
        height: 1rem !important;
    }
    
    .progress-container [data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, #4caf50 0%, #45a049 100%) !important;
        border-radius: 10px !important;
        height: 100% !important;
    }
    
    .tech-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    /* Enhanced text visibility for all containers */
    .chat-message *, .sidebar-info *, .progress-container * {
        color: inherit !important;
    }
    
    .chat-message p, .chat-message span, .chat-message div {
        color: inherit !important;
        text-shadow: none !important;
    }
    
    .sidebar-info p, .sidebar-info span, .sidebar-info div {
        color: inherit !important;
        text-shadow: none !important;
    }
    
    /* Fix for any white background issues in progress container */
    .progress-container * {
        background: transparent !important;
    }
    
    .progress-container [data-testid="stProgress"] {
        background: transparent !important;
    }
    
    /* Ensure progress text is visible */
    .progress-container div[style*="text-align: center"] {
        color: #1a1a1a !important;
        font-weight: 600 !important;
        background: transparent !important;
    }
    
    .status-active { background-color: #4caf50; }
    .status-pending { background-color: #ff9800; }
    .status-completed { background-color: #2196f3; }
    
    .floating-action {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }
    
    .footer-gradient {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 3rem;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .chat-message {
            margin-left: 0;
            margin-right: 0;
        }
        
        .user-message, .bot-message {
            margin-left: 0;
            margin-right: 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Enhanced Streamlit application with advanced features"""
    # Page configuration
    st.set_page_config(
        page_title="TalentScout Hiring Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://talentscout.ai/help',
            'Report a bug': "https://talentscout.ai/bug-report",
            'About': "# TalentScout Hiring Assistant\nIntelligent recruitment powered by AI"
        }
    )
    
    # Initialize session start time
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    
    # Enhanced UI styling
    create_enhanced_ui()
    
    # Header with enhanced design
    st.markdown("""
    <div class="main-header fade-in">
        <h1 style="color: white; text-align: center; margin: 0; font-size: 3rem; font-weight: 700;">
            🤖 TalentScout Hiring Assistant
        </h1>
        <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 1rem 0 0 0; font-size: 1.2rem;">
            Intelligent Recruitment Assistant for Technology Professionals
        </p>
        <div style="text-align: center; margin-top: 1rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem;">
                ✨ Powered by Google Gemini AI | 🔒 Secure & Private | 🌍 Multilingual Support
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize hiring assistant
    assistant = HiringAssistant()
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.header("🔧 Controls & Settings")
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 New Chat", use_container_width=True):
                for key in ['conversation_stage', 'candidate_info', 'chat_history', 
                           'tech_questions', 'current_question_index', 'conversation_ended']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        with col2:
            if st.button("💾 Save Session", use_container_width=True):
                st.success("Session saved!")
        
        # Language selection with enhanced UI
        st.subheader("🌐 Language Settings")
        language_options = {}
        for code, info in assistant.language_detector.SUPPORTED_LANGUAGES.items():
            language_options[code] = f"{info['flag']} {info['name']}"
        
        selected_lang = st.selectbox(
            "Select Language", 
            options=list(language_options.keys()),
            format_func=lambda x: language_options[x],
            index=0
        )
        st.session_state.user_language = selected_lang
        
        # Current status with enhanced design
        st.subheader("📊 Session Status")
        stage_descriptions = {
            'greeting': {'name': 'Initial Greeting', 'icon': '👋', 'color': '#ff9800'},
            'collecting_name': {'name': 'Collecting Name', 'icon': '👤', 'color': '#2196f3'},
            'collecting_email': {'name': 'Collecting Email', 'icon': '📧', 'color': '#4caf50'},
            'collecting_phone': {'name': 'Collecting Phone', 'icon': '📱', 'color': '#9c27b0'},
            'collecting_experience': {'name': 'Collecting Experience', 'icon': '⭐', 'color': '#ff5722'},
            'collecting_position': {'name': 'Collecting Position', 'icon': '💼', 'color': '#795548'},
            'collecting_location': {'name': 'Collecting Location', 'icon': '📍', 'color': '#607d8b'},
            'collecting_tech_stack': {'name': 'Collecting Tech Stack', 'icon': '💻', 'color': '#e91e63'},
            'technical_questions': {'name': 'Technical Assessment', 'icon': '🧠', 'color': '#3f51b5'},
            'completed': {'name': 'Assessment Complete', 'icon': '✅', 'color': '#4caf50'}
        }
        
        current_stage = st.session_state.get('conversation_stage', 'greeting')
        stage_info = stage_descriptions.get(current_stage, stage_descriptions['greeting'])
        
        st.markdown(f"""
        <div class="sidebar-info">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{stage_info['icon']}</span>
                <span style="font-weight: 600; color: #d84315;">{stage_info['name']}</span>
            </div>
            <div style="text-align: center;">
                <span class="status-indicator" style="background-color: {stage_info['color']};"></span>
                <span style="font-size: 0.9rem; color: #bf360c; font-weight: 600;">Stage {list(stage_descriptions.keys()).index(current_stage) + 1} of {len(stage_descriptions)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced progress bar
        stages = list(stage_descriptions.keys())
        if current_stage in stages:
            # Calculate progress based on current stage
            completion_map = {
                'greeting': 0,
                'collecting_name': 10,
                'collecting_email': 20,
                'collecting_phone': 30,
                'collecting_experience': 40,
                'collecting_position': 50,
                'collecting_location': 60,
                'collecting_tech_stack': 70,
                'technical_questions': 80,
                'completed': 100
            }
            progress_percentage = completion_map.get(current_stage, 0)
            if progress_percentage > 0:  # Only show progress bar if there's actual progress
                progress = progress_percentage / 100
                st.markdown('<div class="progress-container">', unsafe_allow_html=True)
                st.progress(progress)
                st.markdown(f'<div style="text-align: center; color: #1a1a1a; font-size: 0.9rem; font-weight: 600; margin-top: 0.5rem;">Progress: {progress_percentage:.0f}%</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Candidate info summary with enhanced styling
        if st.session_state.get('candidate_info'):
            st.subheader("👤 Candidate Summary")
            info = st.session_state.candidate_info
            
            summary_data = []
            if 'full_name_original' in info:
                summary_data.append(('Name', info['full_name_original']))
            elif 'full_name' in info:
                summary_data.append(('Name', info['full_name']))
            
            if 'experience' in info:
                summary_data.append(('Experience', f"{info['experience']} years"))
            
            if 'desired_position' in info:
                summary_data.append(('Position', info['desired_position']))
            
            if 'tech_stack' in info and info['tech_stack']:
                tech_display = ''.join([f'<span class="tech-badge">{tech}</span>' for tech in info['tech_stack'][:5]])
                if len(info['tech_stack']) > 5:
                    tech_display += f'<span class="tech-badge">+{len(info["tech_stack"])-5} more</span>'
                summary_data.append(('Tech Stack', tech_display))
            
            for label, value in summary_data:
                if label == 'Tech Stack':
                    st.markdown(f"**{label}:** {value}", unsafe_allow_html=True)
                else:
                    st.text(f"{label}: {value}")
        
        # Session analytics
        st.subheader("📈 Session Analytics")
        session_duration = (datetime.now() - st.session_state.session_start_time).total_seconds() / 60
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Duration", f"{session_duration:.1f}m")
        with col2:
            st.metric("Messages", len(st.session_state.get('chat_history', [])))
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main chat interface with enhanced styling
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.subheader("💬 Interactive Chat Interface")
    
    # Chat container with better scrolling
    chat_container = st.container()
    
    with chat_container:
        # Display chat history with enhanced styling
        if st.session_state.get('chat_history'):
            for i, message in enumerate(st.session_state.chat_history):
                if message['role'] == 'user':
                    # Analyze sentiment for user messages
                    sentiment_analysis = assistant.sentiment_analyzer.analyze_sentiment(message['content'])
                    sentiment_emoji = assistant.sentiment_analyzer.get_sentiment_emoji(sentiment_analysis['sentiment'])
                    
                    st.markdown(f"""
                    <div class="chat-message user-message fade-in">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong>You:</strong>
                            <span style="font-size: 0.8rem; color: #666;">
                                {sentiment_emoji} {sentiment_analysis['sentiment'].replace('_', ' ').title()}
                            </span>
                        </div>
                        <div>{message['content']}</div>
                        <div style="text-align: right; font-size: 0.7rem; color: #999; margin-top: 0.5rem;">
                            {datetime.fromisoformat(message['timestamp']).strftime('%H:%M:%S')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message bot-message fade-in">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong>🤖 TalentScout Assistant:</strong>
                            <span style="font-size: 0.8rem; color: #666;">
                                AI Response
                            </span>
                        </div>
                        <div>{message['content']}</div>
                        <div style="text-align: right; font-size: 0.7rem; color: #999; margin-top: 0.5rem;">
                            {datetime.fromisoformat(message['timestamp']).strftime('%H:%M:%S')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Check if conversation ended
    if st.session_state.get('conversation_ended', False):
        st.markdown("""
        <div class="success-box fade-in">
            <div style="text-align: center;">
                <h2>🎉 Assessment Completed Successfully!</h2>
                <p style="font-size: 1.1rem; margin: 1rem 0;">
                    Thank you for using TalentScout's Hiring Assistant! Your information has been securely recorded.
                </p>
                <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 2rem;">
                    <div style="background: rgba(76, 175, 80, 0.1); padding: 1rem; border-radius: 10px;">
                        <strong>✅ Information Collected</strong><br>
                        <span style="color: #666;">Your profile is complete</span>
                    </div>
                    <div style="background: rgba(33, 150, 243, 0.1); padding: 1rem; border-radius: 10px;">
                        <strong>🧠 Technical Assessment</strong><br>
                        <span style="color: #666;">Questions answered</span>
                    </div>
                    <div style="background: rgba(156, 39, 176, 0.1); padding: 1rem; border-radius: 10px;">
                        <strong>📞 Next Steps</strong><br>
                        <span style="color: #666;">We'll contact you soon</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced analytics for admins
        if st.checkbox("🔐 Show Advanced Analytics Dashboard (Admin)", key="admin_analytics"):
            create_advanced_analytics_dashboard()
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # User input with enhanced styling
    user_input = st.chat_input("💭 Type your message here...", key="user_input")
    
    if user_input:
        # Add typing indicator effect
        with st.spinner('🤖 TalentScout Assistant is thinking...'):
            time.sleep(0.5)  # Brief pause for better UX
            
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Process input and get response
            bot_response = assistant.process_user_input(user_input)
            
            # Add bot response to history
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': bot_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Rerun to update display
            st.rerun()
    
    # Initial greeting if no chat history
    if not st.session_state.get('chat_history') and not st.session_state.get('conversation_ended', False):
        greeting = assistant.language_detector.get_translation('greeting', st.session_state.user_language)
        welcome_message = f"""{greeting}

I'm your AI-powered hiring assistant, designed to streamline your application process with TalentScout. Here's what I'll help you with:

🔹 **Personal Information**: Collect your basic details and contact information
🔹 **Professional Background**: Learn about your experience and career goals  
🔹 **Technical Skills**: Understand your technology stack and expertise
🔹 **Skill Assessment**: Ask relevant technical questions based on your background
🔹 **Next Steps**: Guide you through the recruitment process

**Ready to begin your journey with TalentScout?** 🚀

Simply type "Hello", "Hi", or "Start" to begin the conversation!"""
        
        st.markdown(f"""
        <div class="chat-message bot-message fade-in pulse-animation">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong>🤖 TalentScout Assistant:</strong>
                <span style="font-size: 0.8rem; color: #666;">
                    Welcome Message
                </span>
            </div>
            <div>{welcome_message}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced footer
    st.markdown("""
    <div class="footer-gradient fade-in">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h4 style="margin: 0; color: white;">🔒 Your Privacy Matters</h4>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                    All data encrypted | GDPR Compliant | Secure Processing
                </p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 1.1rem; font-weight: 600;">
                    TalentScout Hiring Assistant v2.0
                </p>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                    Built with ❤️ using Streamlit & Google Gemini AI
                </p>
            </div>
        </div>
        <div style="text-align: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <p style="margin: 0; opacity: 0.8;">
                🌟 Empowering recruitment through intelligent automation | 
                📧 support@talentscout.ai | 
                🌐 www.talentscout.ai
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
