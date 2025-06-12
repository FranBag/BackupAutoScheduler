import tkinter as tk
from tkinter import ttk, messagebox, font  # Importa 'font'
import re
import os
from tkcalendar import Calendar
import datetime


class BackupGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Software de Backups - Dispositivos de Red")
        self.master.geometry("700x650")
        self.master.resizable(False, False)
        # color de fondo de la ventana principal
        self.master.configure(bg="#404040")

        # fuentes
        self.font_titulo = font.Font(family="Verdana", size=14, weight="bold")
        self.font_normal = font.Font(family="Verdana", size=10)
        self.font_boton = font.Font(family="Verdana", size=10, weight="bold")
        self.font_tabla_encabezado = font.Font(family="Verdana", size=10, weight="bold")
        self.font_tabla_contenido = font.Font(family="Verdana", size=9)

        self.fields = self._inicializar_campos()
        self.selected_id = None

        self.simulated_data = [
            {
                "Nombre": "Router Central",
                "IP": "192.168.1.1",
                "Tipo": "Cisco",
                "Usuario": "admin",
                "Contraseña": "admin123",
                "Puerto SSH": "22",
                "Periodicidad": "Diario",
                "Hora": "08:00",
                "Día de Semana": "Lunes",
                "Día Mes": "1",
                "Carpeta Local": "C:/backups/router",
            },
            {
                "Nombre": "Switch Piso3",
                "IP": "192.168.1.2",
                "Tipo": "HP",
                "Usuario": "user",
                "Contraseña": "pass",
                "Puerto SSH": "22",
                "Periodicidad": "Semanal",
                "Hora": "12:00",
                "Día de Semana": "Viernes",
                "Día Mes": "",
                "Carpeta Local": "C:/backups/switch",
            },
        ]

        self.entry_widgets = {}
        self._construir_widgets()

    def _inicializar_campos(self):
        return {
            "Nombre": tk.StringVar(),
            "IP": tk.StringVar(),
            "Tipo": tk.StringVar(),
            "Usuario": tk.StringVar(),
            "Contraseña": tk.StringVar(),
            "Puerto SSH": tk.StringVar(value="22"),
            "Periodicidad": tk.StringVar(),
            "Hora": tk.StringVar(value="08:00"),
            "Día de Semana": tk.StringVar(),
            "Día Mes": tk.StringVar(),
            "Carpeta Local": tk.StringVar(value="C:/backups/"),
        }

    def _construir_widgets(self):
        self._construir_botones_superiores()
        self._construir_lista_dispositivos()
        self._construir_formulario_detalles()
        self._construir_botones_inferiores()

    def _construir_botones_superiores(self):
        frame = tk.Frame(self.master, pady=10, bg="#404040")
        frame.pack()

        # Botón "Nuevo"
        tk.Button(
            frame,
            text="Nuevo",
            width=12,
            command=self._limpiar_formulario,
            bg="#A9DCF0",
            fg="black",
            font=self.font_boton,
        ).grid(row=0, column=0, padx=5)
        # Botón "Editar"
        tk.Button(
            frame,
            text="Editar",
            width=12,
            command=self._editar_dispositivo,
            font=self.font_boton,
        ).grid(row=0, column=1, padx=5)
        # Botón "Eliminar"
        tk.Button(
            frame,
            text="Eliminar",
            width=12,
            command=self._eliminar_dispositivo,
            bg="red",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=2, padx=5)
        # Botón "Realizar Backup"
        tk.Button(frame, text="Realizar Backup", width=16, font=self.font_boton).grid(
            row=0, column=3, padx=5
        )

    def _construir_lista_dispositivos(self):

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
        )  # Fuente de las filas
        style.map("Treeview", background=[("selected", "blue")])
        style.configure(
            "Treeview.Heading",
            background="#606060",
            foreground="white",
            font=self.font_tabla_encabezado,
        )  # Fuente de los encabezados

        cols = ("Nombre", "IP", "Tipo")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=5)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        self.tree.pack(fill="x")
        self.tree.bind("<<TreeviewSelect>>", self._al_seleccionar_arbol)
        self._actualizar_vista_arbol()

    def _construir_formulario_detalles(self):

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

        self.dias_semana_map = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo",
        }

        row_idx = 0
        for label_text, var in self.fields.items():
            tk.Label(
                frame, text=label_text, bg="#404040", fg="white", font=self.font_normal
            ).grid(row=row_idx, column=0, sticky="w", pady=2)

            if label_text in ["Día de Semana", "Día Mes"]:
                entry_frame = tk.Frame(frame, bg="#404040")
                entry_frame.grid(row=row_idx, column=1, sticky="w", pady=2)

                entry = tk.Entry(
                    entry_frame,
                    textvariable=var,
                    width=25,
                    bg="#505050",
                    fg="white",
                    insertbackground="white",
                    font=self.font_normal,
                )
                entry.pack(side=tk.LEFT)
                tk.Button(
                    entry_frame,
                    text="...",
                    command=lambda l=label_text: self._mostrar_calendario(l),
                ).pack(side=tk.LEFT)
                self.entry_widgets[label_text] = entry
            else:

                entry = tk.Entry(
                    frame,
                    textvariable=var,
                    width=35,
                    bg="#505050",
                    fg="white",
                    insertbackground="white",
                    font=self.font_normal,
                )
                entry.grid(row=row_idx, column=1, sticky="w", pady=2)
                self.entry_widgets[label_text] = entry
            row_idx += 1

    def _construir_botones_inferiores(self):
        frame = tk.Frame(self.master, pady=10, bg="#404040")
        frame.pack()

        # Botón "Guardar"
        tk.Button(
            frame,
            text="Guardar",
            width=15,
            command=self._guardar_dispositivo,
            bg="#008000",
            fg="white",
            font=self.font_boton,
        ).grid(row=0, column=0, padx=10)
        # Botón "Cancelar"
        tk.Button(
            frame,
            text="Cancelar",
            width=15,
            command=self._limpiar_formulario,
            font=self.font_boton,
        ).grid(row=0, column=1, padx=10)
        # Botón "Probar Conexión SSH"
        tk.Button(
            frame, text="Probar Conexión SSH", width=20, font=self.font_boton
        ).grid(row=0, column=2, padx=10)

    def _limpiar_formulario(self):
        for var in self.fields.values():
            var.set("")
        self.fields["Puerto SSH"].set("22")
        self.fields["Hora"].set("08:00")
        self.fields["Carpeta Local"].set("C:/backups/")
        self.selected_id = None
        self.tree.selection_set(())
        if "Nombre" in self.entry_widgets:
            self.entry_widgets["Nombre"].focus_set()


    """ ///////////////////////////////////////////////////////
        ///////////   ADAPTAR ESTO CON EL BACKEND   /////////// 
        /////////////////////////////////////////////////////// """
        
    def _al_seleccionar_arbol(self, event):
        selected = self.tree.focus()
        if selected:
            index = int(selected)
            data = self.simulated_data[index]
            for key in self.fields:
                self.fields[key].set(data.get(key, ""))
            self.selected_id = index
            
    """ ///////////////////////////////////////////////////////
        ///////////   ADAPTAR ESTO CON EL BACKEND   /////////// 
        /////////////////////////////////////////////////////// """

    def _validar_ip(self, ip):
        patron = re.compile(
            r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        return bool(patron.match(ip))

    def _validar_hora(self, hora):
        return bool(re.match(r"^(2[0-3]|[01]?[0-9]):[0-5][0-9]$", hora))

    def _guardar_dispositivo(self):
        """ ///////////////////////////////////////////////////////
        ///////////   ADAPTAR ESTO CON EL BACKEND   /////////// 
        /////////////////////////////////////////////////////// """
        
        nuevo_dato = {key: var.get().strip() for key, var in self.fields.items()}
        obligatorios = [
            "Nombre",
            "IP",
            "Tipo",
            "Usuario",
            "Contraseña",
            "Puerto SSH",
            "Carpeta Local",
        ]
        faltantes = [campo for campo in obligatorios if not nuevo_dato.get(campo)]
        if faltantes:
            mensaje = "Por favor completa los siguientes campos:\n- " + "\n- ".join(
                faltantes
            )
            messagebox.showerror("Campos obligatorios", mensaje)
            return

        if not self._validar_ip(nuevo_dato["IP"]):
            messagebox.showerror(
                "IP inválida", "La dirección IP no tiene un formato válido."
            )
            return

        if not self._validar_hora(nuevo_dato["Hora"]):
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

        dia_mes = nuevo_dato.get("Día Mes", "")
        if dia_mes:
            if not dia_mes.isdigit() or not (1 <= int(dia_mes) <= 31):
                messagebox.showerror(
                    "Día del Mes inválido",
                    "Si se indica, el Día del Mes debe ser un número del 1 al 31.",
                )
                return

        carpeta = nuevo_dato["Carpeta Local"]
        if not os.path.isdir(carpeta):
            messagebox.showwarning(
                "Carpeta inexistente",
                f"La carpeta '{carpeta}' no existe en el sistema.",
            )


        if self.selected_id is not None:
            self.simulated_data[self.selected_id] = nuevo_dato
        else:
            self.simulated_data.append(nuevo_dato)

        self._actualizar_vista_arbol()
        self._limpiar_formulario()
        messagebox.showinfo("Éxito", "Dispositivo guardado correctamente.")
        
    """ ///////////////////////////////////////////////////////
        ///////////   ADAPTAR ESTO CON EL BACKEND   /////////// 
        /////////////////////////////////////////////////////// """
        
    def _editar_dispositivo(self):
        selected = self.tree.focus()
        if selected:
            self._al_seleccionar_arbol(None)
            messagebox.showinfo(
                "Edición",
                "Puedes modificar los campos y presionar Guardar para actualizar el dispositivo.",
            )
        else:
            messagebox.showwarning(
                "Seleccionar", "Por favor selecciona un dispositivo para editar."
            )

    def _eliminar_dispositivo(self):
        selected = self.tree.focus()
        if selected:
            index = int(selected)
            confirm = messagebox.askyesno(
                "Confirmar", "¿Estás seguro de que deseas eliminar este dispositivo?"
            )
            if confirm:
                self.simulated_data.pop(index)
                self._actualizar_vista_arbol()
                self._limpiar_formulario()
                messagebox.showinfo("Eliminado", "Dispositivo eliminado correctamente.")
        else:
            messagebox.showwarning(
                "Seleccionar", "Por favor selecciona un dispositivo para eliminar."
            )

    def _actualizar_vista_arbol(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, dispositivo in enumerate(self.simulated_data):
            self.tree.insert(
                "",
                "end",
                iid=i,
                values=(dispositivo["Nombre"], dispositivo["IP"], dispositivo["Tipo"]),
            )

    """ ///////////////////////////////////////////////////////
        ///////////   ADAPTAR ESTO CON EL BACKEND   /////////// 
        /////////////////////////////////////////////////////// """
        
    def _mostrar_calendario(self, target_field):
        def seleccionar_fecha():
            fecha_seleccionada = cal.selection_get()
            if target_field == "Día de Semana":
                dia_semana_num = fecha_seleccionada.weekday()
                self.fields["Día de Semana"].set(self.dias_semana_map[dia_semana_num])
            elif target_field == "Día Mes":
                self.fields["Día Mes"].set(str(fecha_seleccionada.day))
            top.destroy()

        top = tk.Toplevel(self.master)
        top.title("Seleccionar Fecha")
        top.configure(bg="#404040")

        # Calendario
        cal = Calendar(
            top,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            background="#505050",
            foreground="white",
            headersbackground="#606060",
            headersforeground="white",
            normalbackground="#505050",
            normalforeground="white",
            weekendbackground="#505050",
            weekendforeground="red",
            othermonthforeground="gray",
            othermonthbackground="#454545",
            selectbackground="blue",
            selectforeground="white",
            font=self.font_normal,
        )  # fuente del calendario
        cal.pack(pady=10)
        tk.Button(
            top,
            text="Seleccionar",
            command=seleccionar_fecha,
            bg="#008000",
            fg="white",
            font=self.font_boton,
        ).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = BackupGUI(root)
    root.mainloop()
