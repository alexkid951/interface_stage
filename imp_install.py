import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import subprocess

# === Splash Screen ===
def show_splash_screen():
    splash = tk.Tk()
    splash.overrideredirect(True)
    splash.configure(bg="white")
    splash.geometry("300x300+600+300")

    try:
        chemin_logo = r"C:\.venv\macscript\curie2.jpg"
        logo = Image.open(chemin_logo)
        logo = logo.resize((200, 200), Image.Resampling.LANCZOS)
        logo_img = ImageTk.PhotoImage(logo)
        logo_label = tk.Label(splash, image=logo_img, bg="white")
        logo_label.image = logo_img
        logo_label.pack(expand=True)

        text = tk.Label(splash, text="Chargement...", font=("Helvetica", 12), bg="white", fg="black")
        text.pack(pady=10)
    except Exception as e:
        print("Erreur de logo splash:", e)

    splash.update()
    splash.after(2500, splash.destroy)
    splash.mainloop()

# === Application principale ===
class PrinterInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Canon Printer Installer")
        self.root.geometry("500x400")
        self.root.configure(bg="white")

        # Barre de titre
        top_bar = tk.Frame(root, bg="white")
        top_bar.pack(fill="x", pady=(5, 0), padx=5)

        self.flag_frame = tk.Frame(top_bar, bg="white")
        self.flag_frame.pack(side="right", anchor="ne")

        self.flag_fr = ImageTk.PhotoImage(Image.open(r"C:\.venv\macscript\en_flag.jpg").resize((20, 15), Image.Resampling.LANCZOS))
        self.flag_en = ImageTk.PhotoImage(Image.open(r"C:\.venv\macscript\fr_flag.png").resize((20, 15), Image.Resampling.LANCZOS))

        self.language = "fr"
        self.flag_button = tk.Button(self.flag_frame, image=self.flag_fr, command=self.change_language, bg="white", bd=0)
        self.flag_button.pack()

        try:
            chemin_logo = r"C:\.venv\macscript\curie2.jpg"
            logo_img = Image.open(chemin_logo)
            logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
            logo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(root, image=logo, bg="white")
            logo_label.image = logo
            logo_label.pack(pady=10)
        except Exception as e:
            print("Erreur de chargement du logo :", e)

        self.welcome_message = tk.Label(root, text="🖨 Ce logiciel vous permet de rechercher et d’installer une imprimante en un clic.",
                                        font=("Helvetica", 12), bg="white", fg="black", wraplength=480, justify="center")
        self.welcome_message.pack(pady=(0, 10))

        self.title_label = tk.Label(root, text="Canon Driver and Printer Installer", font=("Helvetica", 14, "bold"), bg="white", fg="black")
        self.title_label.pack(pady=5)

        self.name_label = tk.Label(root, text="Nom de l'imprimante (MFPxxxxx ou LPTxxxxx):", bg="white", fg="black")
        self.name_label.pack(pady=5)

        self.pname_entry = tk.Entry(root)
        self.pname_entry.pack(pady=5)

        self.install_button = tk.Button(root, text="Installer l'imprimante", command=self.install_printer, bg="#A8A9AD", fg="black")
        self.install_button.pack(pady=10)

        self.result_label = tk.Label(root, text="", bg="white", fg="black")
        self.result_label.pack()

    def change_language(self):
        if self.language == "fr":
            self.language = "en"
            self.flag_button.config(image=self.flag_en)
            self.update_texts_en()
        else:
            self.language = "fr"
            self.flag_button.config(image=self.flag_fr)
            self.update_texts_fr()

    def update_texts_fr(self):
        self.welcome_message.config(text="🖨 Ce logiciel vous permet de rechercher et d’installer une imprimante en un clic.")
        self.title_label.config(text="Canon Driver and Printer Installer")
        self.install_button.config(text="Installer l'imprimante")
        self.name_label.config(text="Nom de l'imprimante (MFPxxxxx ou LPTxxxxx):")

    def update_texts_en(self):
        self.welcome_message.config(text="🖨 This software allows you to search and install a printer with a single click.")
        self.title_label.config(text="Canon Driver and Printer Installer")
        self.install_button.config(text="Install Printer")
        self.name_label.config(text="Printer name (MFPxxxxx or LPTxxxxx):")

    def execute_command(self, command, password):
        try:
            full_cmd = f"echo {password} | sudo -S {command}"
            subprocess.run(full_cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"[Erreur] {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'exécution : {e}")
            return False
        return True

    def install_printer(self):
        pname = self.pname_entry.get().strip()

        if not pname or len(pname) != 8 or not (pname.startswith("MFP") or pname.startswith("LPT")):
            messagebox.showwarning("Nom invalide", "Le nom de l'imprimante doit faire 8 caractères et commencer par 'MFP' ou 'LPT'.")
            return

        password = simpledialog.askstring("Mot de passe admin", "Entrez le mot de passe de session :", show='*')
        if not password:
            messagebox.showwarning("Mot de passe", "Mot de passe requis pour continuer.")
            return

        self.result_label.config(text="Installation en cours...")

        script_path = "C:\.venv\canon_install.sh"
        success = self.run_shell_script(script_path, password)
        if not success:
            self.result_label.config(text="Erreur lors de l'installation.")
            return

        site_suffix = self.ask_site_location()
        if not site_suffix:
            self.result_label.config(text="Installation annulée.")
            return

        self.configure_printer(pname, site_suffix, password)

        self.result_label.config(text="✅ Installation terminée avec succès.")
        messagebox.showinfo("Succès", "L'imprimante a été installée avec succès.")

    def run_shell_script(self, script_path, password):
        try:
            full_cmd = f"echo {password} | sudo -S bash {script_path}"
            subprocess.run(full_cmd, check=True, shell=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exécution du script : {e}")
            return False
        return True

    def ask_site_location(self):
        site_window = tk.Toplevel(self.root)
        site_window.title("Localisation de l'imprimante")
        site_window.geometry("300x150")
        site_window.configure(bg="white")

        label = tk.Label(site_window, text="L'imprimante est-elle située à Orsay ? (Y/N):", bg="white", fg="black")
        label.pack(pady=20)

        site_entry = tk.Entry(site_window)
        site_entry.pack()

        result = {"value": None}

        def submit_site():
            site = site_entry.get().strip().upper()
            if site == "Y":
                result["value"] = ".curie.u-psud.fr"
                site_window.destroy()
            elif site == "N":
                result["value"] = ".curie.fr"
                site_window.destroy()
            else:
                messagebox.showwarning("Entrée invalide", "Merci de saisir Y ou N.")
                site_entry.delete(0, tk.END)

        submit_button = tk.Button(site_window, text="Valider", command=submit_site, bg="#A8A9AD", fg="black")
        submit_button.pack(pady=10)

        self.root.wait_window(site_window)
        return result["value"]

    def configure_printer(self, pname, site_suffix, password):
        printer_name = pname + site_suffix
        if pname.startswith("M"):
            cmd = f"lpadmin -p {printer_name} -o printer-is-shared=False -E -v lpd://{printer_name} -P /Library/Printers/PPDs/Contents/Resources/CNMCIRAC5735S2.ppd.gz -D {printer_name}"
        else:
            cmd = f"lpadmin -p {printer_name} -o printer-is-shared=False -o APOptionalDuplexer=True -E -v lpd://{printer_name} -P /System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/PrintCore.framework/Versions/A/Resources/Generic.ppd -D {printer_name}"
        self.execute_command(cmd, password)

# === Lancement avec Splash ===
if __name__ == "__main__":
    show_splash_screen()
    root = tk.Tk()
    app = PrinterInstallerApp(root)
    root.mainloop()
