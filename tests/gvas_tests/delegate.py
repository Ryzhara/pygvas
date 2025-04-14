"""
Expected values for delegate test
"""

from gvas.gvas_file import GVASFile
from gvas.properties.property_base import PropertyFactory
from gvas.properties.delegate_property import (
    DelegateProperty,
    Delegate,
    MulticastInlineDelegateProperty,
    MulticastSparseDelegateProperty,
    MulticastScriptDelegate,
)


def expected() -> GVASFile:
    """
    Return the expected GVASFile for delegate.sav

    Returns:
        The expected GVASFile
    """
    file = GVASFile()

    # Set header values
    file.save_game_version = 1
    file.package_version = 522
    file.engine_version_major = 4
    file.engine_version_minor = 27
    file.engine_version_patch = 2
    file.engine_version_build = 0
    file.engine_version = "4.27.2-0"
    file.custom_format_version = 0
    file.custom_format_data = {}

    # Add delegate property
    file.properties["DelegateProperty"] = PropertyFactory(
        type="DelegateProperty",
        value=DelegateProperty(
            value=Delegate(object="/Game/TestObject", function_name="TestFunction")
        ),
    )

    # Add multicast inline delegate property
    delegates = [
        Delegate(object="/Game/TestObject1", function_name="TestFunction1"),
        Delegate(object="/Game/TestObject2", function_name="TestFunction2"),
    ]

    file.properties["MulticastInlineDelegateProperty"] = PropertyFactory(
        type="MulticastInlineDelegateProperty",
        value=MulticastInlineDelegateProperty(
            value=MulticastScriptDelegate(delegates=delegates)
        ),
    )

    # Add multicast sparse delegate property
    file.properties["MulticastSparseDelegateProperty"] = PropertyFactory(
        type="MulticastSparseDelegateProperty",
        value=MulticastSparseDelegateProperty(
            value=MulticastScriptDelegate(delegates=delegates)
        ),
    )

    return file
