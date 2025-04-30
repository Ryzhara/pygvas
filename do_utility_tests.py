import sys
from pathlib import Path
from typing import Union

from colorama import init, Fore
import importlib.metadata
import subprocess

# Import your modules
from pygvas import detect_gvas_format, gvas2json, json2gvas

# Setup
init(autoreset=True)


class UtilityTester:
    PACKAGE_NAME = "pygvas"
    RESOURCE_DIR = Path("resources/test")
    TEST_GVAS = Path("utility_test_result__.gvas")
    TEST_JSON = Path("utility_test_result__.json")
    TEST_HINTS_JSON = Path("utility_test_hints_result__.hints.json")
    success = True

    def run_main_with_args(self, module, *args):
        """Call a module's main() with temporarily overridden sys.argv."""
        self.success = True
        old_argv = sys.argv
        sys.argv = [module.__name__] + list(map(str, args))  # Ensure strings
        try:
            module.main()
        except SystemExit as e:
            if e.code != 0:
                print(Fore.RED + f"{module.__name__} exited with code {e.code}")
                self.success = False
        except Exception as e:
            print(Fore.RED + f"Exception in {module.__name__}: {e}")
            self.success = False
        finally:
            sys.argv = old_argv

    def compare_binary(self, file1: Path, file2: Path):
        try:
            if file1.read_bytes() != file2.read_bytes():
                print(Fore.RED + f"Files differ: {file1} vs {file2}")
                self.success = False
        except FileNotFoundError as e:
            print(Fore.RED + f"File not found: {e}")
            self.success = False

    def clean_temp_files(self):
        for f in [self.TEST_GVAS, self.TEST_JSON, self.TEST_HINTS_JSON]:
            try:
                f.unlink()
            except FileNotFoundError:
                pass

    def do_preliminary_checks(self):
        # --- Check if package is installed ---
        print(
            "You may need to activate your virtual environment before invoking these.\n"
        )
        print(f"Checking if {self.PACKAGE_NAME} is installed...")

        try:
            version = importlib.metadata.version(self.PACKAGE_NAME)
            print(Fore.GREEN + f"{self.PACKAGE_NAME} {version} is already installed.")
        except importlib.metadata.PackageNotFoundError:
            print(
                Fore.YELLOW
                + f"{self.PACKAGE_NAME} is NOT installed. Installing with 'pip install -e .' ..."
            )
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."],
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            if result.returncode != 0:
                print(Fore.RED + f"Installation failed:\n{result.stderr}")
                sys.exit(1)
            else:
                print(Fore.GREEN + f"{self.PACKAGE_NAME} installed successfully.")
                print(Fore.YELLOW + "Please re-run this script to continue.")
                sys.exit(0)

        # --- Clean up ---
        print("\nCleaning up temporary files...")
        self.clean_temp_files()

    def run_test(
        self,
        testfile: Union[str, Path],
        file_extension: Union[str, Path],
        *,
        hints_file: Union[str, Path, None] = None,
        update_hints: bool = False,
    ):
        """
        Run a test for the specified testfile with or without generating hints.

        :param testfile: The base filename to test (without extension)
        :param file_extension: The file extension to append for the specific test (e.g., '.bin' or '.sav')
        :param hints_file: optional hints file to use or create
        :param update_hints: Boolean flag indicating whether to attempt to update or generate hints

        """

        # Step 1: Detect GVAS format
        print(
            Fore.CYAN
            + f"\n===== Testing {testfile}{file_extension} with hints_file={str(hints_file)} and {update_hints} ====="
        )
        self.run_main_with_args(
            detect_gvas_format, self.RESOURCE_DIR / f"{testfile}{file_extension}"
        )

        # Step 2: Run gvas2json
        gvas2json_args = [
            self.RESOURCE_DIR / f"{testfile}{file_extension}",
            self.TEST_JSON,
        ]

        if hints_file:
            gvas2json_args.append(f"--hints_file={hints_file}")
            if update_hints:
                gvas2json_args.append("--update_hints")

        self.run_main_with_args(gvas2json, *gvas2json_args)

        # Step 3: Compare the generated JSON to the expected file
        self.compare_binary(
            self.TEST_JSON, self.RESOURCE_DIR / f"{testfile}{file_extension}.json"
        )

        # Step 4: Run json2gvas and compare the result
        self.run_main_with_args(json2gvas, self.TEST_JSON, self.TEST_GVAS)
        self.compare_binary(
            self.TEST_GVAS, self.RESOURCE_DIR / f"{testfile}{file_extension}"
        )

        # Step 5: Generate hints if necessary and validate
        if update_hints:
            if Path(hints_file).exists():
                print(Fore.GREEN + "Hints file successfully created.")
            else:
                print(Fore.RED + "Failed to create hints file.")
                success = False


def main():
    utility_tester = UtilityTester()
    utility_tester.do_preliminary_checks()

    # --- Run tests ---
    # Testing a BIN file with hints
    utility_tester.run_test(
        "features_01",
        ".bin",
        hints_file=utility_tester.RESOURCE_DIR / "features_01.hints.json",
    )
    # Testing a file without hints, but creating one
    utility_tester.run_test(
        "component8",
        ".sav",
        hints_file=utility_tester.TEST_HINTS_JSON,
        update_hints=True,
    )
    # Testing a Palworld compressed file without hints
    utility_tester.run_test("palworld_zlib", ".sav")

    # --- Cleanup ---
    print("\nCleaning up temporary files...")
    utility_tester.clean_temp_files()

    # --- Final Result ---
    if utility_tester.success:
        print(Fore.GREEN + "\nAll tests passed successfully.")
        sys.exit(0)
    else:
        print(Fore.RED + "\nSome tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
