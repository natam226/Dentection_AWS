import psycopg2
import os
from datetime import datetime

def get_db_connection():
    """Conexión a PostgreSQL con variables de entorno"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "dentection"),
            user=os.getenv("DB_USER", "dentuser"),
            password=os.getenv("DB_PASSWORD", "dentpass")
        )
        return conn
    except Exception as e:
        return None

def init_db():
    """Crear tabla si no existe"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analisis (
                id SERIAL PRIMARY KEY,
                fecha TIMESTAMP DEFAULT NOW(),
                nombre_imagen VARCHAR(255),
                anomalias_detectadas TEXT,
                cantidad_detecciones INTEGER,
                instancia_id VARCHAR(50)
            )
        """)
        conn.commit()
        cur.close()
        conn.close()

def get_instance_id():
    try:
        token = urllib.request.urlopen(
            urllib.request.Request(
                'http://169.254.169.254/latest/api/token',
                headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
                method='PUT'
            ), timeout=1
        ).read().decode()
        req = urllib.request.Request(
            'http://169.254.169.254/latest/meta-data/instance-id',
            headers={'X-aws-ec2-metadata-token': token}
        )
        return urllib.request.urlopen(req, timeout=1).read().decode()
    except:
        return "local"

def guardar_analisis(nombre_imagen, anomalias, cantidad):
    conn = get_db_connection()
    if conn:
        try:
            instancia = get_instance_id()  # ← aquí
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO analisis 
                    (nombre_imagen, anomalias_detectadas, cantidad_detecciones, instancia_id)
                VALUES (%s, %s, %s, %s)
            """, (nombre_imagen, str(anomalias), cantidad, instancia))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            pass

# Inicializar BD al arrancar
init_db()


# =========================================================

import streamlit as st
import cv2
import torch
import pandas as pd
from ultralytics import YOLO
from ultralytics.engine.results import Boxes
from utils.funciones import *

# =========================================================
# CONFIGURACIÓN INICIAL
# =========================================================
st.set_page_config(page_title="Dentection", page_icon="🦷", layout="wide")

@st.cache_resource
def load_model():
    """Carga y retorna el modelo YOLO entrenado."""
    return YOLO("modelo/best_dental_kaggle.pt")

model = load_model()

if "notes" not in st.session_state: st.session_state["notes"] = {}
if "current_index" not in st.session_state: st.session_state["current_index"] = 0

# =========================================================
# INTERFAZ
# =========================================================

