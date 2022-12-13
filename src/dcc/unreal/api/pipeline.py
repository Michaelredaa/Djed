# -*- coding: utf-8 -*-
"""
Documentation:
"""

"""
Description:
"""

# Import Libraries
# ============================================================
import unreal
import os
import json


def createAssetTool():
    """
    To create asset tools helper
    Returns:
    """
    return unreal.AssetToolsHelpers.get_asset_tools()


def buildImportTask(filepath, destination_path, options=None, name=None):
    """
    To build a task for imported asset
    Args:
        filepath (str): the imported asset windows filepath.
        destination_path (str): the unreal path that start with "Game/.../..."
        options (object): object of options to import

    Returns (object): created task object
    """

    if not os.path.isfile(filepath):
        raise WindowsError('File not found: "{}"'.format(filepath))

    task = unreal.AssetImportTask()
    task.filename = filepath
    task.destination_path = destination_path
    if name:
        task.destination_name = name
    task.automated = True  # Avoid dialogs
    task.save = True
    task.replace_existing = True
    task.options = options

    return task


def execteImportTasks(tasks):
    """
    To execute the import tasks
    Args:
        tasks (list): list of tasks

    Returns(list): list of lists of imported objects
    """

    importedAssets = []
    assetTools = createAssetTool()
    assetTools.import_asset_tasks(tasks)

    for task in tasks:
        # task_imported_assets = task.get_editor_property("imported_object_paths")
        task_imported_assets = task.imported_object_paths
        importedAssets.append(task_imported_assets)

    return importedAssets


def buildStaticMeshOptions(**kwargs):
    """
    To creates options for static mesh import
    Returns(object): object with static mesh options

    """

    # unreal.FbxSceneImportOptions()
    options = unreal.FbxImportUI()

    # unreal.FbxImportUI
    options.import_mesh = kwargs.get('import_mesh', True)
    options.import_textures = kwargs.get('import_textures', True)
    options.import_materials = kwargs.get('import_materials', False)
    options.import_as_skeletal = kwargs.get('import_as_skeletal', False)

    # unreal.FbxMeshImportData
    options.static_mesh_import_data.import_translation = unreal.Vector(0.0, 0.0, 0.0)
    options.static_mesh_import_data.import_rotation = unreal.Rotator(90.0, 0.0, 0.0)
    options.static_mesh_import_data.import_uniform_scale = kwargs.get('scale', 1.0)

    # unreal.FbxStaticMeshImportData
    options.static_mesh_import_data.combine_meshes = kwargs.get('combine_meshes', True)
    options.static_mesh_import_data.generate_lightmap_u_vs = kwargs.get('generate_lightmap_u_vs', True)
    options.static_mesh_import_data.auto_generate_collision = kwargs.get('auto_generate_collision', True)
    return options


def buildSKeletalMeshOptions(**kwargs):
    """
    To creates options for skeletal mesh import
    Returns(object): object with skeletal mesh options

    """

    # unreal.FbxSceneImportOptions()

    options = unreal.FbxImportUI()

    # unreal.FbxImportUI
    options.import_mesh = kwargs.get('import_mesh', True)
    options.import_textures = kwargs.get('import_textures', True)
    options.import_materials = kwargs.get('import_materials', False)
    options.import_as_skeletal = kwargs.get('import_as_skeletal', False)

    # unreal.FbxMeshImportData
    options.static_mesh_import_data.import_translation = unreal.Vector(0.0, 0.0, 0.0)
    options.static_mesh_import_data.import_rotation = unreal.Rotator(0.0, 0.0, 0.0)
    options.static_mesh_import_data.import_uniform_scale = kwargs.get('scale', 1.0)

    # unreal.FbxStaticMeshImportData
    options.skeletal_mesh_import_data.import_morph_targets = True
    options.skeletal_mesh_import_data.update_skeleton_reference_pose = False
    return options


