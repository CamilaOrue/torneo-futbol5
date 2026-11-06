def obtener_usuario(correo: str, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT contrasena, rol FROM login WHERE correo = %s", (correo,))
    usuario = cursor.fetchone()
    cursor.close()
    return usuario
