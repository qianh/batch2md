"""Main entry point for batch2md."""

import sys
from .cli import parse_args, run_conversion


def main() -> int:
    """
    Main entry point for batch2md CLI.

    Returns:
        Exit code (0=success, 1=partial failure, 2=error)
    """
    try:
        # Parse arguments
        config = parse_args()

        # Run conversion
        summary = run_conversion(config)

        # Return appropriate exit code
        return summary.exit_code

    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 2

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
