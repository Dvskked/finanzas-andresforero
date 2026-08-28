# Aplicación Web de Finanzas Personales con Dashboard Analítico

Aplicación web completa de **finanzas personales** con un **dashboard analítico**
(predicción de gastos mediante regresión lineal y detección de anomalías con
Z-Score). Incluye backend en **Flask**, frontend responsivo en **HTML/CSS/JS**
con **Chart.js**, y base de datos **MySQL** en **Clever Cloud**.

Lista para desplegar como **Web Service en Render** y subir a **GitHub**.

---

## 🧩 Características

- Registro e inicio de sesión de usuarios (`bcrypt` para hash de contraseñas).
- CRUD de movimientos (ingresos y gastos) con categorías.
- **Dashboard analítico**:
  - Totales de ingresos, gastos y balance.
  - Gráfico de dona: gastos por categoría.
  - Gráfico de líneas: evolución mensual ingresos/gastos.
  - **Predicción de gasto del próximo mes** (regresión lineal con scikit-learn).
  - **Detección de gastos anómalos** (Z-Score, umbral = 2).
- Diseño responsivo adaptable a móviles y escritorio.
- Inicialización automática de la base de datos (DDL + datos demo) al arrancar.

---

## 📂 Estructura del proyecto

```
finanzas-personales/
├── backend/
│   ├── app.py                  # Fábrica de Flask, CORS, inicialización de DB
│   ├── config.py               # Carga de variables de entorno (Clever Cloud)
│   ├── conexion.py             # Pool de conexiones MySQL con reconexión
│   ├── rutas/
│   │   ├── auth.py             # POST /api/usuarios (bcrypt) y login
│   │   ├── categorias.py       # GET/POST /api/categorias
│   │   ├── movimientos.py      # CRUD /api/movimientos y /api/resumen
│   │   └── analitica.py        # /api/analitica/prediccion y /anomalias
│   └── analitica/
│       ├── predictor.py        # Regresión lineal (Pandas + Scikit-learn)
│       └── anomalias.py        # Detección Z-Score (umbral = 2)
├── frontend/
│   ├── index.html              # Dashboard responsivo
│   ├── css/style.css
│   └── js/
│       ├── api.js              # Cliente HTTP fetch (window.API_BASE dinámico)
│       └── charts.js           # Visualizaciones Chart.js (dona y líneas)
├── app.py                      # Punto de entrada (Gunicorn / local)
├── Procfile                    # web: gunicorn app:app
├── requirements.txt
├── database/
│   ├── schema.sql              # DDL (IF NOT EXISTS)
│   └── seed.sql                # Datos demo (no duplicados)
└── README.md
```

---

## 🗄️ Base de datos (Clever Cloud MySQL)

La conexión se configura leyendo variables de entorno con fallbacks a las
credenciales de producción:

| Variable | Valor por defecto |
|---|---|
| `DB_HOST` | `bal4ecgxmnkkhixeiuz-mysql.services.clever-cloud.com` |
| `DB_NAME` | `bal4ecgxmnkkhixeiuz` |
| `DB_USER` | `uumrqajbsuaq5pj1` |
| `DB_PASSWORD` | `jnCrtAO54uKSqdlkHxN5` |
| `DB_PORT` | `3306` |

Al iniciar la aplicación (`backend/app.py`), se ejecuta automáticamente
`database/schema.sql` (creación de tablas con `IF NOT EXISTS`) y
`database/seed.sql` (datos demo con inserciones **no duplicadas**).

---

## 🔌 API REST

Todas las respuestas son **JSON** con la estructura `{ "ok": ..., "datos": ... }`
(o `{ "ok": false, "error": ... }` en fallos).

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/usuarios` | Registro de usuario |
| `POST` | `/api/usuarios/login` | Inicio de sesión |
| `GET` | `/api/categorias` | Listar categorías |
| `POST` | `/api/categorias` | Crear categoría |
| `GET` | `/api/movimientos` | Listar movimientos |
| `POST` | `/api/movimientos` | Crear movimiento |
| `GET` | `/api/movimientos/<id>` | Detalle de movimiento |
| `PUT` | `/api/movimientos/<id>` | Actualizar movimiento |
| `DELETE` | `/api/movimientos/<id>` | Eliminar movimiento |
| `GET` | `/api/resumen` | Totales (ingresos, gastos, balance) |
| `GET` | `/api/analitica/prediccion` | Predicción de gasto del próximo mes |
| `GET` | `/api/analitica/anomalias` | Gastos anómalos (|Z| > 2) |

Se soporta el **preflight CORS** (`OPTIONS`) para todas las rutas `/api/*`.

---

## 🚀 Despliegue en Render (Web Service)

1. Sube este repositorio a **GitHub**.
2. En Render crea un **New Web Service** y conecta el repositorio.
3. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: (lo usa el `Procfile`) `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Root Directory**: raíz del repo.
4. Añade variables de entorno (opcional, si no quieres usar los fallbacks):
   ```
   DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, PORT
   ```
5. Render define automáticamente la variable `PORT`; el `Procfile` la usa.
6. Despliega. La base de datos se inicializa automáticamente al arrancar.

> Es posible que la primera subida tarde unos segundos extras mientras
> Gunicorn arranca los workers y se conecta a Clever Cloud.

---

## 💻 Ejecución local

```bash
# 1. (Opcional) entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar (por defecto puerto 5000, o el que ponga PORT)
python app.py
```

Abre `http://localhost:5000` en tu navegador.

### Usuario demo

- **Email**: `demo@finanzas.com`
- **Contraseña**: `demo1234`

(Las credenciales demo se crean mediante `database/seed.sql`.)

---

## ⚙️ Estructura de respuestas API

Éxito:

```json
{
  "ok": true,
  "datos": { ... }
}
```

Error:

```json
{
  "ok": false,
  "error": "Mensaje detallado del error"
}
```

El frontend (`frontend/js/api.js`) calcula la URL base con
`window.location.origin` o `window.API_BASE`, y si la respuesta no contiene la
clave `.datos` devuelve el JSON completo como fallback para evitar lecturas
`undefined`.
