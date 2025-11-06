import argparse
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from solver import solve_captcha

def main():
    """Main entry point for the CAPTCHA solver CLI."""
    # Load environment variables from a .env file if it exists
    load_dotenv()

    parser = argparse.ArgumentParser(description="Solve a CAPTCHA image using an external service.")
    parser.add_argument(
        "--solve",
        dest="image_path",
        required=True,
        help="The path to the CAPTCHA image file.",
        type=Path
    )
    parser.add_argument(
        "--timeout",
        default=25,
        type=int,
        help="The maximum time in seconds to wait for a solution."
    )
    args = parser.parse_args()

    # Validate that the image path exists
    if not args.image_path.is_file():
        result = {"ok": False, "error": f"File not found: {args.image_path}"}
        print(json.dumps(result))
        sys.exit(1)

    # Call the solver
    solution = solve_captcha(str(args.image_path), args.timeout)

    # Print the result to stdout
    print(json.dumps(solution))

    # Set the exit code
    if solution.get("ok"):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
