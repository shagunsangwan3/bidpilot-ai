import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


async def generate_proposal(
    job_title: str,
    job_description: str,
    budget: str,
):
    prompt = f"""
You are an expert Upwork and Freelancer proposal writer.

Write a professional proposal for the following project.

Job Title:
{job_title}

Job Description:
{job_description}

Budget:
{budget}

Requirements:
- Professional tone
- Personalized
- Mention understanding of the client's requirements
- Explain how the project will be completed
- Mention experience with AI, Python, FastAPI, React and Data Science where relevant
- End with a call to action
- Don't use markdown
- Don't use bullet points unless necessary
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text