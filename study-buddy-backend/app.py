from flask import Flask, request, jsonify
from flask_cors import CORS 
import os
from dotenv import load_dotenv

from file_processor import(
    load_and_extract_text,
    chunk_text,
    create_embedding,
    store_in_pinecone,
    retrieve_from_pinecone,
    generate_answer
)

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

    #base cases
    if 'file' not in request.files:
        return jsonify({"error": "No selected file"}),400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}),400


    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            print(f"Starting the pipeline...")
            text = load_and_extract_text(filepath)
            if not text:
                return jsonify({"error": "Failed to extract, need text file.."}),400
            
            chunks = chunk_text(text)
            if not chunks:
                return jsonify({"error": "Failed to chunk the text."}),400
            embeddings = create_embedding(chunks)
            if embeddings is None:
                return jsonify({"error": "Failed to create embeddings."}),400
            store_in_pinecone(chunks, embeddings)
            print("Ingestion complete")
            return jsonify({"message":f"File '{file.filename}' uploaded and processed successfully."})
        except Exception as e:
            print(f"An error occured : {e}")
            return jsonify({"error": f"An error occured during processing: {e}"}),500

print("Upload endpoint is ready.")

#api for chat questioning

@app.route('/chat', methods=['POST'])

def chat():
    print("Received a chat Request")
    data = request.get_json()
    print(f"REeceived data: {data}")
    user_question = data.get('question')

    chat_history = data.get('history', [])  

    if not user_question:
        return jsonify({"error": "No question provided."}), 400
    
    try:
        retrieved_chunks = retrieve_from_pinecone(user_question)
        final_answer = generate_answer(retrieved_chunks, user_question, chat_history)

        return jsonify({"answer": final_answer, "sources": retrieved_chunks}), 200

    except Exception as e:
        print(f"An error ocurred: {e}")
        return jsonify({"error": str(e)}),500

print("Chat endpoint is ready")

if __name__ == "__main__":
    print("Starting the Flask app")
    app.run(host = '0.0.0.0', port = 5300, debug = True)

