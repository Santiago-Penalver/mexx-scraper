import sqlite3
from flask import Flask, render_template, request

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
    marca_indicada = request.args.get('marca', 'Todo')
    categoria_indicada = request.args.get('categoria', 'Todo')
    
    conexion = sqlite3.connect("mexxlista.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    # Base de la consulta
    query = "SELECT id, nombre, precio, marca, fecha, categoria FROM precios_lista WHERE 1=1"
    params = []
    
    # Filtro de marcas
    if marca_indicada != "Todo":
         if marca_indicada in ["AMD", "Intel", "Genérica"]:
            query += " AND marca LIKE ?"
            params.append(marca_indicada)
         else:
             query += " AND (marca LIKE ? OR nombre LIKE ?)"
             params.append(f"%{marca_indicada}%")
             params.append(f"%{marca_indicada}%")
        
    # Filtro de categorías
    if categoria_indicada != "Todo":
         if categoria_indicada == "Periféricos":
              query += " AND categoria IN ('Teclados y Mouses', 'Audio y Microfonos')"
         elif categoria_indicada in ["RAM", "Memorias"]:
              query += " AND (categoria LIKE '%Memoria&' OR nombre LIKE '%RAM%' OR nombre LIKE '%DDR%')"

         else:
               query += " AND categoria = ?"
               params.append(categoria_indicada)
        
         query += " ORDER BY precio ASC"
    
    cursor.execute(query, params)
    productos = cursor.fetchall()
    conexion.close()
    
    return render_template("productos_cards.html", productos=productos)

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