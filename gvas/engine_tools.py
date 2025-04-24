# Engine version information
import enum

from pydantic.dataclasses import dataclass

from .gvas_utils import *


# Magic number that appears at the start of every GVAS file
GVAS_MAGIC = b"GVAS"
PLZ_MAGIC = b"PlZ"  # not sure why RUST uses a null byte terminator


class CompressionType(enum.Enum):
    UNKNOWN = 0x00
    # None
    NONE = 0x30
    # Zlib
    ZLIB = 0x31
    # Zlib twice
    ZLIB_TWICE = 0x32
    # Palworld specific compression type; NOT IMPLEMENTED
    PLZ = 0xFF


class GameVersion(enum.Enum):
    UNKNOWN = 0
    DEFAULT = 1
    PALWORLD = 2


# Engine version enum
class EngineVersion(enum.Enum):
    UNKNOWN = (-1, -1)
    # Oldest loadable package
    VER_UE4_OLDEST_LOADABLE_PACKAGE = (4, 0)

    VER_UE4_0 = (4, 0)
    VER_UE4_1 = (4, 1)
    VER_UE4_2 = (4, 2)
    VER_UE4_3 = (4, 3)
    VER_UE4_4 = (4, 4)
    VER_UE4_5 = (4, 5)
    VER_UE4_6 = (4, 6)
    VER_UE4_7 = (4, 7)
    VER_UE4_8 = (4, 8)
    VER_UE4_9 = (4, 9)
    VER_UE4_10 = (4, 10)
    VER_UE4_11 = (4, 11)
    VER_UE4_12 = (4, 12)
    VER_UE4_13 = (4, 13)
    VER_UE4_14 = (4, 14)
    VER_UE4_15 = (4, 15)
    VER_UE4_16 = (4, 16)
    VER_UE4_17 = (4, 17)
    VER_UE4_18 = (4, 18)
    VER_UE4_19 = (4, 19)
    VER_UE4_20 = (4, 20)
    VER_UE4_21 = (4, 21)
    VER_UE4_22 = (4, 22)
    VER_UE4_23 = (4, 23)
    VER_UE4_24 = (4, 24)
    VER_UE4_25 = (4, 25)
    VER_UE4_26 = (4, 26)
    VER_UE4_27 = (4, 27)

    VER_UE5_0 = (5, 0)
    VER_UE5_1 = (5, 1)
    VER_UE5_2 = (5, 2)

    # The newest specified version of the Unreal Engine.
    VER_UE4_AUTOMATIC_VERSION = (4, 27)
    # Version plus one
    VER_UE4_AUTOMATIC_VERSION_PLUS_ONE = (4, 28)


# Stores UE4 version in which the GVAS file was saved
@dataclass
class FEngineVersion:
    major: int = 0  # u16 Major version number.
    minor: int = 0  # u16 Minor version number.
    patch: int = 0  # u16 Patch version number.
    change_list: int = 0  # u32 Build id.
    branch: str = "un.known"  # String Build id string.

    def read(self, stream: BinaryIO) -> "FEngineVersion":
        self.major = read_uint16(stream)
        self.minor = read_uint16(stream)
        self.patch = read_uint16(stream)
        self.change_list = read_uint32(stream)
        self.branch = read_string(stream)
        return self

    def write(self, stream: BinaryIO) -> int:
        bytes_written = 0
        bytes_written += write_uint16(stream, self.major)
        bytes_written += write_uint16(stream, self.minor)
        bytes_written += write_uint16(stream, self.patch)
        bytes_written += write_uint32(stream, self.change_list)
        bytes_written += write_string(stream, self.branch)
        return bytes_written


