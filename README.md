
## Descripción

Este proyecto detecta si una persona está parada o sentada usando la cámara web y la librería MediaPipe en Python.

Dependiendo de la postura detectada:

- Si está parado → se enciende un LED rojo.
- Si está sentado → se enciende un LED verde.

La comunicación se realiza entre Python y un Arduino UNO mediante el puerto serial.

---

## ¿Cómo funciona?

1. Se activa la cámara con OpenCV.
2. MediaPipe detecta los puntos del cuerpo (pose landmarks).
3. Se calcula el ángulo de la rodilla.
4. Según el ángulo:
   - Ángulo grande → Persona parada.
   - Ángulo pequeño → Persona sentada.
5. Python envía una letra por el puerto COM5 al Arduino.
6. El Arduino recibe la señal y enciende el LED correspondiente.

---

## Tecnologías utilizadas

- Python 3.11
- OpenCV
- MediaPipe
- PySerial
- Arduino UNO

---

## Conexión Arduino

- LED Rojo → Pin 8
- LED Verde → Pin 9
- Ambos con resistencia de 220 ohmios a GND
- Baudrate: 9600

---

## Ejecución

Instalar dependencias:


pip install -r requirements.txt


Ejecutar el programa:


python src/main.py


Presionar **Q** para salir.

---

## Nota sobre el desarrollo

Este proyecto fue realizado con apoyo de inteligencia artificial como herramienta de guía y apoyo técnico.  
Sin embargo, durante el desarrollo se logró un gran entendimiento del funcionamiento del código, la lógica de detección de postura y la comunicación entre Python y Arduino.

El uso de IA permitió mejorar el aprendizaje y comprender mejor cada parte del sistema.

---

## Realizado por

Santiago Pachon