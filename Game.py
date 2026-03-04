import pygame
import math
import random
import heapq
from pathlib import Path

from config import *
from utils import hex_a_pixel, pixel_a_hex
from hexagon import Hexagono
from dijkstra import DijkstraIA
from dfs_search import DFSIA
from uniform_cost import UniformCostIA
from voice_helper import AsistenteVoz, interpretar_intencion

class GranjaBFS:
    def __init__(self):
        pygame.init()
        base_dir = Path(__file__).resolve().parent
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Aventura en el Campo: Prototipo BFS")
        self.fuente_m = pygame.font.SysFont("Arial", 22)
        self.fuente_l = pygame.font.SysFont("Arial", 30, bold=True)
        self.reloj = pygame.time.Clock()
        self.id_mision = "1"
        self.modo_ia = False
        self.tipos_ia = ["Dijkstra", "DFS", "UCS"]
        self.tipo_ia_idx = 0
        self.tipo_ia = self.tipos_ia[self.tipo_ia_idx]
        self.mensajes_guia = [
            "¿Necesitas ayuda? Presiona ESPACIO para ver una ruta.",
            "Puedes cambiar la misión con teclas 1-5.",
            "Si un camino se ve difícil, prueba otra dirección.",
            "Estoy aquí para ayudarte, paso a paso.",
        ]
        self.asistente_voz = AsistenteVoz()
        self.mascota_rect = pygame.Rect(918, 628, 84, 84)
        ahora = pygame.time.get_ticks()
        self.msg_guia = "¡Hola! Soy tu mascota guía."
        self.msg_guia_expira = 0
        self.prox_msg_guia = ahora + 7000
        self.intervalo_guia_ms = 18000
        self.ultimo_movimiento_ms = ahora
        self.guia_celebro = False
        self.guia_alerta_tiempo = False
        
        self.img_pastor = pygame.transform.scale(pygame.image.load(base_dir / "pastor.png").convert_alpha(), (45, 45))
        self.img_oveja = pygame.transform.scale(pygame.image.load(base_dir / "oveja.png").convert_alpha(), (45, 45))
        self.img_montana = pygame.transform.scale(pygame.image.load(base_dir / "montana.png").convert_alpha(), (int(RADIO_HEX*1.8), int(RADIO_HEX*1.8)))
        self.img_pasto = pygame.transform.scale(pygame.image.load(base_dir / "pasto.png").convert_alpha(), (int(RADIO_HEX*1.8), int(RADIO_HEX*1.8)))
        self.img_barro = pygame.transform.scale(pygame.image.load(base_dir / "barro.png").convert_alpha(), (int(RADIO_HEX*1.8), int(RADIO_HEX*1.8)))
        
        self.crear_mapa()
        if self.asistente_voz.disponible:
            self.hablar_guia("Hola, soy tu mascota guía. Presiona V o haz clic en mí para hablar.", 6500)
        else:
            self.set_mensaje_guia("Instala speechrecognition, pyaudio y pyttsx3 para activar voz.", 7000)

    def crear_mapa(self):
        self.tablero = {}
        r_mapa = 7
        for q in range(-r_mapa, r_mapa + 1):
            for r in range(max(-r_mapa, -q-r_mapa), min(r_mapa, -q+r_mapa) + 1):
                self.tablero[(q, r)] = Hexagono(q, r)
                r_val = random.random()
                if r_val < 0.18 and (q,r) != (0,0):
                    self.tablero[(q, r)].tipo = "obstaculo"
                elif r_val < 0.30 and (q,r) != (0,0):
                    self.tablero[(q, r)].tipo = "barro"
        
        self.pos_granjero = [0, 0]
        self.tiempo = 15
        self.meta = MISIONES[self.id_mision]["meta_pos"]
        self.tablero[self.meta].tipo = "meta"
        self.ganado = False
        self.guia_celebro = False
        self.guia_alerta_tiempo = False
        self.set_mensaje_guia("Nueva misión lista. ¡Vamos!", 5000)
        self.reset_ia()

    def reset_ia(self):
        if self.tipo_ia == "Dijkstra":
            self.ia = DijkstraIA(self.tablero, self.pos_granjero, self.meta)
        elif self.tipo_ia == "DFS":
            self.ia = DFSIA(self.tablero, self.pos_granjero, self.meta)
        elif self.tipo_ia == "UCS":
            self.ia = UniformCostIA(self.tablero, self.pos_granjero, self.meta)

    def mover_granjero(self, destino):
        q, r = self.pos_granjero
        dist = (abs(q - destino[0]) + abs(q + r - destino[0] - destino[1]) + abs(r - destino[1])) / 2
        if dist == 1 and self.tablero[destino].tipo != "obstaculo" and self.tiempo > 0 and not self.ganado:
            costo = 3 if self.tablero[destino].tipo == "barro" else 1
            if self.tiempo >= costo:
                self.tiempo -= costo
                self.pos_granjero = list(destino)
                self.ultimo_movimiento_ms = pygame.time.get_ticks()
                if destino == self.meta: self.ganado = True
                self.reset_ia()

    def set_mensaje_guia(self, texto, duracion_ms=6000):
        self.msg_guia = texto
        self.msg_guia_expira = pygame.time.get_ticks() + duracion_ms

    def hablar_guia(self, texto, duracion_ms=6000):
        self.set_mensaje_guia(texto, duracion_ms)
        self.asistente_voz.hablar(texto)

    def aplicar_intencion_voz(self, intencion):
        if intencion == "usar_dijkstra":
            self.modo_ia = True
            self.tipo_ia = "Dijkstra"
            self.reset_ia()
            self.hablar_guia("Perfecto. Uso Dijkstra para ayudarte.", 5000)
            return

        if intencion == "usar_dfs":
            self.modo_ia = True
            self.tipo_ia = "DFS"
            self.reset_ia()
            self.hablar_guia("Listo. Exploramos con DFS.", 5000)
            return

        if intencion == "usar_ucs":
            self.modo_ia = True
            self.tipo_ia = "UCS"
            self.reset_ia()
            self.hablar_guia("Entendido. Busco por costo uniforme.", 5000)
            return

        if intencion == "pedir_ayuda" or intencion == "afirmar":
            self.modo_ia = True
            self.tipo_ia = "Dijkstra"
            self.reset_ia()
            self.hablar_guia("Te ayudo con una ruta recomendada.", 5000)
            return

        if intencion == "negar":
            self.hablar_guia("Está bien, intento solo. Cuando quieras, me llamas.", 5500)
            return

        if intencion.startswith("mision_"):
            id_mision = intencion.split("_")[1]
            if id_mision in MISIONES:
                self.id_mision = id_mision
                self.crear_mapa()
                self.hablar_guia(f"Vamos a la misión {id_mision}.", 4500)
                return

        self.hablar_guia("No entendí bien. Puedes decir ayuda, dijkstra, dfs, ucs o misión uno a cinco.", 7000)

    def escuchar_microfono(self):
        if not self.asistente_voz.disponible:
            self.set_mensaje_guia("Voz no disponible. Instala speechrecognition, pyaudio y pyttsx3.", 7000)
            return

        self.hablar_guia("Te escucho. Dime qué necesitas.", 3500)
        resultado = self.asistente_voz.escuchar(timeout=4, phrase_time_limit=7)

        if not resultado["ok"]:
            self.hablar_guia(resultado["mensaje"], 6500)
            return

        texto = resultado["texto"]
        self.set_mensaje_guia(f"Escuché: {texto}", 5000)
        intencion = interpretar_intencion(texto)
        self.aplicar_intencion_voz(intencion)

    def actualizar_guia(self):
        ahora = pygame.time.get_ticks()

        if self.ganado and not self.guia_celebro:
            self.set_mensaje_guia("¡Lo lograste! Excelente trabajo.", 7000)
            self.guia_celebro = True
            return

        if self.tiempo <= 5 and not self.guia_alerta_tiempo and not self.ganado:
            self.set_mensaje_guia("Nos queda poco tiempo. Presiona ESPACIO para ayuda.", 7000)
            self.guia_alerta_tiempo = True

        if not self.ganado and self.tiempo > 0 and ahora - self.ultimo_movimiento_ms > 15000:
            self.set_mensaje_guia("¿Te trabaste? Haz clic en un hexágono vecino para avanzar.", 6500)
            self.ultimo_movimiento_ms = ahora
            self.prox_msg_guia = ahora + self.intervalo_guia_ms
            return

        if not self.ganado and self.tiempo > 0 and ahora >= self.prox_msg_guia:
            self.set_mensaje_guia(random.choice(self.mensajes_guia), 6000)
            self.prox_msg_guia = ahora + self.intervalo_guia_ms

    def partir_texto(self, texto, max_ancho):
        palabras = texto.split()
        lineas = []
        linea_actual = ""

        for palabra in palabras:
            prueba = f"{linea_actual} {palabra}".strip()
            if self.fuente_m.size(prueba)[0] <= max_ancho:
                linea_actual = prueba
            else:
                if linea_actual:
                    lineas.append(linea_actual)
                linea_actual = palabra

        if linea_actual:
            lineas.append(linea_actual)

        return lineas[:3]

    def dibujar_guia(self):
        x_panel = 840
        y_burbuja = 515
        w_burbuja = 240
        h_burbuja = 105

        pygame.draw.rect(self.pantalla, COLOR_CAMINO, (x_panel, y_burbuja, w_burbuja, h_burbuja), border_radius=12)
        pygame.draw.rect(self.pantalla, COLOR_BORDE, (x_panel, y_burbuja, w_burbuja, h_burbuja), 2, border_radius=12)

        lineas = self.partir_texto(self.msg_guia, w_burbuja - 20)
        y_texto = y_burbuja + 12
        for linea in lineas:
            self.pantalla.blit(self.fuente_m.render(linea, True, (40, 40, 40)), (x_panel + 10, y_texto))
            y_texto += 26

        centro = (960, 670)
        pygame.draw.circle(self.pantalla, (230, 230, 230), centro, 42)
        pygame.draw.circle(self.pantalla, COLOR_BORDE, centro, 42, 3)
        pygame.draw.circle(self.pantalla, (50, 50, 50), (946, 660), 4)
        pygame.draw.circle(self.pantalla, (50, 50, 50), (974, 660), 4)
        pygame.draw.arc(self.pantalla, (50, 50, 50), (944, 668, 32, 20), math.radians(15), math.radians(165), 3)

        self.pantalla.blit(self.fuente_m.render("Mascota guía", True, COLOR_TEXTO), (900, 715))

    def dibujar(self):
        self.pantalla.fill((20, 50, 20))
        for coords, h in self.tablero.items():
            centro = hex_a_pixel(coords[0], coords[1], RADIO_HEX)
            
            if h.tipo == "obstaculo":
                rect = self.img_montana.get_rect(center=centro)
                self.pantalla.blit(self.img_montana, rect)
            elif h.tipo == "barro":
                rect = self.img_barro.get_rect(center=centro)
                self.pantalla.blit(self.img_barro, rect)
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
            f"CLIC: Caminar / IA Actual: {self.tipo_ia}",
            "ESPACIO: Mostrar Dijkstra",
            "D: Mostrar DFS",
            "U: Mostrar UCS",
            "TECLAS 1-5: Cambiar Destino",
            "V o clic mascota: Hablar",
            "R: Nuevo Terreno",]
        for linea in instrucciones:
            self.pantalla.blit(self.fuente_m.render(linea, True, (200, 200, 200)), (840, y))
            y += 30
        self.pantalla.blit(self.fuente_l.render(f"Tiempo: {self.tiempo} min", True, (255, 200, 50)), (320, 60))
        if self.ganado:
            msg = self.fuente_l.render("¡MISIÓN CUMPLIDA!", True, (255, 255, 0))
            self.pantalla.blit(msg, (320, 20))
        elif self.tiempo <= 0:
            msg = self.fuente_l.render("¡TIEMPO AGOTADO!", True, (255, 50, 50))
            self.pantalla.blit(msg, (320, 20))

        self.dibujar_guia()

    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); return
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    if self.mascota_rect.collidepoint(ev.pos):
                        self.escuchar_microfono()
                        continue
                    m_hex = pixel_a_hex(ev.pos[0], ev.pos[1], RADIO_HEX)
                    if m_hex in self.tablero: self.mover_granjero(m_hex)
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE: 
                        self.modo_ia = True
                        self.tipo_ia = "Dijkstra"
                        self.reset_ia()
                    if ev.key == pygame.K_d:
                        self.modo_ia = True
                        self.tipo_ia = "DFS"
                        self.reset_ia()
                    if ev.key == pygame.K_u:
                        self.modo_ia = True
                        self.tipo_ia = "UCS"
                        self.reset_ia()
                    if ev.key == pygame.K_v:
                        self.escuchar_microfono()
                    if ev.key == pygame.K_r: self.crear_mapa()
                    if ev.unicode in MISIONES: 
                        self.id_mision = ev.unicode
                        self.crear_mapa()
            if self.modo_ia and not self.ia.ia_completa: 
                self.ia.step()
                pygame.time.delay(20)
            self.actualizar_guia()
            self.dibujar()
            pygame.display.flip()
            self.reloj.tick(FPS)

if __name__ == "__main__":
    GranjaBFS().run()