import pygame
import sys
from config import *
from render import Renderizador  # Importamos la clase Renderizador
from estados import *

class JUEGO:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("Juego de Cricket Profesional")
        self.reloj = pygame.time.Clock()
        
        # INSTANCIAMOS EL RENDERIZADOR AQUÍ (Ya existe self.pantalla)
        self.renderizador = Renderizador()
    
        self.estado_actual = "BIENVENIDA"
        self.pantalla_activa = PantallaMenu()
        
        self.dificultad_elegida = None
        self.resultado_final = None
        self.jugando = True

    def ejecutar(self):
        while self.jugando:
            eventos = pygame.event.get()
            for evento in eventos:
                if evento.type == pygame.QUIT:
                    self.jugando = False
                    
            if self.estado_actual == "BIENVENIDA":
                siguiente_estado = self.pantalla_activa.manejar_eventos(eventos)
                if siguiente_estado == "DIFICULTAD":
                    self.estado_actual = "DIFICULTAD"
                    self.pantalla_activa = PantallaDificultad()

            elif self.estado_actual == "DIFICULTAD":
                retorno = self.pantalla_activa.manejar_eventos(eventos)
                if retorno and isinstance(retorno, tuple):
                    siguiente_estado, dif = retorno
                    if siguiente_estado == "JUEGO":
                        self.dificultad_elegida = dif
                        self.estado_actual = "JUEGO"
                        self.pantalla_activa = PantallaJuego(self.dificultad_elegida)

            elif self.estado_actual == "JUEGO":
                self.pantalla_activa.manejar_eventos(eventos)
                
                retorno_juego = self.pantalla_activa.actualizar()
                
                if retorno_juego is not None:
                    siguiente_estado, res = retorno_juego
                    if siguiente_estado == "RESULTADO":
                        self.resultado_final = res
                        self.estado_actual = "RESULTADO"
                        self.pantalla_activa = PantallaResultado(self.resultado_final)

            elif self.estado_actual == "RESULTADO":
                siguiente_estado = self.pantalla_activa.manejar_eventos(eventos)
                if siguiente_estado == "BIENVENIDA":
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)
                    self.estado_actual = "BIENVENIDA"
                    self.pantalla_activa = PantallaMenu()

            # PASAMOS self.renderizador COMO SEGUNDO ARGUMENTO:
            self.pantalla_activa.dibujar(self.pantalla, self.renderizador)
            pygame.display.flip()
            self.reloj.tick(FPS)

        pygame.quit()
        sys.exit()