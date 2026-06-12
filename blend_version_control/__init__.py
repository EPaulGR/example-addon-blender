bl_info = {
    "name": "Blend Version Control",
    "author": "Erick Paul Garcia Ramirez",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Versiones | File > Control de Versiones",
    "description": "Guarda, lista y restaura versiones de archivos .blend",
    "category": "Import-Export",
}

import bpy

from . import operators, properties, ui

classes = (
    properties.BVCVersionItem,
    properties.BVCPreferences,
    properties.BVCSceneProperties,
    operators.BVC_OT_save_version,
    operators.BVC_OT_restore_version,
    operators.BVC_OT_open_versions_folder,
    operators.BVC_OT_refresh_versions,
    operators.BVC_OT_delete_version,
    operators.BVC_OT_prune_versions,
    ui.BVC_PT_main_panel,
    ui.BVC_UL_version_list,
    ui.BVC_MT_file_menu,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bvc_props = bpy.props.PointerProperty(type=properties.BVCSceneProperties)
    bpy.types.TOPBAR_MT_file.append(ui.draw_file_menu)

    if operators.bvc_save_post_handler not in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.append(operators.bvc_save_post_handler)

    if ui.bvc_load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(ui.bvc_load_post_handler)


def unregister():
    if operators.bvc_save_post_handler in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(operators.bvc_save_post_handler)

    if ui.bvc_load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(ui.bvc_load_post_handler)

    bpy.types.TOPBAR_MT_file.remove(ui.draw_file_menu)
    del bpy.types.Scene.bvc_props

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
