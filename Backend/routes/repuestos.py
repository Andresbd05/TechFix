from flask import Blueprint, request, jsonify, g
from utils.auth import require_jwt

# Creamos el Blueprint para el inventario de repuestos
repuestos_bp = Blueprint('repuestos_bp', __name__)


@repuestos_bp.route('/repuestos', methods=['GET'])
@require_jwt
def obtener_repuestos():
    # Importamos mysql aquí adentro para evitar errores de referencias circulares
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT sku_repuesto, nombre, id_marca, precio, stock FROM repuestos")
        datos = cur.fetchall()
        cur.close()

        repuestos = []
        for fila in datos:
            repuestos.append({
                "sku_repuesto": fila[0],
                "nombre": fila[1],
                "id_marca": fila[2],
                "precio": float(fila[3]),
                "stock": fila[4]
            })
        return jsonify({"repuestos": repuestos}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@repuestos_bp.route('/repuestos', methods=['POST'])
@require_jwt
def crear_repuesto():
    from app import mysql
    datos = request.get_json(silent=True) or {}

    # Gestionar inventario: propietario y admin
    if g.usuario.get('rol') not in ['propietario', 'admin']:
        return jsonify({"error": "No tienes permiso para crear repuestos"}), 403

    campos = ['sku_repuesto', 'nombre', 'id_marca', 'precio', 'stock']
    if not all(c in datos for c in campos):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO repuestos (sku_repuesto, nombre, id_marca, precio, stock) VALUES (%s, %s, %s, %s, %s)",
                    (datos['sku_repuesto'], datos['nombre'], datos['id_marca'], datos['precio'], datos['stock']))
        mysql.connection.commit()
        cur.close()

        return jsonify({"mensaje": "Repuesto agregado al inventario exitosamente"}), 201
    except Exception as e:
        mysql.connection.rollback()
        if "1062" in str(e):
            return jsonify({"error": "Ya existe un repuesto con este SKU"}), 409
        return jsonify({"error": str(e)}), 500