# ============================================
# Custom serialization version for changes made in Dev-Editor stream.
class FEditorObjectVersion(enum.IntEnum):

    @property
    def friendly_name(self) -> str:
        return FEditorObjectVersion.__name__

    @property
    def custom_version_guid(self) -> uuid:
        return guid_from_uint32x4(0xE4B068ED, 0xF49442E9, 0xA231DA0B, 0x2E46BB41)

    @property
    def version_mappings(self):
        return {
            EngineVersion.VER_UE4_AUTOMATIC_VERSION: FEditorObjectVersion.LatestVersion,
            EngineVersion.VER_UE4_AUTOMATIC_VERSION_PLUS_ONE: FEditorObjectVersion.VersionPlusOne,
            EngineVersion.VER_UE4_26: FEditorObjectVersion.SkeletalMeshSourceDataSupport16bitOfMaterialNumber,
            EngineVersion.VER_UE4_25: FEditorObjectVersion.SkeletalMeshMoveEditorSourceDataToPrivateAsset,
            EngineVersion.VER_UE4_24: FEditorObjectVersion.SkeletalMeshBuildRefactor,
            EngineVersion.VER_UE4_23: FEditorObjectVersion.RemoveLandscapeHoleMaterial,
            EngineVersion.VER_UE4_22: FEditorObjectVersion.MeshDescriptionRemovedHoles,
            EngineVersion.VER_UE4_21: FEditorObjectVersion.MeshDescriptionNewAttributeFormat,
            EngineVersion.VER_UE4_20: FEditorObjectVersion.SerializeInstancedStaticMeshRenderData,
            EngineVersion.VER_UE4_19: FEditorObjectVersion.AddedMorphTargetSectionIndices,
            EngineVersion.VER_UE4_17: FEditorObjectVersion.GatheredTextEditorOnlyPackageLocId,
            EngineVersion.VER_UE4_16: FEditorObjectVersion.MaterialThumbnailRenderingChanges,
            EngineVersion.VER_UE4_15: FEditorObjectVersion.AddedInlineFontFaceAssets,
            EngineVersion.VER_UE4_14: FEditorObjectVersion.AddedFontFaceAssets,
            EngineVersion.VER_UE4_13: FEditorObjectVersion.SplineComponentCurvesInStruct,
            EngineVersion.VER_UE4_12: FEditorObjectVersion.GatheredTextPackageCacheFixesV1,
            EngineVersion.VER_UE4_OLDEST_LOADABLE_PACKAGE: FEditorObjectVersion.BeforeCustomVersionWasAdded,
        }

    # Before any version changes were made
    # Introduced: ObjectVersion.VER_UE4_OLDEST_LOADABLE_PACKAGE
    BeforeCustomVersionWasAdded = 0

    # Localizable text gathered and stored in packages is now flagged with a localizable text gathering process version
    # Introduced: ObjectVersion.VER_UE4_STREAMABLE_TEXTURE_AABB
    GatheredTextProcessVersionFlagging = enum.auto()

    # Fixed several issues with the gathered text cache stored in package headers
    # Introduced: ObjectVersion.VER_UE4_NAME_HASHES_SERIALIZED
    GatheredTextPackageCacheFixesV1 = enum.auto()

    # Added support for "root" meta-data (meta-data not associated with a particular object in a package)
    # Introduced: ObjectVersion.VER_UE4_INSTANCED_STEREO_UNIFORM_REFACTOR
    RootMetaDataSupport = enum.auto()

    # Fixed issues with how Blueprint bytecode was cached
    # Introduced: ObjectVersion.VER_UE4_INSTANCED_STEREO_UNIFORM_REFACTOR
    GatheredTextPackageCacheFixesV2 = enum.auto()

    # Updated FFormatArgumentData to allow variant data to be marshaled from a BP into C++
    # Introduced: ObjectVersion.VER_UE4_INSTANCED_STEREO_UNIFORM_REFACTOR
    TextFormatArgumentDataIsVariant = enum.auto()

    # Changes to SplineComponent
    # Introduced: ObjectVersion.VER_UE4_INSTANCED_STEREO_UNIFORM_REFACTOR
    SplineComponentCurvesInStruct = enum.auto()

    # Updated ComboBox to support toggling the menu open, better controller support
    # Introduced: ObjectVersion.VER_UE4_COMPRESSED_SHADER_RESOURCES
    ComboBoxControllerSupportUpdate = enum.auto()

    # Refactor mesh editor materials
    # Introduced: ObjectVersion.VER_UE4_COMPRESSED_SHADER_RESOURCES
    RefactorMeshEditorMaterials = enum.auto()

    # Added UFontFace assets
    # Introduced: ObjectVersion.VER_UE4_TemplateIndex_IN_COOKED_EXPORTS
    AddedFontFaceAssets = enum.auto()

    # Add UPROPERTY for TMap of Mesh section, so the serialize will be done normally (and export to text will work correctly)
    # Introduced: ObjectVersion.VER_UE4_ADDED_SEARCHABLE_NAMES
    UPropertryForMeshSection = enum.auto()

    # Update the schema of all widget blueprints to use the WidgetGraphSchema
    # Introduced: ObjectVersion.VER_UE4_ADDED_SEARCHABLE_NAMES
    WidgetGraphSchema = enum.auto()

    # Added a specialized content slot to the background blur widget
    # Introduced: ObjectVersion.VER_UE4_ADDED_SEARCHABLE_NAMES
    AddedBackgroundBlurContentSlot = enum.auto()

    # Updated UserDefinedEnums to have stable keyed display names
    # Introduced: ObjectVersion.VER_UE4_ADDED_SEARCHABLE_NAMES
    StableUserDefinedEnumDisplayNames = enum.auto()

    # Added "Inline" option to UFontFace assets
    # Introduced: ObjectVersion.VER_UE4_ADDED_SEARCHABLE_NAMES
    AddedInlineFontFaceAssets = enum.auto()

    # Fix a serialization issue with static mesh FMeshSectionInfoMap FProperty
    # Introduced: ObjectVersion.VER_UE4_ADDED_SEARCHABLE_NAMES
    UPropertryForMeshSectionSerialize = enum.auto()

    # Adding a version bump for the new fast widget construction in case of problems.
    # Introduced: ObjectVersion.VER_UE4_64BIT_EXPORTMAP_SERIALSIZES
    FastWidgetTemplates = enum.auto()

    # Update material thumbnails to be more intelligent on default primitive shape for certain material types
    # Introduced: ObjectVersion.VER_UE4_64BIT_EXPORTMAP_SERIALSIZES
    MaterialThumbnailRenderingChanges = enum.auto()

    # Introducing a new clipping system for Slate/UMG
    # Introduced: ObjectVersion.VER_UE4_ADDED_SWEEP_WHILE_WALKING_FLAG
    NewSlateClippingSystem = enum.auto()

    # MovieScene Meta Data added as native Serialization
    # Introduced: ObjectVersion.VER_UE4_ADDED_SWEEP_WHILE_WALKING_FLAG
    MovieSceneMetaDataSerialization = enum.auto()

    # Text gathered from properties now adds two variants: a version without the package localization ID (for use at runtime), and a version with it (which is editor-only)
    # Introduced: ObjectVersion.VER_UE4_ADDED_SWEEP_WHILE_WALKING_FLAG
    GatheredTextEditorOnlyPackageLocId = enum.auto()

    # Added AlwaysSign to FNumberFormattingOptions
    # Introduced: ObjectVersion.VER_UE4_ADDED_SOFT_OBJECT_PATH
    AddedAlwaysSignNumberFormattingOption = enum.auto()

    # Added additional objects that must be serialized as part of this new material feature
    # Introduced: ObjectVersion.VER_UE4_ADDED_PACKAGE_SUMMARY_LOCALIZATION_ID
    AddedMaterialSharedInputs = enum.auto()

    # Added morph target section indices
    # Introduced: ObjectVersion.VER_UE4_ADDED_PACKAGE_SUMMARY_LOCALIZATION_ID
    AddedMorphTargetSectionIndices = enum.auto()

    # Serialize the instanced static mesh render data, to avoid building it at runtime
    # Introduced: ObjectVersion.VER_UE4_ADDED_PACKAGE_SUMMARY_LOCALIZATION_ID
    SerializeInstancedStaticMeshRenderData = enum.auto()

    # Change to MeshDescription serialization (moved to release)
    # Introduced: ObjectVersion.VER_UE4_ADDED_PACKAGE_SUMMARY_LOCALIZATION_ID
    MeshDescriptionNewSerializationMovedToRelease = enum.auto()

    # New format for mesh description attributes
    # Introduced: ObjectVersion.VER_UE4_ADDED_PACKAGE_SUMMARY_LOCALIZATION_ID
    MeshDescriptionNewAttributeFormat = enum.auto()

    # Switch root component of SceneCapture actors from MeshComponent to SceneComponent
    # Introduced: ObjectVersion.VER_UE4_FIX_WIDE_STRING_CRC
    ChangeSceneCaptureRootComponent = enum.auto()

    # StaticMesh serializes MeshDescription instead of RawMesh
    # Introduced: ObjectVersion.VER_UE4_FIX_WIDE_STRING_CRC
    StaticMeshDeprecatedRawMesh = enum.auto()

    # MeshDescriptionBulkData contains a uuid used as a DDC key
    # Introduced: ObjectVersion.VER_UE4_FIX_WIDE_STRING_CRC
    MeshDescriptionBulkDatauuid = enum.auto()

    # Change to MeshDescription serialization (removed FMeshPolygon::HoleContours)
    # Introduced: ObjectVersion.VER_UE4_FIX_WIDE_STRING_CRC
    MeshDescriptionRemovedHoles = enum.auto()

    # Change to the WidgetCompoent WindowVisibilty default value
    # Introduced: ObjectVersion.VER_UE4_FIX_WIDE_STRING_CRC
    ChangedWidgetComponentWindowVisibilityDefault = enum.auto()

    # Avoid keying culture invariant display strings during serialization to avoid non-deterministic cooking issues
    # Introduced: ObjectVersion.VER_UE4_FIX_WIDE_STRING_CRC
    CultureInvariantTextSerializationKeyStability = enum.auto()

    # Change to UScrollBar and UScrollBox thickness property (removed implicit padding of 2, so thickness value must be incremented by 4).
    # Introduced: ObjectVersion.VER_UE4_FIX_WIDE_STRING_CRC
    ScrollBarThicknessChange = enum.auto()

    # Deprecated LandscapeHoleMaterial
    # Introduced: ObjectVersion.VER_UE4_FIX_WIDE_STRING_CRC
    RemoveLandscapeHoleMaterial = enum.auto()

    # MeshDescription defined by triangles instead of arbitrary polygons
    # Introduced: ObjectVersion.VER_UE4_FIX_WIDE_STRING_CRC
    MeshDescriptionTriangles = enum.auto()

    # Add weighted area and angle when computing the normals
    # Introduced: ObjectVersion.VER_UE4_ADDED_PACKAGE_OWNER
    ComputeWeightedNormals = enum.auto()

    # SkeletalMesh now can be rebuild in editor = enum.auto() no more need to re-import
    # Introduced: ObjectVersion.VER_UE4_ADDED_PACKAGE_OWNER
    SkeletalMeshBuildRefactor = enum.auto()

    # Move all SkeletalMesh source data into a private uasset in the same package has the skeletalmesh
    # Introduced: ObjectVersion.VER_UE4_ADDED_PACKAGE_OWNER
    SkeletalMeshMoveEditorSourceDataToPrivateAsset = enum.auto()

    # Parse text only if the number is inside the limits of its type
    # Introduced: ObjectVersion.VER_UE4_NON_OUTER_PACKAGE_IMPORT
    NumberParsingOptionsNumberLimitsAndClamping = enum.auto()

    # Make sure we can have more than 255 material in the skeletal mesh source data
    # Introduced: ObjectVersion.VER_UE4_NON_OUTER_PACKAGE_IMPORT
    SkeletalMeshSourceDataSupport16bitOfMaterialNumber = enum.auto()

    # Introduced: ObjectVersion.VER_UE4_AUTOMATIC_VERSION_PLUS_ONE
    VersionPlusOne = enum.auto()
    # Introduced: ObjectVersion.VER_UE4_AUTOMATIC_VERSION
    LatestVersion = enum.auto()


