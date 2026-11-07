import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  # 读取 .env 文件里的内容

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="用一句话介绍你自己",
)

print(response.text)