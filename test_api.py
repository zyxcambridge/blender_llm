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

# from google import genai

# # export GEMINI_API_KEY = "AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg"
# # export YOUR_API_KEY = "AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg"
# GEMINI_API_KEY = "AIzaSyC5zCgXXwCNbUmbQR_phRtmciRSBrCcDqg"
# client = genai.Client(api_key=GEMINI_API_KEY)

# response = client.models.generate_content(model="gemini-2.0-flash", contents=["How does AI work?"])
# print(response.text)

import os
from openai import OpenAI

# token = os.environ["GITHUB_TOKEN"]
import os
token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise RuntimeError("未检测到 GITHUB_TOKEN 环境变量，请设置后重试。")

endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "What is the capital of France?",
        },
    ],
    temperature=1.0,
    top_p=1.0,
    max_tokens=1000,
    model=model_name,
)

print(response.choices[0].message.content)
