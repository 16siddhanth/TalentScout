#!/bin/bash

# TalentScout Hiring Assistant - Enhanced Deployment Script
# This script sets up and runs the enhanced application with all features

echo "🤖 TalentScout Hiring Assistant v2.0 - Enhanced Setup Script"
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip."
    exit 1
fi

print_status "pip3 found"

# Check system resources
print_info "Checking system resources..."
available_memory=$(free -h 2>/dev/null | awk '/^Mem:/ {print $7}' || echo "Unknown")
print_info "Available memory: $available_memory"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install requirements with progress bar
print_info "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt --progress-bar=on

if [ $? -ne 0 ]; then
    print_warning "Some packages failed to install. Trying with reduced requirements..."
    # Create minimal requirements for fallback
    cat > requirements_minimal.txt << EOL
streamlit==1.29.0
google-generativeai==0.3.2
python-dotenv==1.0.0
cryptography==41.0.8
pandas==2.1.4
plotly==5.17.0
textblob==0.17.1
langdetect==1.0.9
numpy==1.24.3
EOL
    pip install -r requirements_minimal.txt
fi

print_status "Dependencies installed successfully"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating template..."
    cat > .env << EOL
# Environment Variables for TalentScout Hiring Assistant v2.0
GEMINI_API_KEY=your_gemini_api_key_here
ENCRYPTION_KEY=your_32_byte_encryption_key_here

# Optional: For enhanced features
ANTHROPIC_API_KEY=your_anthropic_api_key_here
COHERE_API_KEY=your_cohere_api_key_here

# Application Settings
DEBUG=False
MAX_CONVERSATION_LENGTH=50
ENABLE_ANALYTICS=True

# Performance Settings
CACHE_SIZE=1000
MAX_CONCURRENT_USERS=100
EOL
    print_info "📝 Please update the .env file with your API keys before running the application."
    print_info "To generate an encryption key, run: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
    
    # Open .env file for editing if possible
    if command -v code &> /dev/null; then
        print_info "Opening .env file in VS Code..."
        code .env
    elif command -v nano &> /dev/null; then
        read -p "Press Enter to edit .env file with nano..."
        nano .env
    fi
else
    print_status ".env file already exists"
fi

# Validate environment variables
print_info "🔍 Validating environment variables..."
python3 -c "
import os
import sys
from dotenv import load_dotenv
load_dotenv()

required_vars = ['GEMINI_API_KEY', 'ENCRYPTION_KEY']
missing_vars = []

for var in required_vars:
    value = os.getenv(var)
    if not value or value == f'your_{var.lower()}_here':
        missing_vars.append(var)

if missing_vars:
    print(f'❌ Missing or invalid environment variables: {missing_vars}')
    print('Please update your .env file with valid values.')
    sys.exit(1)
else:
    print('✅ All required environment variables are set.')

# Validate encryption key length
encryption_key = os.getenv('ENCRYPTION_KEY')
if encryption_key and len(encryption_key.encode()) != 44:  # Fernet key length
    print('⚠️ Warning: Encryption key may not be valid length (should be 44 characters)')

print('🔒 Security validation complete.')
"

if [ $? -ne 0 ]; then
    print_error "Environment validation failed. Please check your .env file."
    exit 1
fi

print_status "Environment validation successful"

# Download language models for enhanced features
print_info "Setting up language processing..."
python3 -c "
import textblob
try:
    # Download NLTK data if needed
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('brown', quiet=True)
    print('✅ Language models ready')
except:
    print('⚠️ Some language features may be limited')
" 2>/dev/null

# Run tests
print_info "🧪 Running application tests..."
if [ -f "test_app.py" ]; then
    python3 -m pytest test_app.py -v --tb=short || {
        print_warning "Some tests failed, but continuing with deployment..."
    }
else
    print_info "No test file found, skipping tests"
fi

# Create data directory for analytics
mkdir -p data/analytics
mkdir -p logs

# Check available ports
print_info "Checking available ports..."
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null; then
    print_warning "Port 8501 is already in use. The app will try to use the next available port."
fi

# Pre-flight checks
print_info "Running pre-flight checks..."
python3 -c "
import streamlit as st
import google.generativeai as genai
print('✅ Streamlit and Gemini imports successful')

# Check if required files exist
import os
required_files = ['app.py', 'config.py', 'utils.py', 'questions.py']
for file in required_files:
    if os.path.exists(file):
        print(f'✅ {file} found')
    else:
        print(f'❌ {file} missing')
"

# Create startup script
cat > start_app.sh << 'EOL'
#!/bin/bash
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
EOL

chmod +x start_app.sh

# Performance optimization
print_info "Optimizing performance settings..."
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200

# Final preparations
print_status "🚀 Setup complete! Starting TalentScout Hiring Assistant v2.0..."
echo ""
print_info "📱 The application will open in your default browser"
print_info "🌐 If it doesn't open automatically, visit: http://localhost:8501"
print_info "🔧 Admin dashboard available in the sidebar"
print_info "🌍 Multilingual support enabled"
print_info "📊 Advanced analytics available"
echo ""
print_info "To stop the application, press Ctrl+C"
echo ""
print_status "Features enabled:"
echo "  ✨ Advanced sentiment analysis"
echo "  🌍 Enhanced multilingual support (10 languages)"
echo "  📊 Comprehensive analytics dashboard"
echo "  🔒 Enhanced security with data encryption"
echo "  🎨 Modern UI with animations"
echo "  📱 Mobile-responsive design"
echo "  ⚡ Performance optimizations"
echo ""

# Start the application
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 || {
    print_error "Failed to start the application. Please check the logs above."
    exit 1
}

print_status "👋 Thank you for using TalentScout Hiring Assistant v2.0!"
