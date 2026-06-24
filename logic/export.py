# logic/export.py — Styled PDF export for EspressoLab using ReportLab

from datetime import datetime
from pathlib import Path
from typing import List, Optional
import io

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm, cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak, Image as RLImage, KeepTogether
    )
    from reportlab.graphics.shapes import Drawing, Circle, Rect, String as GString
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# --- Brand Colors (ReportLab HexColor) ---
def hc(hex_str: str):
    if REPORTLAB_AVAILABLE:
        return colors.HexColor(hex_str)
    return None

C_BG       = "#0D0D0D"
C_CARD     = "#1E1E1E"
C_ACCENT   = "#C8873A"
C_TEXT     = "#F0EDE8"
C_MUTED    = "#7A7570"
C_SUCCESS  = "#4CAF6E"
C_WARNING  = "#E8A838"
C_DANGER   = "#E05C5C"
C_BORDER   = "#2A2A2A"


def _number_pages(canvas, doc):
    """Draw page number, footer, and dark background."""
    canvas.saveState()
    
    # Draw dark background for the entire page
    if REPORTLAB_AVAILABLE:
        canvas.setFillColor(hc(C_BG))
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        
    canvas.setFillColor(hc(C_MUTED))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(
        A4[0] - 20*mm, 12*mm,
        f"EspressoLab • Página {doc.page}"
    )
    canvas.drawString(20*mm, 12*mm, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    canvas.restoreState()


def export_bean_report(
    bean,
    extractions: list,
    output_path: str,
) -> str:
    """
    Export a styled PDF report for a single bean and its extractions.
    Returns the output path.
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab is not installed. Run: pip install reportlab")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=25*mm,
    )

    styles = getSampleStyleSheet()

    # --- Custom Styles ---
    s_title = ParagraphStyle(
        "Title", fontName="Helvetica-Bold", fontSize=28,
        textColor=hc(C_ACCENT), spaceAfter=8, leading=34,
    )
    s_subtitle = ParagraphStyle(
        "Subtitle", fontName="Helvetica", fontSize=13,
        textColor=hc(C_TEXT), spaceAfter=12, leading=18,
    )
    s_section = ParagraphStyle(
        "Section", fontName="Helvetica-Bold", fontSize=11,
        textColor=hc(C_ACCENT), spaceBefore=14, spaceAfter=6,
    )
    s_body = ParagraphStyle(
        "Body", fontName="Helvetica", fontSize=9,
        textColor=hc(C_TEXT), spaceAfter=3, leading=13,
    )
    s_muted = ParagraphStyle(
        "Muted", fontName="Helvetica", fontSize=8,
        textColor=hc(C_MUTED), spaceAfter=2,
    )
    s_center = ParagraphStyle(
        "Center", fontName="Helvetica", fontSize=9,
        textColor=hc(C_TEXT), alignment=TA_CENTER,
    )
    s_score = ParagraphStyle(
        "Score", fontName="Helvetica-Bold", fontSize=32,
        textColor=hc(C_ACCENT), alignment=TA_CENTER,
    )

    story = []

    # ── COVER SECTION ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 10*mm))

    # Header bar (simulated with a table)
    header_data = [[
        Paragraph("☕ EspressoLab", ParagraphStyle(
            "logo", fontName="Helvetica-Bold", fontSize=10,
            textColor=hc(C_MUTED)
        )),
        Paragraph("Reporte de Café / Bean Report", ParagraphStyle(
            "type", fontName="Helvetica", fontSize=10,
            textColor=hc(C_MUTED), alignment=TA_RIGHT
        )),
    ]]
    header_tbl = Table(header_data, colWidths=["50%", "50%"])
    header_tbl.setStyle(TableStyle([
        ("TEXTCOLOR", (0,0), (-1,-1), hc(C_MUTED)),
        ("LINEBELOW", (0,0), (-1,0), 0.5, hc(C_BORDER)),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 8*mm))

    # Bean title
    story.append(Paragraph(f"{bean.name}", s_title))
    story.append(Paragraph(f"por {bean.roaster}", s_subtitle))
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=hc(C_BORDER)))
    story.append(Spacer(1, 6*mm))

    # Bean detail cards (2-col table)
    def info_row(label, value):
        return [
            Paragraph(label, s_muted),
            Paragraph(str(value) if value else "—", s_body),
        ]

    origin = " / ".join(filter(None, [bean.origin_country, bean.origin_region, bean.origin_farm]))
    bean_info = [
        info_row("Origen / Origin", origin or "—"),
        info_row("Variedad / Variety", bean.variety),
        info_row("Proceso / Process", bean.process),
        info_row("Altura / Altitude", f"{bean.altitude_masl} msnm" if bean.altitude_masl else "—"),
        info_row("Extracciones Registradas", str(len(extractions))),
    ]
    info_table = Table(bean_info, colWidths=[60*mm, None])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), hc(C_CARD)),
        ("BACKGROUND", (1,0), (1,-1), hc("#111111")),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [hc(C_CARD), hc("#1A1A1A")]),
        ("TEXTCOLOR", (0,0), (-1,-1), hc(C_TEXT)),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8*mm))

    # ── EXTRACTIONS SECTION ────────────────────────────────────────────────────
    if extractions:
        story.append(Paragraph("Bitácora de Extracciones / Extraction Log", s_section))
        story.append(HRFlowable(width="100%", thickness=0.5, color=hc(C_BORDER)))
        story.append(Spacer(1, 4*mm))

        # Best shot highlight
        locked = [e for e in extractions if e.is_locked]
        if locked:
            best = max(locked, key=lambda e: e.score)
            best_data = [[
                Paragraph("★ RECETA ÓPTIMA / OPTIMAL RECIPE", ParagraphStyle(
                    "best_h", fontName="Helvetica-Bold", fontSize=9,
                    textColor=hc(C_ACCENT)
                )),
                Paragraph(
                    f"Dosis: <b>{best.dose_in}g</b> → <b>{best.yield_out}g</b> | "
                    f"Ratio: <b>{best.ratio_str}</b> | Tiempo: <b>{best.extraction_time}s</b> | "
                    f"Score: <b>{best.score}/10</b>",
                    ParagraphStyle("best_d", fontName="Helvetica", fontSize=9,
                                   textColor=hc(C_TEXT))
                ),
            ]]
            best_tbl = Table(best_data, colWidths=[60*mm, None])
            best_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), hc("#1E1500")),
                ("LINEAFTER",  (0,0), (0,-1), 1.5, hc(C_ACCENT)),
                ("LINEBEFORE", (0,0), (0,-1), 3, hc(C_ACCENT)),
                ("TOPPADDING", (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ]))
            story.append(best_tbl)
            story.append(Spacer(1, 6*mm))

        # Extraction log table
        col_headers = ["Fecha", "Dosis→Yield", "Ratio", "Tiempo", "Temp", "Molida", "Score", "★"]
        table_data = [col_headers]
        for ext in sorted(extractions, key=lambda e: e.timestamp, reverse=True):
            table_data.append([
                ext.timestamp.strftime("%d/%m/%y"),
                f"{ext.dose_in}g→{ext.yield_out}g",
                ext.ratio_str,
                f"{ext.extraction_time}s",
                f"{ext.water_temp}°C",
                ext.grind_size or "—",
                f"{ext.score:.1f}",
                "★" if ext.is_locked else "",
            ])

        ext_table = Table(table_data, repeatRows=1)
        ext_table.setStyle(TableStyle([
            # Header
            ("BACKGROUND",    (0,0), (-1,0), hc(C_ACCENT)),
            ("TEXTCOLOR",     (0,0), (-1,0), hc("#000000")),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            # Rows
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [hc(C_CARD), hc("#1A1A1A")]),
            ("TEXTCOLOR",     (0,1), (-1,-1), hc(C_TEXT)),
            ("GRID",          (0,0), (-1,-1), 0.3, hc(C_BORDER)),
        ]))
        story.append(ext_table)
        story.append(Spacer(1, 8*mm))

        # Sensory summary (average of all shots)
        if len(extractions) >= 2:
            story.append(Paragraph("Perfil Sensorial Promedio / Avg Sensory Profile", s_section))
            avg_acid   = sum(e.acidity    for e in extractions) / len(extractions)
            avg_sweet  = sum(e.sweetness  for e in extractions) / len(extractions)
            avg_body   = sum(e.body       for e in extractions) / len(extractions)
            avg_bitter = sum(e.bitterness for e in extractions) / len(extractions)
            avg_score  = sum(e.score      for e in extractions) / len(extractions)

            sensory_data = [
                ["Acidez/Acidity", "Dulzor/Sweetness", "Cuerpo/Body", "Amargor/Bitterness", "Score Prom."],
                [f"{avg_acid:.1f}/10", f"{avg_sweet:.1f}/10", f"{avg_body:.1f}/10",
                 f"{avg_bitter:.1f}/10", f"{avg_score:.1f}/10"],
            ]
            sensory_tbl = Table(sensory_data, colWidths=["20%","20%","20%","20%","20%"])
            sensory_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,0), hc(C_CARD)),
                ("TEXTCOLOR",     (0,0), (-1,0), hc(C_MUTED)),
                ("FONTNAME",      (0,0), (-1,0), "Helvetica"),
                ("FONTSIZE",      (0,0), (-1,-1), 8),
                ("ALIGN",         (0,0), (-1,-1), "CENTER"),
                ("BACKGROUND",    (0,1), (-1,1), hc("#111111")),
                ("TEXTCOLOR",     (0,1), (-1,1), hc(C_ACCENT)),
                ("FONTNAME",      (0,1), (-1,1), "Helvetica-Bold"),
                ("FONTSIZE",      (0,1), (-1,1), 13),
                ("TOPPADDING",    (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ("GRID",          (0,0), (-1,-1), 0.3, hc(C_BORDER)),
            ]))
            story.append(sensory_tbl)

    story.append(Spacer(1, 10*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=hc(C_BORDER)))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Exportado con EspressoLab — Professional Coffee Tracking",
        ParagraphStyle("footer", fontName="Helvetica", fontSize=7,
                       textColor=hc(C_MUTED), alignment=TA_CENTER)
    ))

    doc.build(story, onFirstPage=_number_pages, onLaterPages=_number_pages)
    return output_path
