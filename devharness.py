import filecmp
import pathlib
import enum
import json
import sys
import zipfile

from pydantic import ValidationError
from pydantic.dataclasses import dataclasses
from pydantic import TypeAdapter
from pydantic import BaseModel

from gvas.gvas_file import GVASFile, GameFileFormat
from gvas.engine_tools import GameVersion, CompressionType
from gvas.gvas_utils import *


def compare_binary_files(
    file1_path: Union[str, pathlib.Path],
    file2_path: Union[str, pathlib.Path],
    verbose: bool = False,
) -> bool:
    """
    Compares two binary files and reports differences.

    Args:
        file1_path (str): Path to the first file.
        file2_path (str): Path to the second file.
        verbose: print success/fail message
    """
    if filecmp.cmp(file1_path, file2_path, shallow=False):
        if verbose:
            print(f"SUCCESS: Files {file1_path} and {file2_path} are identical.")
        return True
    else:
        if verbose:
            print(f"FAILED: Files {file1_path} and {file2_path} are different.")
        return False


# ============================================
class EnhancedJSONEncoder(json.JSONEncoder):

    def default(self, obj):

        def is_not_empty(value):
            # if isinstance(value, (str, type(None))):
            #     return not not value
            if isinstance(value, (type(None))):
                return not not value

            if isinstance(value, uuid.UUID) and value == MagicConstants.ZERO_GUID:
                return False

            return True

        if isinstance(obj, BaseModel):
            field_dict = obj.model_dump()
            return {
                k: self.default(v) for k, v in field_dict.items() if is_not_empty(v)
            }

        if isinstance(obj, GameFileFormat):
            return {
                "game_version": obj.game_version,
                "compression_type": obj.compression_type,
            }

        if isinstance(obj, enum.IntEnum):
            return obj.name

        if isinstance(obj, uuid.UUID):
            return guid_to_str(obj)

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if isinstance(obj, list):
            return [self.default(item) for item in obj]

        if isinstance(obj, tuple):
            return [self.default(item) for item in obj]

        if isinstance(obj, bytes):
            return obj.hex()

        if isinstance(obj, dict):
            return {k: self.default(v) for k, v in obj.items() if is_not_empty(v)}

        if dataclasses.is_dataclass(obj):
            return {
                k: self.default(v)
                for k, v in dataclasses.asdict(obj).items()
                if is_not_empty(v)
            }

        if isinstance(obj, CompressionType):
            return obj.name

        if isinstance(obj, GameVersion):
            return obj.name

        if isinstance(obj, (int, float, str, bool, type(None))):
            return obj

        return obj


test_file_list: list[tuple[str, Any]] = [
    ("resources/test/islands_of_insight.sav", None),
    ("resources/test/assert_failed.sav", None),
    ("resources/test/component8.sav", None),
    ("resources/test/Delegate.sav", None),
    ("resources/test/Options.sav", None),
    ("resources/test/Profile_0.sav", None),
    ("resources/test/enum_array.sav", None),
    ("resources/test/package_version_525.sav", None),
    ("resources/test/package_version_524.sav", None),
    ("resources/test/Slot1.sav", None),
    ("resources/test/Slot2.sav", None),
    ("resources/test/Slot3.sav", None),
    ("resources/test/transform.sav", None),
    ("resources/test/ro_64bit_fav.sav", None),
    ("resources/test/SaveSlot_03.sav", None),
    ("resources/test/vector2d.sav", None),
    ("resources/test/regression_01.bin", None),
    ("resources/test/features_01.bin", "resources/test/features_01.hints.json"),
    ("resources/test/palworld_zlib.sav", None),
    (
        "resources/test/palworld_zlib_twice.sav",
        "resources/test/palworld_zlib_twice.hints.json",
    ),
]


# this one requires HINTS implementation.
# There is a 16-byte GUID hiding anonymously as a struct_property in a map_property
# See gvas/tests/common/palworld.rs in deserialization_hints() hashmap for testing sequence
# test_file_list = ["resources/test/palworld_zlib_twice.sav"]  # Working!

# game_version = GameVersion.DEFAULT
# compression = CompressionType.NONE

# # game_version = GameVersion.PALWORLD
# # compression = CompressionType.ZLIB
# test_file_list = ["resources/test/palworld_zlib.sav"]  # working!

#   text_property_noarray.bin -- SaveGameData.StructProperty.QuestsStatus.ArrayProperty.QuestsStatus.ShortDescription.TextProperty
#  test_file_list = ["resources/test/text_property_noarray.bin"]  # Working!
# StructProperty["TrackedQuestsNames"] = NameProperty(value="QU91_InvestigateTower_B2")


# there are some "BIN" files:
#   features_01.bin, -- custom struct @ FSDEventRewardsSave.StructProperty.EventsSeen.SetProperty.StructProperty


