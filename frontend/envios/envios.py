"""
frontend/envios/envios.py — Panel de Seguimiento de Envíos
"""

import datetime
import tkinter.messagebox as messagebox
import customtkinter as ctk
from frontend.theme import *
from frontend.components import (
    StyledTable, SearchBar, PrimaryButton, SecondaryButton,
    LabeledEntry, LabeledCombo, Divider, MetricCard,
)
from backend import envios as backend_envios, usuarios as backend_usuarios, db


CIUDADES = ["Medellín", "Bogotá", "Cali", "Pereira", "Bucaramanga", "Barranquilla"]


class EnviosPanel(ctk.CTkFrame):
    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0, **kwargs)
        self.main_window = main_window
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self._form_visible = False
        self._vendedores_idx = {}
        self._envios_rows = []
        self._build()
        self._load_from_backend()

    def _build(self):
        # ── Métricas ──────────────────────────────────────────────────────────
        metrics = ctk.CTkFrame(self, fg_color="transparent")
        metrics.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(18, 0))
        for i in range(3):
            metrics.grid_columnconfigure(i, weight=1)

        self.metric_hoy = MetricCard(metrics, "Envíos hoy", "—", "")
        self.metric_hoy.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.metric_transito = MetricCard(metrics, "En tránsito", "—", "")
        self.metric_transito.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.metric_pend = MetricCard(metrics, "Pendientes", "—", "")
        self.metric_pend.grid(row=0, column=2, sticky="ew")

        # ── Barra búsqueda ───────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=1, column=0, columnspan=2, sticky="ew", padx=24, pady=(14, 10))

        self.search = SearchBar(
            top,
            placeholder="Buscar por guía, cliente, ciudad...",
            btn_text="+ Nuevo envío",
            on_search=self._apply_filters,
            on_add=self._toggle_form,
        )
        self.search.pack(side="left")

        self.ciudad_filter = ctk.CTkComboBox(
            top,
            values=["Todas"] + CIUDADES,
            width=140, height=36,
            font=FONT_BODY,
            fg_color=COLOR_WHITE,
            border_color=COLOR_BORDER,
            corner_radius=BTN_CORNER,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.ciudad_filter.set("Todas")
        self.ciudad_filter.configure(command=lambda _v=None: self._apply_filters())
        self.ciudad_filter.pack(side="left", padx=(12, 0))

        # ── Tabla envíos ─────────────────────────────────────────────────────
        self.table = StyledTable(
            self,
            columns=[
                ("guia", "Guía", 80),
                ("fecha", "Fecha", 100),
                ("producto", "Producto", 170),
                ("destino", "Destino", 100),
                ("vendedor", "Vendedor", 110),
                ("estado", "Estado", 110),
            ],
            rows=[],
        )
        self.table.grid(row=2, column=0, sticky="nsew", padx=(24, 8), pady=(0, 20))
        self.table.tree.bind("<<TreeviewSelect>>", self._on_select)

        self.form_panel = self._build_form()

    def _build_form(self):
        panel = ctk.CTkFrame(self, fg_color=COLOR_WHITE, corner_radius=CORNER_R, border_width=1, border_color=COLOR_BORDER, width=280)
        panel.grid_propagate(False)

        inner = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_fg_color=COLOR_CARD_ALT,
            scrollbar_button_color=COLOR_BORDER_DARK,
            scrollbar_button_hover_color=COLOR_TEXT_MUTED,
        )
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        ctk.CTkLabel(inner, text="Nuevo envío", font=FONT_HEADING, text_color=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 14))
        Divider(inner).pack(fill="x", pady=(0, 14))

        self.f_guia = LabeledEntry(inner, "Nº Guía", placeholder="GU-YYYY-####")
        self.f_guia.pack(fill="x", pady=(0, 10))

        self.f_producto = LabeledEntry(inner, "Producto", placeholder="Chaqueta beige L")
        self.f_producto.pack(fill="x", pady=(0, 10))

        row1 = ctk.CTkFrame(inner, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)
        self.f_cliente = LabeledEntry(row1, "Cliente", placeholder="Juan Pérez")
        self.f_cliente.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.f_destino = LabeledCombo(row1, "Destino", values=CIUDADES)
        self.f_destino.grid(row=0, column=1, sticky="ew")

        self.f_vendedor = LabeledCombo(inner, "Vendedor", values=[])
        self.f_vendedor.pack(fill="x", pady=(0, 10))

        self.f_direccion = ctk.CTkTextbox(inner, height=60, font=FONT_BODY, fg_color=COLOR_WHITE, border_color=COLOR_BORDER, border_width=1, corner_radius=BTN_CORNER)
        self.f_direccion.pack(fill="x", pady=(0, 16))
        self.f_direccion.insert("0.0", "Dirección completa de entrega...")

        Divider(inner).pack(fill="x", pady=(0, 14))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")
        PrimaryButton(btn_row, "Registrar envío", command=self._on_save, width=160).pack(side="left", padx=(0, 8))
        SecondaryButton(btn_row, "Cancelar", command=self._toggle_form, width=90).pack(side="left")

        return panel

    def _toggle_form(self):
        if self._form_visible:
            self.form_panel.grid_remove()
            self._form_visible = False
        else:
            self._load_from_backend()
            self.form_panel.grid(row=2, column=1, sticky="nsew", padx=(0, 24), pady=(0, 20))
            self._form_visible = True

    def _on_select(self, _event=None):
        pass  # Detalle envío futuro

    def _on_save(self):
        if not db.is_available():
            messagebox.showerror("Error", "404 — Backend / base de datos no disponible.")
            return

        guia = self.f_guia.get().strip()
        producto = self.f_producto.get().strip()
        cliente = self.f_cliente.get().strip()
        destino = self.f_destino.get().strip()
        vendedor_nombre = self.f_vendedor.get().strip()
        direccion = self.f_direccion.get("0.0", "end").strip()

        if not all([guia, producto, cliente, destino, vendedor_nombre, direccion]):
            messagebox.showerror("Error", "Completa todos los campos del formulario de envío.")
            return

        vendedor_id = self._vendedores_idx.get(vendedor_nombre)
        if not vendedor_id:
            messagebox.showerror("Error", "No se pudo resolver el vendedor en la base de datos.")
            return

        data = {
            "guia": guia,
            "producto_descripcion": producto,
            "cliente": cliente,
            "ciudad_destino": destino,
            "direccion": direccion,
            "vendedor_id": vendedor_id,
        }

        try:
            backend_envios.registrar_envio(data)
            self._load_from_backend()
            self._toggle_form()
        except Exception as exc:
            messagebox.showerror("Error", f"No se pudo registrar el envío.\n{exc}")

    # ── Backend helpers ─────────────────────────────────────────────────────────
    def _load_from_backend(self):
        if not db.is_available():
            self.table.load_rows([])
            self.metric_hoy.set(value="—", sub="404 backend no disponible")
            self.metric_transito.set(value="—", sub="")
            self.metric_pend.set(value="—", sub="")
            return

        try:
            rows = backend_envios.listar_envios()
        except Exception:
            self.table.load_rows([])
            self.metric_hoy.set(value="—", sub="Error consultando envíos")
            self.metric_transito.set(value="—", sub="")
            self.metric_pend.set(value="—", sub="")
        else:
            self._envios_rows = rows
            tabla_rows = []
            for e in rows:
                tabla_rows.append(
                    (
                        e["guia"],
                        e["fecha"].strftime("%d/%m/%Y") if hasattr(e["fecha"], "strftime") else str(e["fecha"]),
                        e["producto_descripcion"],
                        e["ciudad_destino"],
                        e.get("vendedor", ""),
                        e.get("estado", "").replace("_", " ").title(),
                    )
                )
            self.table.load_rows(tabla_rows)

            # Métricas
            today = datetime.date.today()
            env_hoy = 0
            transito = 0
            pendientes = 0
            for e in rows:
                if e.get("estado") == "EN_TRANSITO":
                    transito += 1
                if e.get("estado") == "PENDIENTE":
                    pendientes += 1
                fecha = e.get("fecha")
                if hasattr(fecha, "date") and fecha.date() == today:
                    env_hoy += 1
            self.metric_hoy.set(value=str(env_hoy), sub="Hoy")
            self.metric_transito.set(value=str(transito), sub="Activos")
            self.metric_pend.set(value=str(pendientes), sub="Prioridad")

        # Vendedores (no admins)
        try:
            usuarios = backend_usuarios.listar_usuarios()
        except Exception:
            return

        self._vendedores_idx = {
            u["nombre"]: u["id"] for u in usuarios if u["rol"].upper() != "ADMIN"
        }
        if self._vendedores_idx:
            if self.f_vendedor.get() not in self._vendedores_idx:
                self.f_vendedor.set(next(iter(self._vendedores_idx.keys())))
            self.f_vendedor.combo.configure(values=list(self._vendedores_idx.keys()))

        self._apply_filters()

    def _apply_filters(self):
        """
        Filtra la tabla usando búsqueda + filtro de ciudad (sin reconsultar MySQL).
        """
        if not self._envios_rows:
            return

        q = (self.search.get() or "").strip().lower()
        ciudad = (self.ciudad_filter.get() or "Todas").strip()

        filtered = []
        for e in self._envios_rows:
            if ciudad != "Todas" and e.get("ciudad_destino") != ciudad:
                continue
            haystack = " ".join(
                [
                    str(e.get("guia", "")),
                    str(e.get("cliente", "")),
                    str(e.get("ciudad_destino", "")),
                    str(e.get("producto_descripcion", "")),
                    str(e.get("vendedor", "")),
                    str(e.get("estado", "")),
                ]
            ).lower()
            if q and q not in haystack:
                continue
            filtered.append(e)

        tabla_rows = []
        for e in filtered:
            tabla_rows.append(
                (
                    e["guia"],
                    e["fecha"].strftime("%d/%m/%Y") if hasattr(e["fecha"], "strftime") else str(e["fecha"]),
                    e["producto_descripcion"],
                    e["ciudad_destino"],
                    e.get("vendedor", ""),
                    e.get("estado", "").replace("_", " ").title(),
                )
            )
        self.table.load_rows(tabla_rows)


