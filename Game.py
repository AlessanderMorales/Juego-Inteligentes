import pygame
import math
import random
from collections import deque

from config import *
from utils import hex_a_pixel, pixel_a_hex
from hexagon import Hexagono

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
        self.img_montana = pygame.transform.scale(pygame.image.load("montana.png").convert_alpha(), (int(RADIO_HEX*1.8), int(RADIO_HEX*1.8)))
        self.img_pasto = pygame.transform.scale(pygame.image.load("pasto.png").convert_alpha(), (int(RADIO_HEX*1.8), int(RADIO_HEX*1.8)))
        
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
            
            if h.tipo == "obstaculo":
                rect = self.img_montana.get_rect(center=centro)
                self.pantalla.blit(self.img_montana, rect)
            else:
                rect = self.img_pasto.get_rect(center=centro)
                self.pantalla.blit(self.img_pasto, rect)
            
            puntos = [ (centro[0] + RADIO_HEX*0.9*math.cos(math.radians(60*i-30)),
                        centro[1] + RADIO_HEX*0.9*math.sin(math.radians(60*i-30))) for i in range(6)]
            
            if h.en_camino and self.modo_ia:
                pygame.draw.polygon(self.pantalla, COLOR_CAMINO, puntos, 5)
            elif h.visitado and self.modo_ia:
                pygame.draw.polygon(self.pantalla, (60, 170, 60), puntos, 3)
                
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