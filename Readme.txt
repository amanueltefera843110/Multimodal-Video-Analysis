# YouTube Transcript AI

YouTube Transcript AI is a Flask web application that lets you analyze any YouTube video by extracting its transcript, generating topic summaries with timestamps, and answering custom questions using Google's Gemini AI.

## Features

- Extracts transcripts from YouTube videos (supports multiple English variants)
- Summarizes major topics with timestamps
- AI-powered Q&A about video content
- Modern, responsive web UI

## How it works

1. Enter a YouTube video URL.
2. (Optional) Ask a question about the video.
3. The app fetches the transcript, sends it to Gemini AI, and displays a summary or answer.

## Setup

1. **Clone the repository**

   ```sh
   git clone https://github.com/yourusername/youtube-transcript-ai.git
   cd youtube-transcript-ai
   ```

2. **Create a virtual environment**

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up your environment variables**

   Create a `.env` file in the project root with your Gemini API key:

   ```
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

5. **Run the app**

   ```sh
   python app.py
   ```

   Visit [http://localhost:5000](http://localhost:5000) in your browser.

## Requirements

See [requirements.txt](requirements.txt).

## License

MIT License

---

*Powered by Flask, YouTube Transcript API, and Google Gemini AI.*