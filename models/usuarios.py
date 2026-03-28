from database import query_db
from werkzeug.security import generate_password_hash, check_password_hash

def get_usuario_by_correo(correo):
    return query_db('SELECT * FROM usuarios WHERE correo=%s AND activo=1', (correo,), one=True)

def get_usuario_by_doc(documento):
    return query_db('SELECT * FROM usuarios WHERE documento=%s AND activo=1', (documento,), one=True)

def get_usuario_by_id(uid):
    return query_db('SELECT * FROM usuarios WHERE id=%s', (uid,), one=True)

def crear_usuario(documento, nombre, apellido, telefono, correo, password, rol, eps):
    hashed = generate_password_hash(password)
    return query_db(
        'INSERT INTO usuarios (documento, nombre, apellido, telefono, correo, password, rol, eps) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
        (documento, nombre, apellido, telefono, correo, hashed, rol, eps),
        commit=True
    )

def actualizar_usuario(uid, nombre, apellido, telefono, eps):
    query_db(
        'UPDATE usuarios SET nombre=%s, apellido=%s, telefono=%s, eps=%s WHERE id=%s',
        (nombre, apellido, telefono, eps, uid),
        commit=True
    )

def verificar_password(usuario, password):
    return check_password_hash(usuario['password'], password)

def get_todos_usuarios():
    return query_db('SELECT id, documento, nombre, apellido, correo, rol, eps, activo, created_at FROM usuarios ORDER BY created_at DESC')

def desactivar_usuario(uid):
    query_db('UPDATE usuarios SET activo=0 WHERE id=%s', (uid,), commit=True)

def activar_usuario(uid):
    query_db('UPDATE usuarios SET activo=1 WHERE id=%s', (uid,), commit=True)
