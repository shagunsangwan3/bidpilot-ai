import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-2.5-flash"


async def summarize_lead(
    title: str,
    description: str,
    notes: str,
    status: str,
    activity_log: str,
) -> str:
    prompt = f"""
You are a CRM assistant. Summarize this lead in 3-4 short bullet points for a
salesperson who hasn't looked at it in a while — what it's about, where it
stands, and anything that needs attention.

Title: {title}
Status: {status}
Description: {description}
Notes: {notes or "(none)"}
Recent activity: {activity_log or "(none)"}

Requirements:
- 3-4 bullet points, each one short sentence
- No markdown headers, no preamble, just the bullets (use "- " prefix)
- Be specific to this lead, not generic advice
"""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


async def write_email(
    client_name: str,
    project_title: str,
    purpose: str,
    context: str,
) -> str:
    prompt = f"""
Write a short, professional email to a client named {client_name} about the
project "{project_title}".

Purpose of this email: {purpose}
Additional context: {context or "(none)"}

Requirements:
- Professional but warm tone, not stiff
- 3-6 sentences, no filler
- No subject line, no markdown, just the email body
- End with a clear next step
"""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


async def improve_text(text: str, instruction: str) -> str:
    prompt = f"""
Rewrite the following text according to this instruction: {instruction}

Text to rewrite:
{text}

Requirements:
- Return ONLY the rewritten text, nothing else
- No markdown, no preamble like "Here's the rewritten version:"
- Keep the same approximate length unless the instruction says otherwise
"""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


async def suggest_pricing(title: str, description: str, category: str) -> str:
    prompt = f"""
You are a freelance/agency pricing advisor. Suggest a price range for this
project based on typical market rates.

Project title: {title}
Category: {category or "(not specified)"}
Description: {description}

Requirements:
- Give a specific price range (e.g. "$2,500 - $4,000")
- Follow it with 2-3 short bullet points explaining the reasoning
  (complexity, scope, typical market rate for this kind of work)
- No markdown headers, no preamble
"""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text
