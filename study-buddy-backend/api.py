import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

print("--- Day 1 Complete: Testing with the Official Google AI Library ---")

try:
    # Get the API key from the environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Make sure it's set in your .env file.")
    
    # Configure the library with your API key
    genai.configure(api_key=api_key)

    # Create the model. We'll use a powerful and recent model.
    # The library handles the 'models/' prefix automatically.
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

    # Send a prompt to the model
    print("Sending a test prompt to the Gemini API...")
    response = model.generate_content("In one sentence, what is the best part about learning to code?")

    # Print the successful response
    print("\nSUCCESS!")
    print(response.text)

except Exception as e:
    print(f"\nAN ERROR OCCURRED: {e}")