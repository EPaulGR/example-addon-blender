"""Propiedades del addon y preferencias de usuario."""

import bpy

from . import version_manager


class BVCVersionItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Nombre")
    filepath: bpy.props.StringProperty(name="Ruta")
    modified: bpy.props.StringProperty(name="Modificado")
    size: bpy.props.StringProperty(name="Tamaño")
    note: bpy.props.StringProperty(name="Nota")


class BVCPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    versions_subdir: bpy.props.StringProperty(
        name="Carpeta de versiones",
        description=(
            "Subcarpeta relativa al .blend donde guardar versiones. "
            "Vacío = carpeta oculta junto al archivo (ej. .mi_proyecto_versions)"
        ),
        default="",
    )

    use_timestamp_naming: bpy.props.BoolProperty(
        name="Usar fecha/hora en el nombre",
        description="Si está activo, usa nombres con timestamp en lugar de v001, v002…",
        default=False,
    )

    auto_version_on_save: bpy.props.BoolProperty(
        name="Versión automática al guardar",
        description="Crea una versión cada vez que guardas el archivo (Ctrl+S)",
        default=False,
    )

    max_versions: bpy.props.IntProperty(
        name="Máximo de versiones",
        description="Cantidad máxima de versiones a conservar (0 = sin límite)",
        default=20,
        min=0,
        max=500,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "versions_subdir")
        layout.prop(self, "use_timestamp_naming")
        layout.prop(self, "auto_version_on_save")
        layout.prop(self, "max_versions")


class BVCSceneProperties(bpy.types.PropertyGroup):
    version_note: bpy.props.StringProperty(
        name="Nota de versión",
        description="Nota opcional que se guarda junto a la versión",
        default="",
    )

    version_list_index: bpy.props.IntProperty(name="Índice", default=0)
    version_items: bpy.props.CollectionProperty(type=BVCVersionItem)


def get_addon_preferences(context) -> BVCPreferences:
    return context.preferences.addons[__package__].preferences


def refresh_version_list(context) -> None:
    scene = context.scene
    props = scene.bvc_props
    prefs = get_addon_preferences(context)

    props.version_items.clear()

    if not bpy.data.filepath:
        return

    for entry in version_manager.list_versions(
        bpy.data.filepath,
        custom_dir=prefs.versions_subdir,
    ):
        item = props.version_items.add()
        item.name = entry.label
        item.filepath = str(entry.path)
        item.modified = entry.modified_str
        item.size = entry.size_str
        item.note = version_manager.get_version_note(entry.path)

    if props.version_list_index >= len(props.version_items):
        props.version_list_index = max(0, len(props.version_items) - 1)
