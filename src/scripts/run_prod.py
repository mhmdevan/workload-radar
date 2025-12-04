import os
import subprocess
from app.config import Config


def main() -> None:
    """Run application using gunicorn WSGI server."""
    cfg = Config()
    workers = int(os.getenv("GUNICORN_WORKERS", "4"))
    bind = f"{cfg.APP_HOST}:{cfg.APP_PORT}"

    cmd = [
        "gunicorn",
        "-w",
        str(workers),
        "-b",
        bind,
        "app:create_app()",
    ]

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
