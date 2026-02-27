import pygame
import math
import random
from collections import deque

ANCHO, ALTO = 1100, 750
RADIO_HEX = 32
FPS = 60

COLOR_PASTO = (34, 139, 34)
COLOR_TIERRA = (139, 69, 19)
COLOR_AGUA = (30, 144, 255)
COLOR_CAMINO = (240, 230, 140)
COLOR_TEXTO = (255, 255, 255)
COLOR_BORDE = (20, 100, 20)

MISIONES = {
    "1": {"nombre": "Ir al Establo",    "color": (200, 50, 50),  "meta_pos": (5, -5)},
    "2": {"nombre": "Buscar el Pozo",   "color": (50, 50, 200),  "meta_pos": (0, 5)},
    "3": {"nombre": "Llegar al Huerto", "color": (50, 200, 50),  "meta_pos": (-5, 5)},
    "4": {"nombre": "Ver las Ovejas",   "color": (230, 230, 230),"meta_pos": (5, 0)},
    "5": {"nombre": "Ir al Molino",     "color": (150, 75, 0),   "meta_pos": (-5, 0)}
}

def hex_a_pixel(q, r, radio):
    x = radio * (3/2 * q)
    y = radio * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
    return (int(x + 450), int(y + ALTO/2))

def pixel_a_hex(x, y, radio):
    x, y = x - 450, y - ALTO/2
    q = (2/3 * x) / radio
    r = (-1/3 * x + math.sqrt(3)/3 * y) / radio
    return hex_round(q, r)

def hex_round(q, r):
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
    if dq > dr and dq > ds: rq = -rr - rs
    elif dr > ds: rr = -rq - rs
    return rq, rr

class Hexagono:
    def __init__(self, q, r):
        self.q, self.r = q, r
        self.tipo = "pasto"
        self.visitado = False
        self.padre = None
        self.en_camino = False

class GranjaBFS:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Aventura en el Campo: Prototipo BFS")
        self.fuente_m = pygame.font.SysFont("Arial", 22)
        self.fuente_l = pygame.font.SysFont("Arial", 30, bold=True)
        self.reloj = pygame.time.Clock()
        self.id_mision = "1"
        self.modo_ia = False
        
        self.img_pastor = pygame.transform.scale(pygame.image.load("pastor.png").convert_alpha(), (45, 45))
        self.img_oveja = pygame.transform.scale(pygame.image.load("oveja.png").convert_alpha(), (45, 45))
        
        self.crear_mapa()

    def crear_mapa(self):
        self.tablero = {}
        r_mapa = 7
        for q in range(-r_mapa, r_mapa + 1):
            for r in range(max(-r_mapa, -q-r_mapa), min(r_mapa, -q+r_mapa) + 1):
                self.tablero[(q, r)] = Hexagono(q, r)
                if random.random() < 0.18 and (q,r) != (0,0):
                    self.tablero[(q, r)].tipo = "obstaculo"
        
        self.pos_granjero = [0, 0]
        self.meta = MISIONES[self.id_mision]["meta_pos"]
        self.tablero[self.meta].tipo = "meta"
        self.ganado = False
        self.reset_ia()

    def reset_ia(self):
        for h in self.tablero.values():
            h.visitado = h.en_camino = False
            h.padre = None
        self.frontera = deque([tuple(self.pos_granjero)])
        self.tablero[tuple(self.pos_granjero)].visitado = True
        self.ia_completa = False

    def bfs_step(self):
        if self.frontera and not self.ia_completa:
            curr = self.frontera.popleft()
            if curr == self.meta:
                self.ia_completa = True
                self.marcar_camino()
                return
            for dq, dr in [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]:
                vec = (curr[0]+dq, curr[1]+dr)
                if vec in self.tablero and not self.tablero[vec].visitado:
                    if self.tablero[vec].tipo != "obstaculo":
                        self.tablero[vec].visitado = True
                        self.tablero[vec].padre = curr
                        self.frontera.append(vec)

    def marcar_camino(self):
        p = self.meta
        while p in self.tablero and self.tablero[p].padre:
            self.tablero[p].en_camino = True
            p = self.tablero[p].padre

    def mover_granjero(self, destino):
        q, r = self.pos_granjero
        dist = (abs(q - destino[0]) + abs(q + r - destino[0] - destino[1]) + abs(r - destino[1])) / 2
        if dist == 1 and self.tablero[destino].tipo != "obstaculo":
            self.pos_granjero = list(destino)
            if destino == self.meta: self.ganado = True
            self.reset_ia()

    def dibujar(self):
        self.pantalla.fill((20, 50, 20))
        for coords, h in self.tablero.items():
            centro = hex_a_pixel(coords[0], coords[1], RADIO_HEX)
            color = COLOR_PASTO
            if h.tipo == "obstaculo": color = (100, 80, 60)
            if h.visitado and self.modo_ia: color = (60, 170, 60)
            if h.en_camino and self.modo_ia: color = COLOR_CAMINO
            
            puntos = [ (centro[0] + RADIO_HEX*0.9*math.cos(math.radians(60*i-30)),
                        centro[1] + RADIO_HEX*0.9*math.sin(math.radians(60*i-30))) for i in range(6)]
            pygame.draw.polygon(self.pantalla, color, puntos)
            pygame.draw.polygon(self.pantalla, COLOR_BORDE, puntos, 1)

            if coords == tuple(self.pos_granjero):
                rect = self.img_pastor.get_rect(center=centro)
                self.pantalla.blit(self.img_pastor, rect)
            elif h.tipo == "meta":
                rect = self.img_oveja.get_rect(center=centro)
                self.pantalla.blit(self.img_oveja, rect)

        pygame.draw.rect(self.pantalla, (40, 40, 40), (820, 0, 280, ALTO))
        y = 40
        self.pantalla.blit(self.fuente_l.render("MISIÓN DE CAMPO", True, COLOR_TEXTO), (840, y))
        y += 60
        mision = MISIONES[self.id_mision]
        pygame.draw.rect(self.pantalla, mision["color"], (840, y, 240, 45))
        self.pantalla.blit(self.fuente_m.render(mision["nombre"], True, (0,0,0) if self.id_mision=="4" else (255,255,255)), (850, y+10))
        y += 100
        instrucciones = [
            "CLIC: Caminar",
            "ESPACIO: Mostrar BFS",
            "TECLAS 1-5: Cambiar Destino",
            "R: Nuevo Terreno",]
        for linea in instrucciones:
            self.pantalla.blit(self.fuente_m.render(linea, True, (200, 200, 200)), (840, y))
            y += 30
        if self.ganado:
            msg = self.fuente_l.render("¡MISIÓN CUMPLIDA!", True, (255, 255, 0))
            self.pantalla.blit(msg, (320, 20))

    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); return
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    m_hex = pixel_a_hex(ev.pos[0], ev.pos[1], RADIO_HEX)
                    if m_hex in self.tablero: self.mover_granjero(m_hex)
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE: 
                        self.modo_ia = not self.modo_ia
                        if self.modo_ia: self.reset_ia()
                    if ev.key == pygame.K_r: self.crear_mapa()
                    if ev.unicode in MISIONES: 
                        self.id_mision = ev.unicode
                        self.crear_mapa()
            if self.modo_ia and not self.ia_completa: 
                self.bfs_step()
                pygame.time.delay(20)
            self.dibujar()
            pygame.display.flip()
            self.reloj.tick(FPS)

if __name__ == "__main__":
    GranjaBFS().run()