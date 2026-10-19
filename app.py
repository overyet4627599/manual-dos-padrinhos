import os, sqlite3, secrets
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "loja.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'Personalizados',
            description TEXT NOT NULL DEFAULT '',
            price REAL NOT NULL DEFAULT 0,
            image TEXT NOT NULL DEFAULT '',
            options TEXT NOT NULL DEFAULT 'Nome, Cor, Tema',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL DEFAULT '',
            delivery_method TEXT NOT NULL DEFAULT 'Combinar entrega',
            address TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            items_json TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Novo pedido',
            created_at TEXT NOT NULL
        );
        """)
        defaults = {
            "store_name": "Ateliê Criativo",
            "tagline": "Personalizados feitos com carinho",
            "whatsapp": "",
            "instagram": "",
            "address": "",
            "welcome_text": "Transforme suas ideias em presentes únicos.",
            "primary_color": "#8b3157",
            "pix_key": "",
            "delivery_info": "Prazo e entrega combinados após a confirmação do pedido."
        }
        for key, value in defaults.items():
            con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (key, value))
        count = con.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        if count == 0:
            now = datetime.now().isoformat(timespec="minutes")
            samples = [
                ("Caneca personalizada", "Canecas", "Caneca de 325 ml personalizada com nome, frase ou foto.", 25.00, "", "Nome, Cor, Tema, Texto ou foto"),
                ("Camiseta personalizada", "Vestuário", "Camiseta personalizada para datas especiais, eventos e presentes.", 45.00, "", "Tamanho, Cor, Nome, Tema"),
                ("Azulejo decorativo", "Decoração", "Peça decorativa personalizada para presentear.", 30.00, "", "Tamanho, Texto, Tema"),
                ("Chaveiro personalizado", "Acessórios", "Chaveiro personalizado com arte, nome ou foto.", 8.00, "", "Modelo, Nome, Tema")
            ]
            con.executemany("""INSERT INTO products(name,category,description,price,image,options,active,created_at)
                VALUES(?,?,?,?,?,?,1,?)""", [(*p, now) for p in samples])

def get_settings():
    with db() as con:
        return {r["key"]: r["value"] for r in con.execute("SELECT key,value FROM settings")}

def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapped

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_settings():
    return {"settings": get_settings(), "year": datetime.now().year}

@app.route("/")
def home():
    category = request.args.get("categoria", "").strip()
    with db() as con:
        if category:
            products = con.execute("SELECT * FROM products WHERE active=1 AND category=? ORDER BY id DESC", (category,)).fetchall()
        else:
            products = con.execute("SELECT * FROM products WHERE active=1 ORDER BY id DESC").fetchall()
        categories = [r["category"] for r in con.execute("SELECT DISTINCT category FROM products WHERE active=1 ORDER BY category")]
    return render_template("index.html", products=products, categories=categories, selected_category=category)

@app.route("/pedido", methods=["POST"])
def place_order():
    name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    delivery = request.form.get("delivery_method", "Combinar entrega")
    address = request.form.get("address", "").strip()
    notes = request.form.get("notes", "").strip()
    product_ids = request.form.getlist("product_id")
    if not name or not phone or not product_ids:
        flash("Informe seu nome, telefone e selecione pelo menos um produto.", "error")
        return redirect(url_for("home") + "#catalogo")

    items = []
    total = 0
    with db() as con:
        for pid in product_ids:
            try:
                product_id = int(pid)
                qty = max(1, min(100, int(request.form.get(f"qty_{pid}", "1"))))
            except (ValueError, TypeError):
                continue
            product = con.execute("SELECT * FROM products WHERE id=? AND active=1", (product_id,)).fetchone()
            if not product:
                continue
            custom = {}
            for option in [x.strip() for x in product["options"].split(",") if x.strip()]:
                val = request.form.get(f"option_{pid}_{option}", "").strip()
                if val:
                    custom[option] = val
            upload = request.files.get(f"art_{pid}")
            if upload and upload.filename and allowed_file(upload.filename):
                filename = secure_filename(upload.filename)
                unique = secrets.token_hex(5) + "_" + filename
                upload.save(os.path.join(UPLOAD_DIR, unique))
                custom["Arquivo enviado"] = unique
            subtotal = round(float(product["price"]) * qty, 2)
            items.append({
                "product_id": product["id"], "name": product["name"],
                "unit_price": float(product["price"]), "quantity": qty,
                "subtotal": subtotal, "customization": custom
            })
            total += subtotal
        if not items:
            flash("Não foi possível validar os produtos selecionados. Tente novamente.", "error")
            return redirect(url_for("home") + "#catalogo")
        con.execute("""INSERT INTO orders(customer_name,phone,email,delivery_method,address,notes,items_json,total,status,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (name, phone, email, delivery, address, notes, __import__("json").dumps(items, ensure_ascii=False),
             round(total, 2), "Novo pedido", datetime.now().isoformat(timespec="minutes")))
        order_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
    return render_template("order_success.html", order_id=order_id, customer_name=name, total=round(total, 2))

