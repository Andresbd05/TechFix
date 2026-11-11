from flask import Blueprint, request, jsonify, g
from utils.auth import require_jwt, require_admin

# Creamos el Blueprint para las reparaciones del taller
reparaciones_bp = Blueprint('reparaciones_bp', __name__)

# Orden en el que avanza una reparación: estado actual -> siguiente estado
FLUJO_ESTADOS = {
    'Recibido': 'En revisión',
    'En revisión': 'En reparación',
    'En reparación': 'Listo',
    'Listo': 'Entregado'
}

IVA = 0.19


def puede_modificar(cedula_tecnico_reparacion):
    # Propietario y admin pueden con cualquiera; el técnico solo con las suyas.
    # El invitado no puede con ninguna.
    rol = g.usuario.get('rol')
    if rol in ('propietario', 'admin'):
        return True
    if rol == 'tecnico':
        return g.usuario.get('cedula_tecnico') == cedula_tecnico_reparacion
    return False


@reparaciones_bp.route('/reparaciones', methods=['GET'])
@require_jwt
def obtener_reparaciones():
    # Importamos mysql aquí adentro para evitar errores de referencias circulares
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_reparacion, id_equipo, cedula_tecnico, estado, diagnostico, fecha_ingreso FROM reparaciones")
        datos = cur.fetchall()
        cur.close()

        reparaciones = []
        for fila in datos:
            reparaciones.append({
                "id_reparacion": fila[0],
                "id_equipo": fila[1],
                "cedula_tecnico": fila[2],
                "estado": fila[3],
                "diagnostico": fila[4],
                "fecha_ingreso": fila[5]
            })
        return jsonify({"reparaciones": reparaciones}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reparaciones_bp.route('/reparaciones', methods=['POST'])
@require_jwt
def crear_reparacion():
    from app import mysql
    datos = request.get_json(silent=True) or {}

    # Crear reparaciones: propietario y admin (el técnico trabaja las que le asignan)
    if g.usuario.get('rol') not in ['propietario', 'admin']:
        return jsonify({"error": "No tienes permiso para crear reparaciones"}), 403

    campos = ['id_reparacion', 'id_equipo', 'diagnostico']
    if not all(datos.get(c) for c in campos):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO reparaciones (id_reparacion, id_equipo, diagnostico) VALUES (%s, %s, %s)",
                    (datos['id_reparacion'], datos['id_equipo'], datos['diagnostico']))
        mysql.connection.commit()
        cur.close()

        return jsonify({"mensaje": "Reparación creada exitosamente"}), 201
    except Exception as e:
        mysql.connection.rollback()
        if "1062" in str(e):
            return jsonify({"error": "Ya existe una reparación con este id"}), 409
        # 1452 = la llave foránea no encuentra el equipo
        if "1452" in str(e):
            return jsonify({"error": "El equipo indicado no existe"}), 400
        return jsonify({"error": str(e)}), 500


