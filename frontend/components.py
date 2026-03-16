"""
frontend/components.py — Componentes reutilizables de UI para Almacor
"""

import tkinter as tk
import customtkinter as ctk
from frontend.theme import *


# ══════════════════════════════════════════════════════════════════════════════
# BOTONES
# ══════════════════════════════════════════════════════════════════════════════

class PrimaryButton(ctk.CTkButton):
    """Botón principal dorado."""
    def __init__(self, parent, text, command=None, width=140, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=36,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_DARK,
            text_color=COLOR_WHITE,
            font=FONT_SUBHEAD,
            corner_radius=BTN_CORNER,
            **kwargs,
        )


class SecondaryButton(ctk.CTkButton):
    """Botón secundario con borde."""
    def __init__(self, parent, text, command=None, width=120, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=36,
            fg_color="transparent",
            hover_color=COLOR_CARD_ALT,
            text_color=COLOR_TEXT_PRIMARY,
            border_color=COLOR_BORDER_DARK,
            border_width=1,
            font=FONT_BODY,
            corner_radius=BTN_CORNER,
            **kwargs,
        )


class DangerButton(ctk.CTkButton):
    """Botón de acción destructiva."""
    def __init__(self, parent, text, command=None, width=120, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=36,
            fg_color=COLOR_DANGER_BG,
            hover_color="#FFCDD2",
            text_color=COLOR_DANGER,
            font=FONT_BODY,
            corner_radius=BTN_CORNER,
            **kwargs,
        )


# ══════════════════════════════════════════════════════════════════════════════
# CAMPOS DE FORMULARIO
# ══════════════════════════════════════════════════════════════════════════════