def buildAnimationOptions(skeleton_path):
    """
    To creates options for animation mesh import

    @param skeleton_path: (str) Skeleton unreal asset path of the skeleton that will be used to bind the animation
    Returns(object): object with skeletal mesh options

    """

    options = unreal.FbxImportUI()

    # unreal.FbxImportUI
    options.import_animations = True
    options.skeleton = unreal.load_asset(skeleton_path)

    # unreal.FbxMeshImportData
    options.static_mesh_import_data.import_translation = unreal.Vector(0.0, 0.0, 0.0)
    options.static_mesh_import_data.import_rotation = unreal.Rotator(0.0, 0.0, 0.0)
    options.static_mesh_import_data.import_uniform_scale = 1.0

    # unreal.FbxAnimSequenceImportData
    options.anim_sequence_import_data.animation_length = unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME
    options.anim_sequence_import_data.remove_redundant_keys = False
    return options


def importStaticMesh(filepath, destination_path, prefix="ST", **kwargs):
    """
    To import a static mesh to unreal
    Args:
        filepath (str): the imported asset windows filepath.
        destination_path (str): the unreal path that start with "Game/.../..."

    Returns(list): list of lists of imported objects
    :param prefix:
    """

    task = buildImportTask(filepath, destination_path, buildStaticMeshOptions(**kwargs), prefix)
    result = execteImportTasks([task])

    return result


def importSkeletalMesh(filepath, destination_path):
    """
    To import a skeletal mesh to unreal
    Args:
        filepath (str): the imported asset windows filepath.
        destination_path (str): the unreal path that start with "Game/.../..."

    Returns(list): list of lists of imported objects
    """

    task = buildImportTask(filepath, destination_path, buildStaticMeshOptions())
    result = execteImportTasks([task])

    return result


def importAnimation(filepath, destination_path, skeleton_path):
    """
    To import animation from fbx filepath and combine it with skeleton
    Args:
        filepath (str): fbx windows file path
        destination_path (str): unreal destination path for imported fbx meshes
        skeleton_path (str): unreal path of skeleton

    Returns (list): list of lists of imported objects

    """
    task = buildImportTask(filepath, destination_path, buildAnimationOptions(skeleton_path))
    result = execteImportTasks([task])
    return result


def importTexture(filepath, destination_path):
    task = buildImportTask(filepath, destination_path)
    result = execteImportTasks([task])
    return result


def createMaterial(game_material_path):
    """
    To creates material in certain path
    :param game_material_path:
    :return: unreal.Object
    """
    assetTools = createAssetTool()
    material_dir, material_name = game_material_path.rsplit('/', 1)
    createDir(material_dir)
    material = assetTools.create_asset(material_name, material_dir, unreal.Material, unreal.MaterialFactoryNew())
    return material


#########################################################
# Utility class to do most of the common functionalities with the ContentBrowser

def saveAsset(asset_path, only_if_is_dirty=True):
    return unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty)


def saveDir(dir_path, only_if_is_dirty=True, recursive=True):
    return unreal.EditorAssetLibrary.save_asset(dir_path, only_if_is_dirty, recursive)


def createDir(dir_path):
    """
    To creates directory in unreal
    Args:
        dir_path (str): the unreal directory to created

    Returns (bool): True if the operation succeeds

    """
    return unreal.EditorAssetLibrary.make_directory(dir_path)


def duplicateDir(from_dir, to_dir):
    return unreal.EditorAssetLibrary.duplicate_directory(from_dir, to_dir)


def renameDir(from_dir, to_dir):
    return unreal.EditorAssetLibrary.rename_directory(from_dir, to_dir)


def deleteDir(dir_path):
    return unreal.EditorAssetLibrary.delete_directory(dir_path)


def dirExists(dir_path):
    return unreal.EditorAssetLibrary.does_directory_exist(dir_path)


def duplicateAsset(from_dir, to_dir):
    return unreal.EditorAssetLibrary.duplicate_asset(from_dir, to_dir)


def renameAsset(from_dir, to_dir):
    return unreal.EditorAssetLibrary.rename_asset(from_dir, to_dir)


