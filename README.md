# 📡 Scripts de Generación de Tráfico Personalizado

Este repositorio contiene un conjunto de scripts en Python diseñados para generar tráfico de red controlado en entornos de laboratorio (por ejemplo, redes 5G). Permiten evaluar el rendimiento de la infraestructura bajo distintas condiciones de carga, mediante la simulación de múltiples tipos de paquetes.

> ⚠️ **Uso Ético**: Estas herramientas están diseñadas exclusivamente para pruebas en entornos controlados. Su uso en redes públicas o sin autorización puede ser ilegal o perjudicial.

---

## 🗂️ Estructura del Proyecto
.
├── config_across.json
├── flood_arp_bandwidth.py
├── flood_icmp_bandwidth.py
├── flood_tcp_socket_bandwidth.py
├── flood_udp_socket_bandwidth.py
└── global_flood_bandwidth.py


---

## ⚙️ Descripción de los Scripts

- `flood_udp_socket_bandwidth.py`  
  Genera tráfico UDP mediante el envío de datagramas usando la librería estándar `socket`.

- `flood_tcp_socket_bandwidth.py`  
  Genera tráfico TCP mediante conexiones persistentes con `socket`.

- `flood_icmp_bandwidth.py`  
  Envía paquetes ICMP utilizando Raw Sockets y estructuras binarias (`struct`).

- `flood_arp_bandwidth.py`  
  Inunda la red con solicitudes ARP utilizando Raw Sockets y múltiples hilos (`threading`).

- `global_flood_bandwidth.py`  
  Orquestador principal: automatiza la ejecución secuencial de los módulos, regula los tiempos y registra los datos de prueba.

---

## 🔧 Configuración

La configuración se encuentra en el archivo `config_across.json`. Esto permite ajustar los parámetros sin modificar el código fuente.

### Ejemplo de parámetros:

```json
{
  "number_of_repetitions": 3,
  "test_order": ["UDP", "TCP", "ICMP", "ARP"],
  "bandwidth_profile_KB": "lambda t: 1024",
  "execution_time": 10,
  "data": "Test payload",
  "src_ip": "192.168.1.10",
  "dst_ip": "192.168.1.100",
  "udp_port": 5005,
  "tcp_port": 5006,
  "arp_src_mac_original": "00:11:22:33:44:55",
  "arp_threads": 4,
  "arp_interface": "eth0"
}
