"""
Sistema de Algoritmos de Grafos (ADA8) - Estructura de datos, Unidad 4
Une en una sola interfaz visual (tkinter) los algoritmos de:
Dijkstra, Floyd, Warshall y Kruskal.
"""
import heapq
import math
import tkinter as tk
from tkinter import ttk, messagebox

INF = float("inf")

# ----------------------------- Colores -----------------------------
AZUL = "#1d4ed8"
VERDE = "#16a34a"
NARANJA = "#f59e0b"
ROJO = "#dc2626"
GRIS = "#9ca3af"
FONDO_NODO = "#dbeafe"

# ------------------------- Grafos de ejemplo -----------------------
POS_PONDERADO = {"A": (80, 100), "B": (250, 60), "C": (120, 290),
                 "D": (340, 190), "E": (300, 385), "F": (510, 300)}
ARISTAS_BASE = [("A", "B", 4), ("A", "C", 2), ("B", "C", 1), ("B", "D", 5),
                ("C", "D", 8), ("C", "E", 10), ("D", "E", 2), ("D", "F", 6),
                ("E", "F", 3)]

POS_DIRIGIDO = {"A": (100, 110), "B": (270, 70), "C": (410, 170),
                "D": (500, 310), "E": (110, 310)}
ARCOS_BASE = [("A", "B"), ("B", "C"), ("C", "D"), ("E", "A")]

RADIO = 20


# =================================================================
#                       ALGORITMOS (generan pasos)
# =================================================================
def formato_matriz(m, nombres, booleana=False):
    """Devuelve una matriz como texto alineado."""
    lineas = ["     " + "".join(f"{n:>5}" for n in nombres)]
    for n, fila in zip(nombres, m):
        celdas = ""
        for x in fila:
            if booleana:
                celdas += f"{int(bool(x)):>5}"
            else:
                celdas += f"{'INF' if x == INF else x:>5}"
        lineas.append(f"{n:>4} {celdas}")
    return "\n".join(lineas)


def pasos_dijkstra(aristas, nodos, origen, destino):
    grafo = {n: {} for n in nodos}
    for u, v, p in aristas:
        grafo[u][v] = p
        grafo[v][u] = p
    dist = {n: INF for n in nodos}
    previo = {n: None for n in nodos}
    dist[origen] = 0
    cola = [(0, origen)]
    visitados = set()
    pasos = [{"texto": f"Inicio: dist[{origen}] = 0 y las demás en INF.",
              "nodos": {origen: NARANJA}, "aristas": {}}]
    while cola:
        d, u = heapq.heappop(cola)
        if u in visitados:
            continue
        visitados.add(u)
        lineas = [f"Se fija el nodo {u} con distancia {d}."]
        for v, peso in grafo[u].items():
            if v in visitados:
                continue
            if d + peso < dist[v]:
                dist[v] = d + peso
                previo[v] = u
                heapq.heappush(cola, (dist[v], v))
                lineas.append(f"   Relajación: dist[{v}] = {dist[v]} (por {u})")
        nodos_col = {n: VERDE for n in visitados}
        nodos_col[u] = NARANJA
        arbol = {frozenset((previo[n], n)): (VERDE, 4, False)
                 for n in visitados if previo[n] is not None}
        pasos.append({"texto": "\n".join(lineas), "nodos": nodos_col,
                      "aristas": arbol})

    resumen = ["Resultado final (distancias desde " + origen + "):"]
    for n in nodos:
        resumen.append(f"   {origen} -> {n}: {dist[n] if dist[n] != INF else 'INF'}")
    arbol = {frozenset((previo[n], n)): (VERDE, 4, False)
             for n in nodos if previo[n] is not None}
    nodos_col = {n: VERDE for n in nodos}
    if destino and dist[destino] != INF:
        ruta = []
        x = destino
        while x is not None:
            ruta.append(x)
            x = previo[x]
        ruta.reverse()
        for a, b in zip(ruta, ruta[1:]):
            arbol[frozenset((a, b))] = (ROJO, 6, False)
        resumen.append(f"\nRuta más corta {origen} -> {destino}: "
                       f"{' -> '.join(ruta)} (costo {dist[destino]})")
    elif destino:
        resumen.append(f"\nNo existe ruta de {origen} a {destino}.")
    pasos.append({"texto": "\n".join(resumen), "nodos": nodos_col,
                  "aristas": arbol})
    return pasos


