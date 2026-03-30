"""
app.py — Punto de entrada del Sistema de Gestión de Inventario.

Ejecutar:
    python app.py

Dependencias:
    servicios.py  — operaciones CRUD y estadísticas
    archivos.py   — persistencia CSV (guardar / cargar)
"""

import os
from Servicios import (
    agregar_producto,
    mostrar_inventario,
    buscar_producto,
    actualizar_producto,
    eliminar_producto,
    mostrar_estadisticas,
)
from Archivos import guardar_csv, cargar_csv, integrar_inventario

# ---------------------------------------------------------------------------
# Helpers de entrada validada
# ---------------------------------------------------------------------------

def _input_float(prompt: str, minimo: float = 0.0) -> float | None:
    """
    Solicita un número flotante al usuario con validación.
    Retorna None si el usuario presiona Enter sin escribir nada (saltar campo).
    """
    valor_str = input(prompt).strip()
    if valor_str == "":
        return None
    try:
        valor = float(valor_str)
        if valor < minimo:
            print(f"  ⚠  El valor debe ser >= {minimo}.")
            return None
        return valor
    except ValueError:
        print("  ⚠  Entrada inválida. Ingrese un número.")
        return None


def _input_int(prompt: str, minimo: int = 0) -> int | None:
    """
    Solicita un número entero al usuario con validación.
    Retorna None si el usuario presiona Enter sin escribir nada (saltar campo).
    """
    valor_str = input(prompt).strip()
    if valor_str == "":
        return None
    try:
        valor = int(valor_str)
        if valor < minimo:
            print(f"  ⚠  El valor debe ser >= {minimo}.")
            return None
        return valor
    except ValueError:
        print("  ⚠  Entrada inválida. Ingrese un número entero.")
        return None


def _input_nombre(prompt: str) -> str | None:
    """Solicita un nombre no vacío y que contenga al menos una letra."""
    nombre = input(prompt).strip()
    if not nombre:
        print("  ⚠  El nombre no puede estar vacío.")
        return None
    # Rechazar cadenas que sean solo dígitos o caracteres no alfabéticos
    if not any(c.isalpha() for c in nombre):
        print("  ⚠  El nombre debe contener al menos una letra.")
        return None
    return nombre


def _input_ruta(prompt: str) -> str | None:
    """Solicita una ruta de archivo no vacía."""
    ruta = input(prompt).strip()
    if not ruta:
        print("  ⚠  La ruta no puede estar vacía.")
        return None
    return ruta


# ---------------------------------------------------------------------------
# Acciones del menú
# ---------------------------------------------------------------------------

def accion_agregar(inventario: list) -> None:
    """Solicita datos de un nuevo producto y lo agrega al inventario."""
    print("\n  — Agregar producto —")
    nombre = _input_nombre("  Nombre   : ")
    if nombre is None:
        return

    precio = _input_float("  Precio   : $", minimo=0.0)
    if precio is None:
        return

    cantidad = _input_int("  Cantidad : ", minimo=0)
    if cantidad is None:
        return

    agregar_producto(inventario, nombre, precio, cantidad)


def accion_mostrar(inventario: list) -> None:
    """Muestra todos los productos del inventario."""
    print("\n  — Inventario actual —")
    mostrar_inventario(inventario)


def accion_buscar(inventario: list) -> None:
    """Busca un producto por nombre y muestra su información."""
    print("\n  — Buscar producto —")
    nombre = _input_nombre("  Nombre a buscar: ")
    if nombre is None:
        return

    producto = buscar_producto(inventario, nombre)
    if producto:
        print(f"\n  Producto encontrado:")
        print(f"    Nombre   : {producto['nombre']}")
        print(f"    Precio   : ${producto['precio']:.2f}")
        print(f"    Cantidad : {producto['cantidad']}")
        subtotal = producto["precio"] * producto["cantidad"]
        print(f"    Subtotal : ${subtotal:.2f}\n")
    else:
        print(f"  ⚠  '{nombre}' no se encontró en el inventario.")


def accion_actualizar(inventario: list) -> None:
    """Actualiza precio y/o cantidad de un producto existente."""
    print("\n  — Actualizar producto —")
    nombre = _input_nombre("  Nombre del producto: ")
    if nombre is None:
        return

    # Verificar existencia antes de pedir nuevos datos
    if buscar_producto(inventario, nombre) is None:
        print(f"  ⚠  '{nombre}' no existe en el inventario.")
        return

    print("  (Presione Enter para dejar sin cambios)")
    nuevo_precio = _input_float("  Nuevo precio   : $")
    nueva_cantidad = _input_int("  Nueva cantidad : ")

    if nuevo_precio is None and nueva_cantidad is None:
        print("  Sin cambios realizados.")
        return

    actualizar_producto(inventario, nombre, nuevo_precio, nueva_cantidad)


