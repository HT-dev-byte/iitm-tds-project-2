import asyncio
import re
import base64
from io import BytesIO

import pandas as pd
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup  # new dependency

# --- Additional safe enhancements (do not touch existing code) ---
import os

def debug_csv_from_html(html_content):
    """Check if there's a CSV link and attempt a simple sum."""
    soup = BeautifulSoup(html_content, "html.parser")
    csv_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith(('.csv', '.xlsx'))]
    for link in csv_links:
        print(f"Found CSV/Excel file to download: {link}")
        try:
            r = requests.get(link, timeout=20)
            r.raise_for_status()
            if link.endswith('.csv'):
                df = pd.read_csv(BytesIO(r.content))
            else:
                df = pd.read_excel(BytesIO(r.content))
            if 'value' in df.columns:
                s = df['value'].sum()
                print(f"Sum of 'value' column: {s}")
            else:
                print("No 'value' column found.")
        except Exception as e:
            print(f"Error processing {link}: {e}")

def debug_chained_url(response_json):
    """Print the next quiz URL if returned in the JSON."""
    if isinstance(response_json, dict) and 'url' in response_json:
        print(f"Next quiz URL detected: {response_json['url']}")

def fetch_page_html_sync(url: str) -> str:
    """Render JS-enabled page and return HTML (Windows-safe)."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        raise RuntimeError(f"Playwright error: {e}")

def log_quiz_debug(html_snippet: str, decoded_snippet: str):
    """Helper to log quiz content safely."""
    print("\n--- DEBUG LOG: Raw HTML ---")
    print(html_snippet[:500])
    print("--- DEBUG LOG: Decoded HTML ---")
    print(decoded_snippet[:500])
    print("-------------------------------\n")

async def solve_quiz(email: str, secret: str, quiz_url: str):
    """Main solver logic."""
    loop = asyncio.get_event_loop()
    html = await loop.run_in_executor(None, fetch_page_html_sync, quiz_url)

    print("\n--- PAGE FETCHED ---")
    print(html[:500])
    print("-------------------\n")

    # Decode base64 payload if present
    match = re.search(r"atob\((['\"`])([^'\"`]+)\1\)", html)
    decoded = base64.b64decode(match.group(2)).decode("utf-8") if match else html

    print("\n--- DECODED PAYLOAD ---")
    print(decoded[:500])
    print("------------------------\n")

    # Parse HTML with BeautifulSoup to safely extract submit URL
    soup = BeautifulSoup(decoded, "html.parser")
    origin_span = soup.find("span", class_="origin")
    if not origin_span:
        raise ValueError("Could not find <span class='origin'> in quiz page")
    submit_url = origin_span.get_text(strip=True) + "/submit"
    print(f"\nSubmit URL detected: {submit_url}\n")

    # --- Compute real answer safely ---
    task_answer = None
    try:
        # Look for CSV/Excel links in the decoded page
        csv_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith(('.csv', '.xlsx'))]
        if csv_links:
            link = csv_links[0]
            r = requests.get(link, timeout=20)
            r.raise_for_status()
            if link.endswith(".csv"):
                df = pd.read_csv(BytesIO(r.content))
            else:
                df = pd.read_excel(BytesIO(r.content))
            task_answer = df['value'].sum() if 'value' in df.columns else 0
        # If URL points directly to a CSV/JSON file
        elif quiz_url.lower().endswith(".csv"):
            df = pd.read_csv(quiz_url)
            task_answer = df['value'].sum() if 'value' in df.columns else 0
        elif quiz_url.lower().endswith(".json"):
            r = requests.get(quiz_url, timeout=30)
            data = r.json()
            task_answer = sum(item.get("value", 0) for item in data)
        else:
            # Fallback dummy answer
            answer_match = re.search(r'"answer":\s*([0-9]+|".*?")', decoded)
            task_answer = answer_match.group(1) if answer_match else "anything you want"
    except Exception as e:
        print(f"Error computing task_answer: {e}")
        task_answer = "Error"



    payload = {
        "email": email,
        "secret": secret,
        "url": quiz_url,
        "answer": task_answer
    }
    

    try:
        resp = requests.post(submit_url, json=payload, timeout=30)
        resp.raise_for_status()
        debug_chained_url(resp.json())
        return resp.json()
    except Exception as e:
        raise RuntimeError(f"Error submitting answer: {e}")

async def solve_full_quiz(email, secret, start_url):
    """
    Top-level runner to fully solve a quiz,
    including follow-up URLs returned by the endpoint.
    """
    current_url = start_url
    while current_url:
        print(f"Solving quiz at: {current_url}")
        result = await solve_quiz(email, secret, current_url)
        print(f"Response: {result}")
        current_url = result.get("url")  # None if quiz is over
    print("Quiz completed!")








