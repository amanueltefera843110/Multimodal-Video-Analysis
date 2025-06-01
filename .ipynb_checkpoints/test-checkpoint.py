

from google import genai
# …etc…

# For Gemini Developer API:
client = genai.Client(api_key="AIzaSyD_iaP7Q1-8blcRIAgUVRM3sdX4VZhaLp4")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="fave thing in world"
)
print(response.text)