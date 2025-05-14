import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from PIL import Image, ImageTk
from html.parser import HTMLParser
class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_text(self):
        return ''.join(self.text_parts).strip()
# Connexion MySQL
def connexion_mysql():
    return mysql.connector.connect(
        host="localhost",
        user="glpi",
        password="mot_de_passe_fort",
        database="glpidb"
    )

# Charger les tickets
description_dict = {}

def charger_tickets():
    conn = connexion_mysql()
    cursor = conn.cursor()
    query = """
    SELECT
        t.id, 
        t.name,
        t.content,
        ts.name AS status_name,
        u.name AS creator_name
    FROM glpi_tickets t
    LEFT JOIN glpi_ticket_statuses ts ON t.status = ts.id
    LEFT JOIN glpi_tickets_users tu ON tu.tickets_id = t.id AND tu.type = 1
    LEFT JOIN glpi_users u ON tu.users_id = u.id
    WHERE t.is_deleted = 0
    ORDER BY t.date_creation DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    tree.delete(*tree.get_children())
    description_dict.clear()
    for row in rows:
        ticket_id, name, content, status, creator = row
        # Vérifier si le statut est 'None' et le remplacer par une valeur par défaut
        status = status if status else "Inconnu"  # "Inconnu" ou "Nouveau", selon votre préférence
        tree.insert("", "end", iid=ticket_id, values=(ticket_id, name, status, creator))
        description_dict[ticket_id] = content  # On garde la description dans le dictionnaire
    conn.close()
from html.parser import HTMLParser

class HTMLTextExtractor(HTMLParser):
    ...
# Double-clic sur un ticket pour afficher la description
def show_description(event):
   ...
    selected_item = tree.focus()
    if selected_item:
        ticket_id = int(selected_item)
        raw_description = description_dict.get(ticket_id, "Pas de description disponible")

        # Nettoyage de description HTML pour affichage
        parser = HTMLTextExtractor()
        parser.feed(raw_description) 
        cleaned_description =  perser.get.text()
    ...
        popup = tk.Toplevel(root)
        popup.title(f"Description du ticket {ticket_id}")

        # Affichage du logo dans la popup (doit être après la création de popup)
        try:
            logo_img = Image.open("logo.png")  # Remplace par ton fichier marrant
            logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img, master=popup)
            logo_label = tk.Label(popup, image=logo_photo)
            logo_label.image = logo_photo  # garder une référence
            logo_label.pack(pady=(10, 0))
        except Exception as e:
            print(f"Erreur chargement logo description : {e}")

        text = tk.Text(popup, wrap="word", width=60, height=15)
        text.insert("1.0", cleaned_description)
        text.config(state="disabled")
        text.pack(padx=10, pady=10)

# Modifier le statut
def modifier_statut():
    selection = tree.focus()
    if not selection:
        messagebox.showwarning("Attention", "Veuillez sélectionner un ticket.")
        return

    ticket_id = tree.item(selection)['values'][0]
    nouveau_statut = statut_combo.get()
    if not nouveau_statut:
        messagebox.showwarning("Attention", "Veuillez sélectionner un nouveau statut.")
        return

    conn = connexion_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM glpi_ticket_statuses WHERE name = %s", (nouveau_statut,))
    resultat = cursor.fetchone()
    if resultat:
        statut_id = resultat[0]
        cursor.execute("UPDATE glpi_tickets SET status = %s WHERE id = %s", (statut_id, ticket_id))
        conn.commit()
        messagebox.showinfo("Succès", f"Le statut du ticket {ticket_id} a été mis à jour.")
        charger_tickets()
    else:
        messagebox.showerror("Erreur", "Statut non trouvé.")
    conn.close()

# Créer un ticket
def creer_ticket():
    nom_ticket = entry_nom_ticket.get()
    id_createur = entry_id_createur.get()
    categorie = entry_categorie.get()
    type_ticket = entry_type.get()if entry_type.get() else '0'  # Valeur par défaut si vide
    attribue_a = entry_attribue.get()
    priorite = entry_priorite.get()

    if not nom_ticket or not id_createur:
        messagebox.showwarning("Attention", "Veuillez remplir au minimum le nom et l'ID du créateur.")
        return

    # Vérifier si la catégorie 'materiel' existe, sinon la créer
    conn = connexion_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM glpi_itilcategories WHERE name = %s", ('materiel',))
    result = cursor.fetchone()
    
    if not result:  # Si la catégorie n'existe pas, on la crée
        cursor.execute("""
            INSERT INTO glpi_itilcategories (name) 
            VALUES (%s)
        """, ('materiel',))
        cursor.execute("SELECT LAST_INSERT_ID()")
        itilcategories_id = cursor.fetchone()[0]  # Récupérer l'ID de la nouvelle catégorie
    else:
        itilcategories_id = result[0]  # Utiliser l'ID existant

    # Insérer le ticket avec le bon itilcategories_id
    cursor.execute("""
        INSERT INTO glpi_tickets (name, status, itilcategories_id, type, priority, users_id_recipient)
        VALUES (%s, 1, %s, %s, %s, %s)
    """, (nom_ticket, itilcategories_id, type_ticket, priorite, attribue_a))
    ticket_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO glpi_tickets_users (tickets_id, users_id, type)
        VALUES (%s, %s, 1)
    """, (ticket_id, id_createur))

    conn.commit()
    conn.close()

    messagebox.showinfo("Succès", f"Ticket créé avec l'ID : {ticket_id}")
    charger_tickets()

