import flood_arp_bandwidth
import flood_icmp_bandwidth
import flood_tcp_socket_bandwidth
import flood_udp_socket_bandwidth

import subprocess
import time
import sys
import logging
import os
import json  
from datetime import datetime


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
        duration = config.get("duration")
        test_order = config.get("test_order")
        number_of_repetitions = config.get("number_of_repetitions")

    except json.JSONDecodeError:
        logging.error(f"Error al leer el archivo de configuración '{config_file}'.")
        sys.exit(1)

def tests_manager():
 
 for contador in range(number_of_repetitions):
   for i in range(len(test_order)):

      if test_order[i] == "udp":
         execute_script("udp", contador)

      elif test_order[i] == "tcp":
         execute_script("tcp", contador)

      elif test_order[i] == "arp":
         execute_script("arp", contador)

      elif test_order[i] == "icmp":
         execute_script("icmp", contador)
               


def execute_script(script_name, contador):
    """
    Ejecutar un script y medir el tiempo de ejecución.
    """
    print(f"Ejecutando {script_name}...\n")  # Mensaje indicando que se está ejecutando el script

    start_EPOCH = time.time()  # EPOCH de arranque (tiempo de inicio en formato UNIX)
    start_time = datetime.fromtimestamp(start_EPOCH).strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora de arranque

    try:

        if script_name == 'udp':
         flood_udp_socket_bandwidth.client(contador)

        elif script_name == 'tcp':
         flood_tcp_socket_bandwidth.client(contador)

        elif script_name == 'arp':
         flood_arp_bandwidth.client(contador)

        elif script_name == 'icmp':
         flood_icmp_bandwidth.client(contador)
        

        finish_EPOCH = time.time()  # EPOCH de parada (tiempo de fin en formato UNIX)
        finish_time = datetime.fromtimestamp(finish_EPOCH).strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora de parada

        # Calcular tiempo de ejecución
        execution_time = finish_EPOCH - start_EPOCH

        # Imprimir resultados con tabulación para alineación
        print(f"EPOCH arranque:\t\t{start_EPOCH:.2f}")
        print(f"EPOCH parada:\t\t{finish_EPOCH:.2f}")
        print(f"Time arranque:\t\t{start_time}")
        print(f"Time parada:\t\t{finish_time}")
        print(f"Tiempo de ejecución:\t{execution_time:.2f} segundos\n")  # Tiempo de ejecución en segundos

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar {script_name}: {e}")

    except KeyboardInterrupt:
        finish_EPOCH = time.time()  # EPOCH de parada si se interrumpe con Ctrl + C
        finish_time = datetime.fromtimestamp(finish_EPOCH).strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora de parada

        # Calcular tiempo de ejecución
        execution_time = finish_EPOCH - start_EPOCH

        # Imprimir resultados con tabulación para alineación
        print(f"\nProceso interrumpido durante la ejecución de {script_name}.")
        print(f"EPOCH arranque:\t\t{start_EPOCH:.2f}")
        print(f"EPOCH parada:\t\t{finish_EPOCH:.2f}")
        print(f"Time arranque:\t\t{start_time}")
        print(f"Time parada:\t\t{finish_time}")
        print(f"Tiempo de ejecución hasta la interrupción:\t{execution_time:.2f} segundos\n")

def main():
     if len(sys.argv) != 2:
        logging.error("Falta el comando")
        sys.exit(1)

     command = sys.argv[1]

     if command =="tests":
        tests_manager()
        
     else:
         logging.error("Orden desconocida")
     sys.exit(1)

     
if __name__ == "__main__":
    main()
