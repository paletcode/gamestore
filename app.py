from colorama import Cursor
from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import date, datetime
import os


app = Flask(__name__)
app.secret_key="1234"

## CONFIGURACION MYSQL
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']     = 'localhost'
app.config['MYSQL_DATABASE_USER']     = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB']       = 'gamestore'
mysql.init_app(app)

##RUTA DE LA CARPETA DE IMAGENES
ARCHIVO = os.path.join('images')
app.config['ARCHIVO'] = ARCHIVO

##acceso a la carpeta images
@app.route('/images/<nombreFoto>')
def images(nombreFoto):
    return send_from_directory(app.config['ARCHIVO'], nombreFoto)

## funcion para cargar la pagina principal
@app.route('/')
def index():

    sql     = "SELECT rutafoto, codigo, nombre, genero, anio, precio FROM games"
    conn    = mysql.connect()
    cursor  = conn.cursor()
    cursor.execute(sql)
    games = cursor.fetchall()
    print(games)

    conn.commit()
    return render_template('juegos/index.html', games = games)

##funcion para cargar el template de la creacion de registros
@app.route('/create')
def create():
    return render_template('juegos/create.html')


## funcion para guardar datos nuevos
@app.route('/store', methods=['POST'])
def storage():
    codigo = request.form['txtCodigo']
    nombre = request.form['txtNombre']
    precio = request.form['txtPrecio']
    genero = request.form['txtGenero']
    foto   = request.files['txtFoto']
    anio   = request.form['txtAnio']
    if codigo =='' or nombre =='' or precio =='' or genero=='' or anio =='':
        flash('Por favor, llena todos los campos del formulario')
        return redirect(url_for('create'))
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if foto.filename != "":
        nfoto = tiempo + foto.filename
        foto.save("images/" + nfoto)

    sql     = "INSERT INTO games (codigo,nombre,precio,genero,rutafoto,anio) VALUES (%s, %s, %s, %s, %s, %s)"
    datos = (codigo, nombre, precio, genero, nfoto, anio)

    conn    = mysql.connect()
    cursor  = conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')



## funcion para borrar un registro
@app.route('/destroy/<string:codigo>')
def destroy(codigo):
     conn    = mysql.connect()
     cursor  = conn.cursor()

     cursor.execute('SELECT rutafoto FROM games WHERE codigo = %s', codigo)
     fila = cursor.fetchall()
     os.remove(os.path.join(app.config['ARCHIVO'], fila[0][0]))
     
     cursor.execute("DELETE FROM games WHERE codigo=%s", (codigo))
     conn.commit()
     return redirect('/')



## funcion para ir al formulario para editar un registro
@app.route('/edit/<string:codigo>')
def edit(codigo):
    conn    = mysql.connect()
    cursor  = conn.cursor()
    cursor.execute("SELECT * FROM games WHERE codigo=%s", (codigo))
    games = cursor.fetchall()
    conn.commit()

    return render_template('juegos/edit.html', games = games)




## funcion para actualizar los datos
@app.route('/update', methods=['POST'])
def update():
    codigo = request.form['txtCodigo']
    nombre = request.form['txtNombre']
    precio = request.form['txtPrecio']
    genero = request.form['txtGenero']
    foto   = request.files['txtFoto']
    anio   = request.form['txtAnio']

    sql     = "UPDATE games SET nombre =%s, precio=%s, genero=%s, anio=%s WHERE codigo =%s"
    datos = (nombre, precio, genero, anio, codigo)

    conn    = mysql.connect()
    cursor  = conn.cursor()
    
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if foto.filename != "":
        nfoto = tiempo + foto.filename
        foto.save("images/" + nfoto)

        cursor.execute('SELECT rutafoto FROM games WHERE codigo = %s', codigo)
        fila = cursor.fetchall()

        os.remove(os.path.join(app.config['ARCHIVO'], fila[0][0]))
        cursor.execute("UPDATE games SET rutafoto=%s WHERE codigo=%s", (nfoto, codigo))
        conn.commit()

    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')



## run de la app en modo debug
if __name__ == '__main__':
    app.run(debug=True)

