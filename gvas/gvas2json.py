import argparse
import json
import sys

from pydantic import TypeAdapter

from gvas import GVASFile


# python gvas2json.py input.txt output.txt
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Read an Unreal Engine .sav (GVAS) and serialize to a JSON output file."
    )
    parser.add_argument("input_file", type=str, help="Path to the input file")
    parser.add_argument("output_file", type=str, help="Path to the output file")
    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        gvas_file, _decompressed_data = GVASFile.read_file(args.input_file)

    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        gvas_file_adaptor = TypeAdapter(GVASFile)
        gvas_file_dict = gvas_file_adaptor.dump_python(gvas_file, exclude_none=True)
        pydantic_json_content = json.dumps(gvas_file_dict, indent=2)
        with open(args.output_file, "w") as f:
            f.write(pydantic_json_content)

    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(
        f"Successfully wrote content from '{args.input_file}' to '{args.output_file}'."
    )


if __name__ == "__main__":
    main()