def pasos_floyd(aristas, nodos, origen, destino):
    n = len(nodos)
    idx = {nom: i for i, nom in enumerate(nodos)}
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    sig = [[None] * n for _ in range(n)]
    for u, v, p in aristas:
        i, j = idx[u], idx[v]
        dist[i][j] = dist[j][i] = p
        sig[i][j] = j
        sig[j][i] = i
    pasos = [{"texto": "Matriz inicial (solo conexiones directas):\n"
                       + formato_matriz(dist, nodos),
              "nodos": {}, "aristas": {}}]
    for k in range(n):
        cambios = 0
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    sig[i][j] = sig[i][k]
                    cambios += 1
        pasos.append({"texto": f"k = {nodos[k]}: se prueba pasar por {nodos[k]} "
                               f"({cambios} mejoras)\n"
                               + formato_matriz(dist, nodos),
                      "nodos": {nodos[k]: NARANJA}, "aristas": {}})
    texto = ["Matriz final de distancias mínimas entre todos los pares:",
             formato_matriz(dist, nodos)]
    arist = {}
    if origen and destino and origen != destino:
        i, j = idx[origen], idx[destino]
        if dist[i][j] == INF:
            texto.append(f"\nNo existe ruta de {origen} a {destino}.")
        else:
            ruta = [i]
            while i != j:
                i = sig[i][j]
                ruta.append(i)
            nombres = [nodos[x] for x in ruta]
            for a, b in zip(nombres, nombres[1:]):
                arist[frozenset((a, b))] = (ROJO, 6, False)
            texto.append(f"\nRuta {origen} -> {destino}: {' -> '.join(nombres)} "
                         f"(costo {dist[idx[origen]][idx[destino]]})")
    pasos.append({"texto": "\n".join(texto),
                  "nodos": {x: VERDE for x in nodos}, "aristas": arist})
    return pasos


def pasos_warshall(arcos, nodos, origen, destino):
    n = len(nodos)
    idx = {nom: i for i, nom in enumerate(nodos)}
    r = [[False] * n for _ in range(n)]
    for u, v in arcos:
        r[idx[u]][idx[v]] = True
    directos = {(idx[u], idx[v]) for u, v in arcos}

    def nuevos():
        return {(nodos[i], nodos[j]): (AZUL, 3, True)
                for i in range(n) for j in range(n)
                if r[i][j] and i != j and (i, j) not in directos}

    pasos = [{"texto": "Matriz de adyacencia inicial (conexiones directas):\n"
                       + formato_matriz(r, nodos, True),
              "nodos": {}, "aristas": {}}]
    for k in range(n):
        antes = sum(sum(f) for f in r)
        for i in range(n):
            for j in range(n):
                r[i][j] = r[i][j] or (r[i][k] and r[k][j])
        nuevas = sum(sum(f) for f in r) - antes
        pasos.append({"texto": f"k = {nodos[k]}: se prueba pasar por {nodos[k]} "
                               f"({nuevas} conexiones nuevas)\n"
                               + formato_matriz(r, nodos, True),
                      "nodos": {nodos[k]: NARANJA}, "aristas": nuevos()})
    texto = ["Cierre transitivo final:", formato_matriz(r, nodos, True), ""]
    nodos_col = {}
    if origen:
        i = idx[origen]
        alc = [nodos[j] for j in range(n) if r[i][j] and j != i]
        texto.append(f"Desde {origen} se llega a: {', '.join(alc) if alc else 'ninguno'}")
        nodos_col = {x: VERDE for x in alc}
        nodos_col[origen] = NARANJA
        if destino and destino != origen:
            texto.append(f"¿Hay camino de {origen} a {destino}? "
                         f"{'SÍ' if r[i][idx[destino]] else 'NO'}")
    pasos.append({"texto": "\n".join(texto), "nodos": nodos_col,
                  "aristas": nuevos()})
    return pasos


