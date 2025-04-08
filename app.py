import os
from flask import Flask, request, render_template, jsonify, url_for
<<<<<<< HEAD
import boto3
import json
import fitz
import logging
from google.generativeai import GenerativeModel

app = Flask(__name__)

# Initialize the boto3 client for Lambda
lambda_client = boto3.client('lambda', region_name='ap-south-1')
s3 = boto3.client('s3')

# Set the API key as an environment variable
os.environ["GOOGLE_API_KEY"] = "AIzaSyBnjqVHJ6QI62sicPiQyv2xk9rPv2uXstU"

local_directory = 'static/files'
os.makedirs(local_directory, exist_ok=True)

# Initialize the GenerativeModel (assuming it reads from the environment variable)
model = GenerativeModel("gemini-1.5-flash")  # Adjust this based on your actual API configuration

# Helper function to split the text for large documents
=======
from dotenv import load_dotenv
import boto3
import json
import fitz 
import logging
from google.generativeai import GenerativeModel

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Environment Variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Set the API key for Google Generative AI
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Initialize AWS clients
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
s3 = boto3.client('s3')

# Create local directory if it doesn't exist
local_directory = 'static/files'
os.makedirs(local_directory, exist_ok=True)

# Initialize Gemini Model
model = GenerativeModel("gemini-1.5-flash")

>>>>>>> ba23b4f (upload)
def split_text(text, max_length=500):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

@app.route('/')
def index():
    return render_template('login.html')

<<<<<<< HEAD
@app.route('/home',methods=['GET'])
=======
@app.route('/home', methods=['GET'])
>>>>>>> ba23b4f (upload)
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
<<<<<<< HEAD

    if file.filename == '':
        return 'No selected file', 400

    # Upload the file to S3
    bucket_name = 'data-bucket-private'
    s3_key = file.filename

=======
    if file.filename == '':
        return 'No selected file', 400

    s3_key = file.filename
>>>>>>> ba23b4f (upload)
    local_file_path = os.path.join(local_directory, s3_key)
    file.save(local_file_path)

    try:
        with open(local_file_path, 'rb') as f:
<<<<<<< HEAD
            s3.upload_fileobj(f, bucket_name, s3_key)
    except Exception as e:
        return f'Error uploading file to S3: {str(e)}', 500
    
    file_url = url_for('static', filename=f'files/{s3_key}')

    # Invoke the Lambda function based on file type
=======
            s3.upload_fileobj(f, BUCKET_NAME, s3_key)
    except Exception as e:
        return f'Error uploading file to S3: {str(e)}', 500

    file_url = url_for('static', filename=f'files/{s3_key}')

>>>>>>> ba23b4f (upload)
    try:
        if file.filename.endswith('.pdf'):
            file_type = 'pdf'
        elif file.filename.endswith('.csv'):
            file_type = 'csv'
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            file_type = 'excel'
        else:
            return 'Unsupported file type', 400
<<<<<<< HEAD
        
    
=======
>>>>>>> ba23b4f (upload)

        response = lambda_client.invoke(
            FunctionName='DocumentTextExtractor',
            InvocationType='RequestResponse',
<<<<<<< HEAD
            Payload=json.dumps({'bucket': bucket_name, 'key': s3_key, 'file_type': file_type})
        )

        # Read the response from Lambda
        payload = json.loads(response['Payload'].read())
        print("Lambda response:", payload)  # Debugging line
=======
            Payload=json.dumps({'bucket': BUCKET_NAME, 'key': s3_key, 'file_type': file_type})
        )

        payload = json.loads(response['Payload'].read())
>>>>>>> ba23b4f (upload)

        if response['StatusCode'] == 200:
            extracted_text = json.loads(payload.get('body', '{}')).get('text', '')
            if not extracted_text:
                return "No extracted text returned from Lambda.", 500
        else:
            return "Lambda function failed.", 500

    except Exception as e:
        return f'Error invoking Lambda function: {str(e)}', 500

