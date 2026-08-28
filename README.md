# 📊 Finanzas Personales — Dashboard Analítico Full-Stack

> Aplicación web completa para registrar **ingresos y gastos**, visualizarlos en un **dashboard interactivo**, **predecir el gasto del próximo mes** con regresión lineal y **detectar anomalías** en los consumos (Z-Score).

**Stack:** Flask (Python) · MySQL · Pandas · Scikit-learn · Chart.js · HTML/CSS/JS vanilla.

---

## ✨ Funcionalidades

- Registro e inicio de sesión de usuarios (contraseñas con hash `bcrypt`).
- CRUD de **categorías** e **ingresos/gastos** (movimientos) con filtros por fecha, categoría y tipo.
- Dashboard con **KPIs**: total de ingresos, total de gastos, balance (ahorro) y gasto proyectado.
- Gráfico **dona** con la distribución del gasto por categoría.
- Gráfico de **líneas** con la tendencia mensual de ingresos vs. gastos.
- **Predicción del gasto del próximo mes** mediante `LinearRegression` (scikit-learn).
- **Detección de anomalías** por desviación Z-score (|Z| > 2).
- API REST en JSON, arquitectura por capas (rutas → lógica → datos).
- Frontend responsivo (móvil / tablet / escritorio) y optimizado para SEO.

---

## 📁 Estructura del Repositorio

```text
finanzas/
├── app.py                 # Punto de entrada (raíz) — Render: gunicorn app:app
├── requirements.txt       # Dependencias (raíz) — build de Render
├── conexion.py            # Conexión a la BD (MySQL en producción / SQLite local)
├── backend/
│   ├── app.py             # Fábrica de la aplicación Flask + frontend estático
│   ├── config.py          # Configuración vía variables de entorno
│   ├── requirements.txt   # Copia de dependencias (opcional)
│   ├── rutas/             # Controladores de la API REST
│   │   ├── auth.py        #   registro / login / usuarios
│   │   ├── categorias.py  #   CRUD categorías
│   │   ├── movimientos.py #   CRUD movimientos con filtros
│   │   ├── resumen.py     #   totales, distribución y series mensuales
│   │   ├── analitica.py   #   predicción y anomalías
│   │   └── dashboard.py   #   endpoint combinado para una sola carga
│   ├── modelos/
│   │   ├── database.py    # Capa de datos: consultas + esquema + seed automático
│   │   └── repositorio.py # Consultas y escrituras de la base de datos
│   └── analitica/
│       ├── agregaciones.py # KPIs, distribución, series mensuales
│       ├── predictor.py    # Regresión lineal para la predicción
│       └── anomalias.py    # Detección de anomalías (Z-Score)
├── frontend/
│   ├── index.html          # Página con SEO y semántica HTML5
│   ├── css/style.css       # Estilos responsivos
│   ├── js/api.js           # Cliente fetch + sesión
│   ├── js/charts.js        # Gráficos Chart.js
│   ├── js/app.js           # Lógica del dashboard
│   └── img/favicon.svg
├── database/
│   ├── schema.sql          # DDL MySQL (opcional, la app lo crea solo)
│   └── seed.sql            # Datos de demostración (opcional)
├── Procfile                # Comando de arranque para Render
├── render.yaml             # Blueprint de Render (opcional)
└── README.md
```

> 💡 **`app.py`, `requirements.txt` y `conexion.py` están en la raíz del repositorio** para que Render los detecte automáticamente al subir el proyecto (manual o por Git). La aplicación crea las tablas y los datos demo automáticamente al primer arranque. Los archivos de `database/` son opcionales.

---

## 🚀 Despliegue en Render (paso a paso)

### 1. Sube el proyecto a GitHub

```bash
git init
git add .
git commit -m "Proyecto Finanzas Personales"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/finanzas-personales.git
git push -u origin main
```

### 2. Crea tu base de datos MySQL en un proveedor gratuito

