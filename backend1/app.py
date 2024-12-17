import os
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import DistilBertTokenizer, DistilBertForQuestionAnswering
from PyPDF2 import PdfReader
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load pre-trained DistilBERT model for question answering
try:
    model_name = 'distilbert-base-uncased-distilled-squad'
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertForQuestionAnswering.from_pretrained(model_name)
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None
    tokenizer = None

def extract_text_from_file(file):
    """
    Extract text from different file types
    """
    try:
        # PDF handling
        if file.filename.lower().endswith('.pdf'):
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        
        # Text file handling
        elif file.filename.lower().endswith('.txt'):
            return file.read().decode('utf-8')
        
        else:
            raise ValueError(f"Unsupported file type: {file.filename}")
    
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        raise

def answer_question(context, question):
    """
    Use DistilBERT to answer questions
    """
    if not model or not tokenizer:
        raise ValueError("Model not loaded properly")

    try:
        # Truncate context if it's too long
        max_context_length = 512 * 3  # Approximate token limit
        context = context[:max_context_length]

        inputs = tokenizer.encode_plus(
            question, context, 
            add_special_tokens=True, 
            return_tensors="pt", 
            max_length=512, 
            truncation=True
        )

        input_ids = inputs["input_ids"].tolist()[0]
        attention_mask = inputs["attention_mask"].tolist()[0]

        start_scores, end_scores = model(
            torch.tensor([input_ids]), 
            attention_mask=torch.tensor([attention_mask])
        )[:2]

        # Find the most likely answer span
        start_index = torch.argmax(start_scores)
        end_index = torch.argmax(end_scores)

        # Convert token ids back to text
        answer_tokens = input_ids[start_index:end_index+1]
        answer = tokenizer.decode(answer_tokens)

        return answer.strip() or "Could not find a specific answer in the text."
    
    except Exception as e:
        logger.error(f"Error in question answering: {e}")
        raise

@app.route('/upload', methods=['POST'])
def upload_file():
    logger.debug("Upload route hit")
    
    # Check if file is present in the request
    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    
    # Check if filename is empty
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Extract text from file
        context = extract_text_from_file(file)
        
        # Limit context length
        context = context[:10000]  # Limit to first 10000 characters
        
        return jsonify({"context": context})
    
    except ValueError as ve:
        logger.error(f"Value error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in file upload: {e}")
        return jsonify({"error": "File processing failed"}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.json
        context = data.get('context', '').strip()
        question = data.get('question', '').strip()

        if not context or not question:
            return jsonify({"error": "Context and question are required"}), 400
        
        answer = answer_question(context, question)
        return jsonify({"answer": answer})
    
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        return jsonify({"error": "Question answering failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)