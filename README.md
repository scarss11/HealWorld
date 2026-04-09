# 🏥 EPS Sura — Sistema de Gestión de Citas Médicas
### Sistema web completo para gestión de citas con diseño corporativo estilo Sura.

Este proyecto es una solución integral para la administración de salud, permitiendo la interacción fluida entre pacientes, doctores y administradores. Desarrollado con **Flask** y **MySQL**.

---

## 📸 Capturas del Sistema
* **Landing Page:** Hero section, servicios y sección de doctores destacados.
* **Dashboard Paciente:** Gestión de próximas citas, historial y motor de reservas.
* **Dashboard Doctor:** Agenda diaria, control de asistencia en tiempo real e historial clínico.
* **Dashboard Admin:** Panel de control total, gestión de usuarios y analítica de reportes.

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/eps-citas-app.git
cd eps-citas-app
```

### 2. Entorno Virtual
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Base de Datos (MySQL)
Importa el esquema inicial a tu servidor local:
```bash
mysql -u root -p < database.sql
```

### 4. Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_DB=eps_citas
MYSQL_PORT=3306
SECRET_KEY=una_clave_segura_larga_y_aleatoria
```

### 5. Configuración de Contraseñas
Para asegurar que los datos de prueba funcionen, ejecuta este script una sola vez para actualizar los hashes:
```python
# fix_passwords.py
import mysql.connector
from werkzeug.security import generate_password_hash

db = mysql.connector.connect(
    host='localhost', 
    user='root', 
    password='tu_password', 
    database='eps_citas'
)
cur = db.cursor()
hashed = generate_password_hash('password123')
cur.execute("UPDATE usuarios SET password = %s", (hashed,))
db.commit()
print("✅ Passwords actualizados a 'password123'")
```

---

## 👤 Cuentas de Acceso (Prueba)

| Rol | Correo | Contraseña |
| :--- | :--- | :--- |
| **Admin** | `admin@eps.com` | `password123` |
| **Paciente** | `juan.perez@gmail.com` | `password123` |
| **Doctor** | `maria.gonzalez@eps.com` | `password123` |

---

## 📁 Estructura del Proyecto

```text
eps_citas_app/
├── app.py                 # Punto de entrada y rutas
├── config.py              # Clases de configuración
├── database.py            # Conexión y métodos CRUD
├── database.sql           # Script de creación de DB
├── models/                # Lógica de negocio por entidad
│   ├── usuarios.py
│   ├── doctores.py
│   └── citas.py
├── templates/             # Vistas Jinja2
│   ├── base_landing.html
│   ├── base_dashboard.html
│   └── ... (carpetas por rol)
├── static/                # Recursos estáticos
│   ├── css/               # landing.css, dashboard.css
│   └── js/                # main.js
└── requirements.txt       # Dependencias
```

---

## ⚙️ Funcionalidades Principales

### 🔹 Pacientes
* **Reservas Inteligentes:** Filtro por especialidad → doctor → disponibilidad.
* **Historial:** Consulta de citas pasadas y estados.
* **Perfil:** Gestión de datos personales y contacto.

### 🔹 Doctores
* **Gestión de Turnos:** Marcar "Atendido" o "No Asistió".
* **Auto-Adelantamiento:** Al cancelar un turno, el sistema reorganiza la cola.
* **Agenda:** Vista semanal de compromisos médicos.

### 🔹 Administradores
* **Control de Acceso:** Crear, activar o suspender cuentas.
* **Reportes:** Estadísticas de rendimiento médico y flujo mensual de citas.

---

## 🎨 Especificaciones de Diseño
* **Paleta:** Azul Sura (`#0033A0`) y Azul Claro (`#00A3E0`).
* **Interfaz:** Sidebar fijo, sombras suaves (Glassmorphism sutil) y tipografía **Inter**.
* **UX:** Badges de estado dinámicos (Pendiente: Amarillo, Atendido: Verde, Cancelado: Rojo).

---

## 🛠️ Tecnologías
* **Backend:** Python 3.10+ / Flask 3.0
* **DB:** MySQL 8.0
* **Seguridad:** Werkzeug (PBKDF2-SHA256), Flask-Session.
* **Frontend:** Jinja2, CSS3 (Flexbox/Grid), JS Vanilla.

---
**HealWorld** | *Licencia MIT — Proyecto Educativo*