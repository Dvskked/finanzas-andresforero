"""
Seguridad: hashing de contraseñas con bcrypt.
"""
import bcrypt


def hash_password(contrasena):
    """Devuelve el hash bcrypt (con salt aleatorio) de la contraseña."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(contrasena.encode("utf-8"), salt).decode("utf-8")


def verificar_password(contrasena, hash_guardado):
    """Compara una contraseña en claro con su hash bcrypt."""
    try:
        return bcrypt.checkpw(
            contrasena.encode("utf-8"), hash_guardado.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False
