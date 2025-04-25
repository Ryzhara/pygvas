import argparse
import json
import sys

from pydantic import TypeAdapter

from gvas.gvas_file import GVASFile


# python gvas2json.py input.txt output.txt
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Read JSON file and convert to an Unreal Engine .sav (GVAS) file."
    )
    parser.add_argument("input_file", type=str, help="Path to the JSON input file")
    parser.add_argument("output_file", type=str, help="Path to the GVAS output file")
    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        gvas_file: GVASFile = GVASFile.deserialize_json_file(args.input_file)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        gvas_file.write_file(args.output_file, None)
    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"Successfully processed the JSON file '{args.input_file}' into '{args.output_file}'."
    )


if __name__ == "__main__":
    main()
