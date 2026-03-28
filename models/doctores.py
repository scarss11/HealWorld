from database import query_db

def get_todos_doctores():
    return query_db('''
        SELECT d.id, d.especialidad, d.consultorio,
               u.nombre, u.apellido, u.correo, u.telefono, u.documento
        FROM doctores d JOIN usuarios u ON d.usuario_id = u.id
        WHERE u.activo = 1
        ORDER BY d.especialidad, u.apellido
    ''')

def get_doctor_by_id(doctor_id):
    return query_db('''
        SELECT d.id, d.especialidad, d.consultorio, d.usuario_id,
               u.nombre, u.apellido, u.correo, u.telefono, u.documento
        FROM doctores d JOIN usuarios u ON d.usuario_id = u.id
        WHERE d.id = %s
    ''', (doctor_id,), one=True)

def get_doctor_by_usuario_id(usuario_id):
    return query_db('SELECT * FROM doctores WHERE usuario_id=%s', (usuario_id,), one=True)

def get_doctores_por_especialidad(especialidad):
    return query_db('''
        SELECT d.id, d.especialidad, d.consultorio,
               u.nombre, u.apellido
        FROM doctores d JOIN usuarios u ON d.usuario_id = u.id
        WHERE d.especialidad = %s AND u.activo = 1
        ORDER BY u.apellido
    ''', (especialidad,))

def get_especialidades():
    rows = query_db('SELECT DISTINCT especialidad FROM doctores ORDER BY especialidad')
    return [r['especialidad'] for r in rows]

def crear_doctor(usuario_id, especialidad, consultorio):
    return query_db(
        'INSERT INTO doctores (usuario_id, especialidad, consultorio) VALUES (%s,%s,%s)',
        (usuario_id, especialidad, consultorio),
        commit=True
    )

def actualizar_doctor(doctor_id, especialidad, consultorio):
    query_db(
        'UPDATE doctores SET especialidad=%s, consultorio=%s WHERE id=%s',
        (especialidad, consultorio, doctor_id),
        commit=True
    )