<<<<<<< HEAD
    return render_template('result.html', text=extracted_text, bucket=bucket_name, key=s3_key, file_url=file_url)
=======
    return render_template('result.html', text=extracted_text, bucket=BUCKET_NAME, key=s3_key, file_url=file_url)
>>>>>>> ba23b4f (upload)

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    text = request.json.get('text')

<<<<<<< HEAD
    # Ensure that we provide the full text to Gemini
    chunks = split_text(text)
    full_text = " ".join(chunks)  # Combine all chunks into a single string

    # Create the input based on the expected format
    input_text = f"Answer the question: {question} \nContext: {full_text}"

    # Logging inputs for debugging
    logging.info(f"Question: {question}")
    logging.info(f"Full Text: {full_text}")
    logging.info(f"Input Text: {input_text}")

    try:
        # Generate response without using 'prompt=' if not required
        response = model.generate_content(input_text)
        answer = response.text.strip()  # Extract and clean the generated answer

        if not answer:
            logging.warning("Received empty response from model")
            return jsonify({'error': 'No answer generated'}), 400
        
        # Replace markdown syntax with HTML bold tags
=======
    chunks = split_text(text)
    full_text = " ".join(chunks)
    input_text = f"Answer the question: {question} \nContext: {full_text}"

    try:
        response = model.generate_content(input_text)
        answer = response.text.strip()

        if not answer:
            return jsonify({'error': 'No answer generated'}), 400

>>>>>>> ba23b4f (upload)
        answer = answer.replace("**", "<strong>")
        answer = answer.replace("*", "<strong>")

    except Exception as e:
<<<<<<< HEAD
        logging.error(f"Error: {str(e)}")
=======
>>>>>>> ba23b4f (upload)
        return jsonify({'error': str(e)}), 500

    return jsonify({'answer': answer})

<<<<<<< HEAD
# Route to submit comment and store it in comments.txt
@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    comment = request.json.get('comment')

=======
@app.route('/submit_comment', methods=['POST'])
def submit_comment():
    comment = request.json.get('comment')
>>>>>>> ba23b4f (upload)
    if not comment:
        return jsonify({'error': 'Comment cannot be empty'}), 400

    try:
<<<<<<< HEAD
        # Append the comment to the comments.txt file
        with open('comments.txt', 'a') as f:
            f.write(comment + "\n")

        # Process the comment using Gemini API for sentiment analysis
=======
        with open('comments.txt', 'a') as f:
            f.write(comment + "\n")

