import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import serial
import threading
import time
import csv
import os
import cv2
import numpy as np
from queue import Queue

class GPSVideo:
    def __init__(self, gps):
        self.gps = gps
        self.gps.title("Datos GPS")
        self.gps.geometry("1000x600")

        self.serGPS = serial.Serial('COM8', 9600)  # Reemplazar
        time.sleep(2)

        self.serServo = serial.Serial('COM12', 9600) #Reemplazar
        time.sleep(2)
        
        # Nombre CSV
        self.csv_file = 'gps_data.csv'
        
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Cabecera
            writer.writerow(['Lat', 'Lon', 'Alt', 'Date'])
        
        self.queue = Queue()

        # Imagen fondo
        self.canvas = tk.Canvas(self.gps, width=1000, height=600)
        self.canvas.pack(fill="both", expand=True)
        self.bg_image = Image.open("C:/Users/sonic/OneDrive/Escritorio/Aerofondo.png") #Colocar dirección de fondo
        self.bg_image = self.bg_image.resize((1000, 600), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        
        # Datos GPS
        self.font_style = ('Helvetica', 20, 'bold')
        self.lat_label = self.canvas.create_text(300, 225, text="Latitud: N/A", fill="white", font=self.font_style)
        self.lon_label = self.canvas.create_text(300, 275, text="Longitud: N/A", fill="white", font=self.font_style)
        self.alt_label = self.canvas.create_text(300, 325, text="Altitud: N/A", fill="white", font=self.font_style)
        self.date_label = self.canvas.create_text(300, 375, text="Fecha: N/A", fill="white", font=self.font_style)
        
        # Servomotor
        self.Xposition = 90
        
        # Iniciar los hilos para leer datos del puerto serial y captura de video
        self.thread_gps = threading.Thread(target=self.gpsSerial)
        self.thread_servo = threading.Thread(target=self.read_servo_serial)
        self.thread_video = threading.Thread(target=self.camMove)
        self.thread_gps.daemon = True
        self.thread_servo.daemon = True
        self.thread_video.daemon = True
        self.thread_gps.start()
        self.thread_servo.start()
        self.thread_video.start()
        
        self.updateGui()

    def upLabels(self, lat, lon, alt, date):
        self.queue.put((lat, lon, alt, date))

    def gpsSerial(self):
        while True:
            if self.serGPS.in_waiting > 0:
                try:
                    line = self.serGPS.readline().decode('utf-8').strip()
                    if line.startswith("Lat:"):
                        parts = line.split(", ")
                        lat = parts[0].split(": ")[1]
                        lon = parts[1].split(": ")[1]
                        alt = parts[2].split(": ")[1].replace("m", "")
                        date = parts[3].split(": ")[1]

                        self.upLabels(lat, lon, alt, date)

                        with open(self.csv_file, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            # Escribir datos CSV
                            writer.writerow([lat, lon, alt, date])
                except UnicodeDecodeError:
                    print("Error al decodificar datos del GPS.")
                except Exception as e:
                    print(f"Error inesperado: {e}")

    def read_servo_serial(self):
        while True:
            #borrar
            time.sleep(0.1)

    def updateGui(self):
        while not self.queue.empty():
            lat, lon, alt, date = self.queue.get()
            self.canvas.itemconfig(self.lat_label, text=f"Latitud: {lat}")
            self.canvas.itemconfig(self.lon_label, text=f"Longitud: {lon}")
            self.canvas.itemconfig(self.alt_label, text=f"Altitud: {alt} m")
            self.canvas.itemconfig(self.date_label, text=f"Fecha: {date}")

        self.gps.after(100, self.updateGui)

    def camMove(self):
        cap = cv2.VideoCapture(0)
        while True:
            _, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (600, 600),200,200)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            red_lower = np.array([161, 155, 84], np.uint8)
            red_upper = np.array([180, 255, 255], np.uint8)
            mask = cv2.inRange(hsv, red_lower, red_upper)
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
            rows, cols, _ = frame.shape
            center_x = int(rows / 2)
            center_y = int(cols / 2)

            for cnt in contours:
                (x, y, w, h) = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "x = "+str(x)+" y = "+str(y)
                cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 0, 255))
                medium_x = int((x + x + w) / 2)
                medium_y = int((y + y + h) / 2)

                if medium_x > center_x + 40:
                    self.Xposition += 2
                    self.serServo.write((str(self.Xposition) + 'a').encode('utf-8'))
                if medium_x < center_x - 40:
                    self.Xposition -= 2
                    self.serServo.write((str(self.Xposition) + 'a').encode('utf-8'))
                
                break

            cv2.imshow("Captura de imagen ", frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    root = tk.Tk()
    app = GPSVideo(root)
    root.mainloop()

    app.serGPS.close()
    app.serServo.close()
    
    #En caso de querer elimicar CSV
    #if os.path.exists(app.csv_file):
        #os.remove(app.csv_file)
        #print(f"Archivo {app.csv_file} eliminado.")
    #else:
        #print(f"El archivo {app.csv_file} no existe.")
