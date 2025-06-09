from flask import Flask, render_template_string, request
from google import genai
from google.genai import types
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Use API key from environment or default to your key
API_KEY = os.getenv("GEMINI_API_KEY") 

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Youtubgbt</title>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <style>
    /* Basic Reset */
    * { margin: 0; padding: 0; box-sizing: border-box; }

    /* Body Styles */
    body {
      background: linear-gradient(135deg, #000000 0%, #330033 100%);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: #eee;
      min-height: 100vh;
      position: relative;
      overflow-x: hidden;
    }
    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at 20% 80%, rgba(255, 0, 0, 0.2) 0%, transparent 50%),
                  radial-gradient(circle at 80% 20%, rgba(128, 0, 128, 0.2) 0%, transparent 50%);
      animation: pulse 25s ease-in-out infinite;
      pointer-events: none;
      z-index: 0;
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1) rotate(0deg); }
      50% { transform: scale(1.1) rotate(2deg); }
    }
    /* Container */
    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 2rem;
      position: relative;
      z-index: 1;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    /* Loader Styles */
    #loader {
      display: none;
      text-align: center;
      margin-bottom: 1rem;
    }
    #loader i {
      font-size: 2rem;
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    /* Header */
    .header {
      text-align: center;
      margin-bottom: 3rem;
    }
    .header h1 {
      font-size: 3.5rem;
      font-weight: 800;
      background: linear-gradient(135deg, #ff0000 0%, #800080 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      text-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    .header p {
      font-size: 1.2rem;
      font-weight: 300;
      letter-spacing: 0.5px;
      color: #ffaaaa;
    }
    /* Main card */
    .main-card {
      background: rgba(20, 20, 20, 0.95);
      backdrop-filter: blur(10px);
      border-radius: 24px;
      padding: 3rem;
      box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
      border: 1px solid rgba(255, 0, 0, 0.3);
    }
    /* Form Styles */
    .form-group { margin-bottom: 2rem; }
    .form-group label {
      display: block;
      font-weight: 600;
      margin-bottom: 0.5rem;
      font-size: 0.95rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #ff6666;
    }
    .input-wrapper {
      position: relative;
    }
    .input-wrapper i {
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      font-size: 1.1rem;
      color: #ff6666;
    }
    .form-input {
      width: 100%;
      padding: 1rem 1rem 1rem 3rem;
      border: 2px solid #800080;
      border-radius: 16px;
      font-size: 1rem;
      background: #1a001a;
      color: #eee;
      transition: all 0.3s;
    }
    .form-input:focus {
      border-color: #ff0000;
      outline: none;
    }
    .submit-btn {
      background: linear-gradient(135deg, #ff0000 0%, #800080 100%);
      color: #fff;
      border: none;
      border-radius: 16px;
      padding: 1rem 2.5rem;
      font-size: 1.1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s;
      text-transform: uppercase;
      letter-spacing: 1px;
      min-width: 200px;
    }
    .submit-btn:hover {
      filter: brightness(110%);
    }
    /* Output Section */
    .output-section {
      margin-top: 2.5rem;
      background: rgba(50, 0, 50, 0.8);
      border-radius: 20px;
      padding: 2rem;
      border: 1px solid rgba(255, 0, 0, 0.3);
    }
    .output-text {
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 1rem;
      line-height: 1.6;
      color: #ffaaaa;
    }
    /* Styled link for timestamps */
    .timestamp {
      color: #ff4444;
      font-weight: bold;
      text-decoration: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Loader element -->
    <div id="loader">
      <i class="fas fa-spinner"></i>
      <p>Processing your request, please wait...</p>
    </div>
    <div class="header">
      <h1><i class="fab fa-youtube"></i> Youtubgbt</h1>
      <p>Ask anything about a YouTube video</p>
    </div>
    <div class="main-card">
      <form method="post" action="/" id="main-form">
        <div class="form-group">
          <label for="url"><i class="fas fa-link"></i> YouTube Video URL</label>
          <div class="input-wrapper">
            <i class="fab fa-youtube"></i>
            <input type="text" id="url" name="url" class="form-input" value="{{ url or '' }}"
                   placeholder="https://www.youtube.com/watch?v=..." required>
          </div>
        </div>
        <div class="form-group">
          <label for="question"><i class="fas fa-question-circle"></i> Ask a Question (Optional)</label>
          <div class="input-wrapper">
            <i class="fas fa-comment-dots"></i>
            <input type="text" id="question" name="question" class="form-input" value="{{ question or '' }}"
                   placeholder="What is happening in the video?">
          </div>
        </div>
        <div style="text-align: center;">
          <button type="submit" class="submit-btn">Submit</button>
        </div>
      </form>
      
      {% if output %}
      <div class="output-section">
        <pre class="output-text">{{ output|safe }}</pre>
      </div>
      {% endif %}
    </div>
  </div>
  <script>
    document.getElementById("main-form").addEventListener("submit", function(e) {
      // Prevent multiple submissions and show the loader animation
      this.style.display = "none";
      document.getElementById("loader").style.display = "block";
    });
  </script>
</body>
</html>
"""

# Base prompt used for generating content
base_prompt = "Transcribe the audio from this video, giving timestamps for salient events in the video. Also provide visual descriptions."

def extract_yt_id_regex(url: str) -> str:
    """Extracts the YouTube video ID from URL."""
    match = re.search(r"[?&]v=([^&]+)", url)
    if not match:
        raise ValueError("Invalid YouTube URL. Please provide a valid URL.")
    return match.group(1).strip()

def filter_image_description(text: str) -> str:
    """
    Removes lines that seem to describe the video's images.
    For example, lines starting with "Image:" or "Screenshot:".
    """
    lines = text.splitlines()
    filtered = [line for line in lines if not re.match(r"^(Image|Screenshot):", line, re.IGNORECASE)]
    return "\n".join(filtered)

def format_timestamps(text: str, video_url: str) -> str:
    """
    Finds timestamps in the format [hh:mm:ss] and converts them into a linked format.
    It trims the hour if it is 0 and constructs a URL with a timestamp parameter.
    """
    def repl(match):
        time_str = match.group(1)  # e.g., "00:00:15"
        hh, mm, ss = time_str.split(":")
        hh_int, mm_int, ss_int = int(hh), int(mm), int(ss)
        total_seconds = hh_int * 3600 + mm_int * 60 + ss_int
        if hh_int == 0:
            display = f"{mm_int:02d}:{ss_int:02d}"
        else:
            display = f"{hh_int:02d}:{mm_int:02d}:{ss_int:02d}"
        separator = "&" if "?" in video_url else "?"
        timestamp_link = f"{video_url}{separator}t={total_seconds}s"
        return f'<a href="{timestamp_link}" class="timestamp"><strong>{display}</strong></a>'
    
    return re.sub(r"\[(\d{2}:\d{2}:\d{2})\]", repl, text)

@app.route("/", methods=["GET", "POST"])
def index():
    url = ""
    question = ""
    output = None
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        question = request.form.get("question", "").strip()
        if url:
            # Validate URL by extracting the video id (raises error if invalid)
            _ = extract_yt_id_regex(url)
            
            if question:
                prompt_text = f"{base_prompt} {question}. Please provide a detailed explanation."
            else:
                prompt_text = base_prompt
            content = types.Content(
                parts=[
                    types.Part(text=prompt_text),
                    types.Part(file_data=types.FileData(file_uri=url)),
                    types.Part(text="Please summarize the video in 3 sentences.")
                ]
            )
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model="models/gemini-2.0-flash",
                contents=content
            )
            # First filter out unwanted image-speak, then format timestamps
            filtered = filter_image_description(response.text)
            output = format_timestamps(filtered, url)

    return render_template_string(HTML_TEMPLATE, url=url, question=question, output=output)

if __name__ == "__main__":
    app.run(debug=True)