def deleteAsset(asset_path):
    return unreal.EditorAssetLibrary.delete_asset(asset_path)


def assetExists(asset_path):
    return unreal.EditorAssetLibrary.does_asset_exist(asset_path)


def listAsset(dir_path, asset_type=None):
    """
    To list all asset in certain directory
    Args:
        dir_path (str):  the unreal dir path
        asset_type (str): the asset type class : MaterialInstanceConstant

    Returns(list(objects)): list of objects of required assets

    """

    assets = []
    for asset in unreal.EditorAssetLibrary.list_assets(dir_path):
        assetObj = unreal.EditorAssetLibrary.load_asset(asset)
        if asset_type is None:
            assets.append(assetObj)
        else:
            asset_data = unreal.EditorAssetLibrary.find_asset_data(asset)
            if asset_data.asset_class == asset_type:
                assets.append(assetObj)

    return assets


def setMaterialInstanceTexture(mi_asset, param_name, tex_path):
    """

    Args:
        mi_asset (object): the instance material object
        param_name (str): the attribute name in instance material : base color, roughness
        tex_path (str): the unreal path of texture asset

    Returns (bool): True if the process is done successfully

    """

    if isinstance(tex_path, str):
        tex_asset = unreal.EditorAssetLibrary.find_asset_data(tex_path).get_asset()
    else:
        tex_asset = tex_path

    # if not unreal.EditorAssetLibrary.does_asset_exist(tex_asset):
    #     unreal.log_warning(f"Can't find texture: {tex_asset}")
    #     return False

    unreal.log_error(f"mi_asset: {mi_asset}")
    unreal.log_error(f"param_name: {param_name}")
    unreal.log_error(f"tex_path: {tex_path}")

    return unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi_asset, param_name, tex_asset)


def makeMaterialInstance(master_path, instance_path):
    """
    To make an instance from master material
    Args:
        master_path (str): the unreal master material path
        instance_path (str): the unreal instance material path

    Returns(object): the object of instance material

    """

    # Get asset object of master material
    master_mtl_asset = unreal.EditorAssetLibrary.find_asset_data(master_path).get_asset()
    mi_dir, mi_name = instance_path.rsplit("/", 1)

    assetTools = createAssetTool()

    # Check if material instance already exists
    if unreal.EditorAssetLibrary.does_asset_exist(instance_path):
        mi_asset = unreal.EditorAssetLibrary.find_asset_data(instance_path).get_asset()
        unreal.log("Asset already exists")
    else:
        instance_factory = unreal.MaterialInstanceConstantFactoryNew()
        mi_asset = assetTools.create_asset(mi_name, mi_dir, unreal.MaterialInstanceConstant, instance_factory)

    unreal.MaterialEditingLibrary.set_material_instance_parent(mi_asset, master_mtl_asset)
    unreal.EditorAssetLibrary.save_loaded_asset(mi_asset)

    # unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi_asset, "Desaturation", 0.3)  # set scalar parameter

    return mi_asset


def makeInstanceWithTextures(master_path, instance_path, texturesData):
    """
    To make an instance material with ites texture
    Args:
        master_path (str): the unreal master material path
        instance_path (str): the unreal instance material path
        texturesData (list(tupels)):  list of tuples contains (attr, texture_path), ("Albedo", '/Game/imported/shnbSkinSG_BaseColor')

    Returns(object): the object of instance material

    """

    instance_mtl_asset = makeMaterialInstance(master_path, instance_path)

    for attr, texture in texturesData:
        setMaterialInstanceTexture(instance_mtl_asset, attr, texture)

    return instance_mtl_asset


def assignMaterial(st_mesh_asset, material_object, mtl_id=0, slot_name=None):
    if isinstance(st_mesh_asset, str):
        st_mesh_asset = unreal.EditorAssetLibrary.find_asset_data(st_mesh_asset).get_asset()
    if slot_name:
        mtl_id = st_mesh_asset.get_material_index(slot_name)
    st_mesh_asset.set_material(mtl_id, material_object)


