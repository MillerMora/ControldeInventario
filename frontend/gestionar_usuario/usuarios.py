"""
frontend/gestionar_usuario/usuarios.py — Panel de Administración de Usuarios
"""

import tkinter.messagebox as messagebox
import customtkinter as ctk
from frontend.theme import *
from frontend.components import (
    StyledTable, PrimaryButton, SecondaryButton, DangerButton,
    LabeledEntry, LabeledCombo, Divider, Badge,
)
from backend import usuarios as backend_usuarios, db


ROLES = ["ADMIN", "EMPLEADO"]


class UsuariosPanel(ctk.CTkFrame):
    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, corner_radius=0, **kwargs)
        self.main_window = main_window
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self._form_visible = False
        self._editing_id   = None
        self._usuarios_cache = []
        self._build()
        self._load_from_backend()

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

        SecondaryButton(top, "Buscar", width=90, command=self._apply_filters).pack(side="left", padx=(0, 8))

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
        self.rol_filter.configure(command=lambda _v=None: self._apply_filters())
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
            rows=[],
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

        inner = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_fg_color=COLOR_CARD_ALT,
            scrollbar_button_color=COLOR_BORDER_DARK,
            scrollbar_button_hover_color=COLOR_TEXT_MUTED,
        )
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
                                      values=["ACTIVO", "INACTIVO"])
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
        print("[UI usuarios] Selection event")
        data = self.table.get_selected()
        if not data:
            print("[UI] No row selected")
            return
        uid, nombre, usuario, rol, estado, _ = data
        self._editing_id = int(uid[2:]) if uid.startswith('U-') else uid  # Parse to int
        print(f"[UI usuarios] Selected ID: {self._editing_id} (raw: {uid})")
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
        self.f_estado.set("ACTIVO")

    def _on_save(self):
        print(f"[UI usuarios] Save clicked, editing_id={self._editing_id}")
        if not db.is_available():
            print("[UI] DB not available")
            messagebox.showerror("Error", "404 — Backend / base de datos no disponible.")
            return

        nombre = self.f_nombre.get().strip()
        usuario = self.f_usuario.get().strip()
        password = self.f_password.get().strip()
        confirm = self.f_confirm.get().strip()
        rol_nombre = self.f_rol.get().strip().upper()
        estado = self.f_estado.get().strip().upper()

        if not nombre or not usuario:
            messagebox.showerror("Error", "Nombre y usuario son obligatorios.")
            return

        if self._editing_id is None and not password:
            messagebox.showerror("Error", "La contraseña es obligatoria para nuevos usuarios.")
            return

        if password and password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return

        try:
            rol_id = backend_usuarios.obtener_rol_id_por_nombre(rol_nombre)
            print(f"[UI] Rol ID: {rol_id}")
        except Exception as exc:
            print(f"[UI ERROR rol] {exc}")
            messagebox.showerror("Error", f"No se pudo obtener el rol.\n{exc}")
            return

        if not rol_id:
            messagebox.showerror("Error", "Rol no encontrado en la base de datos.")
            return

        data = {
            "nombre": nombre,
            "usuario": usuario,
            "password": password or None,
            "rol_id": rol_id,
            "estado": estado,
        }

        try:
            if self._editing_id is None:
                backend_usuarios.crear_usuario(data)
                print("[UI] Created new user")
            else:
                backend_usuarios.actualizar_usuario(self._editing_id, data)
                print("[UI] Updated user")
            print("[UI] Backend success, reloading...")
            self._load_from_backend()
            print("[UI] Reload done, clearing selection")
            self.table.tree.selection_remove(self.table.tree.selection())
            self._close_form()
            self.after(200, self._apply_filters)
            print("[UI] UI updated")
        except Exception as exc:
            print(f"[UI ERROR save] {exc}")
            messagebox.showerror("Error", f"No se pudo guardar el usuario.\n{exc}")

    def _on_delete(self):
        print(f"[UI usuarios] Delete clicked, id={self._editing_id}")
        if self._editing_id is None:
            print("[UI] No ID for delete")
            return
        if not db.is_available():
            print("[UI] DB not available")
            messagebox.showerror("Error", "404 — Backend / base de datos no disponible.")
            return
        try:
            backend_usuarios.eliminar_usuario(self._editing_id)
            print("[UI] Backend delete success")
            self._editing_id = None
            self._load_from_backend()
            print("[UI] Reload after delete")
            self.table.tree.selection_remove(self.table.tree.selection())
            self._close_form()
            self.after(200, self._apply_filters)
            print("[UI] Delete UI updated")
        except Exception as exc:
            print(f"[UI ERROR delete] {exc}")
            messagebox.showerror("Error", f"No se pudo eliminar el usuario.\n{exc}")

    # ── Backend helpers ─────────────────────────────────────────────────────────
    def _load_from_backend(self):
        print("[UI usuarios] _load_from_backend called")
        if not db.is_available():
            print("[UI] DB unavailable in load")
            self.table.load_rows([])
            return

        try:
            usuarios = backend_usuarios.listar_usuarios()
            print(f"[UI] Loaded {len(usuarios)} users from backend")
        except Exception as exc:
            print(f"[UI ERROR load] {exc}")
            self.table.load_rows([])
            return

        self._usuarios_cache = usuarios
        self._apply_filters()

    def _apply_filters(self):
        if not self._usuarios_cache:
            self.table.load_rows([])
            return

        q = (self.search_entry.get() or "").strip().lower()
        rol = (self.rol_filter.get() or "Todos los roles").strip().upper()

        filtered = []
        for u in self._usuarios_cache:
            if rol != "TODOS LOS ROLES" and u.get("rol", "").upper() != rol:
                continue
            haystack = " ".join(
                [
                    str(u.get("nombre", "")),
                    str(u.get("usuario", "")),
                    str(u.get("rol", "")),
                    str(u.get("estado", "")),
                ]
            ).lower()
            if q and q not in haystack:
                continue
            filtered.append(u)

        rows = []
        for u in filtered:
            rows.append(
                (
                    f"U-{u['id']:03d}",
                    u["nombre"],
                    u["usuario"],
                    u["rol"].capitalize(),
                    "Activo" if u["estado"].upper() == "ACTIVO" else "Inactivo",
                    "",
                )
            )
        print(f"[UI] Applying filters, {len(rows)} rows to table")
        self.table.load_rows(rows)

