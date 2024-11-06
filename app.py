import os
from flask import Flask, request, render_template, jsonify, url_for
import boto3
import json
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
def split_text(text, max_length=500):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home',methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    # Upload the file to S3
    bucket_name = 'data-bucket-private'
    s3_key = file.filename

    local_file_path = os.path.join(local_directory, s3_key)
    file.save(local_file_path)

    try:
        with open(local_file_path, 'rb') as f:
            s3.upload_fileobj(f, bucket_name, s3_key)
    except Exception as e:
        return f'Error uploading file to S3: {str(e)}', 500
    
    file_url = url_for('static', filename=f'files/{s3_key}')

    # Invoke the Lambda function based on file type
    try:
        if file.filename.endswith('.pdf'):
            file_type = 'pdf'
        elif file.filename.endswith('.csv'):
            file_type = 'csv'
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            file_type = 'excel'
        else:
            return 'Unsupported file type', 400
        
    

        response = lambda_client.invoke(
            FunctionName='DocumentTextExtractor',
            InvocationType='RequestResponse',
            Payload=json.dumps({'bucket': bucket_name, 'key': s3_key, 'file_type': file_type})
        )

        # Read the response from Lambda
        payload = json.loads(response['Payload'].read())
        print("Lambda response:", payload)  # Debugging line

        if response['StatusCode'] == 200:
            extracted_text = json.loads(payload.get('body', '{}')).get('text', '')
            if not extracted_text:
                return "No extracted text returned from Lambda.", 500
        else:
            return "Lambda function failed.", 500

    except Exception as e:
        return f'Error invoking Lambda function: {str(e)}', 500

    return render_template('result.html', text=extracted_text, bucket=bucket_name, key=s3_key, file_url=file_url)

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    text = request.json.get('text')

    # Ensure that we provide the full text to Gemini
    chunks = split_text(text)
    full_text = " ".join(chunks)  # Combine all chunks into a single string

    # Create the input based on the expected format
    input_text = f"Answer the question: {question} \nContext: {full_text}"

    try:
        # Generate response without using 'prompt=' if not required
        response = model.generate_content(input_text)
        answer = response.text.strip()  # Extract and clean the generated answer
        
# Replace markdown syntax with HTML bold tags
        answer = answer.replace("**", "<strong>")
        
# Replace markdown syntax with HTML bold tags
        answer = answer.replace("*", "<strong>")

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'answer': answer})

@app.route('/delete_file', methods=['POST'])
def delete_file():
    bucket_name = request.json.get('bucket')
    file_key = request.json.get('key')

    if not bucket_name or not file_key:
        return jsonify({'error': 'Bucket name and file key are required.'}), 400

    # Path to the local file
    local_file_path = os.path.join(local_directory, file_key)

    try:
        # Delete the file from S3
        s3.delete_object(Bucket=bucket_name, Key=file_key)

        # Delete the file from the local "files" folder if it exists
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            print(f"Local file {local_file_path} deleted.")
        else:
            print(f"Local file {local_file_path} not found.")

        return jsonify({'message': 'File successfully deleted from both S3 and local storage.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)