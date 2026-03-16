"""
frontend/dashboard/dashboard.py — Panel de Dashboard principal
"""

import customtkinter as ctk
from frontend.theme import *
from frontend.components import MetricCard, StyledTable, AlertBanner, Divider


# Datos de demostración (se reemplazarán con consultas MySQL)
DEMO_METRICAS = [
    ("Productos totales",   "248",    "+12 este mes",      COLOR_SUCCESS),
    ("Ventas hoy",          "$1,340", "8 transacciones",   COLOR_TEXT_MUTED),
    ("Envíos activos",      "14",     "3 en tránsito",     COLOR_INFO),
    ("Stock crítico",       "2",      "requieren reposición", COLOR_WARNING),
]

DEMO_VENTAS = [
    ("Blusa floral",   "M",  "2", "$80",   "Completada",  "Valentina R."),
    ("Jean skinny",    "28", "1", "$65",   "Completada",  "Carlos M."),
    ("Chaqueta beige", "L",  "1", "$120",  "Enviando",    "Valentina R."),
    ("Camiseta básica","S",  "3", "$45",   "Completada",  "Carlos M."),
    ("Blusa flores",   "XS", "1", "$38",   "Completada",  "Valentina R."),
]

DEMO_ENVIOS = [
    ("GU-2024", "Laura P.",  "Chaqueta beige L", "Medellín", "En tránsito"),
    ("GU-2023", "Sofía M.",  "Jean skinny 28",   "Cali",     "Entregado"),
    ("GU-2022", "Andrea L.", "Blusa floral M",   "Bogotá",   "Entregado"),
    ("GU-2021", "Camila F.", "Camiseta S ×2",    "Pereira",  "Pendiente"),
]

DEMO_ALERTAS = [
    ("warning", "Jean slim T.30 — solo 2 unidades (mínimo: 5)"),
    ("danger",  "Blusa flores T.S — solo 1 unidad (mínimo: 5)"),
]


class DashboardPanel(ctk.CTkFrame):
    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0, **kwargs)
        self.main_window = main_window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._build()

    def _build(self):
        # ── Cabecera ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 0))
        ctk.CTkLabel(
            header, text="Buenos días, Admin",
            font=FONT_TITLE, text_color=COLOR_TEXT_PRIMARY,
        ).pack(side="left")
        ctk.CTkLabel(
            header, text="Domingo 15 de marzo, 2026",
            font=FONT_SMALL, text_color=COLOR_TEXT_MUTED,
        ).pack(side="right", pady=(6, 0))

        # ── Tarjetas de métricas ─────────────────────────────────────────────────
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.grid(row=1, column=0, sticky="ew", padx=24, pady=(16, 0))
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)

        for i, (label, value, sub, sub_color) in enumerate(DEMO_METRICAS):
            MetricCard(
                metrics_frame, label=label, value=value,
                sub=sub, sub_color=sub_color,
            ).grid(row=0, column=i, sticky="ew",
                   padx=(0, 10) if i < 3 else (0, 0), pady=0)

        # ── Fila inferior: tablas + alertas ────────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=24, pady=16)
        bottom.grid_columnconfigure(0, weight=3)
        bottom.grid_columnconfigure(1, weight=2)
        bottom.grid_columnconfigure(2, weight=2)
        bottom.grid_rowconfigure(1, weight=1)

        # Ventas recientes
        ctk.CTkLabel(
            bottom, text="Últimas ventas",
            font=FONT_SUBHEAD, text_color=COLOR_TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        ventas_table = StyledTable(
            bottom,
            columns=[
                ("producto", "Producto",  140),
                ("talla",    "Talla",      55),
                ("qty",      "Qty",        45),
                ("total",    "Total",      65),
                ("estado",   "Estado",    100),
                ("vendedor", "Vendedor",  110),
            ],
            rows=DEMO_VENTAS,
        )
        ventas_table.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        # Envíos activos
        ctk.CTkLabel(
            bottom, text="Envíos activos",
            font=FONT_SUBHEAD, text_color=COLOR_TEXT_PRIMARY,
        ).grid(row=0, column=1, sticky="w", pady=(0, 6))

        envios_table = StyledTable(
            bottom,
            columns=[
                ("guia",    "Guía",      70),
                ("cliente", "Cliente",   90),
                ("ciudad",  "Ciudad",    80),
                ("estado",  "Estado",    95),
            ],
            rows=[(r[0], r[1], r[3], r[4]) for r in DEMO_ENVIOS],
        )
        envios_table.grid(row=1, column=1, sticky="nsew", padx=(0, 12))

        # Alertas de stock
        ctk.CTkLabel(
            bottom, text="Alertas de stock",
            font=FONT_SUBHEAD, text_color=COLOR_TEXT_PRIMARY,
        ).grid(row=0, column=2, sticky="w", pady=(0, 6))

        alerts_frame = ctk.CTkFrame(bottom, fg_color="transparent")
        alerts_frame.grid(row=1, column=2, sticky="nsew")

        for level, msg in DEMO_ALERTAS:
            AlertBanner(alerts_frame, msg, level=level).pack(
                fill="x", pady=(0, 8),
            )

        # Botón ir a inventario
        ctk.CTkButton(
            alerts_frame,
            text="Ver inventario completo →",
            font=FONT_SMALL,
            width=180, height=32,
            fg_color="transparent",
            hover_color=COLOR_CARD_ALT,
            text_color=COLOR_ACCENT,
            border_color=COLOR_ACCENT,
            border_width=1,
            corner_radius=BTN_CORNER,
            command=lambda: self.main_window._navigate("inventario")
                    if self.main_window else None,
        ).pack(anchor="w", pady=(4, 0))