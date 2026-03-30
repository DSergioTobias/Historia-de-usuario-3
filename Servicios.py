"""
servicios.py — Módulo de operaciones CRUD sobre el inventario en memoria.
Cada producto se representa como un diccionario con las claves:
    {"nombre": str, "precio": float, "cantidad": int}
"""

# ---------------------------------------------------------------------------
# Funciones CRUD
# ---------------------------------------------------------------------------

def agregar_producto(inventario: list, nombre: str, precio: float, cantidad: int) -> bool:
    """
    Agrega un nuevo producto al inventario.

    Parámetros:
        inventario (list): Lista de dicts que representa el inventario actual.
        nombre (str): Nombre del producto (único, insensible a mayúsculas).
        precio (float): Precio unitario del producto (>= 0).
        cantidad (int): Unidades disponibles (>= 0).

    Retorna:
        bool: True si se agregó, False si el nombre ya existe.
    """
    nombre_norm = nombre.strip().lower()
    for p in inventario:
        if p["nombre"].lower() == nombre_norm:
            print(f"  ⚠  El producto '{p['nombre']}' ya existe. Use 'Actualizar' para modificarlo.")
            return False

    inventario.append({
        "nombre": nombre.strip(),
        "precio": round(float(precio), 2),
        "cantidad": int(cantidad),
    })
    print(f"  ✔  Producto '{nombre.strip()}' agregado correctamente.")
    return True


def mostrar_inventario(inventario: list) -> None:
    """
    Imprime el inventario completo con formato tabular.

    Parámetros:
        inventario (list): Lista de dicts del inventario.

    Retorna:
        None
    """
    if not inventario:
        print("  El inventario está vacío.")
        return

    sep = "─" * 52
    print(f"\n  {sep}")
    print(f"  {'NOMBRE':<22} {'PRECIO':>10} {'CANTIDAD':>10}  {'SUBTOTAL':>10}")
    print(f"  {sep}")
    # Lambda para calcular el subtotal de cada producto (Task 3 – opcional)
    subtotal = lambda p: p["precio"] * p["cantidad"]
    for p in inventario:
        print(f"  {p['nombre']:<22} ${p['precio']:>9.2f} {p['cantidad']:>10}  ${subtotal(p):>9.2f}")
    print(f"  {sep}")
    print(f"  Total de referencias: {len(inventario)}\n")


def buscar_producto(inventario: list, nombre: str) -> dict | None:
    """
    Busca un producto por nombre (insensible a mayúsculas).

    Parámetros:
        inventario (list): Lista de dicts del inventario.
        nombre (str): Nombre a buscar.

    Retorna:
        dict | None: El dict del producto si existe, None en caso contrario.
    """
    nombre_norm = nombre.strip().lower()
    for p in inventario:
        if p["nombre"].lower() == nombre_norm:
            return p
    return None


def actualizar_producto(
    inventario: list,
    nombre: str,
    nuevo_precio: float | None = None,
    nueva_cantidad: int | None = None,
) -> bool:
    """
    Actualiza el precio y/o la cantidad de un producto existente.

    Parámetros:
        inventario (list): Lista de dicts del inventario.
        nombre (str): Nombre del producto a actualizar.
        nuevo_precio (float | None): Nuevo precio (None = no cambiar).
        nueva_cantidad (int | None): Nueva cantidad (None = no cambiar).

    Retorna:
        bool: True si se actualizó, False si el producto no existe.
    """
    producto = buscar_producto(inventario, nombre)
    if producto is None:
        print(f"  ⚠  Producto '{nombre}' no encontrado.")
        return False

    cambios = []
    if nuevo_precio is not None:
        producto["precio"] = round(float(nuevo_precio), 2)
        cambios.append(f"precio=${nuevo_precio:.2f}")
    if nueva_cantidad is not None:
        producto["cantidad"] = int(nueva_cantidad)
        cambios.append(f"cantidad={nueva_cantidad}")

    if cambios:
        print(f"  ✔  '{producto['nombre']}' actualizado → {', '.join(cambios)}.")
    else:
        print("  Sin cambios especificados.")
    return True


def eliminar_producto(inventario: list, nombre: str) -> bool:
    """
    Elimina un producto del inventario por nombre.

    Parámetros:
        inventario (list): Lista de dicts del inventario.
        nombre (str): Nombre del producto a eliminar.

    Retorna:
        bool: True si se eliminó, False si no existía.
    """
    producto = buscar_producto(inventario, nombre)
    if producto is None:
        print(f"  ⚠  Producto '{nombre}' no encontrado.")
        return False

    inventario.remove(producto)
    print(f"  ✔  Producto '{nombre}' eliminado.")
    return True


# ---------------------------------------------------------------------------
# Estadísticas
# ---------------------------------------------------------------------------

def calcular_estadisticas(inventario: list) -> dict:
    """
    Calcula métricas generales del inventario.

    Parámetros:
        inventario (list): Lista de dicts del inventario.

    Retorna:
        dict con las claves:
            unidades_totales  (int)   : suma de todas las cantidades.
            valor_total       (float) : suma de precio * cantidad por producto.
            producto_mas_caro (dict)  : producto con mayor precio unitario.
            producto_mayor_stock (dict): producto con mayor cantidad.
    """
    if not inventario:
        return {}

    # Lambda reutilizable para el subtotal (Task 3 – requerido)
    subtotal = lambda p: p["precio"] * p["cantidad"]

    unidades_totales = sum(p["cantidad"] for p in inventario)
    valor_total = sum(subtotal(p) for p in inventario)
    producto_mas_caro = max(inventario, key=lambda p: p["precio"])
    producto_mayor_stock = max(inventario, key=lambda p: p["cantidad"])

    return {
        "unidades_totales": unidades_totales,
        "valor_total": round(valor_total, 2),
        "producto_mas_caro": producto_mas_caro,
        "producto_mayor_stock": producto_mayor_stock,
    }


def mostrar_estadisticas(inventario: list) -> None:
    """
    Imprime las estadísticas del inventario con formato legible.

    Parámetros:
        inventario (list): Lista de dicts del inventario.

    Retorna:
        None
    """
    if not inventario:
        print("  El inventario está vacío: no hay estadísticas que mostrar.")
        return

    stats = calcular_estadisticas(inventario)
    sep = "─" * 44
    print(f"\n  {sep}")
    print(f"  {'ESTADÍSTICAS DEL INVENTARIO':^44}")
    print(f"  {sep}")
    print(f"  Unidades totales en stock : {stats['unidades_totales']:>10}")
    print(f"  Valor total del inventario: ${stats['valor_total']:>9.2f}")
    caro = stats["producto_mas_caro"]
    print(f"  Producto más caro         : {caro['nombre']} (${caro['precio']:.2f})")
    stock = stats["producto_mayor_stock"]
    print(f"  Mayor stock               : {stock['nombre']} ({stock['cantidad']} ud.)")
    print(f"  {sep}\n")