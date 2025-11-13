# LLM Quiz Solver

A FastAPI-based agent that solves data-centric quizzes automatically for the "LLM Data Sourcing & Analysis" project.

## 🚀 Features
- Verifies secrets for secure access
- Uses AIpipe for LLM utilization
- Fetches data, computes answers, and submits automatically

## 🧩 Endpoint
**POST /solve**

### Example Request
```bash
curl -X POST https://llm-quiz-solver.onrender.com/solve \
-H "Content-Type: application/json" \
-d '{
  "email": "you@example.com",
  "secret": "secret",
  "url": "https://tds-llm-analysis.s-anand.net/demo"
}'
