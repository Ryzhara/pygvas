import filecmp
from pathlib import Path


def compare_binary_files(
    file1_path: Path | str, file2_path: Path | str, verbose: bool = False
) -> bool:
    """
    Compares two binary files and reports differences.

    Args:
        file1_path (str): Path to the first file.
        file2_path (str): Path to the second file.
    """
    if filecmp.cmp(file1_path, file2_path, shallow=False):
        if verbose:
            print(f"SUCCESS: Files {file1_path} and {file2_path} are identical.")
        return True
    else:
        if verbose:
            print(f"FAILED: Files {file1_path} and {file2_path} are different.")
        return False

        # with open(file1_path, "rb") as f1, open(file2_path, "rb") as f2:
        #     file1_bytes = f1.read()
        #     file2_bytes = f2.read()
        # import difflib
        # differ = difflib.Differ()
        # diff = list(
        #     differ.compare(
        #         [f"{i:08x}: {byte:02x}\n" for i, byte in enumerate(file1_bytes)],
        #         [f"{i:08x}: {byte:02x}\n" for i, byte in enumerate(file2_bytes)],
        #     )
        # )
        #
        # print("Differences:")
        # print("".join(diff), end="")
        # return len(diff) > 0
