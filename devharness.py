import json
from dataclasses import dataclass

from gvas import GVASFile, DeserializeError
from gvas import GameVersion, CompressionType
from gvas.utils import *

from test_utilities import compare_binary_files


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
]


# this one requires HINTS implementation.
# There is a 16-byte GUID hiding anonymously as a struct_property in a map_property
# See gvas/tests/common/palworld.rs in hints() hashmap for testing sequence
# test_file_list = ["resources/test/palworld_zlib_twice.sav"]  # Working!

game_version = GameVersion.DEFAULT
compression = CompressionType.NONE

# test_file_list = ["resources/test/palworld_zlib.sav"]  # working!
# game_version = GameVersion.PALWORLD
# compression = CompressionType.ZLIB
# SerializationTools.hints = {
#     "worldSaveData.StructProperty.MapObjectSpawnerInStageSaveData.MapProperty.Value.StructProperty.SpawnerDataMapByLevelObjectInstanceId.MapProperty.Key.StructProperty": "Guid",
#     "worldSaveData.StructProperty.BaseCampSaveData.MapProperty.Key.StructProperty": "Guid",
#     "worldSaveData.StructProperty.GroupSaveDataMap.MapProperty.Key.StructProperty": "Guid",
# }

# test_file_list = ["resources/test/palworld_zlib_twice.sav"]  # working!
# game_version = GameVersion.PALWORLD
# compression = CompressionType.ZLIB_TWICE
# SerializationTools.hints = {
#     "worldSaveData.StructProperty.MapObjectSpawnerInStageSaveData.MapProperty.Value.StructProperty.SpawnerDataMapByLevelObjectInstanceId.MapProperty.Key.StructProperty": "Guid",
#     "worldSaveData.StructProperty.BaseCampSaveData.MapProperty.Key.StructProperty": "Guid",
#     "worldSaveData.StructProperty.GroupSaveDataMap.MapProperty.Key.StructProperty": "Guid",
# }

# there are some "BIN" files:
#   features_01.bin, -- custom struct @ FSDEventRewardsSave.StructProperty.EventsSeen.SetProperty.StructProperty
#   regression_01.bin,  -- custom struct @ FSDEventRewardsSave.StructProperty.EventsSeen.SetProperty.StructProperty
#   text_property_noarray.bin -- SaveGameData.StructProperty.QuestsStatus.ArrayProperty.QuestsStatus.ShortDescription.TextProperty
# test_file_list = ["resources/test/SaveSlot_03.bin"]  # Working!


# always a quick retest
# test_file_list = ["Islands of Insight Example.sav"]  # working!
# test_file_list = ["resources/test/vector2d.sav"]
# test_file_list = ["resources/test/Delegate.sav"]
# test_file_list = ["resources/test/assert_failed.sav"]
# test_file_list = ["resources/test/component8.sav"]

for test_file in test_file_list:
    # print(f"Loading {test_file}")
    # Open and read a save file
    gvas_file = None
    with open(test_file, "rb") as f:
        # print(f"loading file with target: {game_version}")
        try:
            gvas_file, decompressed_data = GVASFile.read(f, game_version, compression)
        except Exception as e:
            print(f"Failed to load {test_file}: {e}")
            continue

    # hack to test JSON conversion
    json_file = f"{test_file}.json"
    with open(json_file, "w") as f:
        json_content = json.dumps(gvas_file, cls=EnhancedJSONEncoder, indent=2)
        f.write(json_content)

    if compression != CompressionType.NONE:
        decompressed_data_file = f"{test_file}.decompressed"
        # print(f"Saving decompressed data {decompressed_data_file}")
        with open(decompressed_data_file, "wb") as f:
            f.write(decompressed_data.getvalue())

    # dump binary to work toward idempotence for read, write, rinse and repeat
    output_file = f"{test_file}.idempotent"
    uncompressed_output_file = f"{test_file}.decompressed.idempotent"
    # print(f"Writing {output_file}")
    with open(output_file, "wb") as f:
        gvas_file.write(f, game_version, compression, uncompressed_output_file)

    compare_binary_files(test_file, output_file)
