from database import query_db
import datetime

def _format_hora(cita):
    """Convierte timedelta a string HH:MM (psycopg2 devuelve time como datetime.time)"""
    if cita and 'hora' in cita:
        h = cita['hora']
        if isinstance(h, datetime.timedelta):
            total = int(h.total_seconds())
            cita['hora'] = '%02d:%02d' % (total // 3600, (total % 3600) // 60)
        elif isinstance(h, datetime.time):
            cita['hora'] = h.strftime('%H:%M')
    return cita

def _format_horas(citas):
    return [_format_hora(c) for c in citas] if citas else []

def get_citas_paciente(paciente_doc):
    citas = query_db('''
        SELECT c.*, d.especialidad, d.consultorio,
               u.nombre AS doctor_nombre, u.apellido AS doctor_apellido
        FROM citas c
        JOIN doctores d ON c.doctor_id = d.id
        JOIN usuarios u ON d.usuario_id = u.id
        WHERE c.paciente_doc = %s
        ORDER BY c.fecha DESC, c.hora DESC
    ''', (paciente_doc,))
    return _format_horas(citas)

def get_citas_proximas_paciente(paciente_doc):
    citas = query_db('''
        SELECT c.*, d.especialidad, d.consultorio,
               u.nombre AS doctor_nombre, u.apellido AS doctor_apellido
        FROM citas c
        JOIN doctores d ON c.doctor_id = d.id
        JOIN usuarios u ON d.usuario_id = u.id
        WHERE c.paciente_doc = %s AND c.fecha >= CURRENT_DATE AND c.estado = 'pendiente'
        ORDER BY c.fecha ASC, c.hora ASC
    ''', (paciente_doc,))
    return _format_horas(citas)

def get_citas_doctor_hoy(doctor_id):
    citas = query_db('''
        SELECT c.*, u.nombre AS paciente_nombre, u.apellido AS paciente_apellido,
               u.telefono AS paciente_tel, u.documento AS paciente_doc_num
        FROM citas c
        JOIN usuarios u ON c.paciente_doc = u.documento
        WHERE c.doctor_id = %s AND c.fecha = CURRENT_DATE
        ORDER BY c.hora ASC
    ''', (doctor_id,))
    return _format_horas(citas)

def get_citas_doctor_semana(doctor_id):
    citas = query_db('''
        SELECT c.*, u.nombre AS paciente_nombre, u.apellido AS paciente_apellido,
               u.documento AS paciente_doc_num
        FROM citas c
        JOIN usuarios u ON c.paciente_doc = u.documento
        WHERE c.doctor_id = %s
          AND c.fecha >= CURRENT_DATE
          AND c.fecha <= CURRENT_DATE + INTERVAL '7 days'
        ORDER BY c.fecha ASC, c.hora ASC
    ''', (doctor_id,))
    return _format_horas(citas)

def get_historial_paciente_doctor(paciente_doc, doctor_id):
    citas = query_db('''
        SELECT c.*, d.especialidad
        FROM citas c
        JOIN doctores d ON c.doctor_id = d.id
        WHERE c.paciente_doc = %s AND c.doctor_id = %s
        ORDER BY c.fecha DESC, c.hora DESC
    ''', (paciente_doc, doctor_id))
    return _format_horas(citas)

def get_cita_by_id(cita_id):
    cita = query_db('SELECT * FROM citas WHERE id=%s', (cita_id,), one=True)
    return _format_hora(cita)

def crear_cita(paciente_doc, doctor_id, tipo_cita, fecha, hora, direccion_eps):
    return query_db(
        'INSERT INTO citas (paciente_doc, doctor_id, tipo_cita, fecha, hora, direccion_eps) VALUES (%s,%s,%s,%s,%s,%s)',
        (paciente_doc, doctor_id, tipo_cita, fecha, hora, direccion_eps),
        commit=True
    )

def cancelar_cita(cita_id, paciente_doc):
    query_db(
        "UPDATE citas SET estado='cancelada' WHERE id=%s AND paciente_doc=%s AND estado='pendiente'",
        (cita_id, paciente_doc), commit=True
    )

def marcar_estado_cita(cita_id, estado, notas=None):
    query_db(
        'UPDATE citas SET estado=%s, notas=%s WHERE id=%s',
        (estado, notas, cita_id), commit=True
    )

def manejar_no_asistio(cita_id, doctor_id, fecha, hora_liberada):
    marcar_estado_cita(cita_id, 'no_asistio', 'No se presentó a la cita')
    siguiente = query_db('''
        SELECT id FROM citas
        WHERE doctor_id=%s AND fecha=%s AND estado='pendiente' AND hora > %s
        ORDER BY hora ASC LIMIT 1
    ''', (doctor_id, fecha, hora_liberada), one=True)
    if siguiente:
        query_db(
            "UPDATE citas SET hora=%s, notas=COALESCE(notas,'') || ' | Hora actualizada por turno liberado' WHERE id=%s",
            (hora_liberada, siguiente['id']), commit=True
        )
    return siguiente

def get_todas_citas(fecha=None, doctor_id=None, estado=None):
    where = ['1=1']
    params = []
    if fecha:
        where.append('c.fecha = %s'); params.append(fecha)
    if doctor_id:
        where.append('c.doctor_id = %s'); params.append(doctor_id)
    if estado:
        where.append('c.estado = %s'); params.append(estado)
    citas = query_db(f'''
        SELECT c.*,
               up.nombre AS paciente_nombre, up.apellido AS paciente_apellido,
               ud.nombre AS doctor_nombre,   ud.apellido AS doctor_apellido,
               d.especialidad
        FROM citas c
        JOIN usuarios up ON c.paciente_doc = up.documento
        JOIN doctores d  ON c.doctor_id = d.id
        JOIN usuarios ud ON d.usuario_id = ud.id
        WHERE {" AND ".join(where)}
        ORDER BY c.fecha DESC, c.hora DESC
    ''', tuple(params))
    return _format_horas(citas)

def get_estadisticas_doctor(doctor_id):
    stats = query_db('''
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN estado='atendida'   THEN 1 ELSE 0 END) AS atendidas,
            SUM(CASE WHEN estado='no_asistio' THEN 1 ELSE 0 END) AS no_asistencias,
            SUM(CASE WHEN estado='cancelada'  THEN 1 ELSE 0 END) AS canceladas,
            SUM(CASE WHEN estado='pendiente'  THEN 1 ELSE 0 END) AS pendientes,
            SUM(CASE WHEN EXTRACT(MONTH FROM fecha)=EXTRACT(MONTH FROM CURRENT_DATE)
                      AND EXTRACT(YEAR  FROM fecha)=EXTRACT(YEAR  FROM CURRENT_DATE)
                     THEN 1 ELSE 0 END) AS este_mes
        FROM citas WHERE doctor_id=%s
    ''', (doctor_id,), one=True)
    return stats

def get_reporte_mensual():
    return query_db('''
        SELECT TO_CHAR(fecha, 'YYYY-MM') AS mes,
               COUNT(*) AS total,
               SUM(CASE WHEN estado='atendida'   THEN 1 ELSE 0 END) AS atendidas,
               SUM(CASE WHEN estado='no_asistio' THEN 1 ELSE 0 END) AS no_asistencias
        FROM citas
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT 12
    ''')

def get_reporte_por_doctor():
    return query_db('''
        SELECT u.nombre, u.apellido, d.especialidad,
               COUNT(*) AS total,
               SUM(CASE WHEN c.estado='atendida'   THEN 1 ELSE 0 END) AS atendidas,
               SUM(CASE WHEN c.estado='no_asistio' THEN 1 ELSE 0 END) AS no_asistencias
        FROM citas c
        JOIN doctores d ON c.doctor_id = d.id
        JOIN usuarios u ON d.usuario_id = u.id
        GROUP BY c.doctor_id, u.nombre, u.apellido, d.especialidad
        ORDER BY total DESC
    ''')

def actualizar_cita(cita_id, fecha, hora, tipo_cita, notas):
    query_db(
        'UPDATE citas SET fecha=%s, hora=%s, tipo_cita=%s, notas=%s WHERE id=%s',
        (fecha, hora, tipo_cita, notas, cita_id), commit=True
    )
