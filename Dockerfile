FROM python:3.7-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade "pip<24.1" && \
    python -m pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DASHBOARD_HOST=0.0.0.0
CMD ["python", "-m", "teacher_agent.main"]