# Rechercher un ticket (par nom, ID ou créateur)
def rechercher_ticket():
    recherche = entry_recherche.get().strip()
    if not recherche:
        messagebox.showwarning("Attention", "Veuillez entrer un critère de recherche.")
        return

    conn = connexion_mysql()
    cursor = conn.cursor()
    query = """
    SELECT
        t.id,
        t.name,
        ts.name AS status_name,
        u.name AS creator_name
    FROM glpi_tickets t
    LEFT JOIN glpi_ticket_statuses ts ON t.status = ts.id
    LEFT JOIN glpi_tickets_users tu ON tu.tickets_id = t.id AND tu.type = 1
    LEFT JOIN glpi_users u ON tu.users_id = u.id
    WHERE t.is_deleted = 0 AND (
        LOWER(t.name) LIKE LOWER(%s) OR
        CAST(t.id AS CHAR) LIKE %s OR
        LOWER(u.name) LIKE LOWER(%s)
    )
    ORDER BY t.date_creation DESC
    """
    like_recherche = f"%{recherche}%"
    cursor.execute(query, (like_recherche, like_recherche, like_recherche))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        messagebox.showinfo("Aucun résultat", "Aucun ticket trouvé pour cette recherche.")
        return

    popup = tk.Toplevel(root)
    popup.title("Résultats de la recherche")
    tree_popup = ttk.Treeview(popup, columns=("ID", "Nom", "Statut", "Créateur"), show="headings")
    for col in ("ID", "Nom", "Statut", "Créateur"):
        tree_popup.heading(col, text=col)
        tree_popup.column(col, width=150)
    tree_popup.pack(padx=10, pady=10, fill="both", expand=True)
    for row in rows:
        tree_popup.insert("", "end", values=row)

# Interface principale
root = tk.Tk()
root.title("GLPI Viewer")

# Chargement et affichage du logo
logo_image = Image.open("logo_glpi_tag.png")
logo_image = logo_image.resize((200, 80), Image.Resampling.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(root, image=logo_photo, bg="white")
logo_label.image = logo_photo
logo_label.pack(pady=10)

# Arbre des tickets
tree = ttk.Treeview(root, columns=("ID", "Nom", "Statut", "Créateur"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
tree.pack(padx=10, pady=10, fill="both", expand=True)
tree.bind("<Double-1>", show_description)

# Recherche
frame_recherche = tk.Frame(root)
frame_recherche.pack(padx=10, pady=5)
tk.Label(frame_recherche, text="Recherche (nom / ID / créateur):").pack(side=tk.LEFT)
entry_recherche = tk.Entry(frame_recherche)
entry_recherche.pack(side=tk.LEFT)
tk.Button(frame_recherche, text="Rechercher", command=rechercher_ticket).pack(side=tk.LEFT)

# Modification du statut
frame_statut = tk.Frame(root)
frame_statut.pack(padx=10, pady=5)
tk.Label(frame_statut, text="Nouveau statut:").pack(side=tk.LEFT)
statut_combo = ttk.Combobox(frame_statut, values=["Nouveau", "En attente", "Résolu"])
statut_combo.pack(side=tk.LEFT)
tk.Button(frame_statut, text="Modifier le statut", command=modifier_statut).pack(side=tk.LEFT)

# Création de ticket
frame_creation = tk.Frame(root)
frame_creation.pack(padx=10, pady=10)

tk.Label(frame_creation, text="Nom du ticket:").grid(row=0, column=0)
entry_nom_ticket = tk.Entry(frame_creation)
entry_nom_ticket.grid(row=0, column=1)

tk.Label(frame_creation, text="ID Créateur:").grid(row=1, column=0)
entry_id_createur = tk.Entry(frame_creation)
entry_id_createur.grid(row=1, column=1)

tk.Label(frame_creation, text="Catégorie ID:").grid(row=2, column=0)
entry_categorie = tk.Entry(frame_creation)
entry_categorie.grid(row=2, column=1)

tk.Label(frame_creation, text="Type (0=Incident, 1=Demande):").grid(row=3, column=0)
entry_type = tk.Entry(frame_creation)
entry_type.grid(row=3, column=1)

tk.Label(frame_creation, text="Attribué à (ID):").grid(row=4, column=0)
entry_attribue = tk.Entry(frame_creation)
entry_attribue.grid(row=4, column=1)

tk.Label(frame_creation, text="Priorité (1 à 5):").grid(row=5, column=0)
entry_priorite = tk.Entry(frame_creation)
entry_priorite.grid(row=5, column=1)

tk.Button(frame_creation, text="Créer un ticket", command=creer_ticket).grid(row=6, column=0, columnspan=2, pady=10)

# Lancement
charger_tickets()
root.mainloop()
