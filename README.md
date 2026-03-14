# 🦷 Dentection AWS — Entorno Multi-Container Altamente Disponible

Despliegue en AWS de **Dentection**, un sistema de detección de 14 anomalías dentales con IA usando YOLOv8, implementado en un entorno Multi-Container altamente disponible con Docker Compose, balanceador de carga y base de datos PostgreSQL.

> Práctica 4 — Computación en la Nube | Universidad Autónoma de Occidente  
> Estudiantes: Valentina Bueno Collazos, David Alejandro Cajiao Lazt, Natalia Moreno Montoya

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Arquitectura de la Infraestructura](#-arquitectura-de-la-infraestructura)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Paso a Paso de Implementación](#-paso-a-paso-de-implementación)
  - [1. Infraestructura de Red](#1-infraestructura-de-red)
  - [2. Security Groups](#2-security-groups)
  - [3. Instancias EC2](#3-instancias-ec2)
  - [4. Dockerización de la App](#4-dockerización-de-la-app)
  - [5. Docker Compose Multi-Container](#5-docker-compose-multi-container)
  - [6. Despliegue en las Instancias](#6-despliegue-en-las-instancias)
  - [7. Application Load Balancer](#7-application-load-balancer)
  - [8. Pruebas de Alta Disponibilidad](#8-pruebas-de-alta-disponibilidad)
- [Integración con Base de Datos](#-integración-con-base-de-datos)
- [Acceso a la Aplicación](#-acceso-a-la-aplicación)
- [Créditos](#-créditos)

---

## 📌 Descripción del Proyecto

Este repositorio contiene el despliegue en AWS de **Dentection**, una herramienta de IA que asiste a odontólogos en la detección de anomalías dentales en radiografías panorámicas.

La aplicación fue adaptada para correr en un entorno de alta disponibilidad con las siguientes características:

- Dos instancias EC2 en zonas de disponibilidad diferentes (`us-east-1a` y `us-east-1b`)
- Contenedores Docker gestionados con Docker Compose
- Base de datos PostgreSQL en contenedor para registrar los análisis realizados
- Application Load Balancer para distribuir el tráfico
- Subredes privadas con salida a internet a través de NAT Gateway
- Política de mínimos privilegios en Security Groups

---

## 🏗️ Arquitectura de la Infraestructura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              INTERNET                                   │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │ HTTP :80
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Application Load Balancer                            │
│                         dentection-alb                                  │
│                    internet-facing │ puerto 80                          │
│              SG-ALB: solo acepta HTTP :80 desde 0.0.0.0/0              │
└────────────────────┬─────────────────────────────┬──────────────────────┘
                     │                             │
         ┌───────────▼─────────────────────────────▼───────────┐
         │              VPC: dentection-vpc                     │
         │                 192.168.0.0/16                       │
         │                                                      │
         │  ┌─────────────────────┐  ┌──────────────────────┐  │
         │  │  public-subnet-1a   │  │   public-subnet-1b   │  │
         │  │   192.168.1.0/24    │  │    192.168.2.0/24    │  │
         │  │   us-east-1a        │  │    us-east-1b         │  │
         │  │                     │  │                      │  │
         │  │  ┌───────────────┐  │  │                      │  │
         │  │  │ NAT Gateway   │  │  │   (ALB node)         │  │
         │  │  │ dentection-nat│  │  │                      │  │
         │  │  └───────┬───────┘  │  │                      │  │
         │  └──────────┼──────────┘  └──────────────────────┘  │
         │             │ (salida a internet                      │
         │             │  para subredes privadas)               │
         │  ┌──────────┼──────────────────────────────────────┐ │
         │  │          │    Tráfico :8501                      │ │
         │  │    ┌─────▼──────────────┐  ┌──────────────────┐ │ │
         │  │    │  private-subnet-1a │  │ private-subnet-1b│ │ │
         │  │    │   192.168.3.0/24   │  │  192.168.4.0/24  │ │ │
         │  │    │   us-east-1a       │  │  us-east-1b      │ │ │
         │  │    │                    │  │                  │ │ │
         │  │    │ ┌────────────────┐ │  │ ┌──────────────┐ │ │ │
         │  │    │ │dentection-     │ │  │ │dentection-   │ │ │ │
         │  │    │ │instance-1      │ │  │ │instance-2    │ │ │ │
         │  │    │ │t3.medium       │ │  │ │t3.medium     │ │ │ │
         │  │    │ │Ubuntu 22.04    │ │  │ │Ubuntu 22.04  │ │ │ │
         │  │    │ │                │ │  │ │              │ │ │ │
         │  │    │ │ ┌────────────┐ │ │  │ │ ┌──────────┐ │ │ │ │
         │  │    │ │ │dentection- │ │ │  │ │ │dentection│ │ │ │ │
         │  │    │ │ │app         │ │ │  │ │ │-app      │ │ │ │ │
         │  │    │ │ │:8501       │ │ │  │ │ │:8501     │ │ │ │ │
         │  │    │ │ └────────────┘ │ │  │ │ └──────────┘ │ │ │ │
         │  │    │ │                │ │  │ │      │       │ │ │ │
         │  │    │ │ ┌────────────┐ │ │  │ │      │ :5432 │ │ │ │
         │  │    │ │ │dentection- │◄├─┼──┼─┼──────┘       │ │ │ │
         │  │    │ │ │db          │ │ │  │ │  IP privada  │ │ │ │
         │  │    │ │ │PostgreSQL  │ │ │  │ │              │ │ │ │
         │  │    │ │ │:5432       │ │ │  │ └──────────────┘ │ │ │
         │  │    │ │ └────────────┘ │ │  │                  │ │ │
         │  │    │ │                │ │  │                  │ │ │
         │  │    │ │ user: appuser  │ │  │ user: appuser    │ │ │
         │  │    │ │ SG-EC2         │ │  │ SG-EC2           │ │ │
         │  │    │ └────────────────┘ │  └──────────────────┘ │ │
         │  │    └────────────────────┘                       │ │
         │  └─────────────────────────────────────────────────┘ │
         └───────────────────────────────────────────────────────┘
```

### Componentes AWS

| Recurso | Nombre | Descripción |
|---|---|---|
| VPC | `taller-vpc` | Red privada `192.168.0.0/16` |
| Subred pública 1 | `public-subnet-a` | `192.168.1.0/24` — us-east-1a |
| Subred pública 2 | `public-subnet-b` | `192.168.2.0/24` — us-east-1b |
| Subred privada 1 | `private-subnet-a` | `192.168.3.0/24` — us-east-1a |
| Subred privada 2 | `private-subnet-b` | `192.168.4.0/24` — us-east-1b |
| NAT Gateway | `taller-nat` | Salida a internet para subredes privadas |
| Instancia 1 | `dentection-instance-1` | t3.medium — us-east-1a |
| Instancia 2 | `dentection-instance-2` | t3.medium — us-east-1b |
| Load Balancer | `dentection-alb` | Application Load Balancer — internet-facing |
| Target Group | `dentection-tg` | HTTP:8501 — apunta a las dos instancias |

---

## 📁 Estructura del Repositorio

```
Dentection_AWS/
├── modelo/
│   └── best_dental_kaggle.pt       # Modelo YOLOv8 entrenado
├── utils/
│   └── funciones.py                # Funciones auxiliares
├── main.py                         # Punto de entrada de la app (navegación)
├── app.py                          # Detector de anomalías + integración BD
├── inicio.py                       # Página de bienvenida
├── requirements.txt                # Dependencias Python
├── packages.txt                    # Dependencias del sistema
├── Dockerfile                      # Imagen Docker de la app
├── docker-compose.yml              # Configuración Multi-Container
├── .gitignore
└── README.md
```

---

## 🚀 Paso a Paso de Implementación

### 1. Infraestructura de Red

#### 1.1 Crear la VPC
- **Nombre:** `taller-vpc`
- **CIDR:** `192.168.0.0/16`

#### 1.2 Crear subredes

| Nombre | AZ | CIDR | Tipo |
|---|---|---|---|
| `public-subnet-1a` | us-east-1a | 192.168.1.0/24 | Pública |
| `public-subnet-1b` | us-east-1b | 192.168.2.0/24 | Pública |
| `private-subnet-1a` | us-east-1a | 192.168.3.0/24 | Privada |
| `private-subnet-1b` | us-east-1b | 192.168.4.0/24 | Privada |

#### 1.3 Internet Gateway
```
Crear → Nombre: taller-igw → Attach a taller-vpc
```

#### 1.4 NAT Gateway
```
Subnet: public-subnet-a
Elastic IP: Allocate new
Nombre: taller-nat
```

#### 1.5 Route Tables

**Route table pública:**
- Ruta `0.0.0.0/0` → Internet Gateway
- Asociar: `public-subnet-a` y `public-subnet-b`

**Route table privada:**
- Ruta `0.0.0.0/0` → NAT Gateway (`taller-nat`)
- Asociar: `private-subnet-a` y `private-subnet-b`

---

### 2. Security Groups

#### lb-sg (Load Balancer)
| Tipo | Puerto | Origen | Descripción |
|---|---|---|---|
| HTTP | 80 | 0.0.0.0/0 | Tráfico público |

#### ec2-sg (Instancias)
| Tipo | Puerto | Origen | Descripción |
|---|---|---|---|
| Custom TCP | 8501 | SG-ALB | Streamlit desde ALB |
| SSH | 22 | Mi IP | Acceso SSH personal |
| PostgreSQL | 5432 | SG-EC2 | Comunicación entre instancias |

> Política de mínimos privilegios: las instancias no son accesibles directamente desde internet, solo a través del ALB.

---

### 3. Instancias EC2

#### Configuración de cada instancia

| Campo | Valor |
|---|---|
| AMI | Ubuntu Server 22.04 LTS |
| Tipo | t3.medium |
| Key pair | `dentection-key` |
| VPC | `taller-vpc` |
| Subnet | `private-subnet-a` (inst. 1) / `private-subnet-b` (inst. 2) |
| IP pública | Deshabilitada |
| Security Group | SG-EC2 |
| Storage | 20 GB gp3 |

#### User Data (instalación automática de Docker)

```bash
#!/bin/bash
set -e
apt-get update -y
apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg lsb-release libgl1 libglib2.0-0

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

curl -SL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

useradd -m -s /bin/bash appuser
usermod -aG docker appuser
systemctl enable docker
systemctl start docker
```

> ⚠️ Si el User Data no se ejecuta correctamente, instalar Docker manualmente con los mismos comandos conectándose a la instancia.

---

### 4. Dockerización de la App

Para la dockerización de la app se generaron un **Dockerfile**, en el cual se genero la imagen que posteriormente fue subida a Docker Hub; y un **docker-compose.yml** con el fin de garantizar un entorno Multi-Container. 

---

### 6. Despliegue en las Instancias

#### Conectarse a las instancias

Las instancias están en subredes privadas. Se puede acceder a ellas con un **Bastion Host** en la subred pública:

```bash
# Desde tu máquina local — conectar al bastion
ssh -i dentection-key.pem ubuntu@IP-PUBLICA-BASTION

# Desde el bastion — saltar a las instancias privadas
ssh -i ~/.ssh/dentection-key.pem ubuntu@IP-PRIVADA-INSTANCIA
```

#### Instancia 1 (app + base de datos)

```bash
sudo su - appuser
git clone https://github.com/natam226/Dentection_AWS.git
cd Dentection_AWS

# Levantar app + BD
docker-compose --profile with-db up -d

# Verificar contenedores
docker ps
```

#### Instancia 2 (solo app, BD remota)

```bash
sudo su - appuser
git clone https://github.com/natam226/Dentection_AWS.git
cd Dentection_AWS

# Levantar solo la app apuntando a la BD de la Instancia 1
DB_HOST=IP-PRIVADA-INSTANCIA-1 docker-compose up -d
```

---

### 7. Application Load Balancer

#### Configuración

| Campo | Valor |
|---|---|
| Nombre | `dentection-alb` |
| Scheme | Internet-facing |
| VPC | `taller-vpc` |
| Subnets | `public-subnet-a` y `public-subnet-b` |
| Security Group | SG-ALB |

#### Target Group

| Campo | Valor |
|---|---|
| Nombre | `dentection-tg` |
| Target type | Instances |
| Protocol:Port | HTTP:8501 |
| Health check path | `/` |
| Healthy threshold | 2 |
| Interval | 10 segundos |

#### Listener
- Puerto **80** → Forward a `dentection-tg`
- **Stickiness activada** (necesario para Streamlit)

---

### 8. Pruebas de Alta Disponibilidad

#### Prueba 1 — Fallo de una instancia

```bash
# 1. Detener la instancia 1 desde la consola EC2
# 2. Esperar ~30 segundos
# 3. Acceder al DNS del ALB
curl http://dentection-alb-XXXX.us-east-1.elb.amazonaws.com

# Resultado esperado: la app sigue funcionando desde la instancia 2 ✅
```

#### Prueba 2 — Recuperación

```bash
# 1. Reiniciar la instancia 1
# 2. Esperar que el health check pase a Healthy (~20 segundos)
# 3. El ALB detecta la instancia y vuelve a distribuir tráfico ✅
```

#### Verificar estado de los targets

Ir a **EC2 → Target Groups → dentection-tg → pestaña Targets** y confirmar que ambas instancias estén en estado **Healthy**.

---

## 🗄️ Integración con Base de Datos

Cada vez que se analiza una radiografía, se guarda un registro en PostgreSQL con:

| Campo | Descripción |
|---|---|
| `id` | ID autoincremental |
| `fecha` | Timestamp del análisis |
| `nombre_imagen` | Nombre del archivo analizado |
| `anomalias_detectadas` | Lista de anomalías encontradas |
| `cantidad_detecciones` | Número total de detecciones |
| `instancia_id` | ID de la instancia EC2 que procesó la solicitud |

---

## 🌐 Acceso a la Aplicación

La aplicación es accesible desde internet a través del DNS del ALB:

```
http://dentection-alb-XXXX.us-east-1.elb.amazonaws.com
```

### Uso

1. Selecciona la pestaña **"Detector de anomalías dentales"**
2. Sube una o varias radiografías panorámicas (JPG, PNG, JPEG)
3. El modelo YOLOv8 procesará las imágenes automáticamente
4. Explora los resultados, filtra por tipo de anomalía y agrega notas clínicas
5. Descarga el reporte PDF completo
6. Cada análisis queda registrado en la base de datos PostgreSQL
