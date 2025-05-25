# Exuni Backend

**Exuni Backend** is the core engine behind [Exuni](https://exuni.ir) – a scalable, modular, and secure e-commerce platform designed to support product-based affiliate marketing with powerful inventory, payment, and discount systems.

---

## 🚀 Features

- ⚙️ Modular architecture with Django & Django REST Framework
- 🛒 Advanced product & inventory management
- 💳 Payment gateway integration (e.g., Zarinpal)
- 🎯 Powerful discount and shipping engine (event-driven, state machine-based)
- 🧾 Financial wallet system with transaction logging
- 📦 Order and fulfillment tracking
- 🔍 Smart autocomplete search (products, brands, categories)
- 📊 Reporting & analytics for product views and user actions
- 🔐 Role-based access control and secure API design
- 🌍 Fully ready for localization (i18n/l10n)

---

## 🧱 Tech Stack

- **Backend**: Python, Django, Django REST Framework
- **Database**: PostgreSQL
- **Payment**: Zarinpal (abstracted for multi-gateway support)
- **Search**: PostgreSQL Full-Text Search + Trigram
- **Architecture**: Scalable, event-driven, audit-logged

---

## 📦 Installation (Development)

```bash
git clone https://github.com/your-username/exuni-backend.git
cd exuni-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Running Tests

```bash
pytest
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📬 Contact

For inquiries or collaboration:
📧 **team@exuni.ir**  
🌐 [exuni.ir](https://exuni.ir)

---

> Designed with care to empower affiliate-first commerce in Iran and beyond.