@app.route("/admin")
@admin_required
def admin_dashboard():
    import json
    with db() as con:
        products = con.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        orders = con.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 100").fetchall()
        total_orders = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        total_revenue = con.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE status!='Cancelado'").fetchone()[0]
        new_orders = con.execute("SELECT COUNT(*) FROM orders WHERE status='Novo pedido'").fetchone()[0]
    parsed_orders = []
    for o in orders:
        d = dict(o)
        try: d["items"] = json.loads(d["items_json"])
        except Exception: d["items"] = []
        parsed_orders.append(d)
    return render_template("admin.html", products=products, orders=parsed_orders,
                           total_orders=total_orders, total_revenue=total_revenue, new_orders=new_orders)

@app.route("/admin/setup", methods=["GET", "POST"])
def admin_setup():
    with db() as con:
        exists = con.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
    if exists:
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if len(username) < 3 or len(password) < 10:
            flash("Use um usuário com pelo menos 3 caracteres e uma senha com pelo menos 10 caracteres.", "error")
        elif password != confirm:
            flash("As senhas não coincidem.", "error")
        else:
            with db() as con:
                con.execute("INSERT INTO admins(username,password_hash) VALUES(?,?)",
                            (username, generate_password_hash(password)))
            flash("Administrador criado. Entre com suas credenciais.", "success")
            return redirect(url_for("admin_login"))
    return render_template("admin_setup.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_id"):
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with db() as con:
            admin = con.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("admin_dashboard"))
        flash("Usuário ou senha inválidos.", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin/produto/salvar", methods=["POST"])
@admin_required
def save_product():
    try:
        product_id = request.form.get("id", "").strip()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "Personalizados").strip() or "Personalizados"
        description = request.form.get("description", "").strip()
        price = float(request.form.get("price", "0").replace(",", "."))
        options = request.form.get("options", "").strip()
        active = 1 if request.form.get("active") == "on" else 0
        if not name or price < 0:
            raise ValueError()
    except (ValueError, TypeError):
        flash("Confira o nome e o preço do produto.", "error")
        return redirect(url_for("admin_dashboard") + "#produtos")
    image_path = request.form.get("current_image", "").strip()
    image = request.files.get("image")
    if image and image.filename and allowed_file(image.filename):
        filename = secrets.token_hex(5) + "_" + secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_DIR, filename))
        image_path = filename
    with db() as con:
        if product_id:
            con.execute("""UPDATE products SET name=?,category=?,description=?,price=?,image=?,options=?,active=? WHERE id=?""",
                        (name, category, description, price, image_path, options, active, int(product_id)))
            flash("Produto atualizado com sucesso.", "success")
        else:
            con.execute("""INSERT INTO products(name,category,description,price,image,options,active,created_at)
                        VALUES(?,?,?,?,?,?,?,?)""",
                        (name, category, description, price, image_path, options, active, datetime.now().isoformat(timespec="minutes")))
            flash("Produto cadastrado com sucesso.", "success")
    return redirect(url_for("admin_dashboard") + "#produtos")

@app.route("/admin/produto/<int:product_id>/excluir", methods=["POST"])
@admin_required
def delete_product(product_id):
    with db() as con:
        con.execute("DELETE FROM products WHERE id=?", (product_id,))
    flash("Produto excluído.", "success")
    return redirect(url_for("admin_dashboard") + "#produtos")

@app.route("/admin/pedido/<int:order_id>/status", methods=["POST"])
@admin_required
def update_order_status(order_id):
    status = request.form.get("status", "")
    allowed = {"Novo pedido", "Em produção", "Aguardando retirada", "Concluído", "Cancelado"}
    if status not in allowed:
        abort(400)
    with db() as con:
        con.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    flash(f"Status do pedido #{order_id} atualizado.", "success")
    return redirect(url_for("admin_dashboard") + "#pedidos")

@app.route("/admin/configuracoes", methods=["POST"])
@admin_required
def save_settings():
    keys = ["store_name", "tagline", "whatsapp", "instagram", "address", "welcome_text", "primary_color", "pix_key", "delivery_info"]
    with db() as con:
        for key in keys:
            value = request.form.get(key, "").strip()
            con.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
    flash("Configurações da loja salvas.", "success")
    return redirect(url_for("admin_dashboard") + "#configuracoes")

@app.route("/health")
def health():
    return {"status": "ok"}

@app.errorhandler(413)
def too_large(_error):
    flash("O arquivo é muito grande. O limite é 12 MB.", "error")
    return redirect(url_for("home") + "#catalogo")

init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))
