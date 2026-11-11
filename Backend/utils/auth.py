from functools import wraps
import jwt
from flask import request, jsonify, g
from config import Config


def require_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token requerido (Authorization: Bearer <token>)"}), 401

        token = auth_header.split(' ', 1)[1]

        try:
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "El token expiró. Inicie sesión nuevamente."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido."}), 401

        g.usuario = payload
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.usuario.get('rol') != 'admin':
            return jsonify({"error": "Acceso denegado. Se requiere rol admin."}), 403
        return f(*args, **kwargs)
    return decorated_function
