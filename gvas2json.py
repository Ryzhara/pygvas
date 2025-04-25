import argparse
import json
import sys

from pydantic import TypeAdapter

from gvas.gvas_file import GVASFile


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
        gvas_file = GVASFile.read_gvas_file(
            args.input_file, deserialization_hints=args.hints_file
        )

    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
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
        f"Successfully processed the UE GVAS file '{args.input_file}' into '{args.output_file}'."
    )


if __name__ == "__main__":
    main()
