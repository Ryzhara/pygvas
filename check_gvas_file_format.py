import argparse
import sys

from gvas.gvas_file import GVASFile, GameFileFormat


# python gvas2json.py input.txt output.txt
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Detects the format and compression of Unreal Engine .sav (GVAS) files."
    )
    parser.add_argument("input_file", type=str, help="Path to the GVAS input file")
    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        game_file_format: GameFileFormat = GVASFile.get_game_file_format(
            args.input_file
        )
        print(
            f"{args.input_file} is {game_file_format.game_version} with {game_file_format.compression_type}"
        )

    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