# ============================================
# Custom serialization version for changes made in //UE5/Release-* stream
class FUE5ReleaseStreamObjectVersion(enum.IntEnum):

    @property
    def friendly_name(self) -> str:
        return FEditorObjectVersion.__name__

    @property
    def custom_version_guid(self) -> uuid:
        return guid_from_uint32x4(0xD89B5E42, 0x24BD4D46, 0x8412ACA8, 0xDF641779)

    @property
    def version_mappings(self):
        return {}

    # Before any version changes were made
    BeforeCustomVersionWasAdded = 0

    # Added Lumen reflections to new reflection enum, changed defaults
    ReflectionMethodEnum = enum.auto()

    # Serialize HLOD info in WorldPartitionActorDesc
    WorldPartitionActorDescSerializeHLODInfo = enum.auto()

    # Removing Tessellation from materials and meshes.
    RemovingTessellation = enum.auto()

    # LevelInstance serialize runtime behavior
    LevelInstanceSerializeRuntimeBehavior = enum.auto()

    # Refactoring Pose Asset runtime data structures
    PoseAssetRuntimeRefactor = enum.auto()

    # Serialize the folder path of actor descs
    WorldPartitionActorDescSerializeActorFolderPath = enum.auto()

    # Change hair strands vertex format
    HairStrandsVertexFormatChange = enum.auto()

    # Added max linear and angular speed to Chaos bodies
    AddChaosMaxLinearAngularSpeed = enum.auto()

    # PackedLevelInstance version
    PackedLevelInstanceVersion = enum.auto()

    # PackedLevelInstance bounds fix
    PackedLevelInstanceBoundsFix = enum.auto()

    # Custom property anim graph nodes (linked anim graphs = enum.auto() control rig etc.) now use optional pin manager
    CustomPropertyAnimGraphNodesUseOptionalPinManager = enum.auto()

    # Add native double and int64 support to FFormatArgumentData
    TextFormatArgumentData64bitSupport = enum.auto()

    # Material layer stacks are no longer considered 'static parameters'
    MaterialLayerStacksAreNotParameters = enum.auto()

    # CachedExpressionData is moved from UMaterial to UMaterialInterface
    MaterialInterfaceSavedCachedData = enum.auto()

    # Add support for multiple cloth deformer LODs to be able to raytrace cloth with a different LOD than the one it is rendered with
    AddClothMappingLODBias = enum.auto()

    # Add support for different external actor packaging schemes
    AddLevelActorPackagingScheme = enum.auto()

    # Add support for linking to the attached parent actor in WorldPartitionActorDesc
    WorldPartitionActorDescSerializeAttachParent = enum.auto()

    # Converted AActor GridPlacement to bIsSpatiallyLoaded flag
    ConvertedActorGridPlacementToSpatiallyLoadedFlag = enum.auto()

    # Fixup for bad default value for GridPlacement_DEPRECATED
    ActorGridPlacementDeprecateDefaultValueFixup = enum.auto()

    # PackedLevelActor started using FWorldPartitionActorDesc (not currently checked against but added as a security)
    PackedLevelActorUseWorldPartitionActorDesc = enum.auto()

    # Add support for actor folder objects
    AddLevelActorFolders = enum.auto()

    # Remove FSkeletalMeshLODModel bulk datas
    RemoveSkeletalMeshLODModelBulkDatas = enum.auto()

    # Exclude brightness from the EncodedHDRCubemap = enum.auto()
    ExcludeBrightnessFromEncodedHDRCubemap = enum.auto()

    # Unified volumetric cloud component quality sample count slider between main and reflection views for consistency
    VolumetricCloudSampleCountUnification = enum.auto()

    # Pose asset uuid generated from source AnimationSequence
    PoseAssetRawDatauuid = enum.auto()

    # Convolution bloom now take into account FPostProcessSettings::BloomIntensity for scatter dispersion.
    ConvolutionBloomIntensity = enum.auto()

    # Serialize FHLODSubActors instead of Fuuids in WorldPartition HLODActorDesc
    WorldPartitionHLODActorDescSerializeHLODSubActors = enum.auto()

    # Large Worlds - serialize double types as doubles
    LargeWorldCoordinates = enum.auto()

    # Deserialize old BP float&double types as real numbers for pins
    BlueprintPinsUseRealNumbers = enum.auto()

    # Changed shadow defaults for directional light components, version needed to not affect old things
    UpdatedDirectionalLightShadowDefaults = enum.auto()

    # Refresh geometry collections that had not already generated convex bodies.
    GeometryCollectionConvexDefaults = enum.auto()

    # Add faster damping calculations to the cloth simulation and rename previous Damping parameter to LocalDamping.
    ChaosClothFasterDamping = enum.auto()

    # Serialize LandscapeActoruuid in FLandscapeActorDesc sub class.
    WorldPartitionLandscapeActorDescSerializeLandscapeActoruuid = enum.auto()

    # add inertia tensor and rotation of mass to convex
    AddedInertiaTensorAndRotationOfMassAddedToConvex = enum.auto()

    # Storing inertia tensor as vec3 instead of matrix.
    ChaosInertiaConvertedToVec3 = enum.auto()

    # For Blueprint real numbers = enum.auto() ensure that legacy float data is serialized as single-precision
    SerializeFloatPinDefaultValuesAsSinglePrecision = enum.auto()

    # Upgrade the BlendMasks array in existing LayeredBoneBlend nodes
    AnimLayeredBoneBlendMasks = enum.auto()

    # Uses RG11B10 format to store the encoded reflection capture data on mobile
    StoreReflectionCaptureEncodedHDRDataInRG11B10Format = enum.auto()

    # Add WithSerializer type trait and implementation for FRawAnimSequenceTrack
    RawAnimSequenceTrackSerializer = enum.auto()

    # Removed font from FEditableTextBoxStyle = enum.auto() and added FTextBlockStyle instead.
    RemoveDuplicatedStyleInfo = enum.auto()

    # Added member reference to linked anim graphs
    LinkedAnimGraphMemberReference = enum.auto()

    # Changed default tangent behavior for new dynamic mesh components
    DynamicMeshComponentsDefaultUseExternalTangents = enum.auto()

    # Added resize methods to media capture
    MediaCaptureNewResizeMethods = enum.auto()

    # Function data stores a map from work to debug operands
    RigVMSaveDebugMapInGraphFunctionData = enum.auto()

    # Changed default Local Exposure Contrast Scale from 1.0 to 0.8
    LocalExposureDefaultChangeFrom1 = enum.auto()

    # Serialize bActorIsListedInSceneOutliner in WorldPartitionActorDesc
    WorldPartitionActorDescSerializeActorIsListedInSceneOutliner = enum.auto()

    # Disabled opencolorio display configuration by default
    OpenColorIODisabledDisplayConfigurationDefault = enum.auto()

    # Serialize ExternalDataLayerAsset in WorldPartitionActorDesc
    WorldPartitionExternalDataLayers = enum.auto()

    # Fix Chaos Cloth fictitious angular scale bug that requires existing parameter rescaling.
    ChaosClothFictitiousAngularVelocitySubframeFix = enum.auto()

    # Store physics thread particles data in single precision
    SinglePrecisonParticleDataPT = enum.auto()

    # Orthographic Near and Far Plane Auto-resolve enabled by default
    OrthographicAutoNearFarPlane = enum.auto()


