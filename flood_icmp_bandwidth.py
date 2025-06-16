import socket
import struct
import random
import signal
import sys
import logging
import os
import json  
import time

# Inicializar el registro (logger)
logging.basicConfig(level=logging.INFO)

# Leer la configuración desde el archivo config_across.json
config_file = 'config_across.json'

if not os.path.exists(config_file):
    logging.error(f"El archivo de configuración '{config_file}' no existe.")
    sys.exit(1)

with open(config_file, 'r') as f:
    try:
        config = json.load(f)
        src_ip = config.get("src_ip")
        dst_ip = config.get("dst_ip")
        execution_time = int(config.get("execution_time"))
        bandwidth_profile_KB = eval(config.get("bandwidth_profile_KB"))

    except json.JSONDecodeError:
        logging.error(f"Error al leer el archivo de configuración '{config_file}'.")
        sys.exit(1)

ICMP_ECHO_REQUEST = 8  # Tipo de mensaje ICMP para solicitud de eco
IP_PROTO_ICMP = 1      # Protocolo ICMP
running = True

def signal_handler(sig, frame):
    global running
    print("\nInterrupción detectada. Deteniendo el flood ICMP...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

def checksum(source_string):
    sum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = struct.unpack("!H", source_string[count:count+2])[0]
        sum = sum + thisVal
        sum = sum & 0xFFFFFFFF
        count = count + 2

    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xFFFFFFFF

    sum = (sum >> 16) + (sum & 0xFFFF)
    sum = sum + (sum >> 16)
    checksum = ~sum & 0xFFFF
    return checksum

def create_packet(id, source_ip, dest_ip):
    ip_header = struct.pack("!BBHHHBBH4s4s",
                            0x45, 0, 40, 0, 0, 255, IP_PROTO_ICMP,
                            0, socket.inet_aton(source_ip), socket.inet_aton(dest_ip))

    icmp_header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = bytes([random.randint(0, 255) for _ in range(56)])
    checksum_value = checksum(icmp_header + data)
    icmp_header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, checksum_value, id, 1)
    packet = ip_header + icmp_header + data
    return packet

def flood_icmp(src_ip, dst_ip, bytes_per_second):

    """
    Realizar un flood ICMP con control preciso de tasa de envío.
    """
    print(f"Ejecutando test ICMP a {bytes_per_second / 1000} KB/s\n")

    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    packet_id = random.randint(1, 65535)
    packet = create_packet(packet_id, src_ip, dst_ip)
    packet_size = len(packet)
    packets_per_second = bytes_per_second // packet_size
    interval = 0.1
    packets_per_interval = packets_per_second * interval

    start_time = time.time()

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= execution_time:
            break  # Terminar el envío después del tiempo de ejecución

        interval_start_time = time.time()
        packets_sent = 0

        while packets_sent < packets_per_interval:
            if time.time() - start_time >= execution_time:
                break
            icmp_socket.sendto(packet, (dst_ip, 1))
            packets_sent += 1

        # Ajustar el tiempo restante
        interval_elapsed_time = time.time() - interval_start_time
        time_to_wait = interval - interval_elapsed_time

        if time_to_wait > 0:
            time.sleep(time_to_wait)

    icmp_socket.close()

def client(contador):
    bandwidth_value = bandwidth_profile_KB(contador)
    bytes_per_second = max(1, bandwidth_value) * 1000
    flood_icmp(src_ip, dst_ip, bytes_per_second)
