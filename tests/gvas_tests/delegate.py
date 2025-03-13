"""
Expected values for delegate test
"""
from gvas.gvas_file import GvasFile
from gvas.properties.property import Property
from gvas.properties.delegate_property import (
    DelegateProperty, Delegate,
    MulticastInlineDelegateProperty, MulticastSparseDelegateProperty,
    MulticastScriptDelegate
)

def expected() -> GvasFile:
    """
    Return the expected GvasFile for delegate.sav
    
    Returns:
        The expected GvasFile
    """
    file = GvasFile()
    
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
    file.properties["DelegateProperty"] = Property(
        type="DelegateProperty",
        value=DelegateProperty(
            value=Delegate(
                object="/Game/TestObject",
                function_name="TestFunction"
            )
        )
    )
    
    # Add multicast inline delegate property
    delegates = [
        Delegate(object="/Game/TestObject1", function_name="TestFunction1"),
        Delegate(object="/Game/TestObject2", function_name="TestFunction2")
    ]
    
    file.properties["MulticastInlineDelegateProperty"] = Property(
        type="MulticastInlineDelegateProperty",
        value=MulticastInlineDelegateProperty(
            value=MulticastScriptDelegate(delegates=delegates)
        )
    )
    
    # Add multicast sparse delegate property
    file.properties["MulticastSparseDelegateProperty"] = Property(
        type="MulticastSparseDelegateProperty",
        value=MulticastSparseDelegateProperty(
            value=MulticastScriptDelegate(delegates=delegates)
        )
    )
    
    return file 