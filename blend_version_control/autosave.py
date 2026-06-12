"""Autoguardado periódico del archivo .blend activo."""

import bpy


def _get_preferences():
    try:
        return bpy.context.preferences.addons[__package__].preferences
    except (KeyError, AttributeError):
        return None


@bpy.app.handlers.persistent
def _auto_save_tick():
    prefs = _get_preferences()
    if prefs is None or not prefs.auto_save_enabled:
        return None

    if bpy.data.filepath and bpy.data.is_dirty:
        if not bpy.app.is_job_running:
            try:
                bpy.ops.wm.save_mainfile()
            except RuntimeError:
                pass

    return prefs.auto_save_interval_minutes * 60.0


def start_timer():
    stop_timer()
    prefs = _get_preferences()
    if prefs is None or not prefs.auto_save_enabled:
        return

    interval = prefs.auto_save_interval_minutes * 60.0
    bpy.app.timers.register(_auto_save_tick, first_interval=interval)


def stop_timer():
    if bpy.app.timers.is_registered(_auto_save_tick):
        bpy.app.timers.unregister(_auto_save_tick)


def restart_timer():
    stop_timer()
    start_timer()
