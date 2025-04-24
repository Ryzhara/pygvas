from pydantic import ValidationError
from pydantic.dataclasses import dataclasses
from pydantic import TypeAdapter
from pydantic import BaseModel
import enum
import json

from gvas.gvas_file import GVASFile, GameFileFormat
from gvas.engine_tools import GameVersion, CompressionType
from gvas.gvas_utils import *
from test_utilities import compare_binary_files


# ============================================
class EnhancedJSONEncoder(json.JSONEncoder):

    def default(self, obj):

        def is_not_empty(value):
            # if isinstance(value, (str, type(None))):
            #     return not not value
            if isinstance(value, (type(None))):
                return not not value

            if isinstance(value, uuid.UUID) and value == ZERO_GUID:
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


test_file_list = [
    "resources/test/islands_of_insight.sav",
    "resources/test/assert_failed.sav",
    "resources/test/component8.sav",
    "resources/test/Delegate.sav",
    "resources/test/Options.sav",
    "resources/test/Profile_0.sav",
    "resources/test/enum_array.sav",
    "resources/test/package_version_525.sav",
    "resources/test/package_version_524.sav",
    "resources/test/Slot1.sav",
    "resources/test/Slot2.sav",
    "resources/test/Slot3.sav",
    "resources/test/transform.sav",
    "resources/test/ro_64bit_fav.sav",
    "resources/test/SaveSlot_03.sav",
    "resources/test/vector2d.sav",
    "resources/test/regression_01.bin",
    #   regression_01.bin once had an error but now is working without hings?
    #   -- custom struct @ FSDEventRewardsSave.StructProperty.EventsSeen.SetProperty.StructProperty
]


# this one requires HINTS implementation.
# There is a 16-byte GUID hiding anonymously as a struct_property in a map_property
# See gvas/tests/common/palworld.rs in hints() hashmap for testing sequence
# test_file_list = ["resources/test/palworld_zlib_twice.sav"]  # Working!

# game_version = GameVersion.DEFAULT
# compression = CompressionType.NONE

# # game_version = GameVersion.PALWORLD
# # compression = CompressionType.ZLIB
# test_file_list = ["resources/test/palworld_zlib.sav"]  # working!

#   text_property_noarray.bin -- SaveGameData.StructProperty.QuestsStatus.ArrayProperty.QuestsStatus.ShortDescription.TextProperty
#  test_file_list = ["resources/test/text_property_noarray.bin"]  # Working!
# StructProperty["TrackedQuestsNames"] = NameProperty(value="QU91_InvestigateTower_B2")


# test_file_list = ["resources/test/palworld_zlib_twice.sav"]  # working!
# # game_version = GameVersion.PALWORLD
# # compression = CompressionType.ZLIB_TWICE
# ContextScopeTracker.hints = {
#     "worldSaveData.StructProperty.MapObjectSpawnerInStageSaveData.MapProperty.Value.StructProperty.SpawnerDataMapByLevelObjectInstanceId.MapProperty.Key.StructProperty": "Guid",
#     "worldSaveData.StructProperty.BaseCampSaveData.MapProperty.Key.StructProperty": "Guid",
#     "worldSaveData.StructProperty.GroupSaveDataMap.MapProperty.Key.StructProperty": "Guid",
# }

