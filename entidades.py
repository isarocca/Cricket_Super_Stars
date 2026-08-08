import pygame
import random
import math
import os
from config import *

class Bateador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames_idle = [
            self.cargar_imagen("assets/entidades/idle1.png", AZUL_BATEADOR),
            self.cargar_imagen("assets/entidades/idle2.png", AZUL_BATEADOR),
            self.cargar_imagen("assets/entidades/idle3.png", AZUL_BATEADOR)
        ]
        
        self.frames_swing = [
            self.cargar_imagen("assets/entidades/jugador2.png", AMARILLO_BATEO),
            self.cargar_imagen("assets/entidades/jugador3.png", AMARILLO_BATEO),
            self.cargar_imagen("assets/entidades/jugador4.png", AMARILLO_BATEO)
        ]
        
        self.estado = "QUIETO"
        self.frame_actual = 0
        
        self.image = self.frames_idle[self.frame_actual]
        self.rect = self.image.get_rect()

        self.hitbox = pygame.Rect(0, 0, 25, 15)
        self.rect.centerx = (ANCHO // 2) - 50
        self.rect.bottom = ALTO - 30
        self.velocidad = 5
        
        self.ultimo_update = pygame.time.get_ticks()
        self.vel_anim_idle = 200   
        self.vel_anim_swing = 80   
        self.en_menu = False

    def cargar_imagen(self, ruta, color_respaldo):
        try:
            img = pygame.image.load(ruta).convert_alpha()
        except pygame.error:
            img = pygame.Surface((120, 120), pygame.SRCALPHA)
            img.fill(color_respaldo)
        return pygame.transform.scale(img, (120, 120))

    def batear(self):
        if self.estado != "BATEANDO":
            self.estado = "BATEANDO"
            self.frame_actual = 0
            self.ultimo_update = pygame.time.get_ticks()

    def update(self):
        if not self.en_menu:
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= self.velocidad
            if teclas[pygame.K_RIGHT] and self.rect.right < ANCHO:
                self.rect.x += self.velocidad

        tiempo_actual = pygame.time.get_ticks()
       
        if self.en_menu or self.estado == "QUIETO":
            lista_frames_activa = self.frames_idle
            velocidad_activa = self.vel_anim_idle
            estado_actual = "QUIETO"
        else:
            lista_frames_activa = self.frames_swing
            velocidad_activa = self.vel_anim_swing
            estado_actual = self.estado

        if tiempo_actual - self.ultimo_update >= velocidad_activa:
            self.ultimo_update = tiempo_actual
            self.frame_actual += 1
            
            if estado_actual == "QUIETO":
                if self.frame_actual >= len(lista_frames_activa):
                    self.frame_actual = 0
                    
            elif estado_actual == "BATEANDO":
                if self.frame_actual >= len(lista_frames_activa):
                    self.estado = "QUIETO"
                    self.frame_actual = 0
                    lista_frames_activa = self.frames_idle 
            
            imagen_nueva = lista_frames_activa[self.frame_actual]

            if self.en_menu:
                # Mantener la escala deseada (720x840) de manera constante en cada tick
                self.image = pygame.transform.scale(imagen_nueva, (720, 840))
                self.rect = self.image.get_rect()
                self.rect.bottomright = (ANCHO+80, ALTO+120)
            else:
                centro_anterior = self.rect.center
                self.image = imagen_nueva
                self.rect = self.image.get_rect()
                self.rect.center = centro_anterior
            
        if not self.en_menu:
            self.hitbox.size = (35, 40)
            self.hitbox.center = self.rect.center
            self.hitbox.y += 15
            self.hitbox.x += 10

class Bola(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image_original = pygame.image.load("assets/entidades/pelota.png").convert_alpha()
        except pygame.error:
            self.image_original = pygame.Surface((40, 40))
            self.image_original.fill((220, 20, 60))
        self.image = pygame.transform.scale(self.image_original, (40, 40))
        self.rect = self.image.get_rect()
        self.vel_base = 6
        self.con_efecto = False
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.bateada = False
        self.activa = False 
        
        self.x_lineal = 0.0          
        self.angulo_efecto = 0.0
        self.amplitud_efecto = 0

    def configurar_dificultad(self, vel_base, con_efecto):
        self.vel_base = vel_base
        self.con_efecto = con_efecto
        self.lanzar_nueva_bola()

    def lanzar_nueva_bola(self):
        self.rect.centerx = ANCHO // 2
        self.rect.centery = ALTO // 2 - 50
    
        self.x_lineal = float(self.rect.centerx)
        self.velocidad_y = self.vel_base + random.uniform(-1.5, 2.5)
        
        objetivo_x = random.randint(ANCHO // 2 - 25, ANCHO // 2 + 25)
        distancia_y_al_home = (ALTO - 100) - self.rect.centery
        tiempo_estimado = distancia_y_al_home / self.velocidad_y
        self.velocidad_x = (objetivo_x - self.rect.centerx) / tiempo_estimado
        
        if self.con_efecto:
            self.angulo_efecto = 0.0  
            self.amplitud_efecto = random.choice([35, -35, 45, -45]) 
        else:
            self.amplitud_efecto = 0
            
        self.bateada = False
        self.activa = True

    def recubrir_batazo(self, posicion_bateador_x):
        self.bateada = True
        diferencia_x = self.rect.centerx - posicion_bateador_x
        self.velocidad_y = -self.vel_base * 1.8
        self.velocidad_x = diferencia_x * 0.25

    def update(self):
        if not self.activa:
            return None
        
        self.rect.y += self.velocidad_y
        
        if not self.bateada:
            self.x_lineal += self.velocidad_x
            
            if self.con_efecto:
                self.angulo_efecto += 0.08  
                desvio = math.sin(self.angulo_efecto) * self.amplitud_efecto
                self.rect.centerx = int(self.x_lineal + desvio)
            else:
                self.rect.centerx = int(self.x_lineal)
        else:
            self.rect.x += self.velocidad_x
  
        if self.bateada:
            if self.rect.centery < 100 or self.rect.left < 0 or self.rect.right > ANCHO:
                self.activa = False
                return "ATERRIZO"
        else:
            if self.rect.top > ALTO:
                self.activa = False
                return "FALLO"  
        return None

class Lanzador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = []
    
        nombres_archivos = [
            "Imagen1.png", "Imagen2.png", "Imagen3.png", "Imagen4.png",
            "Imagen5.png", "Imagen6.png", "Imagen7.png", "Imagen8.png"
        ]
        
        ruta_raiz = os.path.dirname(os.path.abspath(__file__))
        for nombre in nombres_archivos:
            ruta_completa = os.path.join(ruta_raiz, "assets", "entidades", nombre)
            if not os.path.exists(ruta_completa):
                ruta_completa = os.path.join(ruta_raiz, "assets", "entidades", nombre.replace(".png", ".PNG"))
            
            try:
                img = pygame.image.load(ruta_completa).convert_alpha()
            except pygame.error:
                img = pygame.Surface((90, 90), pygame.SRCALPHA)
                img.fill((0, 255, 0))
            img_escalada = pygame.transform.scale(img, (90, 90)) 
            self.frames.append(img_escalada)
            
        self.frame_actual = 0
        self.image = self.frames[self.frame_actual]
        self.rect = self.image.get_rect()
        self.rect.centerx = ANCHO // 2
        self.rect.centery = ALTO // 2 - 50
        self.animando = False
        self.velocidad_animacion = 0.20 
        self.pelota_lanzada = False

    def iniciar_lanzamiento(self):
        self.frame_actual = 0
        self.animando = True
        self.pelota_lanzada = False

    def update(self):
        evento = None
        if self.animando:
            self.frame_actual += self.velocidad_animacion
            if self.frame_actual >= len(self.frames):
                self.frame_actual = 0
                self.animando = False 
            if int(self.frame_actual) == 6 and not self.pelota_lanzada:
                self.pelota_lanzada = True
                evento = "SOLTAR_PELOTA"
        self.image = self.frames[int(self.frame_actual)]
        return evento