# Blend Version Control

Addon de Blender para guardar, listar y restaurar versiones de archivos `.blend`.

## Instalación

1. Comprime la carpeta `blend_version_control` en un archivo `.zip` (la carpeta debe estar en la raíz del zip).
2. En Blender: **Edit > Preferences > Add-ons > Install…**
3. Selecciona el zip y activa **Blend Version Control**.

También puedes instalar en modo desarrollo copiando la carpeta a la ruta de addons de Blender:

```text
~/Library/Application Support/Blender/<versión>/scripts/addons/
```

## Uso

### Panel principal

Abre el panel en **View3D > Sidebar (N) > Versiones**.

- **Nota**: texto opcional que se guarda junto a la versión.
- **Guardar versión**: crea una copia del `.blend` actual.
- **Actualizar lista**: refresca la lista de versiones.
- **Abrir carpeta de versiones**: abre la carpeta donde se almacenan.
- **Limpiar versiones antiguas**: elimina versiones según el límite configurado.

### Menú File

También encontrarás accesos rápidos en **File > Control de Versiones**.

### Preferencias

En **Edit > Preferences > Add-ons > Blend Version Control**:

| Opción | Descripción |
|--------|-------------|
| Carpeta de versiones | Subcarpeta personalizada (vacío = `.nombre_archivo_versions` junto al .blend) |
| Usar fecha/hora | Nombres tipo `proyecto_20250611_143022.blend` en lugar de `v001`, `v002`… |
| Versión automática al guardar | Crea una versión cada vez que guardas con Ctrl+S |
| Máximo de versiones | Límite de versiones a conservar (0 = sin límite) |

## Estructura de archivos

```text
mi_proyecto.blend
.mi_proyecto_versions/
  mi_proyecto_v001.blend
  mi_proyecto_v001.txt      # nota opcional
  mi_proyecto_v002.blend
  ...
```

## Estructura del addon

```text
blend_version_control/
  __init__.py          # Registro del addon
  properties.py        # Preferencias y propiedades de escena
  operators.py         # Operadores (guardar, abrir, eliminar…)
  version_manager.py   # Lógica de versionado
  ui.py                # Paneles y menús
```
