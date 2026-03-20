FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /code

COPY pyproject.toml uv.lock /code/

RUN uv sync --frozen --no-cache

COPY . /code/

EXPOSE 80

CMD [ "uv", "run", "fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0" ]
