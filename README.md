# Finanzas Personales — Dashboard Analítico

Aplicación web de finanzas personales con dashboard analítico (gastos por
categoría, evolución mensual, predicción de gastos y detección de anomalías).

Arquitectura en capas inspirada en el repositorio de referencia
`SantiDev11/Finanzas-Pyton-Kevin-Pedraza`, reimplementada con **Flask**:

```
app.py                      # Entrada Gunicorn / local
backend/
  app.py                    # Fábrica Flask (CORS, JSON errors, estáticos, init BD)
  core/                     # config, excepciones, seguridad (bcrypt)
  database.py               # get_cursor() con commit/rollback automático
  repositories/             # SQL (usuario, categoria, movimiento)
  services/                 # Lógica de negocio
  analitica/                # predictor (regresión lineal) + anomalías (Z-score)
  rutas/                    # Blueprints de la API
database/
  schema.sql                # DDL idempotente (IF NOT EXISTS)
  seed.sql                  # Datos demo (no duplicados)
frontend/
  index.html  css/style.css
  js/  config.js api.js charts.js
```

## API

| Método | Ruta                        | Descripción                 |
|--------|-----------------------------|-----------------------------|
| POST   | `/api/usuarios`             | Registro (bcrypt)           |
| POST   | `/api/usuarios/login`       | Inicio de sesión            |
| GET    | `/api/categorias`           | Listar categorías           |
| POST   | `/api/categorias`           | Crear categoría             |
| GET    | `/api/movimientos?usuario_id=` | Listar movimientos       |
| POST   | `/api/movimientos`          | Crear movimiento            |
| PUT    | `/api/movimientos/<id>`     | Actualizar                  |
| DELETE | `/api/movimientos/<id>`     | Eliminar                    |
| GET    | `/api/resumen?usuario_id=`  | Resumen (ingresos/gastos/balance) |
| GET    | `/api/analitica/prediccion?usuario_id=` | Predicción próximo mes |
| GET    | `/api/analitica/anomalias?usuario_id=`  | Gastos anómalos       |

Toda respuesta es JSON: éxito `{"ok": true, "datos": ...}`, error
`{"ok": false, "error": ...}` (nunca HTML).

## Credenciales

Las variables de entorno del backend se centralizan en `backend/core/config.py`,
con fallbacks a la base **Clever Cloud MySQL**. Para producción basta definir:

```
DB_HOST
DB_NAME
DB_USER
DB_PASSWORD
DB_PORT
PORT
```

## Usuario demo

Email: `demo@finanzas.com` · Contraseña: `demo1234`

## Configuración de la URL de la API (frontend)

`frontend/js/config.js` resuelve `API_BASE_URL` con esta prioridad:

1. `window.API_BASE_URL` (variable global)
2. `<meta name="api-base-url">`
3. `window.API_BASE` (compatibilidad)
4. `window.location.origin` (default: Flask sirve el frontend desde la raíz)

## Instalación y ejecución local

```bash
pip install -r requirements.txt
python app.py            # servidor en 0.0.0.0:8000
```

## Despliegue en Render (Web Service)

- Build command: `pip install -r requirements.txt`
- Start command (lo usa el `Procfile`): `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- El backend ejecuta `schema.sql` + `seed.sql` (idempotentes) al iniciar.
- Define las variables `DB_*` en el servicio.