def pasos_kruskal(aristas, nodos):
    padre = {n: n for n in nodos}

    def buscar(x):
        while padre[x] != x:
            padre[x] = padre[padre[x]]
            x = padre[x]
        return x

    paleta = ["#2563eb", "#16a34a", "#f59e0b", "#9333ea", "#0891b2", "#db2777"]

    def col_nodos():
        raices = sorted({buscar(n) for n in nodos})
        mapa = {r: paleta[i % len(paleta)] for i, r in enumerate(raices)}
        return {n: mapa[buscar(n)] for n in nodos}

    ordenadas = sorted(aristas, key=lambda a: a[2])
    pasos = [{"texto": "Aristas ordenadas por peso:\n   "
                       + ", ".join(f"{u}-{v}({p})" for u, v, p in ordenadas)
                       + "\nCada nodo empieza en su propio conjunto (un color).",
              "nodos": col_nodos(), "aristas": {}}]
    arbol, total = {}, 0
    for u, v, p in ordenadas:
        ru, rv = buscar(u), buscar(v)
        clave = frozenset((u, v))
        if ru != rv:
            padre[ru] = rv
            arbol[clave] = (VERDE, 5, False)
            total += p
            pasos.append({"texto": f"Se agrega {u}-{v} (peso {p}): une dos conjuntos.",
                          "nodos": col_nodos(), "aristas": dict(arbol)})
        else:
            tmp = dict(arbol)
            tmp[clave] = (ROJO, 3, True)
            pasos.append({"texto": f"Se descarta {u}-{v} (peso {p}): formaría un ciclo.",
                          "nodos": col_nodos(), "aristas": tmp})
    lista = ", ".join(f"{tuple(sorted(k))[0]}-{tuple(sorted(k))[1]}" for k in arbol)
    conexo = len({buscar(n) for n in nodos}) == 1
    texto = [f"Árbol de expansión mínima: {lista}",
             f"Costo total: {total}"]
    if not conexo:
        texto.append("Aviso: el grafo no es conexo, se obtuvo un bosque de expansión.")
    pasos.append({"texto": "\n".join(texto), "nodos": col_nodos(),
                  "aristas": dict(arbol)})
    return pasos


