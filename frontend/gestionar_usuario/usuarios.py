"""
frontend/gestionar_usuario/usuarios.py — Panel de Administración de Usuarios
"""

import customtkinter as ctk
from frontend.theme import *
from frontend.components import (
    StyledTable, PrimaryButton, SecondaryButton, DangerButton,
    LabeledEntry, LabeledCombo, Divider, Badge,
)


DEMO_USUARIOS = [
("U-001", "Ana García",    "agarcia",    "Administrador",    "Activo",   "15/03/2026"),
("U-002", "Valentina R.",  "vrodriguez", "Almacén", "Activo",   "12/03/2026"),
("U-003", "Carlos M.",     "cmorales",   "Almacén", "Activo",   "10/03/2026"),
("U-004", "Pedro S.",      "psanchez",   "Almacén",  "Activo",   "08/03/2026"),
("U-005", "Lucía F.",      "lfuentes",   "Almacén", "Inactivo", "01/02/2026"),
]

ROLES = ["Administrador", "Almacén"]


class UsuariosPanel(ctk.CTkFrame):
    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0, **kwargs)
        self.main_window = main_window
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self._form_visible = False
        self._editing_id   = None
        self._build()

    def _build(self):
        # ── Barra superior ─────────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2,
                 sticky="ew", padx=24, pady=(18, 10))

        self.search_entry = ctk.CTkEntry(
            top,
            placeholder_text="Buscar por nombre, usuario o rol...",
            font=FONT_BODY,
            height=38, width=340,
            fg_color=COLOR_WHITE,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=BTN_CORNER,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.search_entry.pack(side="left", padx=(0, 8))

        SecondaryButton(top, "Buscar", width=90).pack(side="left", padx=(0, 8))

        self.rol_filter = ctk.CTkComboBox(
            top,
            values=["Todos los roles"] + ROLES,
            width=160, height=38,
            font=FONT_BODY,
            fg_color=COLOR_WHITE,
            border_color=COLOR_BORDER,
            corner_radius=BTN_CORNER,
            text_color=COLOR_TEXT_PRIMARY,
        )
        self.rol_filter.set("Todos los roles")
        self.rol_filter.pack(side="left", padx=(0, 12))

        PrimaryButton(top, "+ Nuevo usuario",
                      command=self._new_user, width=150).pack(side="left")

        # ── Tabla de usuarios ──────────────────────────────────────────────────
        self.table = StyledTable(
            self,
            columns=[
                ("id",      "ID",          65),
                ("nombre",  "Nombre",     160),
                ("usuario", "Usuario",    120),
                ("rol",     "Rol",         95),
                ("estado",  "Estado",      95),
                ("ultimo",  "Último acceso", 115),
            ],
            rows=DEMO_USUARIOS,
        )
        self.table.grid(row=1, column=0, sticky="nsew",
                        padx=(24, 8), pady=(0, 20))
        self.table.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Panel de formulario ────────────────────────────────────────────────
        self.form_panel = self._build_form()

    def _build_form(self):
        panel = ctk.CTkFrame(
            self,
            fg_color=COLOR_WHITE,
            corner_radius=CORNER_R,
            border_width=1,
            border_color=COLOR_BORDER,
            width=280,
        )
        panel.grid_propagate(False)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=18)

        self.form_title = ctk.CTkLabel(
            inner, text="Nuevo usuario",
            font=FONT_HEADING, text_color=COLOR_TEXT_PRIMARY,
        )
        self.form_title.pack(anchor="w", pady=(0, 14))
        Divider(inner).pack(fill="x", pady=(0, 14))

        self.f_nombre  = LabeledEntry(inner, "Nombre completo",
                                      placeholder="Nombre Apellido")
        self.f_nombre.pack(fill="x", pady=(0, 10))

        self.f_usuario = LabeledEntry(inner, "Nombre de usuario",
                                      placeholder="usuario123")
        self.f_usuario.pack(fill="x", pady=(0, 10))

        self.f_password = LabeledEntry(inner, "Contraseña",
                                       placeholder="Mínimo 6 caracteres", show="•")
        self.f_password.pack(fill="x", pady=(0, 10))

        self.f_confirm  = LabeledEntry(inner, "Confirmar contraseña",
                                       placeholder="Repetir contraseña", show="•")
        self.f_confirm.pack(fill="x", pady=(0, 10))

        self.f_rol     = LabeledCombo(inner, "Rol del usuario", values=ROLES)
        self.f_rol.pack(fill="x", pady=(0, 10))

        self.f_estado  = LabeledCombo(inner, "Estado",
                                      values=["Activo", "Inactivo"])
        self.f_estado.pack(fill="x", pady=(0, 16))

        # Permisos rápidos
        perms_label = ctk.CTkLabel(inner, text="Permisos",
                                   font=FONT_SMALL, text_color=COLOR_TEXT_SECONDARY)
        perms_label.pack(anchor="w", pady=(0, 6))

        perm_frame = ctk.CTkFrame(inner, fg_color=COLOR_CARD_ALT,
                                  corner_radius=8)
        perm_frame.pack(fill="x", pady=(0, 16))

        self.perm_vars = {}
        perms = [
            ("ver_inventario",  "Ver inventario"),
            ("editar_inv",      "Editar inventario"),
            ("registrar_venta", "Registrar ventas"),
            ("gestionar_env",   "Gestionar envíos"),
            ("admin_usuarios",  "Administrar usuarios"),
        ]
        for key, label in perms:
            var = ctk.BooleanVar(value=True)
            self.perm_vars[key] = var
            ctk.CTkCheckBox(
                perm_frame, text=label,
                variable=var, font=FONT_SMALL,
                text_color=COLOR_TEXT_PRIMARY,
                fg_color=COLOR_ACCENT,
                hover_color=COLOR_ACCENT_DARK,
                border_color=COLOR_BORDER_DARK,
            ).pack(anchor="w", padx=12, pady=4)

        Divider(inner).pack(fill="x", pady=(0, 14))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")
        PrimaryButton(btn_row, "Guardar", command=self._on_save,
                      width=120).pack(side="left", padx=(0, 8))
        SecondaryButton(btn_row, "Cancelar", command=self._close_form,
                        width=90).pack(side="left")

        self.delete_btn = DangerButton(inner, "Eliminar usuario",
                                       command=self._on_delete, width=999)
        self.delete_btn.pack(fill="x", pady=(10, 0))
        self.delete_btn.pack_forget()

        return panel

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _new_user(self):
        self._editing_id = None
        self._clear_form()
        self.form_title.configure(text="Nuevo usuario")
        self.delete_btn.pack_forget()
        if not self._form_visible:
            self._open_form()

    def _on_select(self, _event=None):
        data = self.table.get_selected()
        if not data:
            return
        uid, nombre, usuario, rol, estado, _ = data
        self._editing_id = uid
        self.form_title.configure(text=f"Editar — {usuario}")
        self.f_nombre.set(nombre)
        self.f_usuario.set(usuario)
        self.f_rol.set(rol)
        self.f_estado.set(estado)
        self.f_password.clear()
        self.f_confirm.clear()
        self.delete_btn.pack(fill="x", pady=(10, 0))
        if not self._form_visible:
            self._open_form()

    def _open_form(self):
        self.form_panel.grid(row=1, column=1, sticky="nsew",
                             padx=(0, 24), pady=(0, 20))
        self._form_visible = True

    def _close_form(self):
        self.form_panel.grid_remove()
        self._form_visible = False
        self._clear_form()

    def _clear_form(self):
        for field in [self.f_nombre, self.f_usuario, self.f_password, self.f_confirm]:
            field.clear()
        self.f_rol.set(ROLES[0])
        self.f_estado.set("Activo")

    def _on_save(self):
        """
        TODO: backend.usuarios.crear_usuario() / actualizar_usuario()
        nombre   = self.f_nombre.get()
        usuario  = self.f_usuario.get()
        password = self.f_password.get()
        rol      = self.f_rol.get()
        estado   = self.f_estado.get()
        permisos = {k: v.get() for k, v in self.perm_vars.items()}
        """
        pass

    def _on_delete(self):
        """
        TODO: backend.usuarios.eliminar_usuario(self._editing_id)
        """
        pass