def get_material_slot_names(static_mesh):
    sm_component = unreal.StaticMeshComponent()
    sm_component.set_static_mesh(static_mesh)
    return unreal.StaticMeshComponent.get_material_slot_names(sm_component)


AttrsCon = {
    "baseColor": "Albedo",
    "metalness": "Metalness",
    "normalCamera": "Normal",
    "specularRoughness": "Roughness",
    "specular": None,
    "transmission": None,
    "specularColor": None,
    "transmissionColor": None,
    "subsurface": None,
    "subsurfaceColor": None,
    "subsurfaceRadius": None,
    "sheenColor": None,
    "emission": None,
    "emissionColor": None,
    "opacity": None,

}


#########################################################
# Utility

def get_asset(game_path):
    """
    To get the unreal asset object
    :param game_path: The unreal path to required asset
    :return: unreal.Object
    """
    # unreal.AssetData
    return unreal.EditorAssetLibrary.find_asset_data(game_path).get_asset()


def spawn_asset(game_path, translate=(0.0, 0.0, 0.0), rotate=(0.0, 0.0, 0.0)):
    """
    To place the objet in viewport
    :param game_path: The unreal path to required asset
    :param translate: list of translation
    :param rotate: list of rotation
    :return: (unreal.Actor) created actor
    """

    asset_object = get_asset(game_path)

    # unreal.Actor
    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
        asset_object,
        unreal.Vector(translate[0], translate[1], translate[2]),
        unreal.Rotator(rotate[0], rotate[1], rotate[2]))
    return actor


