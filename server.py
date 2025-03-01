from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import asyncio
import logging
import json
import queue
import threading
from open_ai_modules import ChromeExtensionAssistant

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create a global instance of the assistant
assistant = ChromeExtensionAssistant()

@app.route('/create_thread', methods=['POST'])
def create_thread():
    """Create or update a thread for a website"""
    try:
        data = request.json
        website_url = data.get('website_url')
        
        if not website_url:
            return jsonify({"error": "Missing website_url parameter"}), 400
        
        # Run the async function in the Flask context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(assistant.create_or_update_thread(website_url))
        loop.close()
        
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
            
        return jsonify({"thread_id": result["thread_id"]})
    
    except Exception as e:
        logging.error(f"Error in create_thread: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Send a message to the AI assistant (non-streaming)"""
    try:
        data = request.json
        thread_id = data.get('thread_id')
        message = data.get('message')
        
        if not thread_id:
            return jsonify({"error": "Missing thread_id parameter"}), 400
        if not message:
            return jsonify({"error": "Missing message parameter"}), 400
        
        # Get response without streaming
        response = assistant.chat(thread_id, message)
        
        return jsonify({"response": response})
    
    except Exception as e:
        logging.error(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat_stream', methods=['POST'])
def chat_stream():
    """Stream responses from the AI assistant"""
    try:
        data = request.json
        thread_id = data.get('thread_id')
        message = data.get('message')
        
        if not thread_id:
            return jsonify({"error": "Missing thread_id parameter"}), 400
        if not message:
            return jsonify({"error": "Missing message parameter"}), 400
        
        # Create a queue to communicate between threads
        token_queue = queue.Queue()
        
        # Function to collect tokens and put them in the queue
        def token_collector(token):
            token_queue.put(token)
        
        # Function for the background thread that calls the chat_stream method
        def run_chat_stream():
            try:
                # Call the chat_stream method with our token collector function
                assistant.chat_stream(thread_id, message, token_collector)
                # Put a sentinel value to indicate the end of streaming
                token_queue.put(None)
            except Exception as e:
                logging.error(f"Error in streaming thread: {str(e)}")
                token_queue.put(None)  # Signal end of stream on error
        
        # Start the background thread
        threading.Thread(target=run_chat_stream, daemon=True).start()
        
        # Generator function to yield streaming responses
        def generate():
            while True:
                token = token_queue.get()
                if token is None:  # End of stream
                    break
                yield token
        
        # Return a streaming response
        return Response(generate(), mimetype='text/plain')
    
    except Exception as e:
        logging.error(f"Error in chat_stream: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)