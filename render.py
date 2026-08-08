import pygame
from pathlib import Path
from config import ANCHO, ALTO, NEGRO, BLANCO, AMARILLO_BATEO

RUTA_ACTUAL = Path(__file__).resolve().parent
RUTA_FONDOS = RUTA_ACTUAL / "assets" / "fondos"
RUTA_FUENTES = RUTA_ACTUAL / "assets" / "fuentes"

def cargar_fondo(nombre_archivo):
    ruta_completa = RUTA_FONDOS / nombre_archivo
    imagen = pygame.image.load(str(ruta_completa)).convert()
    return pygame.transform.scale(imagen, (ANCHO, ALTO))

class Renderizador:
    def __init__(self):
        self.puntos = pygame.image.load(str(RUTA_FONDOS / "puntos.png")).convert_alpha()
        self.gradas = pygame.image.load(str(RUTA_FONDOS / "gradas.png")).convert_alpha()
        self.tiempo = pygame.image.load(str(RUTA_FONDOS / "tiempo.png")).convert_alpha()
        self.guia = cargar_fondo("guia.png")
        self.guia.set_colorkey(BLANCO)

        # Capas de Strikes
        self.strike3 = pygame.image.load(str(RUTA_FONDOS / "1.png")).convert_alpha()
        self.strike2 = pygame.image.load(str(RUTA_FONDOS / "2.png")).convert_alpha()
        self.strike1 = pygame.image.load(str(RUTA_FONDOS / "3.png")).convert_alpha()
        self.sinstrike = pygame.image.load(str(RUTA_FONDOS / "4.png")).convert_alpha()

        self.strike_1 = pygame.image.load(str(RUTA_FONDOS / "strike_1.png")).convert_alpha()
        self.strike_2 = pygame.image.load(str(RUTA_FONDOS / "strike_2.png")).convert_alpha()
        self.strike_3 = pygame.image.load(str(RUTA_FONDOS / "strike_3.png")).convert_alpha()

        # Fuentes
        self.fuente_vol = pygame.font.SysFont("arial", 30, bold=True)
        self.fuente_juego = pygame.font.SysFont("arial", 30, bold=True)
        archivo_fuente = next(RUTA_FUENTES.glob("Golden Age.ttf"), None)
        if archivo_fuente:
            self.fuente_tiro = pygame.font.Font(str(archivo_fuente), 50)
            self.fuente_txt = pygame.font.Font(str(archivo_fuente), 25)
        else:
            self.fuente_tiro = pygame.font.SysFont("arial", 45, bold=True)
            self.fuente_txt = pygame.font.SysFont("arial", 25)

    def dibujar_menu(self, pantalla, menu):
        pantalla.blit(menu.fondo, (0, 0)) 
        pantalla.blit(menu.logo, menu.logo_rect)
        pantalla.blit(menu.img_cuadro, menu.cuadro_rect)
    
        txt_instrucciones = self.fuente_txt.render("Presiona ENTER para continuar", True, NEGRO)
        pantalla.blit(txt_instrucciones, (ANCHO // 2 - txt_instrucciones.get_width() // 2, 530))
        
        porcentaje = int(menu.volumen * 100)
        txt_vol = self.fuente_vol.render(f"Vol: {porcentaje}%", True, BLANCO)
        pantalla.blit(txt_vol, (30, ALTO - 75))
      
        pygame.draw.rect(pantalla, (80, 80, 80), (30, ALTO - 35, 100, 20), border_radius=3)
        if porcentaje > 0:
            pygame.draw.rect(pantalla, AMARILLO_BATEO, (30, ALTO - 35, porcentaje, 20), border_radius=3)

    def dibujar_dificultad(self, pantalla, estado_dificultad):
        pantalla.blit(estado_dificultad.fondo, (0, 0))
        txt_titulo = estado_dificultad.seleccionar.render("SELECCIONA LA DIFICULTAD", True, NEGRO)
        pantalla.blit(txt_titulo, (ANCHO // 2 - txt_titulo.get_width() // 2, 60))

        texto_botones = [
            estado_dificultad.obtener_dificultades("FACIL"),
            estado_dificultad.obtener_dificultades("MEDIO"),
            estado_dificultad.obtener_dificultades("DIFICIL")
        ]

        for i, boton in enumerate(estado_dificultad.lista_botones):
            es_activa = (i == estado_dificultad.indice_seleccionado)
            boton.dibujar(pantalla, borde_activo=es_activa, lineas_texto=texto_botones[i])

        estado_dificultad.sprites_menu.draw(pantalla)

    def dibujar_juego(self, pantalla, juego):
        # 1. Fondo de césped
        pantalla.blit(juego.fondo, (0, 0))
        
        # 2. Capa inferior de strikes
        if juego.vidas == 2:
            pantalla.blit(self.strike_1, (0, 0))
        elif juego.vidas == 1:
            pantalla.blit(self.strike_2, (0, 0))
        elif juego.vidas <= 0:
            pantalla.blit(self.strike_3, (0, 0))

        # 3. Gradas
        pantalla.blit(self.gradas, (0, 0))

        AZUL = (50, 130, 230)
        AMARILLO = (230, 215, 50)
        GROSOR = 4
        
        puntos_azul = [(ANCHO//2 - 160, ALTO), (ANCHO//2 - 160, 200), (ANCHO//2 + 160, 200), (ANCHO//2 + 160, ALTO)]
        puntos_amarilla = [(ANCHO//2 - 300, ALTO), (ANCHO//2 - 300, 70), (ANCHO//2 + 300, 70), (ANCHO//2 + 300, ALTO)]

        pygame.draw.lines(pantalla, AZUL, False, puntos_azul, GROSOR)
        pygame.draw.lines(pantalla, AMARILLO, False, puntos_amarilla, GROSOR)

        #4. Sprites del juego
        juego.sprites.draw(pantalla)
        if juego.bola.activa:
            pantalla.blit(juego.bola.image, juego.bola.rect)
        pantalla.blit(juego.bateador.image, juego.bateador.rect)
        pygame.draw.rect(pantalla, (255, 0, 0), juego.bateador.hitbox, 2)

        # 5. Capa superior de strikes y HUD
        pantalla.blit(self.guia, (0, 0))
        if juego.vidas == 3:
            pantalla.blit(self.sinstrike, (20, 140))
        elif juego.vidas == 2:
            pantalla.blit(self.strike1, (20, 140))
        elif juego.vidas == 1:
            pantalla.blit(self.strike2, (20, 140))
        else:
            pantalla.blit(self.strike3, (20, 140))

        pantalla.blit(self.puntos, (20, 40))
        pantalla.blit(self.tiempo, (ANCHO - 180 - 20, 60))

        txt_puntos = self.fuente_juego.render(f"{juego.puntuacion}/{juego.puntos_meta}", True, BLANCO)
        pantalla.blit(txt_puntos, (80, 80))
        
        str_tiempo = f"{juego.tiempo_restante}s" if juego.tiempo_restante is not None else "∞"
        txt_tiempo = self.fuente_juego.render(str_tiempo, True, BLANCO)
        pantalla.blit(txt_tiempo, (ANCHO - 130, 100))
        
        if juego.ultimo_tiro_texto:
            txt_aviso = self.fuente_tiro.render(juego.ultimo_tiro_texto, True, juego.color_texto_tiro)
            pantalla.blit(txt_aviso, (ANCHO//2 - txt_aviso.get_width()//2, ALTO//2 + 50))

    def dibujar_resultado(self, pantalla, resultado):
        if resultado.fondo:
            pantalla.blit(resultado.fondo, (0, 0))