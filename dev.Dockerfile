FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Enable bytecode compilation by writing to .pyc files
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of using symlinks since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Then, add the rest of the project source code and install it
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV VIRTUAL_ENV=/opt/venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# document the port
EXPOSE 8000

# Run with auto-reload
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]