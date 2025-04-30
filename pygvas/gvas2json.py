import argparse
import sys

from pygvas.gvas_file import GVASFile


# python gvas2json.py input.txt output.txt
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Read an Unreal Engine .sav (GVAS) and serialize to a JSON output file."
    )
    parser.add_argument("input_file", type=str, help="Path to the GVAS input file")
    parser.add_argument("output_file", type=str, help="Path to the JSON output file")
    parser.add_argument(
        "--hints_file",
        type=str,
        default=None,
        help="Path to optional deserialization hints (JSON) file",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        gvas_file: GVASFile = GVASFile.deserialize_gvas_file(
            args.input_file, deserialization_hints=args.hints_file
        )
    except Exception as e:
        print(f"Error processing input_file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        gvas_file.serialize_to_json_file(args.output_file)
    except Exception as e:
        print(f"Error writing to output file: {e}", file=sys.stderr)
        sys.exit(1)
    print(
        f"Successfully processed the UE GVAS file '{args.input_file}' into '{args.output_file}'."
    )


if __name__ == "__main__":
    main()
