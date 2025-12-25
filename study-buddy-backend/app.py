from flask import Flask, request, jsonify
from flask_cors import CORS 
import os
import time
from dotenv import load_dotenv

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
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            print(f"Starting the pipeline...")
            # Import file processing helpers here to avoid requiring heavy deps at app startup
            from file_processor import load_and_extract_text, chunk_text, create_embedding, store_in_pinecone

            t_total_start = time.perf_counter()

            t0 = time.perf_counter()
            text = load_and_extract_text(filepath) 
            t1 = time.perf_counter()
            extract_ms = round((t1 - t0) * 1000)

            if not text:
                return jsonify({"error": "Failed to extract, need text file.."}),400

            t0 = time.perf_counter()
            chunks = chunk_text(text, use_case=use_case)
            t1 = time.perf_counter()
            chunk_ms = round((t1 - t0) * 1000)
            if not chunks:
                return jsonify({"error": "Failed to chunk the text."}),400

            t0 = time.perf_counter()
            embeddings = create_embedding(chunks, use_case=use_case)
            t1 = time.perf_counter()
            embed_ms = round((t1 - t0) * 1000)
            if embeddings is None:
                return jsonify({"error": "Failed to create embeddings."}),400
            
            t0 = time.perf_counter()
            store_in_pinecone(chunks, embeddings, use_case=use_case)
            t1 = time.perf_counter()
            upsert_ms = round((t1 - t0) * 1000)

            total_ms = round((time.perf_counter() - t_total_start) * 1000)

            print(
                f"Ingestion timings → extract: {extract_ms} ms | chunk: {chunk_ms} ms | embed: {embed_ms} ms | upsert: {upsert_ms} ms | total: {total_ms} ms"
            )
            print("Ingestion complete")
            return jsonify({
                "message": f"File '{file.filename}' uploaded and processed successfully.",
                "latency": {
                    "extract_ms": extract_ms,
                    "chunk_ms": chunk_ms,
                    "embed_ms": embed_ms,
                    "upsert_ms": upsert_ms,
                    "total_ms": total_ms
                }
            })
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
        from file_processor import retrieve_from_pinecone, generate_answer

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
    app.run(host = '0.0.0.0', port = 5300, debug = True)

