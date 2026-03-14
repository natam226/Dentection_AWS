# 🦷 Dentection - Sistema de Detección de Anomalías Dentales

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)

**Dentection** es una herramienta asistida por Inteligencia Artificial diseñada para apoyar a odontólogos en la identificación de patologías y condiciones dentales en radiografías panorámicas. Utiliza un modelo YOLOv8n entrenado específicamente para detectar 14 tipos diferentes de anomalías dentales.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Demo](#-demo)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Arquitectura del Modelo](#-arquitectura-del-modelo)
- [Clases Detectables](#-clases-detectables)
- [Métricas de Rendimiento](#-métricas-de-rendimiento)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Descargo de responsabilidad](#️-descargo-de-responsabilidad)
- [Equipo Dentection](#-equipo-dentection)

## Características

- **Detección en Tiempo Real**: Análisis instantáneo de radiografías panorámicas
- **14 Clases de Anomalías**: Identificación de múltiples condiciones dentales simultáneamente
- **Interfaz Intuitiva**: Aplicación web desarrollada con Streamlit
- **Navegación de Imágenes**: Análisis de múltiples radiografías con navegación anterior/siguiente
- **Filtrado Inteligente**: Filtra resultados por tipo específico de anomalía
- **Interacción Visual**: Selección de detecciones en tabla para resaltado en imagen
- **Visor con Zoom**: Exploración detallada de radiografías con OpenSeadragon
- **Anotaciones Clínicas**: Sistema de notas para observaciones del especialista
- **Estadísticas Visuales**: Gráficos de frecuencia y métricas generales
- **Exportación PDF**: Generación de reportes completos con imágenes, detecciones y notas

## Demo

[Video de Demostración](https://www.youtube.com/watch?v=CO8ihC5-aDU)

## Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación (Para ejecución local)

1. **Clonar el repositorio**
```bash
git clone https://github.com/valentinabc19/entrega_final_proyecto_ia.git
cd entrega_final_proyecto_ia
```

2. **Crear un entorno virtual (recomendado)**
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En macOS/Linux
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Verificar instalación de librerías del sistema (Linux)**
```bash
# Si estás en Linux, asegúrate de tener instalado:
sudo apt-get install libgl1-mesa-glx
```

5. **Descargar el modelo entrenado**

Asegúrate de que el archivo del modelo `best_dental_kaggle.pt` esté en la carpeta `modelo/`.

## Uso

### Ejecución de la Aplicación

#### Ejecución en la nube

Para hacer uso de la aplicacion web directamente desde el navegador accede a `https://dentection.streamlit.app/` 

#### Ejecución en local

```bash
streamlit run main.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Flujo de Trabajo

1. **Cargar Imágenes**: Sube una o varias radiografías panorámicas (JPG, PNG, JPEG) usando el panel lateral
2. **Análisis Automático**: El modelo procesará las imágenes automáticamente
3. **Explorar Resultados**: 
   - Navega entre imágenes con los botones Anterior/Siguiente
   - Usa el visor con zoom para examinar detalles
   - Haz clic en la tabla de resultados para resaltar detecciones específicas
   - Filtra por tipo de anomalía usando el selector desplegable
4. **Agregar Notas**: Registra observaciones clínicas en el campo de anotaciones
5. **Exportar Reporte**: Descarga un PDF completo con resultados y notas

## Arquitectura del Modelo

El sistema utiliza **YOLOv8n (You Only Look Once)**, la arquitectura de detección de objetos más avanzada para procesamiento en tiempo real.

### Especificaciones del Entrenamiento

- **Arquitectura**: YOLOv8n (versión nano, optimizada para velocidad)
- **Dataset**: Radiografías panorámicas dentales anotadas con supervisión experta
- **Épocas**: 100
- **Resolución**: 640x640 píxeles
- **Framework**: Ultralytics YOLO
- **Formato del Modelo**: PyTorch (.pt)

## Clases Detectables

El modelo puede identificar las siguientes 14 condiciones dentales:

| # | Clase | Descripción |
|---|-------|-------------|
| 1 | Tratamiento de conducto | Endodoncia previa |
| 2 | Fractura | Fractura dental |
| 3 | Diastema | Separación entre dientes |
| 4 | Cordal | Muela del juicio |
| 5 | Quiste | Lesión quística |
| 6 | Diente retenido | Diente no erupcionado |
| 7 | Caries | Lesión cariosa |
| 8 | Zona edéntula | Ausencia de dientes |
| 9 | Dientes sanos | Dientes sin patología |
| 10 | Apiñamiento | Malposición por falta de espacio |
| 11 | Diente rotado | Rotación anormal |
| 12 | Supernumerario | Dientes extra |
| 13 | Enanismo radicular | Raíces cortas |
| 14 | Residuo radicular | Fragmento de raíz |

## Métricas de Rendimiento

Resultados obtenidos en el conjunto de validación:

| Métrica | Valor |
|---------|-------|
| **mAP50** | 0.26 |
| **mAP50-95** | 0.10 |
| **Precisión** | 0.43 |
| **Recall** | 0.27 |

> **Nota**: A pesar de las métricas actuales, el modelo ha demostrado ser una herramienta valiosa en la práctica clínica como asistente de detección, ayudando a los odontólogos a identificar anomalías que podrían pasar desapercibidas.

## Estructura del Proyecto

```
entrega_final_proyecto_ia/
│
├── main.py                               # Punto de entrada de la aplicación
├── inicio.py                             # Página de información y tutorial
├── app.py                                # Página principal del detector
├── requirements.txt                      # Dependencias de Python
├── packages.txt                          # Dependencias del sistema
├── .gitignore                  
├── README.md                    
│
├── modelo/
│   └── best_dental_kaggle.pt             # Modelo YOLOv8 entrenado
│   └── detection_model_yolov8.ipynb      # Notebook de entrenamiento del modelo
│
├── utils/
│   └── funciones.py                      # Funciones auxiliares y utilidades
│
   
```

## Tecnologías Utilizadas

### Backend y ML
- **Python 3.8+**: Lenguaje de programación principal
- **PyTorch**: Framework de deep learning
- **Ultralytics YOLO**: Implementación de YOLOv8
- **OpenCV**: Procesamiento de imágenes

### Frontend y Visualización
- **Streamlit**: Framework de aplicación web
- **streamlit-option-menu**: Navegación mejorada
- **OpenSeadragon**: Visor de imágenes con zoom
- **Pandas**: Manipulación de datos
- **FPDF**: Generación de reportes PDF

### Dependencias Completas

Ver `requirements.txt` para la lista completa de dependencias.


## ⚠️ Descargo de Responsabilidad

**Este sistema es una herramienta de asistencia diagnóstica y NO reemplaza el juicio clínico profesional.** Todas las detecciones deben ser validadas por un odontólogo certificado. El modelo está diseñado para apoyar, no sustituir, la evaluación profesional.

## 👥 Equipo Dentection

Desarrollado por **Equipo Dentection** | 2025 

* [Valentina Bueno Collazos](https://github.com/valentinabc19)

* [Liseth Esmeralda Erazo Varela](https://github.com/memerazo)

* [Natalia Moreno Montoya](https://github.com/natam226)

Versión 1.0.0

---

⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub

🦷 **Dentection** - Asistencia inteligente para el cuidado dental
