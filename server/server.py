from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
import util  # Ensure util is used in the code, otherwise remove it

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

class ChatPDFHandler:
    def __init__(self):
        self.api_key = os.getenv('CHATPDF_API_KEY')  # Make sure this environment variable is set
        self.base_url = 'https://api.chatpdf.com/v1'
        self.source_id = None

    def upload_pdf(self, file_path):
        """Upload a PDF file to ChatPDF API"""
        headers = {
            'x-api-key': self.api_key
        }

        with open(file_path, 'rb') as file:
            files = {
                'file': file
            }
            response = requests.post(
                f'{self.base_url}/sources/add-file',
                headers=headers,
                files=files
            )

            if response.status_code == 200:
                self.source_id = response.json().get('sourceId')
                return self.source_id
            else:
                raise Exception(f"Error uploading PDF: {response.text}")

    def chat(self, message):
        """Send a message to ChatPDF API and get response"""
        if not self.source_id:
            raise Exception("No PDF source uploaded yet")

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

        response = requests.post(
            f'{self.base_url}/chats/message',
            headers=headers,
            json=data
        )

        if response.status_code == 200:
            return response.json().get('content')
        else:
            raise Exception(f"Error getting chat response: {response.text}")

# Initialize ChatPDF handler
chatpdf_handler = ChatPDFHandler()

def initialize_chatbot():
    """Initialize chatbot with the pre-loaded PDF"""
    try:
        pdf_path = os.path.join(os.path.dirname(__file__), 'real_estate_guide.pdf')
        source_id = chatpdf_handler.upload_pdf(pdf_path)
        print("Chatbot initialized successfully with the real estate guide")
        return True
    except Exception as e:
        print(f"Error initializing chatbot: {str(e)}")
        return False

@app.route('/')
def home():
    return "Home Price Prediction Server is Running!"

@app.route('/get_location_names', methods=['GET'])
def get_location_names():
    try:
        locations = util.get_location_names()  # Ensure util is being used
        return jsonify({
            'success': True,
            'locations': locations
        })
    except Exception as e:
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

            estimated_price = util.get_estimated_price(location, total_sqft, bhk, bath)  # Ensure util is being used
            
            return jsonify({
                'success': True,
                'estimated_price': estimated_price
            })
    except Exception as e:
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
        
        response = chatpdf_handler.chat(message)
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    print("Starting Python Flask Server For Home Price Prediction...")
    try:
        # Load price prediction artifacts
        util.load_saved_artifacts()  # Ensure util is being used

        # Initialize chatbot with PDF
        initialized = initialize_chatbot()
        if not initialized:
            print("Warning: Chatbot initialization failed")
            
        app.run(debug=True)
    except Exception as e:
        print(f"Error during server startup: {str(e)}")
