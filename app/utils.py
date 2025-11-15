import re
import io
import base64
import httpx
import pandas as pd
from bs4 import BeautifulSoup


# ──────────────────────────────────────────────
# 🧩 1️⃣ Base64 decoding
# ──────────────────────────────────────────────
def extract_and_decode_base64(html: str) -> str | None:
    """
    Finds and decodes a base64 string in an atob(`...`) call inside HTML.
    Returns the decoded text, or None if not found.
    """
    match = re.search(r"atob\(`([^`]+)`\)", html)
    if not match:
        return None
    return base64.b64decode(match.group(1)).decode("utf-8", errors="ignore")


# ──────────────────────────────────────────────
# 🌐 2️⃣ File download
# ──────────────────────────────────────────────
async def download_file(url: str) -> bytes:
    """
    Downloads a file (CSV, PDF, JSON, etc.) and returns the content as bytes.
    """
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.content


# ──────────────────────────────────────────────
# 📊 3️⃣ CSV reader
# ──────────────────────────────────────────────
def read_csv_bytes(file_bytes: bytes) -> pd.DataFrame:
    """
    Reads CSV content from bytes safely, auto-detecting encoding.
    """
    return pd.read_csv(io.BytesIO(file_bytes))


# ──────────────────────────────────────────────
# 🧾 4️⃣ PDF table extractor (using pdfplumber)
# ──────────────────────────────────────────────
def extract_tables_from_pdf(pdf_bytes: bytes) -> list[pd.DataFrame]:
    """
    Extracts all tables from a PDF file and returns a list of DataFrames.
    Requires pdfplumber.
    """
    import pdfplumber
    tables = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            for table in page_tables:
                df = pd.DataFrame(table[1:], columns=table[0])
                tables.append(df)
    return tables


# ──────────────────────────────────────────────
# 🧱 5️⃣ HTML table extractor (using BeautifulSoup)
# ──────────────────────────────────────────────
def extract_tables_from_html(html: str) -> list[pd.DataFrame]:
    """
    Extracts all <table> elements from HTML and returns as DataFrames.
    """
    soup = BeautifulSoup(html, "html.parser")
    tables = []
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells:
                rows.append(cells)
        if headers and rows:
            df = pd.DataFrame(rows, columns=headers)
        elif rows:
            df = pd.DataFrame(rows)
        else:
            continue
        tables.append(df)
    return tables


# ──────────────────────────────────────────────
# 📈 6️⃣ Visualization helper (optional)
# ──────────────────────────────────────────────
def dataframe_to_base64_image(df: pd.DataFrame, kind: str = "bar") -> str:
    """
    Creates a base64-encoded PNG chart from a DataFrame.
    Returns a data URI (data:image/png;base64,...).
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(6, 4))
    try:
        df.plot(kind=kind)
    except Exception:
        df.head(10).plot(kind="bar")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


# ──────────────────────────────────────────────
# 🔢 7️⃣ JSON-safe conversion
# ──────────────────────────────────────────────
def json_safe(obj):
    """
    Converts Numpy/Pandas types to plain Python types for JSON serialization.
    """
    import numpy as np

    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.ndarray, list)):
        return [json_safe(x) for x in obj]
    if isinstance(obj, (pd.Series, pd.Index)):
        return obj.tolist()
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    return obj
