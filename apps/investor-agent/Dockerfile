# mixapp Investor Agent
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

ENV PORT=8000
EXPOSE ${PORT}
# Datadog APM + LLM Observability: ddtrace-run で起動（DD_LLMOBS_ENABLED, DD_AGENT_HOST, DD_API_KEY は実行時 env で指定）
CMD ["ddtrace-run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
