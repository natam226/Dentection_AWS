import base64
from matplotlib import scale
import numpy as np
import cv2
import streamlit as st
import os
import tempfile
from fpdf import FPDF

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def file_to_opencv(uploaded_file):
    """Convierte un archivo subido a un formato OpenCV (BGR)."""
    bytes_data = uploaded_file.read()
    np_data = np.frombuffer(bytes_data, np.uint8)
    return cv2.imdecode(np_data, cv2.IMREAD_COLOR)

def show_zoomable_image(img_rgb):
    """Muestra una imagen RGB con capacidad de zoom usando OpenSeadragon en Streamlit."""
    _, buffer = cv2.imencode(".jpg", cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
    img_base64 = base64.b64encode(buffer).decode()

    html_code = f"""
        <link rel="stylesheet"
              href="https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/openseadragon.min.css" />

        <style>
            /* Fondo general elegante */
            body {{
                background-color: #1e1e1e;
                color: #eee;
                font-family: 'Segoe UI', sans-serif;
            }}

            /* Contenedor del visor */
            #viewer-container {{
                width: 100%;
                height: 700px;
                background: #111;
                border-radius: 14px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,0,0,0.4);
                position: relative;
                border: 1px solid #333;
            }}

            /* Barra superior */
            #viewer-header {{
                padding: 10px 16px;
                background: #222;
                border-bottom: 1px solid #333;
                color: #eee;
                font-size: 18px;
                font-weight: 500;
            }}

            /* Ajustar estilos de openseadragon */
            .openseadragon-canvas {{
                background-color: #000 !important;
            }}
        </style>

        <div id="viewer-container">
            <div id="openseadragon" style="width: 100%; height: 640px;"></div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/openseadragon.min.js"></script>

        <script type="text/javascript">
            var viewer = OpenSeadragon({{
                id: "openseadragon",
                prefixUrl: "https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/images/",
                tileSources: {{
                    type: "image",
                    url: "data:image/jpeg;base64,{img_base64}"
                }},
                showNavigator: true,
                navigatorPosition: "BOTTOM_LEFT",
                gestureSettingsMouse: {{
                    clickToZoom: false,
                    dblClickToZoom: true,
                    dragToPan: true,
                    scrollToZoom: true,
                    pinchToZoom: true
                }},
                animationTime: 0.8,
                blendTime: 0.3,
                zoomPerScroll: 1.2,
                maxZoomPixelRatio: 2
            }});
        </script>
    """

    st.components.v1.html(html_code, height=760, scrolling=False)

def draw_custom_boxes(image, boxes, class_list, selected_index=None):
    """
    Dibuja las cajas sobre la imagen manualmente.
    Escala automáticamente según el tamaño de la imagen.
    """
    img_draw = image.copy()
    h_img, w_img = img_draw.shape[:2]

    # Escala dinámica según el tamaño de la imagen
    scale = min(w_img, h_img) / 1000.0
    font_scale_base = max(0.25, min(0.4, scale * 0.6))
    thickness_base  = max(1, int(1.5 * scale))

    COLOR_DEFAULT   = (255, 0, 0)
    COLOR_HIGHLIGHT = (0, 255, 0)
    COLOR_DIMMED    = (180, 180, 180)

    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf    = float(box.conf[0])
        cls_id  = int(box.cls[0])
        label = f"{class_list[cls_id].replace('_', ' ')} {conf:.0%}"

        if selected_index is not None:
            if i == selected_index:
                color      = COLOR_HIGHLIGHT
                thickness  = thickness_base + 1
                font_scale = font_scale_base
            else:
                color      = COLOR_DIMMED
                thickness  = max(1, thickness_base - 1)
                font_scale = font_scale_base * 0.85
        else:
            color      = COLOR_DEFAULT
            thickness  = thickness_base
            font_scale = font_scale_base

        # Dibujar rectángulo
        cv2.rectangle(img_draw, (x1, y1), (x2, y2), color, thickness)

        # Calcular tamaño del texto para el fondo del label
        text_thickness = max(1, int(font_scale * 1.5))
        (tw, th), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_thickness
        )

        # Padding dinámico alrededor del texto
        pad = max(3, int(th * 0.4))
        label_h = th + pad * 2

        # Fondo del label (arriba del box si cabe, abajo si no)
        if y1 - label_h - baseline >= 0:
            bg_y1 = y1 - label_h - baseline
            bg_y2 = y1
            txt_y = y1 - baseline - pad
        else:
            bg_y1 = y2
            bg_y2 = y2 + label_h + baseline
            txt_y = y2 + th + pad

        cv2.rectangle(img_draw, (x1, bg_y1), (x1 + tw + pad * 2, bg_y2), color, -1)

        # Texto con contorno para legibilidad
        cv2.putText(img_draw, label,
                    (x1 + pad, txt_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                    (0, 0, 0), text_thickness + 1, cv2.LINE_AA)
        cv2.putText(img_draw, label,
                    (x1 + pad, txt_y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                    (255, 255, 255), text_thickness, cv2.LINE_AA)

    return img_draw

def create_pdf(image_rgb, detections, notes, filename, class_list, summary_counts):
    """
    Genera el PDF incluyendo ahora el resumen estadístico.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Reporte: {filename}", ln=True, align='C')
    pdf.ln(5)

    # Resumen de Conteos (NUEVO EN PDF)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Resumen de Hallazgos:", ln=True)
    pdf.set_font("Arial", size=10)
    if not summary_counts.empty:
        for label, count in summary_counts.items():
            pdf.cell(0, 6, f"- {label}: {count}", ln=True)
    else:
        pdf.cell(0, 6, "No se detectaron afecciones.", ln=True)
    pdf.ln(5)

    # Imagen
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        img_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        cv2.imwrite(tmp_file.name, img_bgr)
        pdf.image(tmp_file.name, x=10, y=None, w=190)
        temp_path = tmp_file.name
    os.remove(temp_path)
    pdf.ln(10)

    # Tabla detallada
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Detalle de Detecciones:", ln=True)
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 10, "Clase Predicha", border=1, fill=True)
    pdf.cell(95, 10, "Confianza de Predicción", border=1, fill=True, ln=True)
    pdf.set_font("Arial", size=10)
    
    if detections:
        for box in detections:
            cls_name = class_list[int(box.cls[0])]
            conf = float(box.conf[0])
            pdf.cell(95, 10, f"{cls_name}", border=1)
            pdf.cell(95, 10, f"{conf:.2%}", border=1, ln=True)
    else:
        pdf.cell(190, 10, "Sin detecciones", border=1, ln=True)

    pdf.ln(10)
    # Notas
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Notas del Especialista:", ln=True)
    pdf.set_font("Arial", size=10)
    if notes:
        for n in notes:
            pdf.multi_cell(0, 8, f"- {n}")
    else:
        pdf.cell(0, 8, "Sin notas registradas.", ln=True)
        
    return pdf.output(dest='S').encode('latin-1', 'replace')