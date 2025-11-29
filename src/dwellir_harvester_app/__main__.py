import sys

from dwellir_harvester_app.cli import build_parser, main as cli_main


def main() -> int:
    # Show help if no arguments are provided
    if len(sys.argv) == 1:
        parser = build_parser()
        parser.print_help()
        return 0

    return cli_main()


if __name__ == "__main__":
    sys.exit(main())
