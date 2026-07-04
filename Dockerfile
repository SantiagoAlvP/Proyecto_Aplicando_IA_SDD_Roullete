FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv

COPY . .

RUN uv sync --frozen

CMD ["uv", "run", "project_jackpot.py"]