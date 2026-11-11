from flask import Blueprint, request, jsonify, g
from utils.auth import require_jwt

# Creamos el Blueprint para los clientes
clientes_bp = Blueprint('clientes_bp', __name__)


@clientes_bp.route('/clientes', methods=['GET'])
@require_jwt
def obtener_clientes():
    # Importamos mysql aquí adentro para evitar errores de referencias circulares
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT cedula, nombre, telefono, correo FROM clientes")
        datos = cur.fetchall()
        cur.close()

        clientes = []
        for fila in datos:
            clientes.append({
                "cedula": fila[0],
                "nombre": fila[1],
                "telefono": fila[2],
                "correo": fila[3]
            })
        return jsonify({"clientes": clientes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@clientes_bp.route('/clientes', methods=['POST'])
@require_jwt
def crear_cliente():
    from app import mysql
    datos = request.get_json(silent=True) or {}

    # Gestionar clientes: propietario y admin (el técnico y el invitado solo ven)
    if g.usuario.get('rol') not in ['propietario', 'admin']:
        return jsonify({"error": "No tienes permiso para crear clientes"}), 403

    campos = ['cedula', 'nombre', 'telefono', 'correo']
    if not all(c in datos for c in campos):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO clientes (cedula, nombre, telefono, correo) VALUES (%s, %s, %s, %s)",
                    (datos['cedula'], datos['nombre'], datos['telefono'], datos['correo']))
        mysql.connection.commit()
        cur.close()

        return jsonify({"mensaje": "Cliente creado exitosamente"}), 201
    except Exception as e:
        mysql.connection.rollback()
        if "1062" in str(e):
            return jsonify({"error": "Ya existe un cliente con esta cédula"}), 409
        return jsonify({"error": str(e)}), 500


# Va antes de /clientes/<cedula> para que se lea fácil; Flask igual prioriza la ruta fija
@clientes_bp.route('/clientes/buscar', methods=['GET'])
@require_jwt
def buscar_clientes():
    from app import mysql

    texto = request.args.get('q', '').strip()
    if len(texto) < 2:
        return jsonify({"error": "Escribe al menos 2 caracteres en el parámetro q"}), 400

    patron = f"%{texto}%"

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT cedula, nombre, telefono, correo FROM clientes "
                    "WHERE nombre LIKE %s OR cedula LIKE %s OR telefono LIKE %s ORDER BY nombre",
                    (patron, patron, patron))
        datos = cur.fetchall()
        cur.close()

        clientes = []
        for fila in datos:
            clientes.append({
                "cedula": fila[0],
                "nombre": fila[1],
                "telefono": fila[2],
                "correo": fila[3]
            })
        return jsonify({"clientes": clientes}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@clientes_bp.route('/clientes/<cedula>', methods=['GET'])
@require_jwt
def buscar_cliente(cedula):
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT cedula, nombre, telefono, correo FROM clientes WHERE cedula = %s", (cedula,))
        fila = cur.fetchone()
        cur.close()

        if fila is None:
            return jsonify({"error": "Cliente no encontrado"}), 404

        cliente = {
            "cedula": fila[0],
            "nombre": fila[1],
            "telefono": fila[2],
            "correo": fila[3]
        }
        return jsonify({"cliente": cliente}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@clientes_bp.route('/clientes/<cedula>', methods=['PUT'])
@require_jwt
def actualizar_cliente(cedula):
    from app import mysql
    datos = request.get_json(silent=True) or {}

    if g.usuario.get('rol') not in ['propietario', 'admin']:
        return jsonify({"error": "No tienes permiso para actualizar clientes"}), 403

    campos = ['nombre', 'telefono', 'correo']
    if not all(c in datos for c in campos):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        cur = mysql.connection.cursor()

        # Verificamos que exista antes de actualizar: rowcount no sirve para esto
        # porque MySQL devuelve 0 si los valores nuevos son iguales a los actuales
        cur.execute("SELECT cedula FROM clientes WHERE cedula = %s", (cedula,))
        if cur.fetchone() is None:
            cur.close()
            return jsonify({"error": "Cliente no encontrado"}), 404

        cur.execute("UPDATE clientes SET nombre = %s, telefono = %s, correo = %s WHERE cedula = %s",
                    (datos['nombre'], datos['telefono'], datos['correo'], cedula))
        mysql.connection.commit()
        cur.close()

        return jsonify({"mensaje": "Cliente actualizado exitosamente"}), 200
    except Exception as e:
        mysql.connection.rollback()  # Deshacemos el cambio si algo falló
        return jsonify({"error": str(e)}), 500


@clientes_bp.route('/clientes/<cedula>', methods=['DELETE'])
@require_jwt
def eliminar_cliente(cedula):
    from app import mysql

    if g.usuario.get('rol') not in ['propietario', 'admin']:
        return jsonify({"error": "No tienes permiso para eliminar clientes"}), 403

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT cedula FROM clientes WHERE cedula = %s", (cedula,))
        if cur.fetchone() is None:
            cur.close()
            return jsonify({"error": "Cliente no encontrado"}), 404

        cur.execute("DELETE FROM clientes WHERE cedula = %s", (cedula,))
        mysql.connection.commit()
        cur.close()

        return jsonify({"mensaje": "Cliente eliminado exitosamente"}), 200
    except Exception as e:
        mysql.connection.rollback()
        # 1451 = la llave foránea lo impide (el cliente tiene equipos registrados)
        if "1451" in str(e):
            return jsonify({"error": "No se puede eliminar: el cliente tiene equipos registrados"}), 409
        return jsonify({"error": str(e)}), 500


@clientes_bp.route('/clientes/<cedula>/equipos', methods=['GET'])
@require_jwt
def obtener_equipos_cliente(cedula):
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_equipo, id_marca, tipo_dispositivo, serial_imei FROM equipos WHERE cliente_cedula = %s",
                    (cedula,))
        datos = cur.fetchall()
        cur.close()

        equipos = []
        for fila in datos:
            equipos.append({
                "id_equipo": fila[0],
                "id_marca": fila[1],
                "tipo_dispositivo": fila[2],
                "serial_imei": fila[3]
            })

        if len(equipos) == 0:
            return jsonify({
                "mensaje": "Este cliente no tiene equipos registrados",
                "equipos": []
            }), 200

        return jsonify({"equipos": equipos}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@clientes_bp.route('/clientes/<cedula>/historial', methods=['GET'])
@require_jwt
def historial_cliente(cedula):
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT nombre, telefono, correo FROM clientes WHERE cedula = %s", (cedula,))
        cliente = cur.fetchone()

        if cliente is None:
            cur.close()
            return jsonify({"error": "Cliente no encontrado"}), 404

        cur.execute("SELECT r.id_reparacion, e.id_equipo, e.tipo_dispositivo, m.nombre_marca, "
                    "r.estado, r.diagnostico, r.fecha_ingreso "
                    "FROM equipos e "
                    "LEFT JOIN marcas m ON m.id_marca = e.id_marca "
                    "JOIN reparaciones r ON r.id_equipo = e.id_equipo "
                    "WHERE e.cliente_cedula = %s "
                    "ORDER BY r.fecha_ingreso DESC", (cedula,))
        datos = cur.fetchall()
        cur.close()

        reparaciones = []
        for fila in datos:
            reparaciones.append({
                "id_reparacion": fila[0],
                "id_equipo": fila[1],
                "equipo": f"{fila[2]} {fila[3]}",
                "estado": fila[4],
                "diagnostico": fila[5],
                "fecha_ingreso": fila[6]
            })

        pendientes = [r for r in reparaciones if r["estado"] != 'Entregado']

        return jsonify({
            "cliente": {
                "cedula": cedula,
                "nombre": cliente[0],
                "telefono": cliente[1],
                "correo": cliente[2]
            },
            "total_reparaciones": len(reparaciones),
            "reparaciones_pendientes": len(pendientes),
            "reparaciones": reparaciones
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
