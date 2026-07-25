import os
from app import create_app


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "sim"}


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=_env_bool("DEBUG", False))
