class DFSIA:
    def __init__(self, tablero, start, meta):
        self.tablero = tablero
        self.meta = meta
        self.ia_completa = False
        
        for h in self.tablero.values():
            h.visitado = h.en_camino = False
            h.padre = None
            
        start_tuple = tuple(start)
        self.tablero[start_tuple].visitado = True
        self.frontera = [start_tuple] # Using a stack instead of queue/heap

    def step(self):
        if self.frontera and not self.ia_completa:
            curr = self.frontera.pop() # LIFO pop
            
            if curr == self.meta:
                self.ia_completa = True
                self.marcar_camino()
                return
                
            for dq, dr in [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]:
                vec = (curr[0]+dq, curr[1]+dr)
                if vec in self.tablero:
                    h_vec = self.tablero[vec]
                    if not h_vec.visitado and h_vec.tipo != "obstaculo":
                        h_vec.visitado = True
                        h_vec.padre = curr
                        self.frontera.append(vec)

    def marcar_camino(self):
        p = self.meta
        while p in self.tablero and self.tablero[p].padre:
            self.tablero[p].en_camino = True
            p = self.tablero[p].padre
