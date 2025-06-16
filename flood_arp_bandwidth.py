import socket
import threading
import sys
import signal
import logging
import os
import json
import time

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
        src_ip = config.get("src_ip")
        dst_ip = config.get("dst_ip")
        threads = int(config.get("arp_threads"))
        src_mac_original = config.get("arp_src_mac_original")
        execution_time = int(config.get("execution_time"))
        bandwidth_profile_KB = eval(config.get("bandwidth_profile_KB"))
        arp_interface = config.get("arp_interface")

    except json.JSONDecodeError:
        logging.error(f"Error al leer el archivo de configuración '{config_file}'.")
        sys.exit(1)

src_mac = bytes.fromhex(src_mac_original.replace(':', ''))  # Convertir MAC de origen

# Lista para almacenar los hilos activos
threads_active = []

# Manejador de señal para SIGINT (Ctrl+C)
def signal_handler(sig, frame):
    print("\nInterrupción detectada. Deteniendo todos los hilos...")
    for thread in threads_active:
        thread.join()
    sys.exit(0)

# Función para crear una solicitud ARP
def create_arp_request(src_mac, src_ip, dst_ip):
    dst_mac = b'\xff\xff\xff\xff\xff\xff'  # MAC de destino (broadcast)
    eth_type = b'\x08\x06'  # Tipo ARP (0x0806)

    hw_type = b'\x00\x01'  # Ethernet
    proto_type = b'\x08\x00'  # IPv4
    hw_size = b'\x06'  # Tamaño de la dirección MAC
    proto_size = b'\x04'  # Tamaño de la dirección IP
    opcode = b'\x00\x01'  # Solicitud ARP (1)

    arp_src_mac = src_mac
    arp_src_ip = socket.inet_aton(src_ip)
    arp_dst_ip = socket.inet_aton(dst_ip)

    arp_frame = hw_type + proto_type + hw_size + proto_size + opcode + \
                arp_src_mac + arp_src_ip + b'\x00\x00\x00\x00\x00\x00' + arp_dst_ip

    packet = dst_mac + src_mac + eth_type + arp_frame
    return packet

# Función para enviar un paquete ARP
def send_arp(src_mac, src_ip, dst_ip):
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806))
    sock.bind((arp_interface, 0))

    packet = create_arp_request(src_mac, src_ip, dst_ip)
    sock.send(packet)

def flood_arp(src_mac, src_ip, dst_ip, threads, bytes_per_second):
    
    """
    Realizar un flood ARP con control preciso de tasa de envío.
    """
    print(f"Ejecutando test ARP a {bytes_per_second / 1000} KB/s\n")

    def worker():
        packet = create_arp_request(src_mac, src_ip, dst_ip)
        packet_size = len(packet)

        packets_per_second = bytes_per_second // packet_size
        interval = 0.1  # Intervalo en segundos para el control del envío
        packets_per_interval = packets_per_second * interval

        start_time = time.time()

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= execution_time:
                break  # Terminar el envío después del tiempo de ejecución

            interval_start_time = time.time()
            packets_sent= 0

            while packets_sent < packets_per_interval:
                if time.time() - start_time >= execution_time:
                    break
                send_arp(src_mac, src_ip, dst_ip)
                packets_sent += 1

            # Ajustar el tiempo restante
            interval_elapsed_time = time.time() - interval_start_time
            time_to_wait = interval - interval_elapsed_time

            if time_to_wait > 0:
                time.sleep(time_to_wait)


    # Iniciar los hilos para el flood ARP
    global threads_active
    for _ in range(threads):
        thread = threading.Thread(target=worker)
        threads_active.append(thread)
        thread.start()

    for thread in threads_active:
        thread.join()

# Registrar el manejador de señales para SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

def client(contador):
    bandwidth_value = bandwidth_profile_KB(contador)
    bytes_per_second = max(1, bandwidth_value) * 1000

    flood_arp(src_mac, src_ip, dst_ip, threads, bytes_per_second)
