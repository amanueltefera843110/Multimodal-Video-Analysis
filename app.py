from flask import Flask, render_template_string, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from google import genai
import datetime
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>YouTube Transcript AI</title>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      min-height: 100vh;
      position: relative;
      overflow-x: hidden;
    }
    
    /* Animated background particles */
    body::before {
      content: '';
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                  radial-gradient(circle at 80% 20%, rgba(255, 118, 117, 0.3) 0%, transparent 50%),
                  radial-gradient(circle at 40% 40%, rgba(120, 255, 214, 0.2) 0%, transparent 50%);
      animation: float 20s ease-in-out infinite;
      pointer-events: none;
      z-index: 0;
    }
    
    @keyframes float {
      0%, 100% { transform: translateY(0px) rotate(0deg); }
      33% { transform: translateY(-20px) rotate(2deg); }
      66% { transform: translateY(10px) rotate(-1deg); }
    }
    
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
    
    .header {
      text-align: center;
      margin-bottom: 3rem;
      animation: fadeInUp 0.8s ease-out;
    }
    
    .header h1 {
      font-size: 3.5rem;
      font-weight: 800;
      background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 0.5rem;
      text-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .header p {
      color: rgba(255, 255, 255, 0.8);
      font-size: 1.2rem;
      font-weight: 300;
      letter-spacing: 0.5px;
    }
    
    .main-card {
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(20px);
      border-radius: 24px;
      padding: 3rem;
      box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.2);
      animation: fadeInUp 0.8s ease-out 0.2s both;
      position: relative;
      overflow: hidden;
    }
    
    .main-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #f5576c);
      background-size: 300% 100%;
      animation: gradientShift 3s ease-in-out infinite;
    }
    
    @keyframes gradientShift {
      0%, 100% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
    }
    
    .form-group {
      margin-bottom: 2rem;
      position: relative;
    }
    
    .form-group label {
      display: block;
      font-weight: 600;
      color: #374151;
      margin-bottom: 0.5rem;
      font-size: 0.95rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    
    .input-wrapper {
      position: relative;
    }
    
    .input-wrapper i {
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: #9ca3af;
      font-size: 1.1rem;
      z-index: 2;
    }
    
    .form-input {
      width: 100%;
      padding: 1rem 1rem 1rem 3rem;
      border: 2px solid #e5e7eb;
      border-radius: 16px;
      font-size: 1rem;
      background: #f9fafb;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
    }
    
    .form-input:focus {
      outline: none;
      border-color: #667eea;
      background: #fff;
      transform: translateY(-2px);
      box-shadow: 0 10px 25px rgba(102, 126, 234, 0.15);
    }
    
    .form-input:focus + .input-focus-bg {
      opacity: 1;
      transform: scale(1);
    }
    
    .submit-btn {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 16px;
      padding: 1rem 2.5rem;
      font-size: 1.1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      overflow: hidden;
      text-transform: uppercase;
      letter-spacing: 1px;
      min-width: 200px;
    }
    
    .submit-btn .fa-spin {
      margin-right: 8px;
    }
    
    .submit-btn:disabled {
      cursor: not-allowed;
      background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
    }
    
    .submit-btn::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 100%;
      height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
      transition: left 0.5s;
    }
    
    .submit-btn:hover::before {
      left: 100%;
    }
    
    .submit-btn:hover {
      transform: translateY(-3px);
      box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    .submit-btn:active {
      transform: translateY(-1px);
    }
    
    .output-section {
      margin-top: 2.5rem;
      background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
      border-radius: 20px;
      padding: 2rem;
      border: 1px solid rgba(148, 163, 184, 0.1);
      position: relative;
      animation: slideInUp 0.6s ease-out;
    }
    
    .output-section::before {
      content: '';
      position: absolute;
      top: -2px;
      left: -2px;
      right: -2px;
      bottom: -2px;
      background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
      border-radius: 22px;
      z-index: -1;
      opacity: 0.1;
    }
    
    .output-section h3 {
      color: #1e293b;
      font-size: 1.4rem;
      font-weight: 700;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    
    .output-section h3 i {
      color: #667eea;
      font-size: 1.2rem;
    }
    
    .output-content {
      background: #fff;
      border-radius: 12px;
      padding: 1.5rem;
      border-left: 4px solid #667eea;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    .output-text {
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 1rem;
      line-height: 1.6;
      color: #374151;
      margin: 0;
    }
    
    .loading {
      display: none;
      text-align: center;
      margin-top: 1rem;
    }
    
    .loading.show {
      display: block;
    }
    
    .spinner {
      display: inline-block;
      width: 24px;
      height: 24px;
      border: 3px solid rgba(102, 126, 234, 0.3);
      border-radius: 50%;
      border-top-color: #667eea;
      animation: spin 1s ease-in-out infinite;
      margin-right: 0.5rem;
    }
    
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    @keyframes fadeInUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    @keyframes slideInUp {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .feature-tags {
      display: flex;
      gap: 1rem;
      justify-content: center;
      margin: 2rem 0;
      flex-wrap: wrap;
    }
    
    .feature-tag {
      background: rgba(255, 255, 255, 0.2);
      color: white;
      padding: 0.5rem 1rem;
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 500;
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    @media (max-width: 768px) {
      .container {
        padding: 1rem;
      }
      
      .header h1 {
        font-size: 2.5rem;
      }
      
      .main-card {
        padding: 2rem;
        border-radius: 20px;
      }
      
      .feature-tags {
        gap: 0.5rem;
      }
    }
    
    /* Error styles */
    .error {
      background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
      border-left-color: #ef4444;
    }
    
    .error h3 {
      color: #dc2626;
    }
    
    .error i {
      color: #ef4444 !important;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1><i class="fab fa-youtube"></i> YouTube AI</h1>
      <p>Transform any YouTube video into intelligent insights</p>
      <div class="feature-tags">
        <div class="feature-tag"><i class="fas fa-robot"></i> AI-Powered</div>
        <div class="feature-tag"><i class="fas fa-clock"></i> Timestamped</div>
        <div class="feature-tag"><i class="fas fa-search"></i> Smart Q&A</div>
      </div>
    </div>
    
    <div class="main-card">
      <form method="post" action="/" id="analyzeForm">
        <div class="form-group">
          <label for="url"><i class="fas fa-link"></i> YouTube Video URL</label>
          <div class="input-wrapper">
            <i class="fab fa-youtube"></i>
            <input type="text" id="url" name="url" class="form-input" value="{{ url or '' }}" 
                   placeholder="https://www.youtube.com/watch?v=..." required>
          </div>
        </div>
        
        {% if show_question_field %}
        <div class="form-group">
          <label for="question"><i class="fas fa-question-circle"></i> Ask a Question (Optional)</label>
          <div class="input-wrapper">
            <i class="fas fa-comment-dots"></i>
            <input type="text" id="question" name="question" class="form-input" value="{{ question or '' }}" 
                   placeholder="What are the main points discussed in this video?">
          </div>
          <small style="color: #6b7280; margin-top: 0.5rem; display: block;">
            Leave blank for an automatic topic summary with timestamps
          </small>
        </div>
        {% endif %}
        
        <div style="text-align: center;">
          <button type="submit" class="submit-btn">
            <i class="fas fa-magic"></i>
            {% if show_question_field %}Analyze & Answer{% else %}Analyze Video{% endif %}
          </button>
        </div>
        
        <div class="loading" id="loading">
          <div class="spinner"></div>
          <span>Processing video transcript...</span>
        </div>
      </form>
      
      {% if output %}
      <div class="output-section {% if 'Error:' in output %}error{% endif %}">
        <h3>
          {% if 'Error:' in output %}
            <i class="fas fa-exclamation-triangle"></i>
            Error
          {% elif question %}
            <i class="fas fa-lightbulb"></i>
            AI Answer
          {% else %}
            <i class="fas fa-list-ul"></i>
            Video Topics & Timestamps
          {% endif %}
        </h3>
        <div class="output-content">
          <pre class="output-text">{{ output }}</pre>
        </div>
      </div>
      {% endif %}
    </div>
  </div>
  
  <script>
    const form = document.getElementById('analyzeForm');
    const loading = document.getElementById('loading');
    const submitBtn = document.querySelector('.submit-btn');
    let isSubmitting = false;

    form.addEventListener('submit', function(e) {
      // Prevent multiple submissions
      if (isSubmitting) {
        e.preventDefault();
        return;
      }

      isSubmitting = true;
      loading.classList.add('show');
      submitBtn.style.opacity = '0.7';
      submitBtn.disabled = true;
      
      // Add loading text to button
      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

      // Enable form after timeout (in case of network errors)
      setTimeout(() => {
        if (isSubmitting) {
          resetForm();
        }
      }, 30000); // 30 second timeout

      function resetForm() {
        isSubmitting = false;
        loading.classList.remove('show');
        submitBtn.style.opacity = '1';
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });

    // Add some interactive polish
    document.querySelectorAll('.form-input').forEach(input => {
      input.addEventListener('focus', function() {
        this.parentElement.style.transform = 'scale(1.02)';
      });
      
      input.addEventListener('blur', function() {
        this.parentElement.style.transform = 'scale(1)';
      });
    });
  </script>
</body>
</html>
"""

def extract_yt_id_regex(url: str) -> str:
    """Extract YouTube video ID from various YouTube URL formats"""
    # Common YouTube URL patterns
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # Regular URLs
        r"(?:embed\/)([0-9A-Za-z_-]{11})",  # Embed URLs (fixed typo)
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})" # Short URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1).strip()
    
    raise ValueError("Invalid YouTube URL. Please provide a valid YouTube video URL.")

def format_timestamp(sec: float) -> str:
    """Format seconds to HH:MM:SS - matches original function exactly"""
    td = datetime.timedelta(seconds=int(sec))
    total_seconds = int(td.total_seconds())
    h, remainder = divmod(total_seconds, 3600)
    m, s = divmod(remainder, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def get_transcript_with_timestamps(yt_video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            yt_video_id,
            languages=['en','en-US','en-GB']
        )
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable):
        raise ValueError("Transcript not available for this video. Please try another YouTube link.")
    
    timestamped = []
    for seg in transcript:
        ts = format_timestamp(seg['start'])
        text = seg['text'].replace('\n', ' ')
        timestamped.append(f"[{ts}] {text}")
    
    return "\n".join(timestamped)

@app.route('/', methods=['GET', 'POST'])
def index():
    url = ""
    question = ""
    output = None
    show_question_field = False
    
    if request.method == 'POST':
        # Get form data and clean it exactly like the original
        url = request.form.get('url', '').strip().replace(" ", "")
        question = request.form.get('question', '').strip()
        
        if url:
            try:
                # Extract video ID
                yt_video_id = extract_yt_id_regex(url)
                
                # Get transcript with timestamps
                full_transcript = get_transcript_with_timestamps(yt_video_id)
                
                # Initialize Gemini client
                client = genai.Client(api_key=API_KEY)
                
                # Generate prompt based on whether question is provided
                if not question:
                    # No question - provide topic summary (matches original logic)
                    prompt = (
                        "Below is a YouTube video transcript with timestamps. "
                        "Please identify the major topics covered and for each topic, give a short heading "
                        "and the timestamp where that topic first appears.\n\n"
                        + full_transcript
                    )
                else:
                    # Question provided - answer it (matches original logic)
                    prompt = (
                        f"Answer the following question based on the video transcript:\n\n{full_transcript}\n\nQuestion: {question}"
                    )
                
                # Generate content using Gemini
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                
                output = response.text
                show_question_field = True  # Show question field after first successful transcript fetch
                
            except Exception as e:
                output = f"Error: {e} can you retry with link YouTube URL?"
                show_question_field = False
    
    return render_template_string(
        HTML_TEMPLATE,
        url=url,
        question=question,
        output=output,
        show_question_field=show_question_field
    )

if __name__ == '__main__':
    app.run(debug=True)