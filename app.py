from flask import Flask, render_template, request,flash
from flask import url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = b'proyecto_final'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)



class Usuario(db.Model):
  id = db.Column('id', db.Integer, primary_key = True)
  usuario = db.Column('usuario', db.String(50))
  contrasenia = db.Column('contrasenia', db.String(50))
  perfil = db.Column('perfil', db.String(10))
  cant_tickets = db.Column('cant_tickets', db.Integer)
  total_compras = db.Column('total_compras', db.Integer)

  def __init__ (self, usuario, contrasenia , perfil):
    self.usuario = usuario
    self.contrasenia = contrasenia
    self.perfil = perfil
    self.cant_tickets = 0
    self.total_compras = 0

class Perfil(db.Model):
  id = db.Column('id', db.Integer, primary_key = True)
  nombre = db.Column('nombre', db.String(10))
  precio = db.Column ('precio', db.Integer)
  tickets_vendidos = db.Column ('tickets_venidos', db.Integer)
  dinero_total = db.Column ('dinero_total', db.Integer)

  def __init__(self, nombre, precio):
    self.nombre = nombre
    self.precio = precio
    self.tickets_vendidos = 0
    self.dinero_total = 0

@app.route('/', methods=['GET', 'POST'])
def index():
  if (request.method == 'POST'):
    btn = request.form.get('btn')
    if (btn == 'iniciar-sesion'):
      usuario = request.form.get('usuario')
      contrasenia = request.form.get('contrasenia')
      buscar_usuario = Usuario.query.filter_by(usuario=usuario).first()
      if (buscar_usuario == None):
        return render_template('inicio.html', error1=True)
      else:
        if(contrasenia == buscar_usuario.contrasenia):
          session['usuario'] = usuario
          return redirect(url_for('usuario', usuario=buscar_usuario.usuario))
        else:
          return render_template('inicio.html', error2=True) 
    elif(btn == 'administrador'):
      session['intentos'] = 0
    elif(btn == 'volver'):
      session.clear()
      return render_template('inicio.html')  
    if(session['intentos'] < 3):
      if(btn == 'ingresar'):
        contrasenia = request.form.get('contrasenia')
        if(contrasenia == 'Admin123'):
          return render_template('admin.html')
        else:
          session['intentos'] += 1
          return render_template('inicio.html', admin=True, error2=True, intentos=session['intentos'])
      else:
        return render_template('inicio.html', admin=True)
    else:
        return render_template('inicio.html', admin=False)    
  else:
    return render_template('inicio.html')

@app.route('/admin', methods=['POST','GET'])
def admin():
  if(request.method == 'POST'):
    btn = request.form.get('btn')
    usuarios = Usuario.query.all()
    perfiles = Perfil.query.all()
    if(btn == 'usuarios'):
      session['buscar'] = 'usuario'
      return render_template('admin.html', buscar_usuarios=True, usuarios=usuarios) 
    elif(btn == 'perfiles'):
      session['buscar'] = 'perfil'
      return render_template('admin.html', buscar_perfiles=True, perfiles=perfiles) 
    elif(btn == 'buscar'):
      nombre = request.form.get('lista')
      if(session['buscar'] == 'usuario'):
        buscar_info = Usuario.query.filter_by(usuario=nombre).first()
        tipo_dato = 'usuario'
      if(session['buscar'] == 'perfil'):
        buscar_info = Perfil.query.filter_by(nombre=nombre).first()  
        tipo_dato = 'perfil'
      return render_template('admin.html', buscar_info=buscar_info, nombre=nombre, tipo_dato=tipo_dato) 
    elif(btn == 'volver'):
      session.clear()
      return redirect(url_for('index'))
    else:
      return render_template('admin.html') 
  else:
    return render_template('admin.html') 

