import socket
import time
import signal
import sys
import logging
import os
import json

# Inicializar el registro (logger)
logging.basicConfig(level=logging.INFO)

# Leer la configuración desde el archivo manage-p2.json
config_file = 'config_across.json'

if not os.path.exists(config_file):
    logging.error(f"El archivo de configuración '{config_file}' no existe.")
    sys.exit(1)

with open(config_file, 'r') as f:
    try:
        config = json.load(f)

        # Obtención de parámetros
        dst_ip = config.get("dst_ip")
        port = int(config.get("udp_port"))
        data = eval(config.get("data"))
        execution_time = int(config.get("execution_time"))
        bandwidth_profile_KB = eval(config.get("bandwidth_profile_KB"))

    except json.JSONDecodeError:
        logging.error(f"Error al leer el archivo de configuración '{config_file}'.")
        sys.exit(1)

# Variable global para controlar si se debe detener el envío
running = True

def signal_handler(sig, frame):
    """
    Manejador de señal para SIGINT (Ctrl+C).
    Detener el cliente de manera segura.
    """
    global running
    print("\nInterrupción detectada. Deteniendo el cliente...")
    running = False  # Cambiar la variable para detener el envío de datos

signal.signal(signal.SIGINT, signal_handler)

def client(contador):

    bandwidth_value = bandwidth_profile_KB(contador)
    bytes_per_second = max(1, bandwidth_value)*1000

    print(f"Ejecutando test TCP a {(bytes_per_second/1000)} KB/s\n") 

    # Crear un socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"Conectado a {dst_ip}:{port}")

    interval = len(data) / bytes_per_second  # Tiempo entre envíos de paquetes

    start_time = time.time()
    while running:
        
        s.sendto(data, (dst_ip, port))  # Enviar datos a través de UDP
        time.sleep(interval)  # Controlar el intervalo para mantener el ancho de banda

        # Limitación del tiempo de ejecución
        if time.time() - start_time > execution_time:
            break

    s.close()
    print("Conexión cerrada")

if __name__ == "__main__":
    client()