@repuestos_bp.route('/repuestos/<sku_repuesto>', methods=['GET'])
@require_jwt
def obtener_repuesto(sku_repuesto):
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT sku_repuesto, nombre, id_marca, precio, stock FROM repuestos WHERE sku_repuesto = %s",
                    (sku_repuesto,))
        fila = cur.fetchone()
        cur.close()

        if fila is None:
            return jsonify({"error": "Repuesto no encontrado"}), 404

        repuesto = {
            "sku_repuesto": fila[0],
            "nombre": fila[1],
            "id_marca": fila[2],
            "precio": float(fila[3]),
            "stock": fila[4]
        }
        return jsonify({"repuesto": repuesto}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@repuestos_bp.route('/repuestos/<sku_repuesto>', methods=['PUT'])
@require_jwt
def actualizar_repuesto(sku_repuesto):
    from app import mysql
    datos = request.get_json(silent=True) or {}

    if g.usuario.get('rol') not in ['propietario', 'admin']:
        return jsonify({"error": "No tienes permiso para actualizar repuestos"}), 403

    campos = ['nombre', 'id_marca', 'precio', 'stock']
    if not all(c in datos for c in campos):
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        cur = mysql.connection.cursor()

        # Verificamos que exista antes de actualizar (rowcount da 0 si no cambia nada)
        cur.execute("SELECT sku_repuesto FROM repuestos WHERE sku_repuesto = %s", (sku_repuesto,))
        if cur.fetchone() is None:
            cur.close()
            return jsonify({"error": "Repuesto no encontrado"}), 404

        cur.execute("UPDATE repuestos SET nombre = %s, id_marca = %s, precio = %s, stock = %s WHERE sku_repuesto = %s",
                    (datos['nombre'], datos['id_marca'], datos['precio'], datos['stock'], sku_repuesto))
        mysql.connection.commit()
        cur.close()

        return jsonify({"mensaje": "Repuesto actualizado exitosamente"}), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500


@repuestos_bp.route('/repuestos/<sku_repuesto>', methods=['DELETE'])
@require_jwt
def eliminar_repuesto(sku_repuesto):
    from app import mysql

    if g.usuario.get('rol') not in ['propietario', 'admin']:
        return jsonify({"error": "No tienes permiso para eliminar repuestos"}), 403

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT sku_repuesto FROM repuestos WHERE sku_repuesto = %s", (sku_repuesto,))
        if cur.fetchone() is None:
            cur.close()
            return jsonify({"error": "Repuesto no encontrado"}), 404

        cur.execute("DELETE FROM repuestos WHERE sku_repuesto = %s", (sku_repuesto,))
        mysql.connection.commit()
        cur.close()

        return jsonify({"mensaje": "Repuesto eliminado exitosamente"}), 200
    except Exception as e:
        mysql.connection.rollback()
        # 1451 = la llave foránea lo impide (el repuesto ya se usó en una reparación)
        if "1451" in str(e):
            return jsonify({"error": "No se puede eliminar: el repuesto ya se usó en una reparación"}), 409
        return jsonify({"error": str(e)}), 500


@repuestos_bp.route('/repuestos/marca/<id_marca>', methods=['GET'])
@require_jwt
def obtener_repuestos_por_marca(id_marca):
    from app import mysql

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT sku_repuesto, nombre, precio, stock FROM repuestos WHERE id_marca = %s", (id_marca,))
        datos = cur.fetchall()
        cur.close()

        repuestos = []
        for fila in datos:
            repuestos.append({
                "sku_repuesto": fila[0],
                "nombre": fila[1],
                "precio": float(fila[2]),
                "stock": fila[3]
            })

        if len(repuestos) == 0:
            return jsonify({
                "mensaje": "No hay repuestos registrados para esta marca",
                "repuestos": []
            }), 200

        return jsonify({"repuestos": repuestos}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@repuestos_bp.route('/repuestos/stock-bajo', methods=['GET'])
@require_jwt
def repuestos_stock_bajo():
    from app import mysql

    minimo = request.args.get('minimo', 5, type=int)

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT sku_repuesto, nombre, stock FROM repuestos WHERE stock <= %s ORDER BY stock",
                    (minimo,))
        datos = cur.fetchall()
        cur.close()

        repuestos = []
        for fila in datos:
            repuestos.append({
                "sku_repuesto": fila[0],
                "nombre": fila[1],
                "stock": fila[2]
            })

        return jsonify({
            "minimo": minimo,
            "total_por_pedir": len(repuestos),
            "repuestos": repuestos
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@repuestos_bp.route('/repuestos/<sku_repuesto>/stock', methods=['PATCH'])
@require_jwt
def ajustar_stock(sku_repuesto):
    from app import mysql

    if g.usuario.get('rol') not in ['propietario', 'admin']:
        return jsonify({"error": "No tienes permiso para modificar el inventario"}), 403

    datos = request.get_json(silent=True) or {}
    cantidad = datos.get('cantidad')

    if not isinstance(cantidad, int) or cantidad == 0:
        return jsonify({"error": "cantidad debe ser un número entero distinto de 0 (positivo para entrada, negativo para salida)"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT nombre, stock FROM repuestos WHERE sku_repuesto = %s", (sku_repuesto,))
        repuesto = cur.fetchone()

        if repuesto is None:
            cur.close()
            return jsonify({"error": "Repuesto no encontrado"}), 404

        stock_anterior = repuesto[1]
        if stock_anterior + cantidad < 0:
            cur.close()
            return jsonify({"error": f"No se pueden sacar {-cantidad} unidades: solo hay {stock_anterior}"}), 409

        # El "AND stock + %s >= 0" evita dejar stock negativo si dos peticiones llegan a la vez
        cur.execute("UPDATE repuestos SET stock = stock + %s WHERE sku_repuesto = %s AND stock + %s >= 0",
                    (cantidad, sku_repuesto, cantidad))
        if cur.rowcount == 0:
            mysql.connection.rollback()
            cur.close()
            return jsonify({"error": "Stock insuficiente"}), 409

        mysql.connection.commit()
        cur.close()

        return jsonify({
            "mensaje": "Entrada registrada" if cantidad > 0 else "Salida registrada",
            "sku_repuesto": sku_repuesto,
            "stock_anterior": stock_anterior,
            "stock_nuevo": stock_anterior + cantidad
        }), 200
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500


@repuestos_bp.route('/repuestos/valor-inventario', methods=['GET'])
@require_jwt
def valor_inventario():
    from app import mysql

    # Reportes del inventario: solo el propietario ve cuánto vale
    if g.usuario.get('rol') != 'propietario':
        return jsonify({"error": "Solo el propietario puede ver los reportes del inventario"}), 403

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT IFNULL(m.nombre_marca, 'Sin marca') AS marca, COUNT(*), SUM(r.stock), SUM(r.precio * r.stock) "
                    "FROM repuestos r "
                    "LEFT JOIN marcas m ON m.id_marca = r.id_marca "
                    "GROUP BY marca "
                    "ORDER BY SUM(r.precio * r.stock) DESC")
        datos = cur.fetchall()
        cur.close()

        por_marca = []
        valor_total = 0
        for fila in datos:
            valor = float(fila[3] or 0)
            valor_total += valor
            por_marca.append({
                "marca": fila[0],
                "referencias": fila[1],
                "unidades": int(fila[2] or 0),
                "valor": valor
            })

        return jsonify({
            "valor_total": valor_total,
            "por_marca": por_marca
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
