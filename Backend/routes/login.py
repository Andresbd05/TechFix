import datetime
import jwt
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from utils.auth import require_jwt, require_admin

login_bp = Blueprint('login_bp', __name__)


@login_bp.route('/login', methods=['POST'])
def login():
    from app import mysql
    datos = request.get_json(silent=True) or {}
    username = datos.get('username')
    password = datos.get('password')

    if not username or not password:
        return jsonify({"error": "username y password son obligatorios"}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT id_usuario, password_hash, rol, cedula_tecnico, plan, nombre FROM usuarios WHERE username = %s",
            (username,))
    fila = cur.fetchone()
    cur.close()

    if fila is None or not check_password_hash(fila[1], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    ahora = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": str(fila[0]),
        "username": username,
        "rol": fila[2],
        "cedula_tecnico": fila[3],
        "plan": fila[4],
        "nombre": fila[5],
        "iat": ahora,
        "exp": ahora + datetime.timedelta(minutes=Config.JWT_EXPIRATION_MINUTES)
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

    return jsonify({
        "token": token,
        "tipo": "Bearer",
        "expira_en_minutos": Config.JWT_EXPIRATION_MINUTES
    }), 200


@login_bp.route('/register', methods=['POST'])
@require_jwt
@require_admin
def registrar_usuario():
    from app import mysql
    datos = request.get_json(silent=True) or {}
    username = datos.get('username')
    password = datos.get('password')
    rol = datos.get('rol', 'tecnico')
    # Los usuarios nuevos quedan en el plan Gratis si no se indica otro
    plan = datos.get('plan', 'gratis')
    cedula_tecnico = datos.get('cedula_tecnico')

    if not username or not password:
        return jsonify({"error": "username y password son obligatorios"}), 400
    if rol not in ('propietario', 'admin', 'tecnico', 'invitado'):
        return jsonify({"error": "rol debe ser propietario, admin, tecnico o invitado"}), 400
    if plan not in ('gratis', 'basico', 'pro', 'empresa'):
        return jsonify({"error": "plan debe ser gratis, basico, pro o empresa"}), 400

    # Solo el técnico se asocia a una cédula de técnico; los demás roles no
    if rol != 'tecnico':
        cedula_tecnico = None

    password_hash = generate_password_hash(password)

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (username, password_hash, rol, cedula_tecnico, plan) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (username, password_hash, rol, cedula_tecnico, plan))
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201
    except Exception:
        mysql.connection.rollback()
        return jsonify({"error": "No se pudo registrar (¿usuario duplicado o cédula de técnico inexistente?)"}), 400


@login_bp.route('/perfil', methods=['GET'])
@require_jwt
def perfil():
    return jsonify({
        "usuario": g.usuario.get('username'),
        "nombre": g.usuario.get('nombre'),
        "rol": g.usuario.get('rol'),
        "cedula_tecnico": g.usuario.get('cedula_tecnico'),
        "plan": g.usuario.get('plan')
    }), 200


# Registro público: cualquiera crea su cuenta con nombre, correo y contraseña.
# La cuenta entra como propietario (dueño de su taller) en el plan Gratis.
@login_bp.route('/registro', methods=['POST'])
def registro_publico():
    from app import mysql
    datos = request.get_json(silent=True) or {}
    nombre = (datos.get('nombre') or '').strip()
    email = (datos.get('email') or '').strip().lower()
    password = datos.get('password') or ''

    if not nombre or not email or not password:
        return jsonify({"error": "El nombre, el correo y la contraseña son obligatorios"}), 400
    if '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({"error": "Escribe un correo válido"}), 400
    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    password_hash = generate_password_hash(password)

    try:
        cur = mysql.connection.cursor()
        # El correo se guarda como nombre de usuario; con él se inicia sesión
        cur.execute("INSERT INTO usuarios (username, password_hash, nombre, rol, cedula_tecnico, plan) "
                    "VALUES (%s, %s, %s, 'propietario', NULL, 'gratis')",
                    (email, password_hash, nombre))
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensaje": "Cuenta creada exitosamente"}), 201
    except Exception as e:
        mysql.connection.rollback()
        if "1062" in str(e):
            return jsonify({"error": "Ya existe una cuenta con ese correo"}), 409
        return jsonify({"error": "No se pudo crear la cuenta"}), 400


# Cambiar el plan de la cuenta con la que inicié sesión (simulación de suscripción)
@login_bp.route('/mi-plan', methods=['PUT'])
@require_jwt
def cambiar_mi_plan():
    from app import mysql
    datos = request.get_json(silent=True) or {}
    plan = datos.get('plan')

    if plan not in ('gratis', 'basico', 'pro', 'empresa'):
        return jsonify({"error": "plan debe ser gratis, basico, pro o empresa"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE usuarios SET plan = %s WHERE id_usuario = %s",
                    (plan, g.usuario.get('sub')))
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensaje": "Plan actualizado", "plan": plan}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
