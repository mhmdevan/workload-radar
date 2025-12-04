from app import create_app
from app.config import Config


def main() -> None:
    """Run Flask development server."""
    app = create_app(Config)
    app.run(
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
        debug=app.config["DEBUG"],
    )


if __name__ == "__main__":
    main()
