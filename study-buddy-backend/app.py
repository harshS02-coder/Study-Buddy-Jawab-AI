import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS 
import os
import time
from dotenv import load_dotenv
from ingestion.pipeline import ingest_pipeline
from ingestion.executor import executor
from file_processor import retrieve_from_pinecone, generate_answer

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

UPLOAD_FOLDER = "Upload_path"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

print("Flask app initialized.")

#file uploading api

@app.route('/upload', methods=['POST'])
def upload_and_process():
    print("Received a file upload request.")

    use_case = request.form.get('use_case', 'study')

    #base cases
    if 'file' not in request.files:
        return jsonify({"error": "No selected file"}),400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}),400


    if file:
        filename = f"{uuid.uuid4()}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
             #ASYNC ingestion
            executor.submit(ingest_pipeline, filepath, use_case)
            return jsonify({
                "message": "File uploaded. Processing started."
            }), 202
            # print("Ingestion complete")
        except Exception as e:
            print(f"An error occured : {e}")
            return jsonify({"error": f"An error occured during processing: {e}"}),500

print("Upload endpoint is ready.")

#api for chat questioning

@app.route('/chat', methods=['POST'])

def chat():
    print("Received a chat Request")
    data = request.get_json()
    use_case = data.get('use_case', 'study')
    # print(f"Received data: {data}")
    user_question = data.get('question')

    chat_history = data.get('history', [])  

    if not user_question:
        return jsonify({"error": "No question provided."}), 400
    
    try:
        retrieved_chunks = retrieve_from_pinecone(user_question, use_case=use_case)
        # generate_answer expects (query:str, context_chunks:list[str], chat_history)
        final_answer = generate_answer(user_question, retrieved_chunks, chat_history, use_case=use_case)

        return jsonify({"answer": final_answer, "sources": retrieved_chunks}), 200

    except Exception as e:
        print(f"An error ocurred: {e}")
        return jsonify({"error": str(e)}),500

print("Chat endpoint is ready")

if __name__ == "__main__":
    print("Starting the Flask app")
    app.run(host = '0.0.0.0', port = 5300, debug = False)

