"""Operadores del addon de control de versiones."""

from pathlib import Path

import bpy
from bpy.types import Operator

from . import version_manager
from .properties import get_addon_preferences, refresh_version_list


class BVC_OT_save_version(Operator):
    bl_idname = "bvc.save_version"
    bl_label = "Guardar versión"
    bl_description = "Crea una copia versionada del archivo .blend actual"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath)

    def execute(self, context):
        prefs = get_addon_preferences(context)
        scene_props = context.scene.bvc_props

        try:
            target = version_manager.create_version(
                bpy.data.filepath,
                custom_dir=prefs.versions_subdir,
                use_timestamp=prefs.use_timestamp_naming,
                note=scene_props.version_note,
            )
        except (FileNotFoundError, ValueError) as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        if prefs.max_versions > 0:
            removed = version_manager.prune_old_versions(
                bpy.data.filepath,
                custom_dir=prefs.versions_subdir,
                keep_count=prefs.max_versions,
            )
            if removed:
                self.report({"INFO"}, f"Versión guardada. Se eliminaron {removed} versiones antiguas.")
            else:
                self.report({"INFO"}, f"Versión guardada: {target.name}")
        else:
            self.report({"INFO"}, f"Versión guardada: {target.name}")

        scene_props.version_note = ""
        refresh_version_list(context)
        return {"FINISHED"}


class BVC_OT_restore_version(Operator):
    bl_idname = "bvc.restore_version"
    bl_label = "Abrir versión"
    bl_description = "Abre la versión seleccionada en una nueva ventana de Blender"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty()

    def execute(self, context):
        path = Path(self.filepath)
        if not path.is_file():
            self.report({"ERROR"}, "La versión seleccionada no existe.")
            return {"CANCELLED"}

        version_manager.restore_version(path)
        self.report({"INFO"}, f"Abriendo {path.name}")
        return {"FINISHED"}


class BVC_OT_open_versions_folder(Operator):
    bl_idname = "bvc.open_versions_folder"
    bl_label = "Abrir carpeta de versiones"
    bl_description = "Abre la carpeta donde se almacenan las versiones"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath)

    def execute(self, context):
        prefs = get_addon_preferences(context)
        versions_dir = version_manager.get_versions_dir(
            bpy.data.filepath,
            custom_dir=prefs.versions_subdir,
        )

        if versions_dir is None:
            self.report({"ERROR"}, "No hay archivo .blend activo.")
            return {"CANCELLED"}

        versions_dir.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.path_open(filepath=str(versions_dir))
        return {"FINISHED"}


class BVC_OT_refresh_versions(Operator):
    bl_idname = "bvc.refresh_versions"
    bl_label = "Actualizar lista"
    bl_description = "Actualiza la lista de versiones disponibles"
    bl_options = {"REGISTER"}

    def execute(self, context):
        refresh_version_list(context)
        count = len(context.scene.bvc_props.version_items)
        self.report({"INFO"}, f"{count} versión(es) encontrada(s).")
        return {"FINISHED"}


class BVC_OT_delete_version(Operator):
    bl_idname = "bvc.delete_version"
    bl_label = "Eliminar versión"
    bl_description = "Elimina permanentemente la versión seleccionada"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        path = Path(self.filepath)
        if path.is_file():
            path.unlink()
            note_path = path.with_suffix(".txt")
            note_path.unlink(missing_ok=True)

        refresh_version_list(context)
        self.report({"INFO"}, "Versión eliminada.")
        return {"FINISHED"}


class BVC_OT_prune_versions(Operator):
    bl_idname = "bvc.prune_versions"
    bl_label = "Limpiar versiones antiguas"
    bl_description = "Elimina versiones antiguas según el límite configurado en preferencias"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return bool(bpy.data.filepath)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        prefs = get_addon_preferences(context)
        if prefs.max_versions <= 0:
            self.report({"WARNING"}, "Configura un máximo de versiones en las preferencias del addon.")
            return {"CANCELLED"}

        removed = version_manager.prune_old_versions(
            bpy.data.filepath,
            custom_dir=prefs.versions_subdir,
            keep_count=prefs.max_versions,
        )
        refresh_version_list(context)
        self.report({"INFO"}, f"Se eliminaron {removed} versión(es).")
        return {"FINISHED"}


@bpy.app.handlers.persistent
def bvc_save_post_handler(dummy):
    """Crea una versión automática después de guardar si está habilitado."""
    if not bpy.data.filepath:
        return

    try:
        prefs = bpy.context.preferences.addons[__package__].preferences
    except (KeyError, AttributeError):
        return

    if not prefs.auto_version_on_save:
        return

    try:
        version_manager.create_version(
            bpy.data.filepath,
            custom_dir=prefs.versions_subdir,
            use_timestamp=prefs.use_timestamp_naming,
        )
        if prefs.max_versions > 0:
            version_manager.prune_old_versions(
                bpy.data.filepath,
                custom_dir=prefs.versions_subdir,
                keep_count=prefs.max_versions,
            )
    except (FileNotFoundError, ValueError, OSError):
        pass