# there are some "BIN" files:
#   features_01.bin, -- custom struct @ FSDEventRewardsSave.StructProperty.EventsSeen.SetProperty.StructProperty
test_file_list = ["resources/test/features_01.bin"]
ContextScopeTracker.hints = {
    "SeasonSave.StructProperty.Seasons.MapProperty.Key.StructProperty": "Guid",
    "SeasonSave.StructProperty.Seasons.MapProperty.Value.StructProperty.CompletedSpecialChallenges.MapProperty.Key.StructProperty": "Guid",
    "UnLockedMissionParameters.MapProperty.Key.StructProperty": "Guid",
    "ItemUpgradeSelections.MapProperty.Key.StructProperty": "Guid",
    "ItemUpgradeLoadouts.ArrayProperty.Loadout.MapProperty.Key.StructProperty": "Guid",
    "EnemiesKilled.MapProperty.Key.StructProperty": "Guid",
    "UnlockedItemSkins.MapProperty.Key.StructProperty": "Guid",
    "Resources.StructProperty.OwnedResources.MapProperty.Key.StructProperty": "Guid",
    "FSDEventRewardsSave.StructProperty.EventsSeen.SetProperty.StructProperty": "Guid",
    "GameDLCSave.StructProperty.AnnouncedIDs.SetProperty.StructProperty": "Guid",
    "Drinks.StructProperty.UnlockedDrinks.SetProperty.StructProperty": "Guid",
    "UnlockedItemSkins.MapProperty.Value.StructProperty.Skins.SetProperty.StructProperty": "Guid",
    "UnlockedPickaxeParts.SetProperty.StructProperty": "Guid",
    "MinersManualKnownObjects.SetProperty.StructProperty": "Guid",
}


# always a quick retest
# test_file_list = ["resources/test/assert_failed.sav"]
# test_file_list = ["resources/test/Options.sav"]
# test_file_list = ["resources/test/Delegate.sav"]
# test_file_list = ["resources/test/Slot1.sav"]
# test_file_list = ["resources/test/vector2d.sav"]
# test_file_list = ["resources/test/package_version_525.sav"]
# test_file_list = ["resources/test/islands_of_insight.sav"]
# test_file_list = ["resources/test/SaveSlot_03.sav"]
# test_file_list = ["resources/test/Profile_0.sav"]
# test_file_list = ["resources/test/Slot2.sav"]
# test_file_list = ["resources/test/component8.sav"]
# test_file_list = ["resources/test/enum_array.sav"]
# test_file_list = ["resources/test/package_version_524.sav"]
# test_file_list = ["resources/test/Slot3.sav"]
# test_file_list = ["resources/test/transform.sav"]
# test_file_list = ["resources/test/ro_64bit_fav.sav"]
# ABOVE WORKS


def test_gvas_file(test_file: str):
    # Open and read a .sav file
    gvas_file = None
    try:
        gvas_file: GVASFile
        gvas_file, decompressed_data = GVASFile.read_file(test_file)
    except Exception as e:
        print(f"Failed to load {test_file}: {e}")
        raise e

    if gvas_file.game_file_format.compression_type != CompressionType.NONE:
        decompressed_data_file = f"{test_file}.decompressed"
        # print(f"Saving decompressed data {decompressed_data_file}")
        with open(decompressed_data_file, "wb") as f:
            f.write(decompressed_data.getvalue())

    # dump binary to work toward idempotence for read, write, rinse and repeat
    output_file = f"{test_file}.idempotent"
    uncompressed_output_file = f"{test_file}.decompressed.idempotent"
    gvas_file.write_file(output_file, uncompressed_output_file)

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
    new_gvas.write_file(output_file_too, uncompressed_output_file)

    reread_and_rewrite = compare_binary_files(output_file_too, output_file)

    # assert new_gvas == gvas_file
    # def compare_pydantic_objects(obj1: GVASFile, obj2: GVASFile):
    #     obj1_adaptor = TypeAdapter(GVASFile)
    #     obj2_adaptor = TypeAdapter(GVASFile)
    #
    #     dict1 = obj1_adaptor.dump_python(obj1, exclude_none=False)
    #     dict2 = obj2_adaptor.dump_python(obj2, exclude_none=False)
    #
    #     # print(f"\tGVas objects are{' NOT ' if dict1 != dict2 else ' '}identical")
    #
    # pydantic_object_commpare = compare_pydantic_objects(gvas_file, new_gvas)

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
    with open("GVAS File Schema Dump.json", "w") as f:
        json_string = json.dumps(model_json_schema, indent=2)
        f.write(json_string)
    exit(0)

for test_file in test_file_list:
    test_gvas_file(test_file)
