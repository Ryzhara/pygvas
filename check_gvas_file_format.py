import argparse
import json
import sys

from pydantic import TypeAdapter

from gvas.gvas_file import GVASFile


# python gvas2json.py input.txt output.txt
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Read an Unreal Engine .sav (GVAS) and guess the format and compression."
    )
    parser.add_argument("input_file", type=str, help="Path to the GVAS input file")
    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        GVASFile.print_game_file_format(args.input_file)

    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
