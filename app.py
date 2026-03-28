from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from functools import wraps
from config import Config
import database
import models.usuarios as UsuariosModel
import models.doctores as DoctoresModel
import models.citas as CitasModel

app = Flask(__name__)
app.config.from_object(Config)
database.init_app(app)

# ============================================================
# NO-CACHE GLOBAL: todas las rutas privadas (/paciente, /doctor, /admin, /dashboard)
# Esto garantiza que el navegador nunca cachee páginas protegidas.
# Cuando el usuario presiona Atrás después de logout, el navegador
# se ve forzado a recargar y Flask lo redirige al login.
# ============================================================
PRIVATE_PREFIXES = ('/paciente', '/doctor', '/admin', '/dashboard', '/api')

@app.after_request
def set_no_cache(response):
    """Inyecta headers no-cache en TODAS las respuestas de rutas privadas,
    incluyendo redirects (302). Esto es lo que realmente funciona."""
    path = request.path
    if any(path.startswith(p) for p in PRIVATE_PREFIXES):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
        response.headers['Pragma']  = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# ============================================================
# DECORADORES
# ============================================================
def no_cache(f):
    """Mantener por compatibilidad — el after_request ya cubre todo."""
    return f

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion para acceder.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def rol_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'rol' not in session or session['rol'] not in roles:
                flash('No tienes permisos para acceder.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ============================================================
# LANDING & PAGINAS PUBLICAS
# ============================================================
@app.route('/')
def index():
    doctores = DoctoresModel.get_todos_doctores()[:4]
    return render_template('landing.html', doctores=doctores)

@app.route('/doctores')
def pagina_doctores():
    doctores = DoctoresModel.get_todos_doctores()
    return render_template('pages/doctores.html', doctores=doctores)

@app.route('/servicios')
def pagina_servicios():
    return render_template('pages/servicios.html')

@app.route('/contacto')
def pagina_contacto():
    return render_template('pages/contacto.html')

# ============================================================
# AUTH
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        correo   = request.form.get('correo', '').strip()
        password = request.form.get('password', '')
        usuario  = UsuariosModel.get_usuario_by_correo(correo)
        if usuario and UsuariosModel.verificar_password(usuario, password):
            session['usuario_id'] = usuario['id']
            session['nombre']     = usuario['nombre']
            session['apellido']   = usuario['apellido']
            session['rol']        = usuario['rol']
            session['documento']  = usuario['documento']
            flash(f"Bienvenido, {usuario['nombre']}!", 'success')
            return redirect(url_for('dashboard'))
        flash('Correo o contrasena incorrectos.', 'danger')
    return render_template('auth/login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        documento = request.form.get('documento', '').strip()
        nombre    = request.form.get('nombre', '').strip()
        apellido  = request.form.get('apellido', '').strip()
        telefono  = request.form.get('telefono', '').strip()
        correo    = request.form.get('correo', '').strip()
        password  = request.form.get('password', '')
        eps       = request.form.get('eps', '').strip()
        if UsuariosModel.get_usuario_by_doc(documento):
            flash('Ya existe un usuario con ese documento.', 'danger')
            return render_template('auth/registro.html')
        if UsuariosModel.get_usuario_by_correo(correo):
            flash('Ya existe un usuario con ese correo.', 'danger')
            return render_template('auth/registro.html')
        UsuariosModel.crear_usuario(documento, nombre, apellido, telefono, correo, password, 'paciente', eps)
        flash('Registro exitoso. Ya puedes iniciar sesion.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/registro.html')

@app.route('/logout')
def logout():
    session.clear()
    # Respuesta con headers no-cache y script replace para limpiar historial
    resp = make_response(render_template('auth/logged_out.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    resp.headers['Pragma']  = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/dashboard')
@login_required
def dashboard():
    rol = session.get('rol')
    if rol == 'paciente':  return redirect(url_for('paciente_dashboard'))
    if rol == 'doctor':    return redirect(url_for('doctor_dashboard'))
    if rol == 'admin':     return redirect(url_for('admin_dashboard'))
    return redirect(url_for('index'))

# ============================================================
# PACIENTE
# ============================================================
@app.route('/paciente/dashboard')
@login_required
@rol_required('paciente')
@no_cache
def paciente_dashboard():
    proximas = CitasModel.get_citas_proximas_paciente(session['documento'])
    todas    = CitasModel.get_citas_paciente(session['documento'])
    return render_template('paciente/dashboard.html', proximas=proximas, todas=todas)

@app.route('/paciente/mis-citas')
@login_required
@rol_required('paciente')
@no_cache
def paciente_mis_citas():
    citas = CitasModel.get_citas_paciente(session['documento'])
    return render_template('paciente/mis_citas.html', citas=citas)

@app.route('/paciente/reservar', methods=['GET', 'POST'])
@login_required
@rol_required('paciente')
@no_cache
def paciente_reservar():
    especialidades = DoctoresModel.get_especialidades()
    if request.method == 'POST':
        doctor_id   = request.form.get('doctor_id')
        tipo_cita   = request.form.get('tipo_cita', '').strip()
        fecha       = request.form.get('fecha', '').strip()
        hora        = request.form.get('hora', '').strip()
        direccion   = request.form.get('direccion_eps', '').strip()
        if not all([doctor_id, tipo_cita, fecha, hora]):
            flash('Todos los campos son obligatorios.', 'danger')
        else:
            CitasModel.crear_cita(session['documento'], doctor_id, tipo_cita, fecha, hora, direccion)
            flash('Cita reservada exitosamente.', 'success')
            return redirect(url_for('paciente_dashboard'))
    return render_template('paciente/reservar.html', especialidades=especialidades)

@app.route('/paciente/cancelar/<int:cita_id>', methods=['POST'])
@login_required
@rol_required('paciente')
def paciente_cancelar_cita(cita_id):
    CitasModel.cancelar_cita(cita_id, session['documento'])
    flash('Cita cancelada.', 'info')
    return redirect(url_for('paciente_mis_citas'))

@app.route('/paciente/perfil', methods=['GET', 'POST'])
@login_required
@rol_required('paciente')
@no_cache
def paciente_perfil():
    usuario = UsuariosModel.get_usuario_by_id(session['usuario_id'])
    if request.method == 'POST':
        UsuariosModel.actualizar_usuario(
            session['usuario_id'],
            request.form.get('nombre','').strip(),
            request.form.get('apellido','').strip(),
            request.form.get('telefono','').strip(),
            request.form.get('eps','').strip()
        )
        session['nombre']   = request.form.get('nombre','').strip()
        session['apellido'] = request.form.get('apellido','').strip()
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('paciente_perfil'))
    return render_template('paciente/perfil.html', usuario=usuario)

@app.route('/api/doctores/<especialidad>')
@login_required
def api_doctores_especialidad(especialidad):
    doctores = DoctoresModel.get_doctores_por_especialidad(especialidad)
    return jsonify(doctores)

# ============================================================
# DOCTOR
# ============================================================
@app.route('/doctor/dashboard')
@login_required
@rol_required('doctor')
@no_cache
def doctor_dashboard():
    doctor = DoctoresModel.get_doctor_by_usuario_id(session['usuario_id'])
    if not doctor:
        flash('Perfil de doctor no encontrado.', 'danger')
        return redirect(url_for('logout'))
    citas_hoy = CitasModel.get_citas_doctor_hoy(doctor['id'])
    stats     = CitasModel.get_estadisticas_doctor(doctor['id'])
    return render_template('doctor/dashboard.html', doctor=doctor, citas_hoy=citas_hoy, stats=stats)

@app.route('/doctor/agenda')
@login_required
@rol_required('doctor')
@no_cache
def doctor_agenda():
    doctor      = DoctoresModel.get_doctor_by_usuario_id(session['usuario_id'])
    citas_semana = CitasModel.get_citas_doctor_semana(doctor['id'])
    return render_template('doctor/agenda.html', doctor=doctor, citas_semana=citas_semana)

@app.route('/doctor/marcar-atendido/<int:cita_id>', methods=['POST'])
@login_required
@rol_required('doctor')
def doctor_marcar_atendido(cita_id):
    notas = request.form.get('notas', '')
    CitasModel.marcar_estado_cita(cita_id, 'atendida', notas)
    flash('Paciente marcado como atendido.', 'success')
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/marcar-no-asistio/<int:cita_id>', methods=['POST'])
@login_required
@rol_required('doctor')
def doctor_marcar_no_asistio(cita_id):
    doctor = DoctoresModel.get_doctor_by_usuario_id(session['usuario_id'])
    cita   = CitasModel.get_cita_by_id(cita_id)
    if cita:
        siguiente = CitasModel.manejar_no_asistio(cita_id, doctor['id'], cita['fecha'], cita['hora'])
        if siguiente:
            flash('Marcado como no asistio. El siguiente paciente fue adelantado.', 'info')
        else:
            flash('Marcado como no asistio.', 'info')
    return redirect(url_for('doctor_dashboard'))

@app.route('/doctor/historial/<paciente_doc>')
@login_required
@rol_required('doctor')
@no_cache
def doctor_historial_paciente(paciente_doc):
    doctor   = DoctoresModel.get_doctor_by_usuario_id(session['usuario_id'])
    paciente = UsuariosModel.get_usuario_by_doc(paciente_doc)
    citas    = CitasModel.get_historial_paciente_doctor(paciente_doc, doctor['id'])
    return render_template('doctor/historial_paciente.html', paciente=paciente, citas=citas)

@app.route('/doctor/editar-cita/<int:cita_id>', methods=['GET', 'POST'])
@login_required
@rol_required('doctor')
@no_cache
def doctor_editar_cita(cita_id):
    cita = CitasModel.get_cita_by_id(cita_id)
    if request.method == 'POST':
        CitasModel.actualizar_cita(
            cita_id,
            request.form.get('fecha'),
            request.form.get('hora'),
            request.form.get('tipo_cita'),
            request.form.get('notas', '')
        )
        flash('Cita actualizada.', 'success')
        return redirect(url_for('doctor_agenda'))
    return render_template('doctor/editar_cita.html', cita=cita)

@app.route('/doctor/perfil', methods=['GET', 'POST'])
@login_required
@rol_required('doctor')
@no_cache
def doctor_perfil():
    doctor  = DoctoresModel.get_doctor_by_usuario_id(session['usuario_id'])
    usuario = UsuariosModel.get_usuario_by_id(session['usuario_id'])
    if request.method == 'POST':
        DoctoresModel.actualizar_doctor(doctor['id'], request.form.get('especialidad'), request.form.get('consultorio'))
        UsuariosModel.actualizar_usuario(session['usuario_id'], request.form.get('nombre'), request.form.get('apellido'), request.form.get('telefono'), usuario['eps'])
        flash('Perfil actualizado.', 'success')
        return redirect(url_for('doctor_perfil'))
    return render_template('doctor/perfil.html', doctor=doctor, usuario=usuario)

# ============================================================
# ADMIN
# ============================================================
@app.route('/admin/dashboard')
@login_required
@rol_required('admin')
@no_cache
def admin_dashboard():
    citas_recientes = CitasModel.get_todas_citas()[:10]
    reporte  = CitasModel.get_reporte_mensual()[:6]
    doctores = DoctoresModel.get_todos_doctores()
    return render_template('admin/dashboard.html', citas_recientes=citas_recientes, reporte=reporte, doctores=doctores)

@app.route('/admin/usuarios')
@login_required
@rol_required('admin')
@no_cache
def admin_usuarios():
    usuarios = UsuariosModel.get_todos_usuarios()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@rol_required('admin')
def admin_nuevo_usuario():
    if request.method == 'POST':
        documento    = request.form.get('documento','').strip()
        nombre       = request.form.get('nombre','').strip()
        apellido     = request.form.get('apellido','').strip()
        telefono     = request.form.get('telefono','').strip()
        correo       = request.form.get('correo','').strip()
        password     = request.form.get('password','')
        rol          = request.form.get('rol','paciente')
        eps          = request.form.get('eps','').strip()
        especialidad = request.form.get('especialidad','').strip()
        consultorio  = request.form.get('consultorio','').strip()
        uid = UsuariosModel.crear_usuario(documento, nombre, apellido, telefono, correo, password, rol, eps)
        if rol == 'doctor' and especialidad:
            DoctoresModel.crear_doctor(uid, especialidad, consultorio)
        flash('Usuario creado exitosamente.', 'success')
        return redirect(url_for('admin_usuarios'))
    return render_template('admin/nuevo_usuario.html')

@app.route('/admin/usuarios/editar/<int:uid>', methods=['POST'])
@login_required
@rol_required('admin')
def admin_editar_usuario(uid):
    nombre       = request.form.get('nombre','').strip()
    apellido     = request.form.get('apellido','').strip()
    telefono     = request.form.get('telefono','').strip()
    eps          = request.form.get('eps','').strip()
    rol          = request.form.get('rol','').strip()
    especialidad = request.form.get('especialidad','').strip()
    consultorio  = request.form.get('consultorio','').strip()
    UsuariosModel.actualizar_usuario(uid, nombre, apellido, telefono, eps)
    from database import query_db
    query_db('UPDATE usuarios SET rol=%s WHERE id=%s', (rol, uid), commit=True)
    if rol == 'doctor' and especialidad:
        doctor = DoctoresModel.get_doctor_by_usuario_id(uid)
        if doctor:
            DoctoresModel.actualizar_doctor(doctor['id'], especialidad, consultorio)
        else:
            DoctoresModel.crear_doctor(uid, especialidad, consultorio)
    flash('Usuario actualizado correctamente.', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/toggle/<int:uid>', methods=['POST'])
@login_required
@rol_required('admin')
def admin_toggle_usuario(uid):
    usuario = UsuariosModel.get_usuario_by_id(uid)
    if usuario['activo']:
        UsuariosModel.desactivar_usuario(uid)
        flash('Usuario desactivado.', 'info')
    else:
        UsuariosModel.activar_usuario(uid)
        flash('Usuario activado.', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/citas')
@login_required
@rol_required('admin')
@no_cache
def admin_citas():
    fecha     = request.args.get('fecha','')
    doctor_id = request.args.get('doctor_id','')
    estado    = request.args.get('estado','')
    citas = CitasModel.get_todas_citas(
        fecha     if fecha     else None,
        int(doctor_id) if doctor_id else None,
        estado    if estado    else None
    )
    doctores = DoctoresModel.get_todos_doctores()
    return render_template('admin/citas.html', citas=citas, doctores=doctores,
                           filtro_fecha=fecha, filtro_doctor=doctor_id, filtro_estado=estado)

@app.route('/admin/reportes')
@login_required
@rol_required('admin')
@no_cache
def admin_reportes():
    mensual    = CitasModel.get_reporte_mensual()
    por_doctor = CitasModel.get_reporte_por_doctor()
    return render_template('admin/reportes.html', mensual=mensual, por_doctor=por_doctor)

if __name__ == '__main__':
    app.run(debug=True)