@reparaciones_bp.route('/reparaciones/<id_reparacion>', methods=['GET'])
@require_jwt
def buscar_reparacion(id_reparacion):
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_reparacion, id_equipo, cedula_tecnico, estado, diagnostico, fecha_ingreso "
                    "FROM reparaciones WHERE id_reparacion = %s", (id_reparacion,))
        fila = cur.fetchone()
        cur.close()

        if fila is None:
            return jsonify({"error": "Reparación no encontrada"}), 404

        reparacion = {
            "id_reparacion": fila[0],
            "id_equipo": fila[1],
            "cedula_tecnico": fila[2],
            "estado": fila[3],
            "diagnostico": fila[4],
            "fecha_ingreso": fila[5]
        }
        return jsonify({"reparacion": reparacion}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reparaciones_bp.route('/reparaciones/<id_reparacion>', methods=['DELETE'])
@require_jwt
def eliminar_reparacion(id_reparacion):
    from app import mysql

    if g.usuario.get('rol') not in ['propietario', 'admin']:
        return jsonify({"error": "No tienes permiso para eliminar reparaciones"}), 403

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_reparacion FROM reparaciones WHERE id_reparacion = %s", (id_reparacion,))
        if cur.fetchone() is None:
            cur.close()
            return jsonify({"error": "Reparación no encontrada"}), 404

        cur.execute("DELETE FROM reparaciones WHERE id_reparacion = %s", (id_reparacion,))
        mysql.connection.commit()
        cur.close()

        return jsonify({"mensaje": "Reparación eliminada exitosamente"}), 200
    except Exception as e:
        mysql.connection.rollback()
        # 1451 = la llave foránea lo impide (la reparación tiene repuestos usados)
        if "1451" in str(e):
            return jsonify({"error": "No se puede eliminar: la reparación tiene repuestos registrados"}), 409
        return jsonify({"error": str(e)}), 500


@reparaciones_bp.route('/reparaciones/<id_reparacion>/asignar', methods=['PUT'])
@require_jwt
@require_admin
def asignar_tecnico(id_reparacion):
    from app import mysql
    datos = request.get_json(silent=True) or {}
    cedula_tecnico = datos.get('cedula_tecnico')

    if not cedula_tecnico:
        return jsonify({"error": "El campo cedula_tecnico es obligatorio"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT estado FROM reparaciones WHERE id_reparacion = %s", (id_reparacion,))
        reparacion = cur.fetchone()

        cur.execute("SELECT nombre, reparacion_activa_id FROM tecnicos WHERE cedula_tecnico = %s", (cedula_tecnico,))
        tecnico = cur.fetchone()

        if reparacion is None:
            cur.close()
            return jsonify({"error": "Reparación no encontrada"}), 404
        if reparacion[0] in ('Listo', 'Entregado'):
            cur.close()
            return jsonify({"error": "La reparación ya terminó, no se le puede cambiar el técnico"}), 409
        if tecnico is None:
            cur.close()
            return jsonify({"error": "Técnico no encontrado"}), 404
        if tecnico[1] and tecnico[1] != id_reparacion:
            cur.close()
            return jsonify({"error": f"{tecnico[0]} está ocupado con la reparación {tecnico[1]}"}), 409

        # Liberamos al técnico anterior, asignamos el nuevo y lo marcamos como ocupado
        cur.execute("UPDATE tecnicos SET reparacion_activa_id = NULL WHERE reparacion_activa_id = %s",
                    (id_reparacion,))
        cur.execute("UPDATE reparaciones SET cedula_tecnico = %s WHERE id_reparacion = %s",
                    (cedula_tecnico, id_reparacion))
        cur.execute("UPDATE tecnicos SET reparacion_activa_id = %s WHERE cedula_tecnico = %s",
                    (id_reparacion, cedula_tecnico))
        mysql.connection.commit()
        cur.close()

        return jsonify({"mensaje": f"Reparación {id_reparacion} asignada a {tecnico[0]}"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500


@reparaciones_bp.route('/reparaciones/<id_reparacion>/avanzar', methods=['PUT'])
@require_jwt
def avanzar_estado(id_reparacion):
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT estado, cedula_tecnico FROM reparaciones WHERE id_reparacion = %s", (id_reparacion,))
        reparacion = cur.fetchone()

        if reparacion is None:
            cur.close()
            return jsonify({"error": "Reparación no encontrada"}), 404

        estado_actual = reparacion[0]
        cedula_tecnico = reparacion[1]

        if cedula_tecnico is None:
            cur.close()
            return jsonify({"error": "Primero hay que asignar un técnico a la reparación"}), 409
        if not puede_modificar(cedula_tecnico):
            cur.close()
            return jsonify({"error": "Solo puedes avanzar las reparaciones que tienes asignadas"}), 403
        if estado_actual not in FLUJO_ESTADOS:
            cur.close()
            return jsonify({"error": f"La reparación está en '{estado_actual}' y ya no puede avanzar"}), 409

        nuevo_estado = FLUJO_ESTADOS[estado_actual]

        cur.execute("UPDATE reparaciones SET estado = %s WHERE id_reparacion = %s", (nuevo_estado, id_reparacion))

        # Cuando queda lista, el técnico se libera para tomar otra reparación
        if nuevo_estado == 'Listo':
            cur.execute("UPDATE tecnicos SET reparacion_activa_id = NULL WHERE reparacion_activa_id = %s",
                        (id_reparacion,))

        mysql.connection.commit()
        cur.close()

        return jsonify({
            "mensaje": "Estado actualizado",
            "estado_anterior": estado_actual,
            "estado_nuevo": nuevo_estado
        }), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500


@reparaciones_bp.route('/reparaciones/<id_reparacion>/repuestos', methods=['POST'])
@require_jwt
def usar_repuesto(id_reparacion):
    from app import mysql
    datos = request.get_json(silent=True) or {}
    sku_repuesto = datos.get('sku_repuesto')
    cantidad = datos.get('cantidad', 1)

    if not sku_repuesto:
        return jsonify({"error": "El campo sku_repuesto es obligatorio"}), 400
    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"error": "cantidad debe ser un número entero mayor que 0"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT estado, cedula_tecnico FROM reparaciones WHERE id_reparacion = %s", (id_reparacion,))
        reparacion = cur.fetchone()

        cur.execute("SELECT nombre, stock FROM repuestos WHERE sku_repuesto = %s", (sku_repuesto,))
        repuesto = cur.fetchone()

        if reparacion is None:
            cur.close()
            return jsonify({"error": "Reparación no encontrada"}), 404
        if not puede_modificar(reparacion[1]):
            cur.close()
            return jsonify({"error": "Solo puedes agregar repuestos a las reparaciones que tienes asignadas"}), 403
        if reparacion[0] in ('Listo', 'Entregado'):
            cur.close()
            return jsonify({"error": "La reparación ya terminó, no se le pueden agregar repuestos"}), 409
        if repuesto is None:
            cur.close()
            return jsonify({"error": "Repuesto no encontrado"}), 404
        if repuesto[1] < cantidad:
            cur.close()
            return jsonify({"error": f"Stock insuficiente: solo quedan {repuesto[1]} unidades de {repuesto[0]}"}), 409

        # Descontamos del inventario solo si alcanza (evita stock negativo con peticiones simultáneas)
        cur.execute("UPDATE repuestos SET stock = stock - %s WHERE sku_repuesto = %s AND stock >= %s",
                    (cantidad, sku_repuesto, cantidad))
        if cur.rowcount == 0:
            mysql.connection.rollback()
            cur.close()
            return jsonify({"error": "Stock insuficiente"}), 409

        # Si el repuesto ya estaba en la reparación, sumamos la cantidad
        cur.execute("INSERT INTO reparacion_repuestos (id_reparacion, sku_repuesto, cantidad) VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE cantidad = cantidad + %s",
                    (id_reparacion, sku_repuesto, cantidad, cantidad))
        mysql.connection.commit()
        cur.close()

        return jsonify({
            "mensaje": f"Se usaron {cantidad} x {repuesto[0]} en la reparación {id_reparacion}",
            "stock_restante": repuesto[1] - cantidad
        }), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500


@reparaciones_bp.route('/reparaciones/<id_reparacion>/cotizacion', methods=['GET'])
@require_jwt
def cotizar_reparacion(id_reparacion):
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_reparacion FROM reparaciones WHERE id_reparacion = %s", (id_reparacion,))
        if cur.fetchone() is None:
            cur.close()
            return jsonify({"error": "Reparación no encontrada"}), 404

        cur.execute("SELECT r.sku_repuesto, r.nombre, r.precio, rr.cantidad "
                    "FROM reparacion_repuestos rr "
                    "JOIN repuestos r ON r.sku_repuesto = rr.sku_repuesto "
                    "WHERE rr.id_reparacion = %s", (id_reparacion,))
        datos = cur.fetchall()
        cur.close()

        detalle = []
        subtotal = 0
        for fila in datos:
            precio = float(fila[2])
            cantidad = fila[3]
            valor = precio * cantidad
            subtotal += valor
            detalle.append({
                "sku_repuesto": fila[0],
                "nombre": fila[1],
                "precio_unitario": precio,
                "cantidad": cantidad,
                "valor": valor
            })

        iva = round(subtotal * IVA, 2)

        return jsonify({
            "id_reparacion": id_reparacion,
            "repuestos": detalle,
            "subtotal": subtotal,
            "iva": iva,
            "total": subtotal + iva
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reparaciones_bp.route('/mis-reparaciones', methods=['GET'])
@require_jwt
def mis_reparaciones():
    from app import mysql

    cedula_tecnico = g.usuario.get('cedula_tecnico')
    if not cedula_tecnico:
        return jsonify({"error": "Tu usuario no está asociado a ningún técnico"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_reparacion, id_equipo, estado, diagnostico, fecha_ingreso FROM reparaciones "
                    "WHERE cedula_tecnico = %s ORDER BY fecha_ingreso", (cedula_tecnico,))
        datos = cur.fetchall()
        cur.close()

        reparaciones = []
        for fila in datos:
            reparaciones.append({
                "id_reparacion": fila[0],
                "id_equipo": fila[1],
                "estado": fila[2],
                "diagnostico": fila[3],
                "fecha_ingreso": fila[4]
            })
        return jsonify({"reparaciones": reparaciones}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
