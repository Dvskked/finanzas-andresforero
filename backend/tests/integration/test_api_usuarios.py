from fastapi.testclient import TestClient


def test_api_crear_usuario_exitoso(client: TestClient):
    """1. Crear usuario correctamente (Status 201)."""
    payload = {
        "nombre": "Pedro Pascal",
        "correo": "pedro@example.com",
        "contrasena": "MiPasswordSeguro2026*"
    }
    response = client.post("/api/usuarios", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "id_usuario" in data
    assert data["nombre"] == "Pedro Pascal"
    assert data["correo"] == "pedro@example.com"


def test_api_crear_usuario_rechazar_correo_invalido(client: TestClient):
    """2. Rechazar correo inválido (Status 422)."""
    payload = {
        "nombre": "Pedro Pascal",
        "correo": "correo-no-valido",
        "contrasena": "MiPasswordSeguro2026*"
    }
    response = client.post("/api/usuarios", json=payload)
    assert response.status_code == 422


def test_api_crear_usuario_sin_campos_requeridos(client: TestClient):
    """3. Rechazar usuario sin campos requeridos (Status 422)."""
    # Sin contraseña
    payload_sin_pass = {
        "nombre": "Pedro Pascal",
        "correo": "pedro@example.com"
    }
    response = client.post("/api/usuarios", json=payload_sin_pass)
    assert response.status_code == 422

    # Sin nombre
    payload_sin_nombre = {
        "correo": "pedro@example.com",
        "contrasena": "MiPasswordSeguro2026*"
    }
    response = client.post("/api/usuarios", json=payload_sin_nombre)
    assert response.status_code == 422

    # Nombre vacío o solo espacios
    payload_nombre_vacio = {
        "nombre": "   ",
        "correo": "pedro@example.com",
        "contrasena": "MiPasswordSeguro2026*"
    }
    response = client.post("/api/usuarios", json=payload_nombre_vacio)
    assert response.status_code == 422


def test_api_crear_usuario_rechazar_correo_duplicado(client: TestClient):
    """4. Rechazar correo duplicado (Status 409 Conflict)."""
    payload = {
        "nombre": "Usuario Uno",
        "correo": "duplicado@example.com",
        "contrasena": "PasswordValido123*"
    }
    # Primera creación: exitosa
    r1 = client.post("/api/usuarios", json=payload)
    assert r1.status_code == 201

    # Segunda creación con el mismo correo: conflicto 409
    r2 = client.post("/api/usuarios", json=payload)
    assert r2.status_code == 409
    assert "ya se encuentra registrado" in r2.json()["detail"]


def test_api_crear_usuario_no_expone_contrasena_ni_hash(client: TestClient):
    """5 y 6. Verificar que la respuesta jamás expone contrasena ni contrasena_hash."""
    payload = {
        "nombre": "Diana Prince",
        "correo": "diana@themyscira.com",
        "contrasena": "LazoDeLaVerdad2026*"
    }
    response = client.post("/api/usuarios", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "contrasena" not in data
    assert "contrasena_hash" not in data
    assert "password" not in data


def test_api_login_exitoso(client: TestClient):
    """Iniciar sesión con credenciales correctas devuelve perfil y no expone hash."""
    client.post("/api/usuarios", json={
        "nombre": "Marta Díaz",
        "correo": "marta@example.com",
        "contrasena": "Martita2026*"
    })

    response = client.post("/api/usuarios/login", json={
        "correo": "marta@example.com",
        "contrasena": "Martita2026*"
    })
    assert response.status_code == 200

    data = response.json()
    assert "id_usuario" in data
    assert data["nombre"] == "Marta Díaz"
    assert data["correo"] == "marta@example.com"
    assert "contrasena" not in data
    assert "contrasena_hash" not in data


def test_api_login_contrasena_incorrecta(client: TestClient):
    """Iniciar sesión con contraseña incorrecta devuelve 401."""
    client.post("/api/usuarios", json={
        "nombre": "Marta Díaz",
        "correo": "marta2@example.com",
        "contrasena": "Martita2026*"
    })

    response = client.post("/api/usuarios/login", json={
        "correo": "marta2@example.com",
        "contrasena": "ClaveEquivocada9*"
    })
    assert response.status_code == 401
    assert "detail" in response.json()


def test_api_login_correo_inexistente(client: TestClient):
    """Iniciar sesión con correo no registrado devuelve 401."""
    response = client.post("/api/usuarios/login", json={
        "correo": "fantasma@example.com",
        "contrasena": "CualquierClave1*"
    })
    assert response.status_code == 401


def test_api_login_correo_invalido(client: TestClient):
    """Iniciar sesión con correo malformado devuelve 422."""
    response = client.post("/api/usuarios/login", json={
        "correo": "correo-invalido",
        "contrasena": "CualquierClave1*"
    })
    assert response.status_code == 422


def test_api_obtener_usuario_por_id(client: TestClient):
    """Obtener un usuario por su ID devuelve su perfil público."""
    creado = client.post("/api/usuarios", json={
        "nombre": "Juan Pérez",
        "correo": "juan@example.com",
        "contrasena": "Juanito2026*"
    })
    id_usuario = creado.json()["id_usuario"]

    response = client.get(f"/api/usuarios/{id_usuario}")
    assert response.status_code == 200
    data = response.json()
    assert data["id_usuario"] == id_usuario
    assert data["nombre"] == "Juan Pérez"
    assert "contrasena_hash" not in data


def test_api_obtener_usuario_inexistente(client: TestClient):
    """Obtener un usuario inexistente devuelve 404."""
    response = client.get("/api/usuarios/999999")
    assert response.status_code == 404
