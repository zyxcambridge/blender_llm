# from google import genai

# client = genai.Client(api_key="AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg")

# response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     contents="Explain how AI works in a few words",
# )

# print(response.text)
# print(response)

# curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=GEMINI_API_KEY" \
# - H 'Content-Type: application/json' \
# - X POST \
# - d '{
#   "contents": [{
#     "parts":[{"text": "Explain how AI works"}]
#     }]
#    }'

from google import genai

# client = genai.Client(api_key="AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg")

# response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     contents="Explain how AI works in a few words",
# )

# print(response.text)
# print(response)

# from google import genai

# client = genai.Client(api_key="AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg")

# response = client.models.generate_content(model="gemini-2.0-flash", contents=["How does AI work?"])
# print(response.text)

from google import genai

# export GEMINI_API_KEY = "AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg"
# export YOUR_API_KEY = "AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg"
GEMINI_API_KEY = "AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg"
client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(model="gemini-2.0-flash", contents=["How does AI work?"])
print(response.text)
