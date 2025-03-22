FROM python:3.11-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install the application dependencies.
WORKDIR /app

# Copiar arquivos de dependências antes para evitar que o cache do Docker seja invalidado
COPY pyproject.toml uv.lock ./

RUN uv venv && uv sync --frozen --no-cache

# Definir que todos os comandos a partir daqui usem o ambiente virtual
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application into the container.
COPY . .

EXPOSE 8000

# Iniciar a aplicação com o caminho correto do `uvicorn`
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]