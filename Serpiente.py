import turtle
import time
import random
import os

# Constantes del juego
DELAY = 0.1
ANCHO_PANTALLA = 600
ALTO_PANTALLA = 600
NIVELES = 5
PUNTOS_POR_NIVEL = 100
NUM_COMIDAS = 3

# Colores de los diferentes tipos de comida
COLOR_VENENOSA = "purple"
COLOR_FIT = "green"
COLOR_GRASAS = "yellow"
COLOR_REYES = "orange"

# Archivo para guardar el récord
ARCHIVO_RECORD = "record.txt"

# Abstract Factory
class FabricaComida:
    def crear_comida(self):
        raise NotImplementedError

class FabricaVenenosa(FabricaComida):
    def crear_comida(self):
        return ComidaVenenosa()

class FabricaFit(FabricaComida):
    def crear_comida(self):
        return ComidaFit()

class FabricaGrasas(FabricaComida):
    def crear_comida(self):
        return ComidaGrasas()

class FabricaReyes(FabricaComida):
    def crear_comida(self):
        return ComidaReyes()

# Clase base Comida
class Comida:
    def __init__(self):
        self.segmento = turtle.Turtle()
        self.segmento.speed(0)
        self.segmento.shape("circle")
        self.segmento.penup()
        self.x = 0
        self.y = 0
        self.color = "black"
        self.mover()
    
    def mover(self):
        x = random.randint(-(ANCHO_PANTALLA//2 - 20), (ANCHO_PANTALLA//2 - 20))
        y = random.randint(-(ALTO_PANTALLA//2 - 20), (ALTO_PANTALLA//2 - 20))
        self.segmento.goto(x, y)
        self.x = x
        self.y = y
    
    def aplicar_efecto(self, snake):
        raise NotImplementedError

class ComidaVenenosa(Comida):
    def __init__(self):
        super().__init__()
        self.segmento.color(COLOR_VENENOSA)
        self.color = COLOR_VENENOSA

    def aplicar_efecto(self, snake):
        if len(snake.segmentos) > 1:
            eliminado = snake.segmentos.pop()
            eliminado.goto(1000, 1000)
            eliminado.hideturtle()
        snake.puntaje = max(0, snake.puntaje - 1)
        snake.actualizar_puntaje()

class ComidaFit(Comida):
    def __init__(self):
        super().__init__()
        self.segmento.color(COLOR_FIT)
        self.color = COLOR_FIT

    def aplicar_efecto(self, snake):
        snake.puntaje += 1
        snake.actualizar_puntaje()
        snake.agregar_segmento()

class ComidaGrasas(Comida):
    def __init__(self):
        super().__init__()
        self.segmento.color(COLOR_GRASAS)
        self.color = COLOR_GRASAS

    def aplicar_efecto(self, snake):
        snake.puntaje += 3
        snake.actualizar_puntaje()
        for _ in range(3):
            snake.agregar_segmento()
        snake.delay_temporal = snake.delay * 2
        snake.tiempo_efecto = time.time() + 5

class ComidaReyes(Comida):
    def __init__(self):
        super().__init__()
        self.segmento.color(COLOR_REYES)
        self.color = COLOR_REYES

    def aplicar_efecto(self, snake):
        snake.puntaje += 5
        snake.actualizar_puntaje()
        for _ in range(5):
            snake.agregar_segmento()
        snake.delay_temporal = max(0.02, snake.delay * 0.5)
        snake.tiempo_efecto = time.time() + 5

# Clase Snake (juego principal)
class Snake:
    def __init__(self):
        self.ventana = turtle.Screen()
        self.ventana.title("Snake Game con Abstract Factory")
        self.ventana.bgcolor("lightblue")
        self.ventana.setup(width=ANCHO_PANTALLA, height=ALTO_PANTALLA)
        self.ventana.tracer(0)

        self.puntaje = 0
        self.nivel = 1
        self.delay = DELAY
        self.delay_temporal = DELAY
        self.tiempo_efecto = 0
        self.record = self.cargar_record()

        self.marcador = turtle.Turtle()
        self.marcador.speed(0)
        self.marcador.color("black")
        self.marcador.penup()
        self.marcador.hideturtle()
        self.marcador.goto(0, ALTO_PANTALLA/2 - 40)

        self.segmentos = []
        self.cabeza = turtle.Turtle()
        self.cabeza.speed(0)
        self.cabeza.shape("square")
        self.cabeza.color("black")
        self.cabeza.penup()
        self.cabeza.goto(0, 0)
        self.cabeza.direccion = "stop"
        self.segmentos.append(self.cabeza)

        self.comidas = []

        self.fabricas_comida = [
            FabricaVenenosa(),
            FabricaFit(),
            FabricaGrasas(),
            FabricaReyes()
        ]

        self.mostrar_menu_inicio()
        self.generar_comidas()
        self.actualizar_puntaje()

        self.ventana.listen()
        self.ventana.onkeypress(self.ir_arriba, "Up")
        self.ventana.onkeypress(self.ir_abajo, "Down")
        self.ventana.onkeypress(self.ir_izquierda, "Left")
        self.ventana.onkeypress(self.ir_derecha, "Right")
        self.ventana.onkeypress(self.reiniciar, "space")
    
    def mostrar_menu_inicio(self):
        menu = turtle.Turtle()
        menu.hideturtle()
        menu.penup()
        menu.goto(0, 0)
        menu.write("Bienvenido al Snake Game\n\nUsa las flechas para moverte.\nPresiona 'Espacio' para comenzar.", align="center", font=("Courier", 16, "normal"))
        self.ventana.update()
        # Esperar hasta que el usuario presione espacio para continuar
        self.ventana.onkeypress(lambda: menu.clear(), "space")
        self.ventana.listen()
        # Pausa aquí esperando la tecla espacio para limpiar menú y seguir
        while menu.isvisible():
            self.ventana.update()
            time.sleep(0.1)

    def cargar_record(self):
        if os.path.exists(ARCHIVO_RECORD):
            with open(ARCHIVO_RECORD, "r") as f:
                try:
                    return int(f.read())
                except:
                    return 0
        return 0

    def guardar_record(self):
        with open(ARCHIVO_RECORD, "w") as f:
            f.write(str(self.record))

    def generar_comidas(self):
        # Crear NUM_COMIDAS alimentos simultáneos
        for _ in range(NUM_COMIDAS):
            fabrica = random.choice(self.fabricas_comida)
            comida = fabrica.crear_comida()
            self.comidas.append(comida)

    def actualizar_puntaje(self):
        texto = f"Puntaje: {self.puntaje}  Nivel: {self.nivel}  Récord: {self.record}\n"
        texto += "Comidas disponibles: Verde (+1), Amarillo (+3), Naranja (+5), Morado (-1)"
        self.marcador.clear()
        self.marcador.write(texto, align="center", font=("Courier", 18, "normal"))

    def ir_arriba(self):
        if self.cabeza.direccion != "down":
            self.cabeza.direccion = "up"

    def ir_abajo(self):
        if self.cabeza.direccion != "up":
            self.cabeza.direccion = "down"

    def ir_izquierda(self):
        if self.cabeza.direccion != "right":
            self.cabeza.direccion = "left"

    def ir_derecha(self):
        if self.cabeza.direccion != "left":
            self.cabeza.direccion = "right"

    def agregar_segmento(self):
        nuevo = turtle.Turtle()
        nuevo.speed(0)
        nuevo.shape("square")
        nuevo.color("grey")
        nuevo.penup()
        self.segmentos.append(nuevo)

    def mover(self):
        if time.time() > self.tiempo_efecto:
            self.delay_temporal = self.delay

        for i in range(len(self.segmentos) - 1, 0, -1):
            x = self.segmentos[i - 1].xcor()
            y = self.segmentos[i - 1].ycor()
            self.segmentos[i].goto(x, y)

        if self.cabeza.direccion == "up":
            self.cabeza.sety(self.cabeza.ycor() + 20)
        elif self.cabeza.direccion == "down":
            self.cabeza.sety(self.cabeza.ycor() - 20)
        elif self.cabeza.direccion == "left":
            self.cabeza.setx(self.cabeza.xcor() - 20)
        elif self.cabeza.direccion == "right":
            self.cabeza.setx(self.cabeza.xcor() + 20)

    def verificar_colision_comida(self):
        for comida in self.comidas:
            if self.cabeza.distance(comida.segmento) < 20:
                comida.aplicar_efecto(self)
                comida.segmento.goto(1000, 1000)
                comida.segmento.hideturtle()
                self.comidas.remove(comida)
                # Generar una nueva comida
                fabrica = random.choice(self.fabricas_comida)
                nueva_comida = fabrica.crear_comida()
                self.comidas.append(nueva_comida)
                # Verificar si se pasa nivel
                if self.puntaje >= self.nivel * PUNTOS_POR_NIVEL and self.nivel < NIVELES:
                    self.nivel += 1
                    self.delay *= 0.8  # Aumenta la velocidad
                    self.delay_temporal = self.delay
                return True
        return False

    def verificar_colision_bordes(self):
        return (self.cabeza.xcor() > ANCHO_PANTALLA/2 - 20 or 
                self.cabeza.xcor() < -(ANCHO_PANTALLA/2 - 20) or 
                self.cabeza.ycor() > ALTO_PANTALLA/2 - 20 or 
                self.cabeza.ycor() < -(ALTO_PANTALLA/2 - 20))

    def verificar_colision_cuerpo(self):
        for segmento in self.segmentos[1:]:
            if self.cabeza.distance(segmento) < 20:
                return True
        return False

    def reiniciar(self):
        self.cabeza.goto(0, 0)
        self.cabeza.direccion = "stop"

        # Ocultar segmentos
        for segmento in self.segmentos[1:]:
            segmento.goto(1000, 1000)
            segmento.hideturtle()

        self.segmentos = [self.cabeza]
        self.puntaje = 0
        self.nivel = 1
        self.delay = DELAY
        self.delay_temporal = DELAY
        self.tiempo_efecto = 0

        # Limpiar comidas y generar nuevas
        for comida in self.comidas:
            comida.segmento.goto(1000, 1000)
            comida.segmento.hideturtle()
        self.comidas.clear()
        self.generar_comidas()

        self.actualizar_puntaje()

    def juego(self):
        while True:
            self.ventana.update()
            if self.cabeza.direccion != "stop":
                self.mover()
                if self.verificar_colision_bordes() or self.verificar_colision_cuerpo():
                    if self.puntaje > self.record:
                        self.record = self.puntaje
                        self.guardar_record()
                    self.reiniciar()
                self.verificar_colision_comida()
            time.sleep(self.delay_temporal)

if __name__ == "__main__":
    juego = Snake()
    juego.juego()
