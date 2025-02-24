from flask import Flask, request, jsonify
import util
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

class ChatPDFHandler:
    def __init__(self):
        self.api_key = os.getenv('CHATPDF_API_KEY')
        if not self.api_key:
            raise ValueError("CHATPDF_API_KEY not found in environment variables")
        self.base_url = 'https://api.chatpdf.com/v1'
        self.source_id = None

    def upload_pdf(self, file_path):
        """Upload a PDF file to ChatPDF API"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at: {file_path}")

        headers = {
            'x-api-key': self.api_key
        }

        with open(file_path, 'rb') as file:
            files = {
                'file': file
            }
            try:
                response = requests.post(
                    f'{self.base_url}/sources/add-file',
                    headers=headers,
                    files=files
                )
                response.raise_for_status()  # Raise exception for bad status codes
                self.source_id = response.json().get('sourceId')
                return self.source_id
            except requests.exceptions.RequestException as e:
                logger.error(f"Error uploading PDF to ChatPDF API: {str(e)}")
                if response.text:
                    logger.error(f"API Response: {response.text}")
                raise

    def chat(self, message):
        """Send a message to ChatPDF API and get response"""
        if not self.source_id:
            # If no PDF is loaded, provide a default response
            return "I apologize, but I'm currently unable to access the real estate guide. I can still help with general questions about the website and price predictions."

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        data = {
            'sourceId': self.source_id,
            'messages': [
                {
                    'role': 'user',
                    'content': message
                }
            ]
        }

        try:
            response = requests.post(
                f'{self.base_url}/chats/message',
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json().get('content')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting chat response: {str(e)}")
            if response.text:
                logger.error(f"API Response: {response.text}")
            return "I apologize, but I encountered an error processing your request. Please try again."

# Initialize ChatPDF handler
try:
    chatpdf_handler = ChatPDFHandler()
except Exception as e:
    logger.error(f"Error initializing ChatPDFHandler: {str(e)}")
    chatpdf_handler = None

def initialize_chatbot():
    """Initialize chatbot with the pre-loaded PDF"""
    if not chatpdf_handler:
        logger.error("ChatPDFHandler not initialized")
        return False

    try:
        # Construct absolute path to PDF
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_dir, 'real_estate_guide.pdf')
        
        logger.info(f"Attempting to load PDF from: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found at: {pdf_path}")
            return False

        source_id = chatpdf_handler.upload_pdf(pdf_path)
        logger.info("Chatbot initialized successfully with the real estate guide")
        return True
    except Exception as e:
        logger.error(f"Error initializing chatbot: {str(e)}")
        return False

# Your existing routes...
@app.route('/')
def home():
    return "Home Price Prediction Server is Running!"

@app.route('/get_location_names', methods=['GET'])
def get_location_names():
    try:
        locations = util.get_location_names()
        return jsonify({
            'success': True,
            'locations': locations
        })
    except Exception as e:
        logger.error(f"Error getting location names: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/predict_home_price', methods=['POST'])
def predict_home_price():
    try:
        if request.method == 'POST':
            total_sqft = float(request.form['total_sqft'])
            location = request.form['location']
            bhk = int(request.form['bhk'])
            bath = int(request.form['bath'])

            estimated_price = util.get_estimated_price(location, total_sqft, bhk, bath)
            
            return jsonify({
                'success': True,
                'estimated_price': estimated_price
            })
    except Exception as e:
        logger.error(f"Error predicting home price: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'success': False, 'error': 'No message provided'})
        
        if not chatpdf_handler:
            return jsonify({
                'success': True,
                'response': "I apologize, but the chatbot service is currently unavailable. Please try again later."
            })
        
        response = chatpdf_handler.chat(message)
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == "__main__":
    print("Starting Python Flask Server For Home Price Prediction...")
    try:
        # Load price prediction artifacts
        util.load_saved_artifacts()
        
        # Initialize chatbot with PDF
        initialized = initialize_chatbot()
        if not initialized:
            logger.warning("Chatbot initialization failed - continuing without chatbot functionality")
            
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Error during server startup: {str(e)}")