>>>>>>> ba23b4f (upload)
        sentiment = analyze_comment_sentiment(comment)

        return jsonify({'message': 'Comment submitted successfully', 'sentiment': sentiment}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

<<<<<<< HEAD
# Function to analyze sentiment using Gemini API
def analyze_comment_sentiment(comment):
    try:
        # Formulate the prompt to instruct Gemini to respond only with "Good" or "Bad"
        input_text = f"Analyze the sentiment of this comment and respond with only 'Good' or 'Bad' or 'Neutral': {comment}"
        response = model.generate_content(input_text)
        
        # Directly return the response text from Gemini
        return response.text.strip()
    except Exception as e:
        return "Error analyzing sentiment"

    
=======
def analyze_comment_sentiment(comment):
    try:
        input_text = f"Analyze the sentiment of this comment and respond with only 'Good' or 'Bad' or 'Neutral': {comment}"
        response = model.generate_content(input_text)
        return response.text.strip()
    except Exception:
        return "Error analyzing sentiment"

>>>>>>> ba23b4f (upload)
@app.route('/comment', methods=['POST'])
def add_comment():
    comment_text = request.json.get('comment')
    if not comment_text:
        return jsonify({'error': 'No comment provided'}), 400

<<<<<<< HEAD
    # Use Gemini API to analyze the comment
=======
>>>>>>> ba23b4f (upload)
    input_text = f"Categorize this comment as good or bad: {comment_text}"

    try:
        response = model.generate_content(input_text)
<<<<<<< HEAD
        comment_category = response.text.strip()  # Get the categorization result

        # Store the comment in comments.txt with its category
=======
        comment_category = response.text.strip()

>>>>>>> ba23b4f (upload)
        with open('comments.txt', 'a') as f:
            f.write(f"Comment: {comment_text}\nCategory: {comment_category}\n\n")

        return jsonify({'message': 'Comment added successfully', 'category': comment_category}), 200

    except Exception as e:
        return jsonify({'error': f"Error analyzing comment: {str(e)}"}), 500

@app.route('/comments')
def comments():
    comments_list = []

    try:
<<<<<<< HEAD
        # Read comments from the comments.txt file
=======
>>>>>>> ba23b4f (upload)
        with open('comments.txt', 'r') as f:
            comments_data = f.readlines()

        for comment in comments_data:
            sentiment = analyze_comment_sentiment(comment.strip())
            comments_list.append({'text': comment.strip(), 'sentiment': sentiment})

    except Exception as e:
        return f"Error reading comments: {str(e)}", 500

    return render_template('comments.html', comments=comments_list)

<<<<<<< HEAD

@app.route('/dashboard')
def dashboard():
    bucket_name = 'data-bucket-private'
    documents = []

    try:
        # List objects in the specified S3 bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        for obj in response.get('Contents', []):
            # Get the document key (file name)
            key = obj['Key']
            
            # Get presigned URL for viewing the document inline
            presigned_url = s3.generate_presigned_url('get_object',
                                                      Params={'Bucket': bucket_name, 'Key': key},
                                                      ExpiresIn=3600)

            # Extract the page count for PDF documents
            page_count = 0
            if key.endswith('.pdf'):
                # Download the document temporarily to extract page count
                file_obj = s3.get_object(Bucket=bucket_name, Key=key)
                pdf_file = file_obj['Body'].read()

                # Use PyMuPDF to get page count
=======
@app.route('/dashboard')
def dashboard():
    documents = []

    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)

        for obj in response.get('Contents', []):
            key = obj['Key']
            presigned_url = s3.generate_presigned_url('get_object',
                                                      Params={'Bucket': BUCKET_NAME, 'Key': key},
                                                      ExpiresIn=3600)
            page_count = 0
            if key.endswith('.pdf'):
                file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
                pdf_file = file_obj['Body'].read()
>>>>>>> ba23b4f (upload)
                doc = fitz.open(stream=pdf_file, filetype="pdf")
                page_count = doc.page_count

            documents.append({
                'key': key,
                'url': presigned_url,
<<<<<<< HEAD
                'page_count': page_count  # Include page count
=======
                'page_count': page_count
>>>>>>> ba23b4f (upload)
            })
    except Exception as e:
        return f"Error fetching documents from S3: {str(e)}", 500

    return render_template('dashboard.html', documents=documents)

<<<<<<< HEAD

=======
>>>>>>> ba23b4f (upload)
@app.route('/delete_file', methods=['POST'])
def delete_file():
    bucket_name = request.json.get('bucket')
    file_key = request.json.get('key')

    if not bucket_name or not file_key:
        return jsonify({'error': 'Bucket name and file key are required.'}), 400

<<<<<<< HEAD
    # Path to the local file
    local_file_path = os.path.join(local_directory, file_key)

    try:
        # Delete the file from S3
        s3.delete_object(Bucket=bucket_name, Key=file_key)

        # Delete the file from the local "files" folder if it exists
=======
    local_file_path = os.path.join(local_directory, file_key)

    try:
        s3.delete_object(Bucket=bucket_name, Key=file_key)

>>>>>>> ba23b4f (upload)
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            print(f"Local file {local_file_path} deleted.")
        else:
            print(f"Local file {local_file_path} not found.")

        return jsonify({'message': 'File successfully deleted from both S3 and local storage.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(host='0.0.0.0',debug=True)
=======
    app.run(host='0.0.0.0', debug=True)
>>>>>>> ba23b4f (upload)
