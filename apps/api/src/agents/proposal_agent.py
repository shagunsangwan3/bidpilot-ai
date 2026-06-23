from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()

agent = Agent(
    "openai:gpt-4o-mini"
)

async def generate_proposal(
    job_title: str,
    job_description: str,
    budget: str
):
    prompt = f"""
You are an expert Upwork freelancer.

Write a professional proposal.

Job Title:
{job_title}

Job Description:
{job_description}

Budget:
{budget}

Keep it concise, personalized and persuasive.
"""

    result = await agent.run(prompt)

    return result.output