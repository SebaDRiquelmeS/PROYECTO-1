import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import os

# Importamos la lógica de tu proyecto (asegúrate que tu otro archivo se llame 'proyecto_final.py')
# Si tu archivo tiene otro nombre, cambia 'proyecto_final' por ese nombre.
import proyecto_final as backend

class CompiladorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Sintáctico LL(1) - Proyecto 01")
        self.root.geometry("900x700")

        # --- Variables ---
        self.file_path = None
        self.ll1_table = None

        # --- UI Layout ---
        
        # 1. Sección Superior: Botones
        frame_top = tk.Frame(self.root, pady=10)
        frame_top.pack(fill="x")

        btn_load = tk.Button(frame_top, text="📂 Cargar Archivo .java", command=self.load_file, bg="#e1e1e1", font=("Arial", 10))
        btn_load.pack(side="left", padx=20)

        self.lbl_file = tk.Label(frame_top, text="Ningún archivo cargado", fg="gray")
        self.lbl_file.pack(side="left")

        btn_run = tk.Button(frame_top, text="▶ Ejecutar Análisis", command=self.run_analysis, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        btn_run.pack(side="right", padx=20)

        # 2. Sección Central: Código Fuente y Consola
        paned_window = tk.PanedWindow(self.root, orient="vertical")
        paned_window.pack(fill="both", expand=True, padx=10, pady=5)

        # Área de Código
        frame_code = tk.LabelFrame(paned_window, text="Código Fuente", padx=5, pady=5)
        paned_window.add(frame_code)
        self.txt_code = scrolledtext.ScrolledText(frame_code, height=10, font=("Consolas", 10))
        self.txt_code.pack(fill="both", expand=True)

        # Área de Resultados (Salida del Parser)
        frame_output = tk.LabelFrame(paned_window, text="Salida del Analizador", padx=5, pady=5)
        paned_window.add(frame_output)
        self.txt_output = scrolledtext.ScrolledText(frame_output, height=15, bg="#f0f0f0", font=("Consolas", 9))
        self.txt_output.pack(fill="both", expand=True)

        # 3. Sección Inferior: Botones para ver Tablas
        frame_bottom = tk.Frame(self.root, pady=10)
        frame_bottom.pack(fill="x")
        
        tk.Button(frame_bottom, text="Ver Gramática", command=lambda: self.show_json("resultado_gramatica.json")).pack(side="left", padx=10)
        tk.Button(frame_bottom, text="Ver First", command=lambda: self.show_json("resultado_conjunto_first.json")).pack(side="left", padx=10)
        tk.Button(frame_bottom, text="Ver Follow", command=lambda: self.show_json("resultado_conjunto_follow.json")).pack(side="left", padx=10)
        tk.Button(frame_bottom, text="Ver Tabla LL(1)", command=lambda: self.show_json("resultado_tabla_sintactica.json")).pack(side="left", padx=10)

        # Inicializar backend (Generar tablas al arrancar)
        self.init_backend()

    def init_backend(self):
        """Ejecuta los algoritmos generadores al inicio."""
        self.log("Inicializando algoritmos del compilador...")
        try:
            # Generar y guardar todo usando las funciones de tu backend
            backend.write_to_file(backend.GRAMMAR, "resultado_gramatica.json")
            
            self.first_sets = backend.calculate_first_sets(backend.GRAMMAR, backend.NON_TERMINALS)
            backend.write_to_file(self.first_sets, "resultado_conjunto_first.json")
            
            self.follow_sets = backend.calculate_follow_sets(backend.GRAMMAR, backend.START_SYMBOL, self.first_sets)
            backend.write_to_file(self.follow_sets, "resultado_conjunto_follow.json")
            
            self.ll1_table = backend.build_ll1_table(backend.GRAMMAR, self.first_sets, self.follow_sets)
            backend.write_to_file(self.ll1_table, "resultado_tabla_sintactica.json")
            
            self.log("✅ Tablas generadas correctamente (First, Follow, LL1). Listo para analizar.")
        except Exception as e:
            self.log(f"❌ Error crítico inicializando backend: {e}")
            messagebox.showerror("Error", f"Error al generar tablas: {e}")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Java Files", "*.java"), ("All Files", "*.*")])
        if file_path:
            self.file_path = file_path
            self.lbl_file.config(text=os.path.basename(file_path), fg="black")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.txt_code.delete(1.0, tk.END)
                self.txt_code.insert(tk.END, content)
            self.log(f"Archivo cargado: {file_path}")

    def run_analysis(self):
        code = self.txt_code.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Aviso", "El área de código está vacía.")
            return

        self.log("\n--- INICIANDO ANÁLISIS ---")
        try:
            # Redirigir prints es complicado en GUI simple, así que simulamos la ejecución
            lexer = backend.Lexer(code)
            parser = backend.LL1Parser(self.ll1_table, lexer, backend.START_SYMBOL)
            
            # Ejecutamos paso a paso para mostrarlo en la GUI (modificación ligera del loop)
            self.log(f"{'PILA':<40} | {'TOKEN':<15} | ACCIÓN")
            self.log("-" * 70)
            
            # Nota: Aquí estamos replicando el loop del parser para poder imprimir en la GUI
            # Lo ideal sería que tu clase Parser tuviera un callback, pero esto sirve para el demo.
            while parser.stack:
                top = parser.stack[-1]
                token = parser.current_token.type
                stack_str = str(parser.stack)
                
                if top in backend.TERMINALS or top == backend.TOKEN_EOF:
                    if top == token:
                        self.log(f"{stack_str:<40} | {token:<15} | Match: {token}")
                        parser.stack.pop()
                        parser.current_token = parser.lexer.get_next_token()
                    else:
                        raise Exception(f"Se esperaba '{top}' pero llegó '{token}'")
                elif top in backend.NON_TERMINALS:
                    if token in self.ll1_table[top]:
                        prod = self.ll1_table[top][token]
                        self.log(f"{stack_str:<40} | {token:<15} | Regla: {top} -> {' '.join(prod)}")
                        parser.stack.pop()
                        if prod != [backend.TOKEN_EPSILON]:
                            for s in reversed(prod):
                                parser.stack.append(s)
                    else:
                        raise Exception(f"No hay regla para [{top}, {token}]")
                else:
                    raise Exception(f"Símbolo desconocido: {top}")
            
            self.log("-" * 70)
            self.log(">>> ✅ EL CÓDIGO ES SINTÁCTICAMENTE CORRECTO <<<")
            messagebox.showinfo("Resultado", "Análisis Exitoso: El código es correcto.")

        except Exception as e:
            self.log(f"\n>>> ❌ ERROR DE SINTAXIS: {e} <<<")
            messagebox.showerror("Error de Sintaxis", str(e))

    def log(self, message):
        self.txt_output.insert(tk.END, message + "\n")
        self.txt_output.see(tk.END)

    def show_json(self, filename):
        if os.path.exists(filename):
            top = tk.Toplevel(self.root)
            top.title(filename)
            top.geometry("600x400")
            text = scrolledtext.ScrolledText(top, font=("Consolas", 9))
            text.pack(fill="both", expand=True)
            with open(filename, 'r', encoding='utf-8') as f:
                text.insert(tk.END, f.read())
        else:
            messagebox.showerror("Error", f"No se encuentra el archivo {filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CompiladorApp(root)
    root.mainloop()