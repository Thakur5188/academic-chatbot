import os
from flask import Flask, render_template, request, Response
from google import genai
from google.genai import types

app = Flask(__name__)

# SECURITY UPGRADE: This pulls the key safely from the cloud server
API_KEY = os.environ.get("AIzaSyDSVfV4NUz_JqIxDwDJlV2CEzMS4stzErk") 

# Safety check to prevent crashing if the key is missing
if not API_KEY:
    print("WARNING: API Key not found. Please set the GEMINI_API_KEY environment variable.")

client = genai.Client(api_key=API_KEY)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")
    grade_level = data.get("grade")
    chat_history = data.get("history", []) 

    contents = []
    for msg in chat_history:
        contents.append(
            types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=msg["text"])]
            )
        )
        
    current_prompt = f"(Student level: {grade_level}. Explain appropriately.)\nQuestion: {user_message}"
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=current_prompt)]
        )
    )

    def generate():
        try:
            response = client.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=contents
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"Error: {str(e)}"

    # This is the magic line that sends pure streaming text instead of JSON
    return Response(generate(), mimetype='text/plain')

if __name__ == "__main__":
    app.run(debug=True)