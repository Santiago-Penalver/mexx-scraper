# Lista centralizada de exclusión para todas las tiendas
PALABRAS_EXCLUIDAS = [
    # Servicios y no-hardware
    "ARMADO",
    "SERVICE",
    "INSTALACION",
    "INSTALACIÓN",
    "GARANTIA",
    "GARANTÍA",
    "LICENCIA",
    "ENVIO",
    "ENVÍO",
    # Accesorios y fundas
    "FUNDA",
    "APOYA",
    "REPOSAMUÑECA",
    # Eh?
    "ROBOT"
    # Cables, adaptadores y extensores
    "CABLE",
    "ADAPTADOR",
    "EXTENSOR",
    "SPLITTER",
    # Almacenamiento menor / Portátil
    "PEN DRIVE",
    "PENDRIVE",
    "MEMORIA MICRO SD",
    "MICROSD",
]


def es_producto_valido(nombre, precio):
    """Filtra servicios, armados e ítems inválidos."""
    try:
        precio_num = float(precio)
        if precio_num <= 0:
            return False
    except (ValueError, TypeError):
        return False

    nombre_upper = nombre.upper()
    for palabra in PALABRAS_EXCLUIDAS:
        if palabra in nombre_upper:
            return False

    return True