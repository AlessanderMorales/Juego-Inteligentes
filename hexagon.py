class Hexagono:
    def __init__(self, q, r):
        self.q, self.r = q, r
        self.tipo = "pasto"
        self.visitado = False
        self.padre = None
        self.en_camino = False