# always a quick retest
# test_file_list = [("resources/test/assert_failed.sav", None)]
# test_file_list = [("resources/test/Options.sav", None)]
# test_file_list = [("resources/test/Delegate.sav", None)]
# test_file_list = [("resources/test/Slot1.sav", None)]
# test_file_list = [("resources/test/vector2d.sav", None)]
# test_file_list = [("resources/test/package_version_525.sav", None)]
# test_file_list = [("resources/test/islands_of_insight.sav", None)]
# test_file_list = [("resources/test/SaveSlot_03.sav", None)]
# test_file_list = [("resources/test/Profile_0.sav", None)]
# test_file_list = [("resources/test/Slot2.sav", None)]
# test_file_list = [("resources/test/component8.sav", None)]
# test_file_list = [("resources/test/enum_array.sav", None)]
# test_file_list = [("resources/test/package_version_524.sav", None)]
# test_file_list = [("resources/test/Slot3.sav", None)]
# test_file_list = [("resources/test/transform.sav", None)]
# test_file_list = [("resources/test/ro_64bit_fav.sav", None)]
# test_file_list = [
#     (
#         "resources/test/palworld_zlib_twice.sav",
#         "resources/test/palworld_zlib_twice.hints.json",
#     )
# ]
# test_file_list = [
#     ("resources/test/features_01.bin", "resources/test/features_01.hints.json")
# ]


def test_gvas_file(test_file: str, hints: str) -> None:
    # Open and read a .sav file
    UnitTestGlobals.set_inside_unit_tests()
    gvas_file = None
    try:
        gvas_file: GVASFile
        gvas_file = GVASFile.deserialize_gvas_file(
            test_file, deserialization_hints=hints
        )
    except Exception as e:
        print(f"Failed to load {test_file}: {e}")
        raise e

    if gvas_file.game_file_format.compression_type != CompressionType.NONE:
        decompressed_data_file = f"{test_file}.decompressed"
        with open(test_file, "rb") as f:
            decompressed_data = f.read()
        # print(f"Saving decompressed data {decompressed_data_file}")
        with open(decompressed_data_file, "wb") as f:
            f.write(decompressed_data)

    # dump binary to work toward idempotence for read, write, rinse and repeat
    output_file = f"{test_file}.idempotent"
    uncompressed_output_file = f"{test_file}.decompressed.idempotent"
    gvas_file.serialize_to_gvas_file(output_file, uncompressed_output_file)

    idempotent = compare_binary_files(test_file, output_file)

    # create json with pydantic
    pydantic_json_file = f"{test_file}.pydantic.json"

    gvas_file_adaptor = TypeAdapter(GVASFile)
    gvas_file_dict = gvas_file_adaptor.dump_python(gvas_file, exclude_none=True)
    pydantic_json_content = json.dumps(gvas_file_dict, indent=2)
    with open(pydantic_json_file, "w") as f:
        f.write(pydantic_json_content)

    # create json the old fashioned way
    json_file = f"{test_file}.json"
    try:
        # we get a lot of circular references from the Literal["TypeNameString"] used for Pydantic
        json_content = json.dumps(
            gvas_file, cls=EnhancedJSONEncoder, indent=2, check_circular=True
        )
        with open(json_file, "w") as f:
            f.write(json_content)
    except OverflowError as e:
        print(f"Circular reference detected: {e}")

    # # THIS METHOD WORKS, TOO.
    # # Note that this method writes out float values differently.
    # pydantic_json_content = gvas_file_adaptor.dump_json(
    #     gvas_file, exclude_none=True, indent=2, round_trip=False
    # )
    # with open(f"{pydantic_json_file}.too", "wb") as f:
    #     f.write(pydantic_json_content)

    json_old_and_new = compare_binary_files(json_file, pydantic_json_file)

    # create JSON zip if large
    # we store output of PYDANTIC specific serialzation but without 'pydantic' file name components
    is_it_zip_worthy = pathlib.Path(pydantic_json_file)
    if is_it_zip_worthy.exists():
        file_stat = is_it_zip_worthy.stat()
        if file_stat.st_size > 8_000_000:
            try:
                with zipfile.ZipFile(f"{json_file}.zip", "w") as zipf:
                    zipf.write(json_file, arcname=pathlib.Path(json_file).name)
                print(f"File '{json_file}' zipped successfully to '{json_file}.zip'")
            except FileNotFoundError:
                print(f"Error: File not found: '{json_file}'")
            except Exception as e:
                print(f"An error occurred: {e}")

    # Re-load and deserialize that JSON
    with open(pydantic_json_file, "r") as f:
        pydantic_json_content_dict = json.load(f)

    try:
        new_gvas = gvas_file_adaptor.validate_python(pydantic_json_content_dict)
        # new_gvas2 = GVASFile.model_validate(pydantic_json_content_dict)
    except ValidationError as e:
        # print(e)
        print(e.errors())  # JSON-style breakdown
        raise e

    # this way is better? or does it not validate?
    # new_gvas = GVASFile(**pydantic_json_content_dict)

    # Now write that GVAS file back out for round trip test
    output_file_too = f"{test_file}.idempotent.too"
    uncompressed_output_file = f"{test_file}.decompressed.idempotent.too"
    new_gvas.serialize_to_gvas_file(output_file_too, uncompressed_output_file)

    reread_and_rewrite = compare_binary_files(output_file_too, output_file)

    if idempotent and json_old_and_new and reread_and_rewrite:
        print(f"SUCCESS testing {test_file}")
        return

    if not idempotent:
        print(
            f"\tFAILED: {test_file} != {output_file} Reserialized gvas file is NOT IDENTICAL to original."
        )

    if not json_old_and_new:
        print(
            f"\tFAILED: {test_file} Reserialized JSON file is NOT IDENTICAL to original."
        )

    if not reread_and_rewrite:
        print(
            f"\tFAILED: {test_file} Deserialized of JSON FAILED. The saved GVAS is NOT IDENTICAL to first serialization."
        )


