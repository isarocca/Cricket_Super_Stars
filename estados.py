import pygame
from pathlib import Path
from config import ANCHO, ALTO, NEGRO, BLANCO, AMARILLO_BATEO, ROJO_BOLA, VERDE_PASTO , DIFICULTADES
from entidades import Bateador, Bola, Lanzador
from render import Renderizador, cargar_fondo

RUTA_ACTUAL = Path(__file__).resolve().parent
RUTA_FONDOS = RUTA_ACTUAL / "assets" / "fondos"
RUTA_SONIDOS = RUTA_ACTUAL / "assets" / "sonidos"
RUTA_FUENTES = RUTA_ACTUAL / "assets" / "fuentes"

class Boton:
    def __init__(self, x, y, ancho, alto, texto, nombre_imagen, color_texto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_texto = color_texto
        ruta_img = RUTA_FONDOS / nombre_imagen
        imagen_original = pygame.image.load(str(ruta_img)).convert_alpha()
        self.imagen = pygame.transform.scale(imagen_original, (ancho, alto))
        
        archivo_fuente = next(RUTA_FUENTES.glob("Nowster Cute.otf"), None)
        self.fuente_datos = pygame.font.SysFont("arial black", 35, bold=True)

    def chequear_clic(self, pos_raton):
        return self.rect.collidepoint(pos_raton)

    def dibujar(self, pantalla, borde_activo=False, lineas_texto=None):  
        pantalla.blit(self.imagen, self.rect.topleft)

        if borde_activo:
            rect_borde = self.rect.inflate(12, 12)
            pygame.draw.rect(pantalla, (255, 255, 255), rect_borde, width=4, border_radius=12)
            
        if lineas_texto:
            y_offset = self.rect.centery - 45
            for linea in lineas_texto:
                txt_surface = self.fuente_datos.render(linea, True, BLANCO)
                txt_rect = txt_surface.get_rect(centerx=self.rect.centerx+40, top=y_offset)
                pantalla.blit(txt_surface, txt_rect)
                y_offset += 35


class PantallaMenu:
    def __init__(self):
        self.fondo = cargar_fondo("inicio.png")
        self.volumen = 0.5
        
        pygame.mixer.music.load(str(RUTA_SONIDOS / "menu.mp3"))
        pygame.mixer.music.play(-1) 
        pygame.mixer.music.set_volume(self.volumen)
        self.snd_seleccion = pygame.mixer.Sound(str(RUTA_SONIDOS / "click.mp3"))
        self.snd_seleccion.set_volume(self.volumen)


        
        imagen_logo = pygame.image.load(str(RUTA_FONDOS / "logo.png")).convert_alpha()
        self.logo = pygame.transform.scale(imagen_logo, (500, 400))
            
        self.logo_rect = self.logo.get_rect(centerx=ANCHO // 2, top=55)
        
        imagen_cuadro = pygame.image.load(str(RUTA_FONDOS / "cuadro.png")).convert_alpha()    
        self.img_cuadro = pygame.transform.scale(imagen_cuadro, (550, 120)) 
        self.cuadro_rect = self.img_cuadro.get_rect(centerx=ANCHO // 2, centery=550)

    def manejar_eventos(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN: 
                if event.key == pygame.K_RETURN:
                    if self.snd_seleccion:
                        self.snd_seleccion.play()
                    return "DIFICULTAD"
        
                elif event.key == pygame.K_UP:
                    self.volumen = min(1.0, self.volumen + 0.1)
                    pygame.mixer.music.set_volume(self.volumen)
                    if self.snd_seleccion:
                        self.snd_seleccion.set_volume(self.volumen)
                        
                elif event.key == pygame.K_DOWN:
                    self.volumen = max(0.0, self.volumen - 0.1)
                    pygame.mixer.music.set_volume(self.volumen)
                    if self.snd_seleccion:
                        self.snd_seleccion.set_volume(self.volumen)
        return "BIENVENIDA"

    def dibujar(self, pantalla,renderizador):
        renderizador.dibujar_menu(pantalla, self)


class PantallaDificultad:
    def __init__(self):
        self.fondo = cargar_fondo("menu.png")
        self.fuente_titulo = pygame.font.SysFont("arial", 40, bold=True)
        
        ancho_carta = 630
        alto_carta = 120
        x_pos = 60
        y_facil = 200
        y_medio = y_facil + alto_carta + 25
        y_dificil = y_medio + alto_carta + 25
        
        self.btn_facil = Boton(x_pos, y_facil, ancho_carta, alto_carta, "FÁCIL", "facil.png", BLANCO)
        self.btn_medio = Boton(x_pos, y_medio, ancho_carta, alto_carta, "MEDIO", "medio.png", BLANCO)
        self.btn_dificil = Boton(x_pos, y_dificil, ancho_carta, alto_carta, "DIFÍCIL", "dificil.png", BLANCO)
        self.lista_botones = [self.btn_facil, self.btn_medio, self.btn_dificil]
        self.indice_seleccionado = 0
        
        self.bateador = Bateador()
        self.bateador.en_menu = True
        self.bateador.image = pygame.transform.scale(self.bateador.frames_idle[0], (720, 840))
        self.bateador.rect = self.bateador.image.get_rect()
        self.bateador.rect.bottomright = (ANCHO+80, ALTO+120)
        
        self.sprites_menu = pygame.sprite.Group(self.bateador)
        
        try:
            self.snd_seleccion = pygame.mixer.Sound(str(RUTA_SONIDOS / "click.mp3"))
            self.snd_preseleccion = pygame.mixer.Sound(str(RUTA_SONIDOS / "preseleccion.mp3"))
            self.snd_preseleccion.set_volume(0.7)
        except pygame.error:
            self.snd_seleccion = None
            self.snd_preseleccion = None

        archivo_fuente = next(RUTA_FUENTES.glob("Golden Age.ttf"), None)
        if archivo_fuente:
            self.seleccionar = pygame.font.Font(str(archivo_fuente), 50)
        else:
            self.seleccionar = pygame.font.SysFont("arial", 45, bold=True)
        
    def obtener_dificultades(self, clave_diccionario):
        datos = DIFICULTADES[clave_diccionario]
        tiempo_txt = datos.get('tiempo') if datos.get('tiempo') is not None else '∞'
        return [
            f"{datos.get('dificultad')}",
            f"Puntos: {datos.get('puntos_meta', 3)}  Tiempo: {tiempo_txt}"           
        ]
    
    def manejar_eventos(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.indice_seleccionado = (self.indice_seleccionado + 1) % 3
                    if getattr(self, 'snd_preseleccion', None):
                        self.snd_preseleccion.play()
                elif event.key == pygame.K_UP:
                    self.indice_seleccionado = (self.indice_seleccionado - 1) % 3
                    if getattr(self, 'snd_preseleccion', None):
                        self.snd_preseleccion.play()
                elif event.key == pygame.K_RETURN:
                    if self.snd_seleccion:
                        self.snd_seleccion.play()
                    pygame.mixer.music.stop()
                    dificultades_mapeo = {0: "FACIL", 1: "MEDIO", 2: "DIFICIL"}
                    return "JUEGO", dificultades_mapeo[self.indice_seleccionado]  
                                          
        self.sprites_menu.update()
        return "DIFICULTAD", None

    def dibujar(self, pantalla,renderizador):
        renderizador.dibujar_dificultad(pantalla, self)


class PantallaJuego:
    def __init__(self, dificultad):
        self.config_nivel = DIFICULTADES[dificultad]
        self.lanzador = Lanzador()
        self.bateador = Bateador()
        self.bola = Bola()
        
        self.bola.configurar_dificultad(self.config_nivel["vel_pelota"], self.config_nivel["efecto"])
        self.bola.activa = False
        self.sprites = pygame.sprite.Group(self.lanzador, self.bateador, self.bola)
        self.puntuacion = 0
        self.puntos_meta = self.config_nivel["puntos_meta"]
        self.vidas = 3
        
        self.home_x = ANCHO // 2
        self.home_y = ALTO - 50
        self.esperando_lanzamiento = True
        self.frames_espera = 60
        self.ultimo_tiro_texto = ""
        self.color_texto_tiro = BLANCO
        self.fondo = cargar_fondo("juego.png")
        self.tiempo_restante = self.config_nivel["tiempo"]
        
        if self.tiempo_restante is not None:
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)

        self.snd_strike = pygame.mixer.Sound(str(RUTA_SONIDOS / "strike.mp3"))
        self.snd_strike.set_volume(0.6)
        self.snd_swing = pygame.mixer.Sound(str(RUTA_SONIDOS / "swing.mp3"))
        self.snd_swing.set_volume(0.6)
        self.snd_hit = pygame.mixer.Sound(str(RUTA_SONIDOS / "hit.mp3"))
        self.snd_hit.set_volume(0.6)

        self.snd_lanzamiento = pygame.mixer.Sound(str(RUTA_SONIDOS / "bola.mp3"))
        self.snd_publico = pygame.mixer.Sound(str(RUTA_SONIDOS / "publico.wav"))
        self.snd_lanzamiento.set_volume(0.6)
        
        self.esperando_fin_juego = False
        self.frames_espera_fin = 30

    def finalizar_temporizador(self):
        if self.tiempo_restante is not None:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)

    def manejar_eventos(self, eventos):
        for event in eventos:
            if event.type == pygame.USEREVENT + 1 and self.tiempo_restante is not None:
                if not self.esperando_lanzamiento: 
                    self.tiempo_restante -= 1

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.bola.activa and not self.bola.bateada:
                    self.bateador.batear()
                    self.snd_swing.play()
                    if self.bateador.hitbox.colliderect(self.bola.rect):
                        self.bola.recubrir_batazo(self.bateador.hitbox.centerx)
                        self.snd_hit.play()

    def actualizar(self):
        if self.esperando_fin_juego:
            self.frames_espera_fin -= 1
            if self.frames_espera_fin <= 0:
                self.finalizar_temporizador()
                return "RESULTADO", "PERDISTE"
            return "JUEGO", None

        self.bateador.update()
        evento_lanzador = self.lanzador.update()
        if evento_lanzador == "SOLTAR_PELOTA":
            self.bola.lanzar_nueva_bola()
        
        if self.esperando_lanzamiento:
            self.frames_espera -= 1
            if self.frames_espera <= 0:
                self.esperando_lanzamiento = False
                self.ultimo_tiro_texto = ""
                if self.snd_lanzamiento:
                    self.snd_lanzamiento.play()
                self.lanzador.iniciar_lanzamiento() 
            return "JUEGO", None 
            
        resultado_bola = self.bola.update()
        
        if resultado_bola == "FALLO":
            self.vidas -= 1
            if self.vidas > 0:
                if self.snd_strike:
                    self.snd_strike.play()
                self.ultimo_tiro_texto = "STRIKE!"
                self.color_texto_tiro = ROJO_BOLA
                self.activar_espera(90)
            else:
                if self.snd_strike:
                    self.snd_strike.play()
                self.ultimo_tiro_texto = "TERCER STRIKE, OUT!"
                self.color_texto_tiro = ROJO_BOLA
                self.esperando_fin_juego = True  

        elif resultado_bola == "ATERRIZO":
            bx = self.bola.rect.centerx
            by = self.bola.rect.centery
    
            x_izq_azul = ANCHO // 2 - 160
            x_der_azul = ANCHO // 2 + 160
            y_superior_azul = 200
            
            x_izq_amarilla = ANCHO // 2 - 300
            x_der_amarilla = ANCHO // 2 + 300
            y_superior_amarilla = 70

            if (x_izq_azul <= bx <= x_der_azul) and (by >= y_superior_azul):
                self.puntuacion += 2
                self.ultimo_tiro_texto = "Hit Corto! +2 Puntos"
                self.color_texto_tiro = VERDE_PASTO
                
            elif (x_izq_amarilla <= bx <= x_der_amarilla) and (by >= y_superior_amarilla):
                self.puntuacion += 5
                self.ultimo_tiro_texto = "Batazo Profundo! +5 Puntos"
                self.color_texto_tiro = VERDE_PASTO
           
            else:
                self.puntuacion += 10
                self.ultimo_tiro_texto = "HOME RUN! +10 Puntos"
                if self.snd_publico:
                    self.snd_publico.play()
                self.color_texto_tiro = AMARILLO_BATEO
                
            self.activar_espera(120)
       
        if self.puntuacion >= self.puntos_meta:
            self.finalizar_temporizador()
            return "RESULTADO", "GANASTE"
    
        if self.tiempo_restante is not None and self.tiempo_restante <= 0:
            self.finalizar_temporizador()
            return "RESULTADO", "PERDISTE"

        return "JUEGO", None
    
    def activar_espera(self, num_frames):
        self.esperando_lanzamiento = True
        self.frames_espera = num_frames

    def dibujar(self, pantalla,renderizador):
        renderizador.dibujar_juego(pantalla, self)

class PantallaResultado:
    def __init__(self, resultado):
        self.resultado = resultado
        self.fondo = cargar_fondo("victoria.jpg" if self.resultado == "GANASTE" else "derrota.jpg")
        
        self.snd_victoria = pygame.mixer.Sound(str(RUTA_SONIDOS / "victoria.mp3"))
        self.snd_derrota = pygame.mixer.Sound(str(RUTA_SONIDOS / "derrota.mp3"))
            
        if self.resultado == "GANASTE":
            self.snd_victoria.play()
        else:
            self.snd_derrota.play()

    def manejar_eventos(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return "BIENVENIDA"
        return "RESULTADO"

    def dibujar(self, pantalla,renderizador):
        renderizador.dibujar_resultado(pantalla, self)