with st.sidebar:
    st.header("Panel de Control")
    uploaded_files = st.file_uploader("Imágenes", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    class_names = [
        'tratamiento_conducto', 'fractura', 'diastema', 'cordal', 'quiste',
        'diente_retenido', 'caries', 'zona_dentula', 'dientes_sanos',
        'apinamiento', 'diente_rotado', 'supernumerario',
        'enanismo_radicular', 'residuo_radicular'
    ]
    
    selected_class = st.selectbox("Filtrar Clase:", ["Mostrar todas"] + class_names)

if uploaded_files:
    if st.session_state["current_index"] >= len(uploaded_files):
        st.session_state["current_index"] = 0

    # Botones de navegación
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("← Anterior"):
            if st.session_state["current_index"] > 0:
                st.session_state["current_index"] -= 1
                st.rerun()
    with c3:
        # subcolumnas: la de la derecha contendrá el botón, así queda alineado a la derecha
        spacer, btn_col = st.columns([2, 1])
        with btn_col:
            if st.button("Siguiente →"):
                if st.session_state["current_index"] < len(uploaded_files) - 1:
                    st.session_state["current_index"] += 1
                    st.rerun()

    current_file = uploaded_files[st.session_state["current_index"]]
    file_id = current_file.name
    if file_id not in st.session_state["notes"]: st.session_state["notes"][file_id] = []

    st.subheader(f"Analizando: {file_id}")

    # Procesamiento
    img_original = file_to_opencv(current_file)
    results = model.predict(img_original, imgsz=640)
    r = results[0]

    boxes_data = r.boxes.data
    if selected_class != "Mostrar todas":
        keep = [i for i, b in enumerate(r.boxes) if class_names[int(b.cls[0])] == selected_class]
        filtered_boxes = Boxes(boxes_data[keep], r.orig_shape) if keep else Boxes(torch.zeros((0, 6)), r.orig_shape)
    else:
        filtered_boxes = r.boxes

    # Dataframe preparation
    table_data = []
    for i, box in enumerate(filtered_boxes):
        table_data.append({
            "ID": i,
            "Etiqueta": class_names[int(box.cls[0])],
            "Confianza": float(box.conf[0])
        })
    
    df_detections = pd.DataFrame(table_data)

    guardar_analisis(
        file_id,
        df_detections["Etiqueta"].tolist() if not df_detections.empty else [],
        len(df_detections)
    )

    if not df_detections.empty:
        # Formato visual para la tabla (% de confianza)
        df_display = df_detections.copy()
        df_display["Confianza"] = df_display["Confianza"].apply(lambda x: f"{x:.2%}")
    else:
        df_display = pd.DataFrame()

    # Layout Principal
    col_img, col_details = st.columns([2, 1])

    # --- COLUMNA DERECHA: DATOS Y ESTADÍSTICAS ---
    with col_details:
        st.markdown("### 📋 Resultados Detallados")
        
        selected_box_index = None
        
        if not df_display.empty:
            # 1. Tabla Interactiva
            event = st.dataframe(
                df_display[["Etiqueta", "Confianza"]], # Mostramos solo columnas relevantes
                on_select="rerun",
                selection_mode="single-row",
                width='stretch',
                height=200
            )
            if event.selection.rows:
                row_idx = event.selection.rows[0]
                selected_box_index = df_detections.iloc[row_idx]["ID"]

            # -----------------------------------------------------
            # NUEVO: SECCIÓN DE ESTADÍSTICAS
            # -----------------------------------------------------
            st.divider()
            st.markdown("### 📊 Estadísticas")
            
            # A. Métricas Generales
            st.metric("Total Hallazgos", len(df_detections))

            # B. Preparar datos para conteo y gráfico
            # value_counts() devuelve una serie: index=Clase, value=Cantidad
            counts = df_detections["Etiqueta"].value_counts()
            
            # C. Gráfico de Barras Simple
            st.markdown("**Frecuencia por afección:**")
            st.bar_chart(counts, color="#4347AC", height=200)

        else:
            st.info("No se encontraron objetos para esta clase.")
            counts = pd.Series() # Vacio para PDF

    # --- COLUMNA IZQUIERDA: IMAGEN ---
    with col_img:
        img_final = draw_custom_boxes(
            img_original, 
            filtered_boxes, 
            class_names, 
            selected_index=selected_box_index
        )
        img_final_rgb = cv2.cvtColor(img_final, cv2.COLOR_BGR2RGB)
        show_zoomable_image(img_final_rgb)

    # --- PIE DE PÁGINA: NOTAS Y EXPORTAR ---
    st.divider()
    st.markdown("#### 📝 Anotaciones del Especialista")
    
    ca, cb = st.columns([4, 1])
    with ca:
        note_in = st.text_input("Observación:", key=f"nt_{file_id}")
    with cb:
        st.write("")
        st.write("")
        if st.button("Guardar", key=f"bn_{file_id}"):
            if note_in:
                st.session_state["notes"][file_id].append(note_in)
                st.rerun()

    saved_notes = st.session_state["notes"][file_id]
    if saved_notes:
        for n in saved_notes:
            st.info(f"• {n}")

    st.write("---")
    
    # Generamos PDF pasando también los conteos (counts)
    if not df_detections.empty:
        counts_for_pdf = df_detections["Etiqueta"].value_counts()
    else:
        counts_for_pdf = pd.Series()

    pdf_data = create_pdf(
        img_final_rgb, 
        filtered_boxes, 
        saved_notes, 
        file_id, 
        class_names, 
        counts_for_pdf # Pasamos el resumen al PDF
    )
    
    st.download_button(
        "📄 Descargar Reporte PDF Completo", 
        data=pdf_data, 
        file_name=f"Reporte_{file_id}.pdf", 
        mime="application/pdf"
    )

else:
    st.info("Sube imágenes en el panel lateral.")