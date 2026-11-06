from app.repositories import reporte as repo


# este service es para armar el diccoinario conlos equipo sque luego van a la tabla de posiciones de una edición del torneo

def tabla_posiciones(conn, id_torneo):

    # una fila en cero para cada equipo del torneo
    tabla = {}
    for equipo in repo.equipos_del_torneo(conn, id_torneo):
        tabla[equipo["id_equipo"]] = {
            "equipo": equipo["nombre"],
            "PJ": 0, "PG": 0, "PE": 0, "PP": 0,
            "GF": 0, "GC": 0, "DG": 0, "Pts": 0,
        }

        # sumar a cada equipo los resultados de sus partidos jugados
    for partido in repo.resultados_del_torneo(conn, id_torneo):

        local = tabla[partido["id_equipo_local"]]
        visitante = tabla[partido["id_equipo_visitante"]]
        gl = partido["goles_local"]
        gv = partido["goles_visitante"]

        # Partidos jugados
        local["PJ"] += 1
        visitante["PJ"] += 1

        # Goles a favor y en contra
        local["GF"] += gl
        local["GC"] += gv
        visitante["GF"] += gv
        visitante["GC"] += gl

        # Ganado, empatado o perdido, y los puntos
        if gl > gv:                 # ganó el local
            local["PG"] += 1
            local["Pts"] += 3
            visitante["PP"] += 1
        elif gl < gv:               # ganó el visitante
            visitante["PG"] += 1
            visitante["Pts"] += 3
            local["PP"] += 1
        else:                       # empate
            local["PE"] += 1
            local["Pts"] += 1
            visitante["PE"] += 1
            visitante["Pts"] += 1

    # dif de goles de cada equipo
    for fila in tabla.values():
        fila["DG"] = fila["GF"] - fila["GC"]

    # retorna la tabla con los datos de cada equipo
    return sorted(
        tabla.values(),
        key=lambda fila: (fila["Pts"], fila["DG"], fila["GF"]), # mismo criterio que ORDER BY Pts DESC, DG DESC, GF DESC
        reverse=True, # de mayor a menor
    )