def accion_eliminar(inventario: list) -> None:
    """Elimina un producto del inventario previa confirmación."""
    print("\n  — Eliminar producto —")
    nombre = _input_nombre("  Nombre del producto: ")
    if nombre is None:
        return

    if buscar_producto(inventario, nombre) is None:
        print(f"  ⚠  '{nombre}' no existe en el inventario.")
        return

    confirmacion = input(f"  ¿Confirmar eliminación de '{nombre}'? (S/N): ").strip().upper()
    if confirmacion == "S":
        eliminar_producto(inventario, nombre)
    else:
        print("  Eliminación cancelada.")


def accion_estadisticas(inventario: list) -> None:
    """Muestra las estadísticas del inventario."""
    mostrar_estadisticas(inventario)


def accion_guardar(inventario: list) -> None:
    """Solicita una ruta y guarda el inventario en CSV."""
    print("\n  — Guardar CSV —")
    ruta = _input_ruta("  Ruta de destino (ej. inventario.csv): ")
    if ruta is None:
        return
    guardar_csv(inventario, ruta)


def accion_cargar(inventario: list) -> list:
    """
    Solicita una ruta, carga un CSV y permite sobrescribir o fusionar.

    Retorna:
        list: El nuevo inventario (puede ser el mismo si hubo error).
    """
    print("\n  — Cargar CSV —")
    ruta = _input_ruta("  Ruta del archivo CSV: ")
    if ruta is None:
        return inventario

    cargado = cargar_csv(ruta)
    if not cargado:
        print("  No se cargaron productos (archivo vacío o con errores).")
        return inventario

    nuevo_inventario, accion = integrar_inventario(inventario, cargado)

    print(f"\n  Resumen de carga:")
    print(f"    Productos cargados : {len(cargado)}")
    print(f"    Acción aplicada    : {accion}")
    print(f"    Total en inventario: {len(nuevo_inventario)}\n")

    return nuevo_inventario


# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------

OPCIONES = {
    "1": "Agregar producto",
    "2": "Mostrar inventario",
    "3": "Buscar producto",
    "4": "Actualizar producto",
    "5": "Eliminar producto",
    "6": "Estadísticas",
    "7": "Guardar CSV",
    "8": "Cargar CSV",
    "9": "Salir",
}


def mostrar_menu() -> None:
    """Imprime el menú principal."""
    print("\n" + "═" * 44)
    print(f"  {'SISTEMA DE GESTIÓN DE INVENTARIO':^40}")
    print("═" * 44)
    for clave, descripcion in OPCIONES.items():
        print(f"  {clave}. {descripcion}")
    print("═" * 44)


def main() -> None:
    """Bucle principal del programa."""
    # Inventario en memoria: lista de dicts
    inventario: list = []

    print("\n  Bienvenido al Sistema de Gestión de Inventario.")
    print("  Use las opciones del menú para operar el inventario.\n")

    while True:
        mostrar_menu()

        opcion = input("  Seleccione una opción (1-9): ").strip()

        # Validar que la opción sea un número entre 1 y 9
        if opcion not in OPCIONES:
            print(f"  ⚠  Opción '{opcion}' no válida. Ingrese un número del 1 al 9.")
            continue

        try:
            if opcion == "1":
                accion_agregar(inventario)
            elif opcion == "2":
                accion_mostrar(inventario)
            elif opcion == "3":
                accion_buscar(inventario)
            elif opcion == "4":
                accion_actualizar(inventario)
            elif opcion == "5":
                accion_eliminar(inventario)
            elif opcion == "6":
                accion_estadisticas(inventario)
            elif opcion == "7":
                accion_guardar(inventario)
            elif opcion == "8":
                # cargar puede retornar un inventario nuevo
                inventario = accion_cargar(inventario)
            elif opcion == "9":
                print("\n  ¡Hasta luego! Inventario cerrado.\n")
                break

        except KeyboardInterrupt:
            # Ctrl+C en medio de un input: volver al menú limpiamente
            print("\n  Operación interrumpida. Volviendo al menú...")
        except Exception as e:
            # Cualquier error inesperado: informar sin cerrar la aplicación
            print(f"\n  ✖  Error inesperado: {e}")
            print("  El programa sigue en ejecución. Vuelva al menú.")


if __name__ == "__main__":
    main()