class LabeledEntry(ctk.CTkFrame):
    """Campo de texto con etiqueta superior."""
    def __init__(self, parent, label, placeholder="", show=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        ctk.CTkLabel(
            self, text=label, font=FONT_SMALL,
            text_color=COLOR_TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", pady=(0, 3))
        entry_kwargs = dict(
            placeholder_text=placeholder,
            font=FONT_BODY,
            height=36,
            fg_color=COLOR_WHITE,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=BTN_CORNER,
            text_color=COLOR_TEXT_PRIMARY,
        )
        if show:
            entry_kwargs["show"] = show
        self.entry = ctk.CTkEntry(self, **entry_kwargs)
        self.entry.pack(fill="x")

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

    def clear(self):
        self.entry.delete(0, "end")


class LabeledCombo(ctk.CTkFrame):
    """Combobox con etiqueta superior."""
    def __init__(self, parent, label, values=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        ctk.CTkLabel(
            self, text=label, font=FONT_SMALL,
            text_color=COLOR_TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", pady=(0, 3))
        self.combo = ctk.CTkComboBox(
            self,
            values=values or [],
            font=FONT_BODY,
            height=36,
            fg_color=COLOR_WHITE,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=BTN_CORNER,
            button_color=COLOR_BORDER_DARK,
            dropdown_fg_color=COLOR_WHITE,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.combo.pack(fill="x")

    def get(self):
        return self.combo.get()

    def set(self, value):
        self.combo.set(value)


# ══════════════════════════════════════════════════════════════════════════════
# TARJETA MÉTRICA (dashboard)
# ══════════════════════════════════════════════════════════════════════════════

class MetricCard(ctk.CTkFrame):
    """Tarjeta de métrica para el dashboard."""
    def __init__(self, parent, label, value, sub="", sub_color=None, **kwargs):
        super().__init__(
            parent,
            fg_color=COLOR_WHITE,
            corner_radius=CORNER_R,
            border_width=1,
            border_color=COLOR_BORDER,
            **kwargs,
        )
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=18, pady=14, fill="both", expand=True)

        self._label_lbl = ctk.CTkLabel(
            inner, text=label, font=FONT_SMALL,
            text_color=COLOR_TEXT_MUTED, anchor="w",
        )
        self._label_lbl.pack(anchor="w")

        self._value_lbl = ctk.CTkLabel(
            inner, text=value, font=(FONT_FAMILY, 26, "bold"),
            text_color=COLOR_TEXT_PRIMARY, anchor="w",
        )
        self._value_lbl.pack(anchor="w", pady=(2, 0))

        self._sub_lbl = ctk.CTkLabel(
            inner, text=sub or "", font=FONT_MICRO,
            text_color=sub_color or COLOR_TEXT_MUTED, anchor="w",
        )
        self._sub_lbl.pack(anchor="w", pady=(2, 0))

        if not sub:
            self._sub_lbl.pack_forget()

    def set(self, *, label=None, value=None, sub=None, sub_color=None):
        if label is not None:
            self._label_lbl.configure(text=label)
        if value is not None:
            self._value_lbl.configure(text=value)
        if sub is not None:
            if sub == "":
                self._sub_lbl.configure(text="")
                self._sub_lbl.pack_forget()
            else:
                self._sub_lbl.configure(text=sub)
                if not self._sub_lbl.winfo_ismapped():
                    self._sub_lbl.pack(anchor="w", pady=(2, 0))
        if sub_color is not None:
            self._sub_lbl.configure(text_color=sub_color)


# ══════════════════════════════════════════════════════════════════════════════
# TABLA PERSONALIZADA (tkinter Treeview estilizado)
# ══════════════════════════════════════════════════════════════════════════════

class StyledTable(ctk.CTkFrame):
    """
    Tabla con Treeview estilizado al tema Almacor.
    Parámetros:
        columns: list[tuple(id, encabezado, ancho)]
        rows:    list[tuple] — datos de ejemplo/placeholder
    """
    def __init__(self, parent, columns, rows=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_WHITE,
                         corner_radius=CORNER_R,
                         border_width=1, border_color=COLOR_BORDER, **kwargs)

        import tkinter.ttk as ttk

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Almacor.Treeview",
            background=COLOR_WHITE,
            foreground=COLOR_TEXT_PRIMARY,
            fieldbackground=COLOR_WHITE,
            rowheight=ROW_H,
            font=("Helvetica Neue", 12),
            borderwidth=0,
        )
        style.configure(
            "Almacor.Treeview.Heading",
            background=COLOR_CARD_ALT,
            foreground=COLOR_TEXT_SECONDARY,
            font=("Helvetica Neue", 11, "bold"),
            relief="flat",
            borderwidth=0,
        )
        style.map("Almacor.Treeview",
                  background=[("selected", COLOR_ACCENT_DARK)],
                  foreground=[("selected", COLOR_WHITE)])
        style.layout("Almacor.Treeview", [
            ("Almacor.Treeview.treearea", {"sticky": "nswe"})
        ])

        col_ids = [c[0] for c in columns]
        self.tree = ttk.Treeview(
            self,
            columns=col_ids,
            show="headings",
            style="Almacor.Treeview",
            selectmode="browse",
        )

        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor="w", stretch=False)

        # Scrollbar vertical
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        vsb.pack(side="right", fill="y", pady=8, padx=(0, 6))

        # Filas alternas
        self.tree.tag_configure("odd",  background=COLOR_WHITE)
        self.tree.tag_configure("even", background=COLOR_CARD_ALT)

        if rows:
            self.load_rows(rows)

    def load_rows(self, rows):
        self.clear()
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_selected(self):
        sel = self.tree.selection()
        if sel:
            return self.tree.item(sel[0], "values")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# BADGE DE ESTADO
# ══════════════════════════════════════════════════════════════════════════════

STATUS_COLORS = {
    "Disponible":  (COLOR_SUCCESS_BG, COLOR_SUCCESS),
    "Stock bajo":  (COLOR_WARNING_BG, COLOR_WARNING),
    "Crítico":     (COLOR_DANGER_BG,  COLOR_DANGER),
    "Activo":      (COLOR_SUCCESS_BG, COLOR_SUCCESS),
    "Inactivo":    (COLOR_DANGER_BG,  COLOR_DANGER),
    "Completada":  (COLOR_SUCCESS_BG, COLOR_SUCCESS),
    "Enviando":    (COLOR_INFO_BG,    COLOR_INFO),
    "En tránsito": (COLOR_INFO_BG,    COLOR_INFO),
    "Entregado":   (COLOR_SUCCESS_BG, COLOR_SUCCESS),
    "Pendiente":   (COLOR_WARNING_BG, COLOR_WARNING),
    "Cancelado":   (COLOR_DANGER_BG,  COLOR_DANGER),
    "Dueño":       ("#FCE4EC",        "#880E4F"),
    "Vendedor":    (COLOR_INFO_BG,    COLOR_INFO),
    "Almacén":     (COLOR_WARNING_BG, COLOR_WARNING),
}


class Badge(ctk.CTkLabel):
    """Etiqueta de estado con color semántico."""
    def __init__(self, parent, status, **kwargs):
        bg, fg = STATUS_COLORS.get(status, (COLOR_CARD_ALT, COLOR_TEXT_SECONDARY))
        super().__init__(
            parent,
            text=f"  {status}  ",
            font=FONT_MICRO,
            fg_color=bg,
            text_color=fg,
            corner_radius=12,
            **kwargs,
        )


# ══════════════════════════════════════════════════════════════════════════════
# ALERTA (banner)
# ══════════════════════════════════════════════════════════════════════════════

class AlertBanner(ctk.CTkFrame):
    """Banner de alerta de stock bajo u otros avisos."""
    def __init__(self, parent, message, level="warning", **kwargs):
        color_map = {
            "warning": (COLOR_WARNING_BG, COLOR_WARNING),
            "danger":  (COLOR_DANGER_BG,  COLOR_DANGER),
            "info":    (COLOR_INFO_BG,     COLOR_INFO),
            "success": (COLOR_SUCCESS_BG,  COLOR_SUCCESS),
        }
        bg, fg = color_map.get(level, color_map["info"])
        super().__init__(parent, fg_color=bg, corner_radius=8, **kwargs)
        ctk.CTkLabel(
            self, text=f"⚠  {message}", font=FONT_SMALL,
            text_color=fg, anchor="w",
        ).pack(padx=14, pady=8, anchor="w")


# ══════════════════════════════════════════════════════════════════════════════
# SEPARADOR
# ══════════════════════════════════════════════════════════════════════════════

class Divider(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("fg_color", COLOR_BORDER)
        super().__init__(parent, height=1, **kwargs)


# ══════════════════════════════════════════════════════════════════════════════
# BARRA DE BÚSQUEDA
# ══════════════════════════════════════════════════════════════════════════════

class SearchBar(ctk.CTkFrame):
    """Campo de búsqueda con icono y botón integrado."""
    def __init__(self, parent, placeholder="Buscar...", btn_text="+ Agregar",
                 on_search=None, on_add=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            font=FONT_BODY,
            height=38,
            width=340,
            fg_color=COLOR_WHITE,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=BTN_CORNER,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.entry.pack(side="left", padx=(0, 8))

        SecondaryButton(self, "Buscar", command=on_search, width=90).pack(side="left", padx=(0, 8))
        PrimaryButton(self, btn_text, command=on_add, width=130).pack(side="left")

    def get(self):
        return self.entry.get()