ENGINE_VERSION_CLASSES = Union[FEditorObjectVersion | FUE5ReleaseStreamObjectVersion]


# ============================================
# Don NOT make this @dataclass because then our class variable syntax is wrong. ;)
class EngineVersionTool:
    """
    This class corresponds to the Rust package use of "options" and scoped property stacks.
    It is never instantiated and avoids cluttering signatures with mostly unused parameters.

    If your file fails while parsing with a DeserializeError::MissingHint error you need hints.
    When a struct is stored inside ArrayProperty/SetProperty/MapProperty in GvasFile it does not
    contain type annotations. This means that a library parsing the file must know the type
    beforehand. That’s why you need hints.
    """

    custom_versions: dict[str, int] = {}
    engine_major: int = 4
    engine_minor: int = 0

    @classmethod
    def set_engine_version(cls, engine_major: int, engine_minor: int) -> None:
        cls.engine_major = engine_major
        cls.engine_minor = engine_minor

    @classmethod
    def version_is_at_least(cls, engine_major: int, engine_minor: int):
        return engine_major >= cls.engine_major and engine_minor >= cls.engine_minor

    def version_is_less_than(cls, engine_major: int, engine_minor: int):
        return engine_major < cls.engine_major and engine_minor < cls.engine_minor

    # initialization requirements
    @classmethod
    def set_custom_versions(cls, custom_versions: dict[str, int]) -> None:
        cls.custom_versions = custom_versions

    @classmethod
    def supports_version(cls, required_version: ENGINE_VERSION_CLASSES) -> bool:
        guid_key_str = guid_to_str(required_version.custom_version_guid)
        supported_version = cls.custom_versions.get(guid_key_str, 0)
        return supported_version >= required_version.value
