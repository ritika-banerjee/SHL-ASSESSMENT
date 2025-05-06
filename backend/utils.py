import re
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the model
model = genai.GenerativeModel(model_name="gemini-2.0-flash")



def find_job_summary(summary: str):
    """
    Extract the Job Summary using the model's generate_content method.
    """
    prompt = """Extract the following from this job description. Return in raw JSON format without comments:
    
                - Summary: (brief summary of what job or task is being described)
                - Skills: (comma-separated list)
                - Duration: (in minutes)
                - Experience Level: (entry, mid, senior)
                - Job Domain: (if known, like Software Dev, Marketing, etc.)

                Text:
                
                """
            
    input_text = f"{prompt}\n{summary}"

    response = model.generate_content(
        contents=input_text,
        generation_config={
            "temperature": 0.7,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 300
        }
    )

    job_summary = response.text.strip() 
    return job_summary

def extract_url_from_text(text: str) -> str:
    """Extract URL from text input, supports direct links and markdown/HTML."""
    url_match = re.search(r'https?://[^\s<>")]+', text)
    if url_match:
        return url_match.group(0)

    soup = BeautifulSoup(text, "html.parser")
    a_tag = soup.find("a", href=True)
    if a_tag:
        return a_tag['href']

    md_match = re.search(r'\[.*?\]\((https?://.*?)\)', text)
    if md_match:
        return md_match.group(1)

    return None

async def extract_job_description(text: str) -> str:
    url = extract_url_from_text(text)
    if not url:
        return text

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True) 
        page = await browser.new_page()

        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_selector("body", timeout=10000)
            content = await page.content()
        except Exception as e:
            await browser.close()
            return f"Failed to load page: {e}"

        await browser.close()

        soup = BeautifulSoup(content, 'html.parser')
        
        job_blocks = soup.find_all(True, {
            "class": lambda x: x and any(kw in x.lower() for kw in [
                "description", "job", "content", "details", "posting", "text", "main"
            ])
        })

        if not job_blocks:
            return "No potential job content blocks found."

        # Pick the largest block by visible text length
        largest_block = max(job_blocks, key=lambda tag: len(tag.get_text(strip=True)), default=None)

        if largest_block:
            return largest_block.get_text(separator="\n", strip=True)

        return "Job description not found."

async def get_job_description_from_input(input_text: str) -> str:
    return await extract_job_description(input_text)

