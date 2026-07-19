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
     conexion = sqlite3.connect("mexxlista.db")
     conexion.row_factory = sqlite3.Row
     cursor = conexion.cursor()

     if marca_indicada == "Todo":
          cursor.execute("SELECT id, nombre, precio, marca, fecha FROM precios_lista ORDER BY precio ASC")
     else:
          cursor.execute("SELECT id, nombre, precio, marca, fecha FROM precios_lista WHERE marca = ? ORDER BY precio ASC", (marca_indicada,))
     productos = cursor.fetchall()
     conexion.close
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