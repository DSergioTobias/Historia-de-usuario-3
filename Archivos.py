"""
archivos.py — Persistencia del inventario en formato CSV.

Formato esperado:
    Encabezado: nombre,precio,cantidad
    Separador : coma (,)
    Encoding  : UTF-8
"""

import csv
import os

# Encabezado canónico del CSV
HEADER = ["nombre", "precio", "cantidad"]


# ---------------------------------------------------------------------------
# Guardar
# ---------------------------------------------------------------------------

def guardar_csv(inventario: list, ruta: str, incluir_header: bool = True) -> bool:
    """
    Escribe el inventario en un archivo CSV.

    Parámetros:
        inventario    (list) : Lista de dicts del inventario.
        ruta          (str)  : Ruta (absoluta o relativa) del archivo destino.
        incluir_header(bool) : Si True, escribe la fila de encabezado.

    Retorna:
        bool: True si se guardó correctamente, False ante cualquier error.

    Reglas:
        - Verifica que el inventario no esté vacío antes de continuar.
        - Maneja PermissionError y cualquier OSError con mensaje descriptivo.
        - Crea directorios intermedios si no existen.
    """
    # Validar que haya datos
    if not inventario:
        print("  ⚠  El inventario está vacío. No hay nada que guardar.")
        return False

    try:
        # Crear directorio si no existe
        directorio = os.path.dirname(ruta)
        if directorio:
            os.makedirs(directorio, exist_ok=True)

        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADER, extrasaction="ignore")
            if incluir_header:
                writer.writeheader()
            writer.writerows(inventario)

        print(f"  ✔  Inventario guardado en: {os.path.abspath(ruta)}")
        return True

    except PermissionError:
        print(f"  ✖  Sin permiso de escritura en: {ruta}")
    except OSError as e:
        print(f"  ✖  Error al guardar el archivo: {e}")

    return False


# ---------------------------------------------------------------------------
# Cargar
# ---------------------------------------------------------------------------

def cargar_csv(ruta: str) -> list:
    """
    Lee un CSV y retorna una lista de dicts con estructura de inventario.

    Parámetros:
        ruta (str): Ruta del archivo CSV a leer.

    Retorna:
        list: Lista de dicts {"nombre": str, "precio": float, "cantidad": int}.
              Lista vacía si hay error irrecuperable o no hay filas válidas.

    Reglas de validación por fila:
        - Exactamente 3 columnas (nombre, precio, cantidad).
        - precio convertible a float >= 0.
        - cantidad convertible a int >= 0.
        - Filas inválidas se omiten y se acumula un contador de errores.

    Excepciones manejadas:
        FileNotFoundError, UnicodeDecodeError, ValueError, Exception genérica.
    """
    productos = []
    filas_invalidas = 0

    try:
        with open(ruta, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)

            # --- Validar encabezado ---
            try:
                encabezado = next(reader)
            except StopIteration:
                print("  ✖  El archivo está vacío.")
                return []

            encabezado_norm = [c.strip().lower() for c in encabezado]
            if encabezado_norm != HEADER:
                print(
                    f"  ✖  Encabezado inválido: se esperaba '{','.join(HEADER)}' "
                    f"pero se encontró '{','.join(encabezado)}'."
                )
                return []

            # --- Procesar filas ---
            for numero, fila in enumerate(reader, start=2):
                if len(fila) != 3:
                    filas_invalidas += 1
                    continue

                nombre, precio_str, cantidad_str = fila
                nombre = nombre.strip()

                if not nombre:
                    filas_invalidas += 1
                    continue

                try:
                    precio = float(precio_str)
                    cantidad = int(cantidad_str)
                    if precio < 0 or cantidad < 0:
                        raise ValueError("Valores negativos no permitidos.")
                except ValueError:
                    filas_invalidas += 1
                    continue

                productos.append({
                    "nombre": nombre,
                    "precio": round(precio, 2),
                    "cantidad": cantidad,
                })

    except FileNotFoundError:
        print(f"  ✖  Archivo no encontrado: {ruta}")
        return []
    except UnicodeDecodeError:
        print(f"  ✖  Error de codificación al leer: {ruta} (¿es UTF-8?)")
        return []
    except Exception as e:
        print(f"  ✖  Error inesperado al leer el archivo: {e}")
        return []

    # --- Informe de filas inválidas ---
    if filas_invalidas:
        print(f"  ⚠  {filas_invalidas} fila(s) inválida(s) omitida(s).")

    return productos


# ---------------------------------------------------------------------------
# Lógica de integración: sobrescribir o fusionar
# ---------------------------------------------------------------------------

def integrar_inventario(inventario_actual: list, cargado: list) -> tuple[list, str]:
    """
    Pregunta al usuario si sobrescribir o fusionar el inventario cargado
    con el inventario actual y aplica la acción elegida.

    Política de fusión (si el usuario elige N):
        - Si el nombre ya existe: suma la cantidad y usa el precio nuevo.
        - Si el nombre no existe: agrega el producto directamente.

    Parámetros:
        inventario_actual (list): Inventario en memoria.
        cargado           (list): Productos leídos del CSV.

    Retorna:
        tuple[list, str]: (nuevo_inventario, descripcion_accion)
    """
    print("\n  Política de fusión (opción N):")
    print("    • Nombre existente → suma cantidad + actualiza precio al nuevo valor.")
    print("    • Nombre nuevo     → se agrega directamente.")
    respuesta = input("\n  ¿Sobrescribir inventario actual? (S/N): ").strip().upper()

    if respuesta == "S":
        return cargado, "reemplazo"

    # Fusión
    fusionado = list(inventario_actual)  # copia superficial
    for prod in cargado:
        existente = next(
            (p for p in fusionado if p["nombre"].lower() == prod["nombre"].lower()),
            None,
        )
        if existente:
            existente["cantidad"] += prod["cantidad"]
            existente["precio"] = prod["precio"]
        else:
            fusionado.append(dict(prod))

    return fusionado, "fusión"