@app.route('/usuario_<usuario>', methods=['GET', 'POST'])
def usuario(usuario):
  buscar_usuario = Usuario.query.filter_by(usuario=usuario).first()
  buscar_perfil = Perfil.query.filter_by(nombre=buscar_usuario.perfil).first()
  session['perfil'] = buscar_perfil.nombre
  if(request.method == 'POST'):
    btn = request.form.get('btn')
    if (btn == 'calcular'):
      cant_tickets = (request.form.get('cant_tickets'))
      if(cant_tickets == ''):
        return render_template('usuario.html', usuario=usuario, perfil=buscar_usuario.perfil, precio=buscar_perfil.precio, cant_tickets=cant_tickets,  error1=True )
      else: 
        cant_tickets = int(cant_tickets)
        session['cant_tickets'] = cant_tickets
        precio_total = cant_tickets * buscar_perfil.precio
        session['precio_total'] = precio_total
        return render_template('usuario.html', usuario=usuario, perfil=buscar_usuario.perfil, precio=buscar_perfil.precio, cant_tickets=cant_tickets, precio_total=precio_total )
    elif (btn == 'pagar'):
      session['pago'] = 0
      return redirect(url_for('pago'))
    elif (btn in ['volver','cancelar']):
      session.clear()
      return redirect(url_for('index'))
  else:
    return render_template('usuario.html', usuario=usuario, perfil=buscar_usuario.perfil, precio=buscar_perfil.precio)

@app.route('/portal-pago', methods=['POST', 'GET'])
def pago():
  if (request.method == 'POST'):
    btn = (request.form.get('btn'))
    if(btn in ['500','1000','2000','5000']):
      session['pago'] += int(btn)
      return render_template('pago.html', precio_total=session['precio_total'], pago=session['pago'])
    elif(btn == 'pagar'):
      if (session['pago'] >= session['precio_total']):
        buscar_usuario = Usuario.query.filter_by(usuario=session['usuario']).first()
        buscar_perfil = Perfil.query.filter_by(nombre=buscar_usuario.perfil).first()
        buscar_usuario.cant_tickets = session['cant_tickets']
        buscar_usuario.total_compras = session['pago']
        buscar_perfil.tickets_vendidos += session['cant_tickets']
        buscar_perfil.dinero_total += session['pago']
        devuelta = session['pago'] - session['precio_total']
        db.session.commit()
        return render_template('pago.html', devuelta=devuelta, pagado=True)
      else:
        return render_template('pago.html', precio_total=session['precio_total'], pago=session['pago'], error1=True)
    elif(btn in ['volver','cancelar']):
      session.clear()  
      return redirect(url_for('index'))
  else:  
    return render_template('pago.html', precio_total=session['precio_total'])
  
@app.route('/registro-usuario', methods=['POST', 'GET'])
def registro():
  if(request.method == 'POST'):
    btn = request.form.get('btn')
    if(btn == 'registrarse'):
      usuario = request.form.get('usuario')
      buscar_usuario = Usuario.query.filter_by(usuario=usuario).first()
      if(buscar_usuario == None):
        perfil = request.form.get('perfiles')
        contrasenia = request.form.get('contrasenia')
        if(usuario == '' or perfil == '' or contrasenia == ''):
          return render_template('registro.html', error1=True)
        else:
          user = Usuario(usuario,contrasenia,perfil)
          db.session.add(user)
          db.session.commit()
          return render_template('registro.html', registrado=True, usuario=usuario)
      else:
        return render_template('registro.html', error2=True)
    elif(btn in ['volver','iniciar-sesion']):
      return redirect(url_for('index'))  
  else:  
    return render_template('registro.html')
if __name__ == '__main__':
  with app.app_context():
    db.create_all()
    
    perfiles = [
      Perfil('ocasional', 3250) ,
      Perfil('frecuente', 3100),
      Perfil('estudiante', 1500)
    ]   
    db.session.add_all(perfiles)
    db.session.commit() 
  app.run(debug = True)