# =================================================================
#                          INTERFAZ TKINTER
# =================================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title("Sistema de Algoritmos de Grafos - ADA8")
        root.geometry("1180x700")
        root.configure(bg="white")

        self.aristas = list(ARISTAS_BASE)
        self.arcos = list(ARCOS_BASE)
        self.modo = "dijkstra"
        self.pasos, self.indice, self.trabajo = [], 0, None

        # ---- barra superior: algoritmos ----
        barra = tk.Frame(root, bg="white")
        barra.pack(fill="x", padx=10, pady=(10, 4))
        self.botones = {}
        for clave, nombre in [("dijkstra", "Dijkstra"), ("floyd", "Floyd"),
                              ("warshall", "Warshall"), ("kruskal", "Kruskal")]:
            b = tk.Button(barra, text=nombre, width=12, relief="raised",
                          command=lambda c=clave: self.cambiar_modo(c))
            b.pack(side="left", padx=4)
            self.botones[clave] = b
        self.titulo = tk.Label(barra, text="", bg="white", fg=AZUL,
                               font=("DejaVu Sans", 11, "bold"))
        self.titulo.pack(side="left", padx=16)

        cuerpo = tk.Frame(root, bg="white")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=4)

        # ---- izquierda: lienzo y controles ----
        izq = tk.Frame(cuerpo, bg="white")
        izq.pack(side="left", fill="both")
        self.lienzo = tk.Canvas(izq, width=590, height=440, bg="white",
                                highlightthickness=1, highlightbackground="#d1d5db")
        self.lienzo.pack()

        ctrl = tk.Frame(izq, bg="white")
        ctrl.pack(fill="x", pady=8)
        tk.Label(ctrl, text="Origen:", bg="white").grid(row=0, column=0, sticky="e")
        self.cb_origen = ttk.Combobox(ctrl, width=4, state="readonly")
        self.cb_origen.grid(row=0, column=1, padx=4)
        tk.Label(ctrl, text="Destino:", bg="white").grid(row=0, column=2, sticky="e")
        self.cb_destino = ttk.Combobox(ctrl, width=4, state="readonly")
        self.cb_destino.grid(row=0, column=3, padx=4)
        tk.Button(ctrl, text="Siguiente paso", command=self.siguiente).grid(
            row=0, column=4, padx=4)
        tk.Button(ctrl, text="Ejecutar todo", command=self.ejecutar_todo).grid(
            row=0, column=5, padx=4)
        tk.Button(ctrl, text="Reiniciar", command=self.reiniciar).grid(
            row=0, column=6, padx=4)

        tk.Label(ctrl, text="Agregar:", bg="white").grid(row=1, column=0, sticky="e", pady=6)
        self.cb_u = ttk.Combobox(ctrl, width=4, state="readonly")
        self.cb_u.grid(row=1, column=1, padx=4)
        tk.Label(ctrl, text="a", bg="white").grid(row=1, column=2)
        self.cb_v = ttk.Combobox(ctrl, width=4, state="readonly")
        self.cb_v.grid(row=1, column=3, padx=4)
        tk.Label(ctrl, text="Peso:", bg="white").grid(row=1, column=4, sticky="e")
        self.e_peso = tk.Entry(ctrl, width=5)
        self.e_peso.insert(0, "3")
        self.e_peso.grid(row=1, column=5, sticky="w", padx=4)
        tk.Button(ctrl, text="Agregar arista", command=self.agregar).grid(
            row=1, column=6, padx=4)
        tk.Button(ctrl, text="Grafo original", command=self.restablecer).grid(
            row=1, column=7, padx=4)

        # ---- derecha: bitácora ----
        der = tk.Frame(cuerpo, bg="white")
        der.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(der, text="Bitácora de ejecución", bg="white",
                 font=("DejaVu Sans", 10, "bold")).pack(anchor="w")
        marco = tk.Frame(der)
        marco.pack(fill="both", expand=True)
        sb = tk.Scrollbar(marco)
        sb.pack(side="right", fill="y")
        self.log = tk.Text(marco, width=58, height=30, wrap="word",
                           font=("Liberation Mono", 9), bg="#f3f4f6",
                           yscrollcommand=sb.set, state="disabled")
        self.log.pack(side="left", fill="both", expand=True)
        sb.config(command=self.log.yview)

        for cb in (self.cb_origen, self.cb_destino):
            cb.bind("<<ComboboxSelected>>", lambda e: self.reiniciar())
        self.cambiar_modo("dijkstra")

    # ---------------- utilidades ----------------
    def nodos(self):
        return sorted((POS_DIRIGIDO if self.modo == "warshall" else POS_PONDERADO))

    def posiciones(self):
        return POS_DIRIGIDO if self.modo == "warshall" else POS_PONDERADO

    def escribir(self, texto, limpiar=False):
        self.log.config(state="normal")
        if limpiar:
            self.log.delete("1.0", "end")
        self.log.insert("end", texto + "\n\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def cancelar_animacion(self):
        if self.trabajo is not None:
            self.root.after_cancel(self.trabajo)
            self.trabajo = None

    # ---------------- modos ----------------
    def cambiar_modo(self, modo):
        self.cancelar_animacion()
        self.modo = modo
        nombres = {"dijkstra": "Dijkstra: ruta más corta desde un origen",
                   "floyd": "Floyd: rutas más cortas entre todos los pares",
                   "warshall": "Warshall: cierre transitivo (grafo dirigido)",
                   "kruskal": "Kruskal: árbol de expansión mínima"}
        self.titulo.config(text=nombres[modo])
        for c, b in self.botones.items():
            b.config(relief="sunken" if c == modo else "raised",
                     bg=AZUL if c == modo else "#e5e7eb",
                     fg="white" if c == modo else "black")
        nodos = self.nodos()
        for cb in (self.cb_origen, self.cb_destino, self.cb_u, self.cb_v):
            cb["values"] = nodos
        self.cb_origen.set(nodos[0])
        self.cb_destino.set(nodos[-1])
        self.cb_u.set(nodos[0])
        self.cb_v.set(nodos[1])
        usa_od = modo != "kruskal"
        estado = "readonly" if usa_od else "disabled"
        self.cb_origen.config(state=estado)
        self.cb_destino.config(state=estado)
        self.e_peso.config(state="disabled" if modo == "warshall" else "normal")
        self.reiniciar()

    def reiniciar(self):
        self.cancelar_animacion()
        self.pasos, self.indice = [], 0
        self.dibujar()
        self.escribir(f"{self.titulo.cget('text')}\nPulsa 'Siguiente paso' para ver "
                      f"el algoritmo paso a paso o 'Ejecutar todo'.", limpiar=True)

    def restablecer(self):
        self.aristas = list(ARISTAS_BASE)
        self.arcos = list(ARCOS_BASE)
        self.reiniciar()

    def agregar(self):
        u, v = self.cb_u.get(), self.cb_v.get()
        if u == v:
            messagebox.showwarning("Arista inválida", "Elige dos nodos distintos.")
            return
        if self.modo == "warshall":
            if (u, v) not in self.arcos:
                self.arcos.append((u, v))
        else:
            try:
                peso = int(self.e_peso.get())
                if peso <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Peso inválido", "El peso debe ser un entero positivo.")
                return
            self.aristas = [a for a in self.aristas if {a[0], a[1]} != {u, v}]
            self.aristas.append((u, v, peso))
        self.reiniciar()

    # ---------------- ejecución ----------------
    def generar(self):
        o, d = self.cb_origen.get(), self.cb_destino.get()
        if self.modo == "dijkstra":
            self.pasos = pasos_dijkstra(self.aristas, self.nodos(), o, d)
        elif self.modo == "floyd":
            self.pasos = pasos_floyd(self.aristas, self.nodos(), o, d)
        elif self.modo == "warshall":
            self.pasos = pasos_warshall(self.arcos, self.nodos(), o, d)
        else:
            self.pasos = pasos_kruskal(self.aristas, self.nodos())
        self.indice = 0
        self.escribir(self.titulo.cget("text"), limpiar=True)

    def siguiente(self):
        if not self.pasos or self.indice >= len(self.pasos):
            if self.pasos and self.indice >= len(self.pasos):
                return
            self.generar()
        paso = self.pasos[self.indice]
        self.indice += 1
        self.dibujar(paso)
        self.escribir(f"[Paso {self.indice}/{len(self.pasos)}]\n{paso['texto']}")

    def ejecutar_todo(self):
        self.cancelar_animacion()
        self.generar()
        self._animar()

    def _animar(self):
        if self.indice < len(self.pasos):
            self.siguiente()
            self.trabajo = self.root.after(800, self._animar)
        else:
            self.trabajo = None

    # ---------------- dibujo ----------------
    def dibujar(self, paso=None):
        c = self.lienzo
        c.delete("all")
        pos = self.posiciones()
        paso = paso or {"nodos": {}, "aristas": {}}
        dirigido = self.modo == "warshall"

        # aristas / arcos base
        if dirigido:
            base = [(u, v, None) for u, v in self.arcos]
        else:
            base = self.aristas
        for u, v, p in base:
            clave = (u, v) if dirigido else frozenset((u, v))
            color, ancho, punteada = paso["aristas"].get(clave, (GRIS, 2, False))
            self._linea(pos[u], pos[v], color, ancho, punteada, dirigido)
            if p is not None:
                mx, my = (pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2
                c.create_rectangle(mx - 12, my - 10, mx + 12, my + 10,
                                   fill="white", outline="")
                c.create_text(mx, my, text=str(p), font=("DejaVu Sans", 10, "bold"),
                              fill="#111827")
        # conexiones derivadas (Warshall): no están en la lista base
        if dirigido:
            directos = {(u, v) for u, v in self.arcos}
            for clave, (color, ancho, punteada) in paso["aristas"].items():
                if clave not in directos:
                    self._linea(pos[clave[0]], pos[clave[1]], color, ancho,
                                punteada, True)
        # nodos
        for n, (x, y) in pos.items():
            color = paso["nodos"].get(n, FONDO_NODO)
            claro = color == FONDO_NODO
            c.create_oval(x - RADIO, y - RADIO, x + RADIO, y + RADIO, fill=color,
                          outline=AZUL, width=2)
            c.create_text(x, y, text=n, font=("DejaVu Sans", 12, "bold"),
                          fill="#111827" if claro else "white")
        # leyenda
        if dirigido:
            c.create_text(10, 425, anchor="w", font=("DejaVu Sans", 9), fill="#475569",
                          text="Gris: arco directo   Azul punteado: conexión nueva (cierre transitivo)")
        else:
            c.create_text(10, 425, anchor="w", font=("DejaVu Sans", 9), fill="#475569",
                          text="Verde: aceptado   Rojo: ruta final / descartado   Naranja: nodo actual")

    def _linea(self, p1, p2, color, ancho, punteada, flecha):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        largo = math.hypot(dx, dy)
        ux, uy = dx / largo, dy / largo
        x1, y1 = p1[0] + ux * RADIO, p1[1] + uy * RADIO
        x2, y2 = p2[0] - ux * RADIO, p2[1] - uy * RADIO
        opciones = {"fill": color, "width": ancho}
        if punteada:
            opciones["dash"] = (6, 4)
        if flecha:
            opciones["arrow"] = tk.LAST
            opciones["arrowshape"] = (12, 14, 5)
        self.lienzo.create_line(x1, y1, x2, y2, **opciones)


if __name__ == "__main__":
    ventana = tk.Tk()
    App(ventana)
    ventana.mainloop()
