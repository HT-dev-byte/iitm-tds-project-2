# LLM Quiz Solver

A FastAPI-based agent that solves data-centric quizzes automatically for the "LLM Data Sourcing & Analysis" project.

## 🚀 Features
- Verifies secrets for secure access
- Uses AIpipe for LLM utilization
- Fetches data, computes answers, and submits automatically

## 🧩 Endpoint
**POST /solve_quiz**

### Example Request
```PowerShell
$body = @{
    email = "you@example.com"
    secret = "secret"
    url = "https://tds-llm-analysis.s-anand.net/demo"
} | ConvertTo-Json


Invoke-RestMethod -Uri "http://127.0.0.1:8000/solve_quiz" -Method Post -ContentType "application/json" -Body $body

