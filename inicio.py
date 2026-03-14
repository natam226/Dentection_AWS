import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dentection", page_icon="🦷", layout="wide")

# =========================================================
# INTERFAZ
# =========================================================

st.subheader("Acerca de Dentection")

st.markdown("""
¡Bienvenido a Dentection! \n
**Dentection** es una herramienta asistida por Inteligencia Artificial diseñada para apoyar a odontólogos 
en la identificación de patologías y condiciones dentales en radiografías panorámicas.
A continuación, te proporcionamos una guía rápida para comenzar a utilizar la aplicación:
            """)

tab1, tab2, tab3 = st.tabs(["⁜ Tutorial de Uso", "⁜ Sobre el Modelo", "⁜ Métricas de Rendimiento"])

with tab1:
    st.header("¿Cómo usar la aplicación?")
    
    st.markdown("""
    1. **Navega al detector de anomalías dentales:** Ve a la página **"Detector de anomalías dentales"** usando el menú de la parte superior de la página.
    2. **Sube tus Imágenes:** Arrastra o selecciona tus radiografías (formatos JPG, PNG) en la barra lateral.
    3. **Analiza:** El modelo procesará automáticamente la imagen.
    4. **Interactúa:**
        - Usa los botones **Anterior/Siguiente** para cambiar de imagen.
        - Haz clic en la **tabla de resultados** para resaltar hallazgos específicos.
        - Agrega **notas clínicas** en el campo de texto inferior.
        - Filtra los resultados por tipo de anomalía usando el menú desplegable en la barra lateral.
    5. **Exporta:** Haz clic en **"Descargar Reporte PDF"** para obtener un informe completo con las imágenes y tus notas.
    """)

    st.divider()
    st.subheader("Video de demostración")
    st.markdown("Mira este breve video para ver el flujo de uso de la aplicación.")

    # Opción A: insertar un video de YouTube (reemplaza la URL)
    st.video("https://www.youtube.com/watch?v=CO8ihC5-aDU")

    st.success("¡Listo para empezar! Haz clic en 'Detector de anomalías dentales' en la barra superior.")
with tab2:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Nuestro modelo de detección está basado en la arquitectura **YOLOv8n**, entrenada específicamente para identificar 
        diversas anomalías dentales en radiografías panorámicas. Utilizamos un conjunto de datos
        anotado con la guia de expertos odontólogos para garantizar la precisión y relevancia clínica de las predicciones.
        
        **Características del Modelo:**
        - Detección en tiempo real.
        - Capacidad para identificar múltiples anomalías en una sola imagen.
        - Interfaz interactiva para facilitar la revisión y anotación de resultados.
        """)

        st.header("Arquitectura YOLOv8")
        st.write("""
        Este sistema utiliza la arquitectura **YOLOv8 (You Only Look Once)**, el estado del arte en detección de objetos en tiempo real.
        
        **Características del entrenamiento:**
        - **Dataset:** Entrenado con un conjunto de datos publico de radiografías panorámicas.
        - **Épocas:** 100 épocas de entrenamiento.
        - **Clases:** El modelo se entrena usando 14 clases distintas.
        """)
        

    with col2:
        st.header("Clases Detectables")
        clases = [
            'Tratamiento de conducto', 'Fractura', 'Diastema', 'Cordal', 'Quiste',
            'Diente retenido', 'Caries', 'Zona edéntula', 'Dientes sanos',
            'Apiñamiento', 'Diente rotado', 'Supernumerario',
            'Enanismo radicular', 'Residuo radicular'
        ]
        st.dataframe(pd.DataFrame(clases, columns=["Anomalías"]), hide_index=True, width='stretch')

    st.info("El modelo se ejecuta localmente en el servidor, garantizando que las imágenes procesadas no se almacenan permanentemente.")
    st.info("El modelo está diseñado para asistir, no reemplazar, el juicio clínico profesional.")

with tab3:
    st.header("Desempeño del Modelo")
    st.write("A continuación se presentan las métricas obtenidas en el conjunto de validación:")

    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.metric(label="mAP50", value="0.26")
    with c2:
        st.metric(label="mAP50-95", value="0.10")
    with c3:
        st.metric(label="Precisión", value="0.43")
    with c4:
        st.metric(label="Recall", value="0.27")

    st.info("A pesar de las métricas actuales, el modelo ha demostrado ser una herramienta valiosa en la práctica clínica, ayudando a los odontólogos a identificar anomalías que podrían pasar desapercibidas.")
    

st.markdown("""             
---
Desarrollado por **Equipo Dentection** | 2025 🦷            
            Versión 1.0.0
""")