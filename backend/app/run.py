"""Production demo entrypoint. Run with PYTHONPATH=backend from the repo root."""

import argparse
import os

import uvicorn
from dotenv import load_dotenv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", help="Optional dotenv file; existing environment values take precedence")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    args = parser.parse_args()
    if args.env_file:
        load_dotenv(args.env_file, override=False)
    # Import only after env-file loading; app creation reads environment settings.
    from app.main import app

    uvicorn.run(
        app, host=args.host, port=args.port, workers=1,
        access_log=False, log_level="critical", server_header=False,
        timeout_keep_alive=5, timeout_graceful_shutdown=35,
        limit_concurrency=64,
    )


if __name__ == "__main__":
    main()
