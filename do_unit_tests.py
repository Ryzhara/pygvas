import unittest
import sys
import argparse
from colorama import init, Fore, Style

# Initialize colorama
init()

# --- Parse arguments ---
parser = argparse.ArgumentParser(description="Run unit tests with optional verbosity.")
parser.add_argument("-v", action="store_true", help="Enable verbose output")
args = parser.parse_args()

verbosity = 2 if args.v else 1
success = True

# --- Set color constants ---
SUCCESS_COLOR = Fore.GREEN
FAILURE_COLOR = Fore.RED
NEUTRAL_COLOR = Fore.WHITE

print(
    NEUTRAL_COLOR
    + "You may need to activate your virtual environment before invoking these."
)


# --- Run a test suite from a directory ---
def run_test_suite_from_dir(test_dir):
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()


# --- Run a specific test file ---
def run_test_file(test_file):
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_file)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()


# --- Execute tests ---
if not run_test_suite_from_dir("tests/gvas_core"):
    success = False

if not run_test_file("tests.test_gvas_examples"):
    success = False

# --- Final output ---
final_color = SUCCESS_COLOR if success else FAILURE_COLOR
print(
    final_color
    + ("All tests passed!" if success else "Some tests failed.")
    + Style.RESET_ALL
)
sys.exit(0 if success else 1)
