import heapq

class UniformCostIA:
    def __init__(self, tablero, start, meta):
        self.tablero = tablero
        self.meta = meta
        self.ia_completa = False
        
        for h in self.tablero.values():
            h.visitado = h.en_camino = False
            h.padre = None
            h.costo = float('inf')
            
        start_tuple = tuple(start)
        self.tablero[start_tuple].costo = 0
        self.frontera = [(0, start_tuple)]

    def step(self):
        if self.frontera and not self.ia_completa:
            costo_actual, curr = heapq.heappop(self.frontera)
            
            # UCS only marks as visited/explored upon pop
            if self.tablero[curr].visitado:
                return
                
            self.tablero[curr].visitado = True
            
            if curr == self.meta:
                self.ia_completa = True
                self.marcar_camino()
                return
                
            for dq, dr in [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]:
                vec = (curr[0]+dq, curr[1]+dr)
                if vec in self.tablero:
                    h_vec = self.tablero[vec]
                    if h_vec.tipo != "obstaculo" and not h_vec.visitado:
                        costo_paso = 3 if h_vec.tipo == "barro" else 1
                        nuevo_costo = costo_actual + costo_paso
                        
                        if nuevo_costo < h_vec.costo:
                            h_vec.costo = nuevo_costo
                            h_vec.padre = curr
                            heapq.heappush(self.frontera, (nuevo_costo, vec))

    def marcar_camino(self):
        p = self.meta
        while p in self.tablero and self.tablero[p].padre:
            self.tablero[p].en_camino = True
            p = self.tablero[p].padre
