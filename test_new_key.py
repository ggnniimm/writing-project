import google.generativeai as genai
import os

key = "AIzaSyC7rqRhbHs9QhKDpq7wHKaLrFuS7rOkyWA"

def test_key():
    try:
        genai.configure(api_key=key)
        print(f"Testing Key: ...{key[-5:]}")
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content("Hello")
        if response.text:
            print("✅ Key is Valid!")
            return True
    except Exception as e:
        print(f"❌ Key Failed: {e}")
        return False

if __name__ == "__main__":
    test_key()
