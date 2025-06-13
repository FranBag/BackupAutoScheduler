import tkinter as tk
from tkinter import ttk, messagebox, font
import re
import os
import datetime


class BackupGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Software de Backups - Dispositivos de Red")
        self.master.geometry("700x650")
        self.master.resizable(False, False)
        self.master.configure(bg="#404040")

        # Fuentes
        self.font_titulo = font.Font(family="Verdana", size=14, weight="bold")
        self.font_normal = font.Font(family="Verdana", size=10)
        self.font_boton = font.Font(family="Verdana", size=10, weight="bold")
        self.font_tabla_encabezado = font.Font(family="Verdana", size=10, weight="bold")
        self.font_tabla_contenido = font.Font(family="Verdana", size=9)

        self.fields = self.inicializar_campos()
        self.selected_id = None

        self.simulated_data = [
            {
                "Nombre": "Router Central",
                "IP": "192.168.1.1",
                "Usuario": "admin",
                "Contraseña": "admin123",
                "Puerto SSH": "22",
                "Hora": "08:00",
                "Periodicidad": "Diaria",
            },
            {
                "Nombre": "Switch Piso3",
                "IP": "192.168.1.2",
                "Usuario": "user",
                "Contraseña": "pass",
                "Puerto SSH": "22",
                "Hora": "12:00",
                "Periodicidad": "Semanal",
            },
        ]

        self.entry_widgets = {}
        self.construir_widgets()

    def inicializar_campos(self):
        return {
            "Nombre": tk.StringVar(),
            "IP": tk.StringVar(),
            "Usuario": tk.StringVar(),
            "Contraseña": tk.StringVar(),
            "Puerto SSH": tk.StringVar(value="22"),
            "Hora": tk.StringVar(value="08:00"),
            "Periodicidad": tk.StringVar(value="Diaria"),
        }

    def construir_widgets(self):
        self.construir_botones_superiores()
        self.construir_lista_dispositivos()
        self.construir_formulario_detalles()
        self.construir_botones_inferiores()

    def construir_botones_superiores(self):
        frame = tk.Frame(self.master, pady=10, bg="#404040")
        frame.pack()

        tk.Button(
            frame,
            text="Nuevo",
            width=12,
            command=self.habilitar_nuevo_dispositivo,
            bg="#BAE7E1",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            frame,
            text="Editar",
            width=12,
            command=self.editar_dispositivo,
            font=self.font_boton,
        ).grid(row=0, column=1, padx=5)

        tk.Button(
            frame,
            text="Eliminar",
            width=12,
            command=self.eliminar_dispositivo,
            bg="red",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=2, padx=5)

        tk.Button(
            frame,
            text="Gestionar Backup",
            width=16,
            font=self.font_boton,
            command=self.abrir_ventana_backups,
        ).grid(row=0, column=3, padx=5)

    def abrir_ventana_backups(self):
        ventana = tk.Toplevel(self.master)
        ventana.title("Historial de Backups")
        ventana.geometry("600x400")
        ventana.configure(bg="#404040")
        ventana.resizable(False, False)
        tk.Label(
            ventana,
            text="Lista de Backups Realizados",
            bg="#404040",
            fg="white",
            font=self.font_titulo,
        ).pack(pady=10)

        frame_tabla = tk.Frame(ventana, bg="#404040")
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar_y = ttk.Scrollbar(frame_tabla, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(frame_tabla, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        columnas = ("Fecha", "Dispositivo", "Estado", "Ruta")
        tree = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=10,
        )
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=140)

        tree.pack(fill="both", expand=True)
        scrollbar_y.config(command=tree.yview)
        scrollbar_x.config(command=tree.xview)

        backups_simulados = [
            ("2025-06-10 08:00", "Router Central", "Éxito", "/backups/router1.bak"),
            ("2025-06-11 12:00", "Switch Piso3", "Error", "—"),
            ("2025-06-12 08:00", "Router Central", "Éxito", "/backups/router1.bak"),
        ]
        for backup in backups_simulados:
            tree.insert("", "end", values=backup)

    def construir_lista_dispositivos(self):

        frame = tk.LabelFrame(
            self.master,
            text="Dispositivos Registrados",
            padx=10,
            pady=10,
            bg="#404040",
            fg="white",
            font=self.font_titulo,
        )
        frame.pack(padx=10, pady=5, fill="x")

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#505050",
            foreground="white",
            fieldbackground="#505050",
            font=self.font_tabla_contenido,
        )
        style.map("Treeview", background=[["selected", "blue"]])
        style.configure(
            "Treeview.Heading",
            background="#606060",
            foreground="white",
            font=self.font_tabla_encabezado,
        )

        container = tk.Frame(frame)
        container.pack(fill="both", expand=True)
        # Barra vertical
        scrollbar_y = ttk.Scrollbar(container, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")

        # Barrita horizontal
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")

        cols = ("Nombre", "IP", "Usuario", "Contraseña", "Periodicidad")
        self.tree = ttk.Treeview(
            container,
            columns=cols,
            show="headings",
            height=5,
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
        )
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        self.tree.pack(fill="both", expand=True)

        # Vincular las scrollbars con el Treeview
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        self.tree.bind("<<TreeviewSelect>>", self.al_seleccionar_arbol)
        self.actualizar_vista_arbol()

        self.tree_menu = tk.Menu(self.master, tearoff=0)
        self.tree_menu.add_command(
            label="Mostrar Contraseña", command=self.mostrar_contrasena_tab
        )
        self.tree_menu.add_command(
            label="Ocultar Contraseña", command=self.ocultar_contrasena_tabla
        )
        for col in cols:
            if col == "Periodicidad":
                self.tree.column(col, width=120)
            else:
                self.tree.column(col, width=200)

        self.tree.bind("<Button-3>", self._mostrar_menu_tabla)

    def habilitar_nuevo_dispositivo(
        self,
    ):
        self.limpiar_formulario()
        for entry in self.entry_widgets.values():
            entry.config(state="normal")
        messagebox.showinfo(
            "Nuevo dispositivo", "Puedes ingresar los detalles de un nuevo dispositivo."
        )

    def _mostrar_menu_tabla(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.tree_menu.post(event.x_root, event.y_root)

    def mostrar_contrasena_tab(self):
        for i, dispositivo in enumerate(self.simulated_data):
            self.tree.item(
                i,
                values=(
                    dispositivo["Nombre"],
                    dispositivo["IP"],
                    dispositivo["Usuario"],
                    dispositivo["Contraseña"],
                ),
            )

    def ocultar_contrasena_tabla(self):
        for i, dispositivo in enumerate(self.simulated_data):
            contrasena_oculta = "*" * len(dispositivo["Contraseña"])
            self.tree.item(
                i,
                values=(
                    dispositivo["Nombre"],
                    dispositivo["IP"],
                    dispositivo["Usuario"],
                    contrasena_oculta,
                ),
            )

    def construir_formulario_detalles(self):

        frame = tk.LabelFrame(
            self.master,
            text="Detalles del Dispositivo",
            padx=10,
            pady=10,
            bg="#404040",
            fg="white",
            font=self.font_titulo,
        )
        frame.pack(padx=10, pady=5, fill="both", expand=True)

        row_idx = 0
        for label_text, var in self.fields.items():
            tk.Label(
                frame, text=label_text, bg="#404040", fg="white", font=self.font_normal
            ).grid(row=row_idx, column=0, sticky="w", pady=2)

            if label_text == "Contraseña":
                entry = tk.Entry(
                    frame,
                    textvariable=var,
                    width=35,
                    bg="#505050",
                    fg="white",
                    insertbackground="white",
                    font=self.font_normal,
                    show="*",
                    state="disabled",
                )
                toggle_button = tk.Button(
                    frame,
                    text="Mostrar",
                    width=12,
                    command=lambda e=entry: self._toggle_password_visibility(e),
                    bg="#606060",
                    fg="white",
                    font=self.font_normal,
                    state="disabled",
                )
                toggle_button.grid(row=row_idx, column=2, padx=5)
                self.entry_widgets["__toggle_button"] = toggle_button
            else:
                entry = tk.Entry(
                    frame,
                    textvariable=var,
                    width=35,
                    bg="#505050",
                    fg="white",
                    insertbackground="white",
                    font=self.font_normal,
                    state="disabled",
                )
            if label_text == "Periodicidad":
                options = ["Diaria", "Semanal", "Mensual", "Anual"]
                entry = ttk.Combobox(
                    frame,
                    textvariable=var,
                    values=options,
                    state="disabled",
                    width=32,
                    font=self.font_normal,
                )
                entry.current(0)

            entry.grid(row=row_idx, column=1, sticky="w", pady=2)
            self.entry_widgets[label_text] = entry
            row_idx += 1
        self.limpiar_btn = tk.Button(
            frame,
            text="Limpiar",
            width=12,
            command=self.limpiar_formulario,
            bg="#A9DCF0",
            fg="black",
            font=self.font_boton,
            state="disabled",  # Bloqueado por defecto
        )
        self.limpiar_btn.grid(row=row_idx, column=2, sticky="", pady=5, padx=5)

    def habilitar_campos(
        self,
    ):  # Habilita todos los campos de entrada y botones relacionados.
        for entry in self.entry_widgets.values():
            entry.config(state="normal")
        if "__toggle_button" in self.entry_widgets:
            self.entry_widgets["__toggle_button"].config(state="normal")
        if hasattr(self, "limpiar_btn"):
            self.limpiar_btn.config(state="normal")

    def bloquear_campos(
        self,
    ):  # Deshabilita todos los campos de entrada y botones relacionados.
        for entry in self.entry_widgets.values():
            entry.config(state="disabled")
        if "__toggle_button" in self.entry_widgets:
            self.entry_widgets["__toggle_button"].config(state="disabled")
        if hasattr(self, "limpiar_btn"):
            self.limpiar_btn.config(state="disabled")

    def _toggle_password_visibility(self, entry):
        if entry.cget("show") == "*":
            entry.config(show="")
            entry.master.children["!button"].config(text="Ocultar")
        else:
            entry.config(show="*")
            entry.master.children["!button"].config(text="Mostrar")

    def construir_botones_inferiores(self):
        frame = tk.Frame(self.master, pady=10, bg="#404040")
        frame.pack()

        tk.Button(
            frame,
            text="Guardar",
            width=15,
            command=self.guardar_dispositivo,
            bg="#008000",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            frame,
            text="Cancelar",
            width=15,
            command=self.limpiar_formulario,
            font=self.font_boton,
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            frame, text="Probar Conexión SSH", width=20, font=self.font_boton
        ).grid(row=0, column=2, padx=10)

    def limpiar_formulario(self):
        for var in self.fields.values():
            var.set("")
        self.fields["Puerto SSH"].set("22")
        self.fields["Hora"].set("08:00")
        self.selected_id = None
        self.tree.selection_set(())
        if "Nombre" in self.entry_widgets:
            self.entry_widgets["Nombre"].focus_set()

    def al_seleccionar_arbol(self, event):
        selected = self.tree.focus()
        if selected:
            index = int(selected)
            data = self.simulated_data[index]
            for key in self.fields:
                self.fields[key].set(data.get(key, ""))
            self.selected_id = index

    def validar_ip(self, ip):
        partes = ip.strip().split(".")
        if len(partes) != 4:
            return False
        try:
            return all(0 <= int(parte) <= 255 for parte in partes)
        except ValueError:
            return False

    def validar_hora(self, hora):
        try:
            datetime.datetime.strptime(hora.strip(), "%H:%M")
            return True
        except ValueError:
            return False

    def guardar_dispositivo(self):
        nuevo_dato = {key: var.get().strip() for key, var in self.fields.items()}
        obligatorios = [
            "Nombre",
            "IP",
            "Usuario",
            "Contraseña",
            "Puerto SSH",
            "Periodicidad",
        ]
        faltantes = [campo for campo in obligatorios if not nuevo_dato.get(campo)]
        if faltantes:
            mensaje = "Por favor completa los siguientes campos:\n- " + "\n- ".join(
                faltantes
            )
            messagebox.showerror("Campos obligatorios", mensaje)
            return

        if not self.validar_ip(nuevo_dato["IP"]):
            messagebox.showerror(
                "IP inválida", "La dirección IP no tiene un formato válido."
            )
            return

        if not self.validar_hora(nuevo_dato["Hora"]):
            messagebox.showerror(
                "Hora inválida", "La hora debe tener el formato HH:MM (24h)."
            )
            return

        if not nuevo_dato["Puerto SSH"].isdigit():
            messagebox.showerror("Puerto inválido", "El puerto SSH debe ser numérico.")
            return
        puerto = int(nuevo_dato["Puerto SSH"])
        if not (1 <= puerto <= 65535):
            messagebox.showerror(
                "Puerto inválido", "El puerto SSH debe estar entre 1 y 65535."
            )
            return

        if self.selected_id is not None:
            self.simulated_data[self.selected_id] = nuevo_dato
        else:
            self.simulated_data.append(nuevo_dato)

        self.actualizar_vista_arbol()
        self.limpiar_formulario()
        messagebox.showinfo("Éxito", "Dispositivo guardado correctamente.")

    def editar_dispositivo(self):
        selected = self.tree.focus()
        if selected:
            self.al_seleccionar_arbol(None)
            self.habilitar_campos()  # Habilita los campos para edición
            messagebox.showinfo(
                "Edición",
                "Puedes modificar los campos y presionar Guardar para actualizar el dispositivo.",
            )
        else:
            messagebox.showwarning(
                "Seleccionar", "Por favor selecciona un dispositivo para editar."
            )

    def eliminar_dispositivo(self):
        selected = self.tree.focus()
        if selected:
            index = int(selected)
            confirm = messagebox.askyesno(
                "Confirmar", "¿Estás seguro de que deseas eliminar este dispositivo?"
            )
            if confirm:
                self.simulated_data.pop(index)
                self.actualizar_vista_arbol()
                self.limpiar_formulario()
                messagebox.showinfo("Eliminado", "Dispositivo eliminado correctamente.")
        else:
            messagebox.showwarning(
                "Seleccionar", "Por favor selecciona un dispositivo para eliminar."
            )

    def actualizar_vista_arbol(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, dispositivo in enumerate(self.simulated_data):
            contrasena_oculta = "*" * len(dispositivo["Contraseña"])
            self.tree.insert(
                "",
                "end",
                iid=i,
                values=(
                    dispositivo["Nombre"],
                    dispositivo["IP"],
                    dispositivo["Usuario"],
                    contrasena_oculta,
                    dispositivo["Periodicidad"],
                ),
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = BackupGUI(root)
    root.mainloop()
