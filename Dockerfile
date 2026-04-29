FROM python:3.11-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./

RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN uv pip install --python /opt/venv/bin/python .

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