Necesitas un MySQL accesible desde internet. Opciones gratuitas:
[Aiven](https://aiven.io), [Railway](https://railway.app) (MySQL), Clever Cloud, o tu hosting.

Cuando lo tengas, anota estos 5 datos:

| Variable | Ejemplo |
|---|---|
| `MYSQL_HOST` | `mysql-xxxxx.aivencloud.com` |
| `MYSQL_PORT` | `3306` |
| `MYSQL_USER` | `avnadmin` |
| `MYSQL_PASSWORD` | `****` |
| `MYSQL_DATABASE` | `finanzas_personales` (o el que crees) |

No necesitas importar los scripts SQL: **la aplicación crea las tablas y los datos demo sola**. (Si prefieres, puedes ejecutar `database/schema.sql` y `database/seed.sql`.)

### 3. Crea el Web Service en Render

1. En [render.com](https://render.com) → **New** → **Web Service** → conecta tu repositorio de GitHub.
2. Configura:

| Campo | Valor |
|---|---|
| **Build command** | `pip install -r requirements.txt` |
| **Start command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |

> La raíz del repositorio ya contiene `app.py`, `requirements.txt` y `conexion.py`, por lo que Render los detecta sin configuración adicional (subida manual a Web Service o Blueprint).

3. En **Environment** agrega las variables:

```
MYSQL_HOST
MYSQL_PORT
MYSQL_USER
MYSQL_PASSWORD
MYSQL_DATABASE
SECRET_KEY   (por ejemplo: una cadena aleatoria larga)
SEED_DEMO=true
```

> Si tu proveedor de MySQL exige TLS/SSL, agrega también `MYSQL_SSL=true`. Si prefieres no usar `MYSQL_HOST` etc., define solo `DATABASE_URL=mysql://usuario:pass@host:puerto/bd`.

4. **Deploy** → espera la construcción. Al terminar, entra a la URL que Render te da
   (p. ej. `https://finanzas-personales.onrender.com`).

> También puedes usar el archivo `render.yaml` de este repositorio (**New → Blueprint**) — de todos modos te pedirá las variables de conexión.

### 4. Inicia sesión con los datos demo

```
Correo:      ana@example.com
Contraseña:  123456
```

---

## 🧪 Ejecución local (sin MySQL)

Si no defines variables `MYSQL_*`, la app usa automáticamente **SQLite** (modo desarrollo):

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python app.py
```

Abre <http://localhost:8000>. (Opcional: copia `.env.example` a `.env` y rellena una conexión MySQL para probar el motor real.)

---

## 🔌 API REST

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/usuarios` | Registrar usuario `{nombre, correo, contrasena}` |
| `POST` | `/api/usuarios/login` | Login `{correo, contrasena}` → devuelve usuario |
| `GET` | `/api/usuarios` | Listar usuarios |
| `GET` | `/api/categorias?id_usuario=` | Categorías del usuario |
| `POST` | `/api/categorias` | Crear categoría `{id_usuario, nombre, tipo}` |
| `PUT` | `/api/categorias/{id}` | Actualizar categoría |
| `DELETE` | `/api/categorias/{id}?id_usuario=` | Eliminar (bloqueado si tiene movimientos) |
| `GET` | `/api/movimientos?id_usuario=&desde=&hasta=&categoria=&tipo=` | Movimientos con filtros |
| `POST` | `/api/movimientos` | Registrar movimiento `{id_usuario, id_categoria, tipo, monto, fecha, descripcion}` |
| `PUT` | `/api/movimientos/{id}` | Actualizar movimiento |
| `DELETE` | `/api/movimientos/{id}?id_usuario=` | Eliminar movimiento |
| `GET` | `/api/resumen?id_usuario=&mes=` | Totales: ingresos, gastos, balance |
| `GET` | `/api/resumen/categorias?id_usuario=` | Gasto por categoría |
| `GET` | `/api/resumen/mensual?id_usuario=` | Series mensuales |
| `GET` | `/api/analitica/prediccion?id_usuario=` | Predicción del próximo mes |
| `GET` | `/api/analitica/anomalias?id_usuario=` | Movimientos anómalos |
| `GET` | `/api/dashboard?id_usuario=` | Todo el panel en una sola llamada |
| `GET` | `/api/salud` | Estado del servicio y de la base de datos |

---

## 🔐 Seguridad y buenas prácticas

- Contraseñas almacenadas con **bcrypt**.
- Entrada validada en el backend (montos, fechas, tipos, longitudes).
- Errores de la API siempre como JSON con códigos HTTP correctos.
- Transacciones SQL con `rollback` ante fallos.
- No se sube `.env`, `.gitignore` ignora secretos y archivos de base de datos.
- SQL parametrizado (protección contra inyección).

---

## 📊 Rúbrica del proyecto (cómo se cubre)

| Criterio | Cómo se cumple |
|---|---|
| Modelo de BD (15) | 3FN: `usuarios`, `categorias`, `ingresos_gastos`, llaves e índices analíticos. |
| API REST (20) | Endpoints JSON con GET/POST/PUT/DELETE y manejo de errores. |
| Frontend e integración (20) | CRUD operativo desde la página, estados asíncronos y UX responsive. |
| Módulo analítico (25) | Regresión lineal para predicción + Z-Score para anomalías. |
| Visualización (10) | Chart.js: dona por categoría y líneas ingresos vs gastos. |
| Documentación (10) | Este README + código comentado en español. |

---

## 📦 Dependencias

`Flask` · `flask-cors` · `mysql-connector-python` · `pandas` · `scikit-learn` · `bcrypt` · `gunicorn` · `python-dotenv`

> El frontend usa **Chart.js 4** desde CDN, sin instalación local.

---

## ❓ Solución de problemas

- **`base_de_datos: "error"` en `/api/salud`** → revisa `MYSQL_HOST`, `MYSQL_PASSWORD`, etc. en Render y que el host permita conexiones externas (y el firewall del proveedor).
- **La página carga pero el dashboard dice "Error..."** → revisa los logs de Render; en general es la conexión a MySQL.
- **Error de SSL** → activa `MYSQL_SSL=true`.
- **Tiempo de arranque lento** → normal: Render instala pandas y scikit-learn la primera vez.
```