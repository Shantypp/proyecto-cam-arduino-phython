import serial, time

ser = serial.Serial("COM5", 9600, timeout=1)
time.sleep(2)

print("Enviando P (rojo)...")
ser.write(b"P")
time.sleep(2)

print("Enviando S (verde)...")
ser.write(b"S")
time.sleep(2)

ser.close()
print("Listo.")