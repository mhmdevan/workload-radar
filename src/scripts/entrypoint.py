import os


def main() -> None:
    """Entry point that switches between dev and prod modes."""
    app_env = os.getenv("APP_ENV", "development").lower()

    if app_env == "development":
        from .run_dev import main as run_dev

        run_dev()
    else:
        from .run_prod import main as run_prod

        run_prod()


if __name__ == "__main__":
    main()
