from flask import Flask
from flask import render_template , request, redirect ,url_for,flash
from flaskext.mysql import MySQL
from flask import send_from_directory

from datetime import datetime
import os



app = Flask(__name__)

app.secret_key='prueba'


mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema'
mysql.init_app(app)


# creamos una carpeta para guardar la ruta donde se van a actualizar las fotos
CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA



# vamos a crear un acceso como url que se puso en el archivo edit
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):

    return send_from_directory(app.config['CARPETA'],nombreFoto)

# funcion para conectar a la base de datos
@app.route('/')
def index():
# Estoy haciendo la conexión a la base de datos
    sql = "SELECT * FROM  `empleados`;"
    connect = mysql.connect()
    cursor = connect.cursor()
    cursor.execute(sql)
# selecciona la infromacion para saber realmente que tiene la bd y lo imprimo en conole

    empleados=cursor.fetchall()
    print(empleados)

 # minuto 44:04 youtube https://www.youtube.com/watch?v=gUED5uFmyQI&list=PLSuKjujFoGJ0aSWgVraU74g3VVNWFXsWR
    connect.commit()
    return render_template('empleados/index.html', empleados=empleados)
# funcion para eliminar
@app.route("/destroy/<int:id>")
def destroy(id):
    connect = mysql.connect()
    cursor = connect.cursor()
    cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
    fila = cursor.fetchall()
# para remover 
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
    cursor.execute("DELETE FROM empleados WHERE id=%s", (id))
    connect.commit()
# cuando haga el borrado regrea a la url de donde vino
    return redirect('/')

# funcion para editar
@app.route("/edit/<int:id>")
def edit(id):
    connect = mysql.connect()
    cursor = connect.cursor()
# se consulta la informacion , se busca el id 
    cursor.execute("SELECT * FROM empleados WHERE id=%s", (id))
    empleados=cursor.fetchall()
  
    return render_template('empleados/edit.html',empleados=empleados)
#funcion  para actualizar
@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    # La foto se redirecciona de diferente manera , por ser un archivo.
    _foto = request.files['txtFoto']
    # ESta es la diferencia entre edit y create y se crea una sentencia sql
    id = request.form['txtID']

    sql = "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s"
    datos = (_nombre, _correo, id)

    connect = mysql.connect()
    cursor = connect.cursor()

    if _foto.filename != '':
        cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id,))
        fila = cursor.fetchone()
        # para remover 
        os.remove(os.path.join(app.config['CARPETA'], fila[0]))
        nuevoNombreFoto = str(datetime.now().strftime("%Y%H%M%S")) + _foto.filename
        # aqui , buscamos como se llama esa foto
        _foto.save(os.path.join(app.config['CARPETA'], nuevoNombreFoto))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s", (nuevoNombreFoto, id))

    cursor.execute(sql, datos)
    connect.commit()

    return redirect('/')

@app.route('/create', methods=['GET'])
def create():
    return render_template('empleados/create.html')



@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']


    if _nombre =='' or _correo =='' or _foto =='':
        flash('REcuerda llenar lo datos de los campos')
        return redirect(url_for('create'))

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
        nuevoNombreFoto = tiempo + _foto.filename
        _foto.save(os.path.join(app.config['CARPETA'], nuevoNombreFoto))

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
    datos = (_nombre, _correo, nuevoNombreFoto)

    connect = mysql.connect()
    cursor = connect.cursor()
    cursor.execute(sql, datos)
    connect.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