dump_model = False
if dump_model:
    model_json_schema = GVASFile.model_json_schema()
    with open("gvas_file_schema.json", "w") as f:
        json_string = json.dumps(model_json_schema, indent=2)
        f.write(json_string)
    exit(0)


class FloatHandler:
    """
    IEEE-754 32-bit format (single precision)
        1 bit = sign (0 = positive, 1 = negative)
        8 bits = exponent (bias = 127)
        23 bits = mantissa (fractional part)

    For normal numbers:
        Value = (-1)^sign * 2^(exponent-127) * (1.fraction_bits)

    For special cases:
        Exponent 255 (all ones)

    If mantissa == 0 ➔ infinity
        If mantissa ≠ 0 ➔ NaN
    """

    @staticmethod
    def unpack_float(float_value):
        """
        Unpacks a 32-bit IEEE 754 float into its sign, exponent, and mantissa.

        Args:
            float_value: The float value to unpack.

        Returns:
            A tuple containing the sign (0 or 1), exponent (integer), and mantissa (float).
        """

        # GVAS is little endian
        packed_value = struct.pack("<f", float_value)
        int_value = struct.unpack("<I", packed_value)[0]

        sign = (int_value >> 31) & 1
        exponent = (int_value >> 23) & 0xFF
        mantissa = int_value & 0x7FFFFF

        if exponent == 0:
            exponent_unbiased = 1 - 127
        elif exponent == 255:
            exponent_unbiased = float("inf")
        else:
            exponent_unbiased = exponent - 127

        if exponent == 0:
            mantissa_normalized = mantissa / (2**23)
        else:
            mantissa_normalized = 1 + mantissa / (2**23)

        return (
            sign,
            exponent,
            exponent_unbiased,
            mantissa,
            mantissa_normalized,
            int_value,
        )

    @staticmethod
    def build_ieee_float(sign: int, exponent: int, mantissa: Union[int, str]):
        # Start by setting the sign bit
        sign = (1 if sign < 0 else 0) << 31

        if mantissa == "inf":
            exponent = 0xFF << 23
            mantissa = 0x000000
        elif mantissa == "nan":
            exponent = 0xFF << 23
            # Quiet NaN (just needs nonzero mantissa, 1st bit set often)
            mantissa = 0x400000
        else:
            # Regular number
            exponent = (exponent & 0xFF) << 23
            mantissa = mantissa & 0x7FFFFF  # Only 23 bits

        # Combine the parts
        integer_bits = sign | exponent | mantissa

        # Pack into 4 bytes (little-endian if needed)
        gvas_integer_bytes = struct.pack(
            "<I", integer_bits
        )  # '>I' = big-endian unsigned int (network byte order)

        return integer_bits, gvas_integer_bytes


test_floats = False
if test_floats:
    for float_value in [31415.9, 3.141592653]:
        # Example usage
        sign, exponent, exponent_unbiased, mantissa, mantissa_normalized, int_value = (
            FloatHandler.unpack_float(float_value)
        )

        float_value_back = float("nan")
        integer_bits = 0xDEADBEEF
        integer_bits, gvas_integer_bytes = FloatHandler.build_ieee_float(
            sign, exponent, mantissa
        )
        float_value_back = struct.unpack("<f", gvas_integer_bytes)[0]

        print(
            f"{float_value=}, {float_value_back=}, {sign=}, {exponent=}, {mantissa=}, {mantissa_normalized=}, {int_value=}, {integer_bits=}"
        )

    sys.exit(0)

for test_file, hints in test_file_list:
    test_gvas_file(test_file, hints)