# Main
# =====================================================================================================================
def main():
    MasterMaterial_VT = '/Game/MSPresets/MS_DefaultMaterial/MS_DefaultMaterial_VT'
    MasterMaterial = '/Game/MSPresets/MS_DefaultMaterial/MS_DefaultMaterial'
    # MasterMaterial_VT = '/Game/MSPresets/MS_DefaultMaterial/MS_DefaultMaterial_VT'

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_tools.import_assets_with_dialog('/Game/imported')

    fbx_path = "old_car.fbx"
    json_path = fbx_path.replace("fbx", "json")

    with open(json_path, "r") as f:
        jsonData = json.load(f)

    if not jsonData:
        unreal.log_error("Can not read json file: '{}'".format(json_path))

    '''
    destination_path = "/Game/imported/"

    assets_pathes = importStaticMesh(fbx_path, destination_path+"ST_MESH")

    for asset_path in assets_pathes[0]:
        asset = unreal.EditorAssetLibrary.find_asset_data(asset_path).get_asset()
        actor = unreal.EditorLevelLibrary.spawn_actor_from_object(asset, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))

        #actions = get_material_slot_names(asset)

        mtl = unreal.EditorAssetLibrary.find_asset_data("/Game/imported/mtl").get_asset()

        assignMaterial(asset, mtl, 0)
    '''

    for name in jsonData:
        destination_path = f"/Game/imported/{name}/"
        ST_path = destination_path + "ST_MESH"
        MTL_path = destination_path + "Materials"
        TX_path = destination_path + "Texture"

        assets_pathes = importStaticMesh(fbx_path, ST_path, "ST")
        # loop on assets

        counter = 0

        sgsData = jsonData[name]
        for sg in sgsData:
            geos = sgsData[sg]["geos"]
            for geo in geos:
                asset_path = ST_path + "/ST_" + geo

                if assetExists(asset_path):
                    # get asset object
                    asset = unreal.EditorAssetLibrary.find_asset_data(asset_path).get_asset()
                    mtl_id = geos[geo]["id"]
                    udim = geos[geo]["udim"]
                    mtls = geos[geo]["materials"]
                    if not mtls:
                        continue
                    mtl = list(mtls.keys())[0]
                    # mtl_asset = unreal.EditorAssetLibrary.find_asset_data("/Game/imported/mtl").get_asset()

                    textures_data = mtls[mtl]["textures"]

                    # textures_data = [r"P:/Projects/2021/Kira_and_Jinn/05_Textures/OldCar_New/OldCar_v01/Normal/OldCar_Normal.1001.tif",
                    #             r"P:/Projects/2021/Kira_and_Jinn/05_Textures/OldCar_New/OldCar_v01/BaseColor/OldCar_BaseColor.1001.tif",
                    #             r"P:/Projects/2021/Kira_and_Jinn/05_Textures/OldCar_New/OldCar_v01/OldCar_Wheel_Dirt_Mask/OldCar_Wheel_Dirt_Mask_BaseColor.1001.tif"]

                    tx_data = []
                    for tx_node in textures_data:
                        filepath = textures_data[tx_node]["filepath"]  # windows path
                        plugs = textures_data[tx_node]["plugs"]
                        colorSpace = textures_data[tx_node]["colorspace"]

                        if not filepath:
                            continue

                        import_tex_path = TX_path + "/" + os.path.basename(filepath).split(".", 1)[0]
                        if assetExists(import_tex_path):
                            textures = [unreal.EditorAssetLibrary.find_asset_data(import_tex_path).get_asset()]

                        else:
                            textures = importTexture(filepath, TX_path)[0]

                        if not textures:
                            continue

                        for plug in plugs:
                            attr = AttrsCon[plug]
                            if attr:
                                tx_data.append((attr, textures[0]))

                    if len(udim) > 1:
                        Material2Used = MasterMaterial_VT
                    else:
                        if udim[0] == 1001 and len(udim) == 1:
                            Material2Used = MasterMaterial
                        else:
                            Material2Used = MasterMaterial_VT

                    inst_mtl_path = MTL_path + "/" + mtl
                    if assetExists(inst_mtl_path):
                        mtl_asset = unreal.EditorAssetLibrary.find_asset_data(inst_mtl_path).get_asset()
                    else:
                        mtl_asset = makeInstanceWithTextures(Material2Used, inst_mtl_path, tx_data)

                    if mtl_asset:
                        assignMaterial(asset, mtl_asset, mtl_id)

                    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(asset, unreal.Vector(0.0, 0.0, 0.0),
                                                                              unreal.Rotator(0.0, 0.0, 0.0))

    # path = '/Game/imported/ST_MESH/IMP_pSphere2.IMP_pSphere2'
    # asset = unreal.EditorAssetLibrary.find_asset_data(path).get_asset()
    # mtl = unreal.EditorAssetLibrary.find_asset_data("/Game/imported/mtl").get_asset()
    #
    # assignMaterial(path, mtl)
    #

    # import asset
    # filename = r"C:\Users\michael.reda\Documents\Unreal Projects\Pythons\unreal\_maya\mayaFiles\fbx\spheres.fbx"
    # textureDir = r"P:\Projects\2021\Hsn-RnD\03_Production\Assets\AboShanab\Textures\Substance\v0001"
    #
    # destination_path = "/Game/imported/Texture"
    #
    # assets_pathes = importStaticMesh(filename, destination_path)
    #
    # tx_path = os.path.join(textureDir, "shnbSkinSG_BaseColor.1001.tif")
    # textures = importTexture(tx_path, destination_path)
    # unreal.log_error("textures: {}".format(textures))
    # unreal.log_error("objetcs: {}".format(type(assets_pathes[0][0])))

    # MasterMaterial = r'/Game/MSPresets/MS_DefaultMaterial/MS_DefaultMaterial_VT'
    # instance = r'/Game/imported/MI_foo3'
    #
    # tex_data = [('Albedo', '/Game/imported/shnbSkinSG_BaseColor'), ('Normal', '/Game/imported/shnbSkinSG_Normal.shnbSkinSG_Normal')]
    #
    # inst_mtl = makeInstanceWithTextures(MasterMaterial, instance, tex_data)
    #
    # assignMaterial('/Game/test/geos/ch_01_Shnb_Body', inst_mtl, mtl_id=0)


if __name__ == '__main__':
    print(__name__)
