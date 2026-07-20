import sqlite3
from flask import Flask, render_template, request
import math

app = Flask(__name__)

def productos_mexx_db():
     try:
          conexion = sqlite3.connect("mexxlista.db")
          conexion.row_factory = sqlite3.Row
          cursor = conexion.cursor()

          cursor.execute("SELECT id, nombre, precio, marca, fecha FROM precios_lista ORDER BY precio ASC")
          productos = cursor.fetchall()

          conexion.close()
          return productos
     except sqlite3.OperationalError:
          return []

@app.route("/")
def index():
    productos = productos_mexx_db()
    return render_template("indexmexxlist.html", productos=productos)

@app.route("/filtrar")
def filtrar_productos():
    marca_indicada = request.args.get("marca", "Todo")
    categoria_indicada = request.args.get("categoria", "Todo")
    
    # Paginación
    pagina = request.args.get("pagina", 1, type=int)
    por_pagina = 12 
    offset = (pagina - 1) * por_pagina

    conexion = sqlite3.connect("mexxlista.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    query_base = "FROM precios_lista WHERE 1=1"
    params = []

    # Filtro de Marca
    if marca_indicada != "Todo":
        if marca_indicada in ["AMD", "Intel", "Genérica"]:
            query_base += " AND marca = ?"
            params.append(marca_indicada)
        else:
            query_base += " AND (marca LIKE ? OR nombre LIKE ?)"
            params.append(f"%{marca_indicada}%")
            params.append(f"%{marca_indicada}%")

    # Filtro de Categoría
    if categoria_indicada != "Todo":
        if categoria_indicada == "Periféricos":
            query_base += " AND categoria IN ('Teclados y Mouses', 'Audio y Microfonos')"
        elif categoria_indicada in ["RAM", "Memorias"]:
            query_base += " AND (categoria LIKE '%Memoria%' OR nombre LIKE '%RAM%' OR nombre LIKE '%DDR%')"
        else:
            query_base += " AND categoria = ?"
            params.append(categoria_indicada)

    cursor.execute(f"SELECT COUNT(*) {query_base}", params)
    total_productos = cursor.fetchone()[0]
    total_paginas = math.ceil(total_productos / por_pagina) if total_productos > 0 else 1
    query_final = f"SELECT id, nombre, precio, marca, fecha, categoria {query_base} ORDER BY precio ASC LIMIT ? OFFSET ?"
    params_final = params + [por_pagina, offset]

    cursor.execute(query_final, params_final)
    productos = cursor.fetchall()
    conexion.close()

    return render_template(
        "productos_cards.html", 
        productos=productos,
        pagina_actual=pagina,
        total_paginas=total_paginas,
        marca_actual=marca_indicada,
        categoria_actual=categoria_indicada
    )
@app.route('/detalle/<int:producto_id>')
def producto_seleccionado(producto_id):
     conexion = sqlite3.connect("mexxlista.db")
     conexion.row_factory = sqlite3.Row
     cursor = conexion.cursor()

     cursor.execute("SELECT id, nombre, precio, marca, fecha FROM precios_lista WHERE id = ?", (producto_id,))
     producto = cursor.fetchone()
     conexion.close

     if producto:
          return render_template("producto_detalle.html", prod=producto)
     return "<p class='text-gray-400 p-4'>Producto no encontrado</p>"

if __name__ == '__main__':
     app.run(debug=True, port=5000)