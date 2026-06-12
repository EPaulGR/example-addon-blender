"""Paneles e interfaz de usuario."""

import bpy

from .properties import refresh_version_list


class BVC_PT_main_panel(bpy.types.Panel):
    bl_label = "Control de Versiones"
    bl_idname = "BVC_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Versiones"

    def draw(self, context):
        layout = self.layout
        scene_props = context.scene.bvc_props

        if not bpy.data.filepath:
            layout.label(text="Guarda el archivo primero", icon="ERROR")
            return

        col = layout.column(align=True)
        col.prop(scene_props, "version_note", text="Nota")
        col.operator("bvc.save_version", icon="FILE_TICK")

        row = layout.row(align=True)
        row.operator("bvc.refresh_versions", icon="FILE_REFRESH")
        row.operator("bvc.open_versions_folder", icon="FILE_FOLDER")
        row.operator("bvc.prune_versions", icon="TRASH")

        layout.separator()
        layout.label(text="Versiones guardadas:")

        if not scene_props.version_items:
            layout.label(text="Sin versiones aún", icon="INFO")
            return

        layout.template_list(
            "BVC_UL_version_list",
            "",
            scene_props,
            "version_items",
            scene_props,
            "version_list_index",
            rows=6,
        )

        if scene_props.version_items:
            index = scene_props.version_list_index
            if 0 <= index < len(scene_props.version_items):
                item = scene_props.version_items[index]
                box = layout.box()
                box.label(text=f"Modificado: {item.modified}")
                box.label(text=f"Tamaño: {item.size}")
                if item.note:
                    box.label(text=f"Nota: {item.note}")

                row = layout.row(align=True)
                op = row.operator("bvc.restore_version", icon="IMPORT", text="Abrir")
                op.filepath = item.filepath
                op = row.operator("bvc.delete_version", icon="X", text="Eliminar")
                op.filepath = item.filepath


class BVC_UL_version_list(bpy.types.UIList):
    bl_idname = "BVC_UL_version_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.label(text=item.name, icon="FILE_BLEND")
            row.label(text=item.modified)
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text=item.name, icon="FILE_BLEND")


class BVC_MT_file_menu(bpy.types.Menu):
    bl_label = "Control de Versiones"
    bl_idname = "BVC_MT_file_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("bvc.save_version", icon="FILE_TICK")
        layout.operator("bvc.open_versions_folder", icon="FILE_FOLDER")
        layout.operator("bvc.refresh_versions", icon="FILE_REFRESH")


def draw_file_menu(self, context):
    self.layout.separator()
    self.layout.menu("BVC_MT_file_menu")


@bpy.app.handlers.persistent
def bvc_load_post_handler(dummy):
    refresh_version_list(bpy.context)
