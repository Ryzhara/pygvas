import json
from xml.etree.ElementTree import indent

import gvas
from gvas import GVASFile, DeserializeError
from gvas import GameVersion, CompressionType
from gvas.utils import *

from test_utilities import compare_binary_files
from tests.common.utils import test_gvas_file

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
# test_file_list = ["resources/test/enum_array.sav"]
# test_file_list = ["resources/test/assert_failed.sav"]
# test_file_list = ["resources/test/component8.sav"]
# test_file_list = ["resources/test/ro_64bit_fav.sav"]


def test_gvas_file(test_file: str):
    # Open and read a .sav file
    gvas_file = None
    with open(test_file, "rb") as f:
        # print(f"loading file with target: {game_version}")
        try:
            gvas_file, decompressed_data = GVASFile.read(f, game_version, compression)
        except Exception as e:
            print(f"Failed to load {test_file}: {e}")
            raise e

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

    # create json the old fashioned way
    json_file = f"{test_file}.json"
    json_content = json.dumps(gvas_file, cls=EnhancedJSONEncoder, indent=2)
    with open(json_file, "w") as f:
        f.write(json_content)

    # create json with pydantic
    pydantic_json_file = f"{test_file}.pydantic.json"
    from pydantic import TypeAdapter

    gvas_file_adaptor = TypeAdapter(GVASFile)
    gvas_file_dict = gvas_file_adaptor.dump_python(gvas_file, exclude_none=True)
    pydantic_json_content = json.dumps(gvas_file_dict, indent=2)

    # by using @field_serializer("values") decorators and the exclude_none=True
    # setting we don't need EnhancedJSONEncoder
    # pydantic_json_content2 = json.dumps(
    #     gvas_file_dict, cls=EnhancedJSONEncoder, indent=2
    # )
    # assert pydantic_json_content == pydantic_json_content2

    # json_content = gvas_file_adaptor.dump_json(gvas_file, indent=2)
    with open(pydantic_json_file, "w") as f:
        f.write(pydantic_json_content)

    compare_binary_files(json_file, pydantic_json_file)

    # lets test the round tripo
    with open(pydantic_json_file, "r") as f:
        pydantic_json_content_dict = json.load(f)

    # print(type(pydantic_json_content_dict))

    new_gvas = gvas_file_adaptor.validate_python(pydantic_json_content_dict)
    # print(type(new_gvas))

    # now write it back out
    output_file_too = f"{test_file}.idempotent.too"
    with open(output_file_too, "wb") as f:
        gvas_file.write(f, game_version, compression)

    compare_binary_files(output_file_too, output_file)

    # assert new_gvas == gvas_file
    def compare_pydantic_objects(obj1: GVASFile, obj2: GVASFile):
        obj1_adaptor = TypeAdapter(GVASFile)
        obj2_adaptor = TypeAdapter(GVASFile)

        dict1 = obj1_adaptor.dump_python(obj1, exclude_none=False)
        dict2 = obj2_adaptor.dump_python(obj2, exclude_none=False)

        print(f"\tGVas objects are{' NOT ' if dict1 != dict2 else ' '}identical")

    compare_pydantic_objects(gvas_file, new_gvas)


for test_file in test_file_list:
    test_gvas_file(test_file)
