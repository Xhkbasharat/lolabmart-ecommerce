
<div align="center">

# 🍃 LolabMart

### Your Valley. Your Marketplace.

**A dedicated digital marketplace for Lolab Valley, Kupwara.**

Discover local products. Support local sellers. Strengthen our valley.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web_Framework-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 🌿 About LolabMart

LolabMart is a community-focused e-commerce platform built exclusively for **Lolab Valley, Kupwara**.

Its purpose is to bring local sellers and customers together through a dedicated online marketplace where products genuinely offered by people and businesses from Lolab Valley can be discovered.

Unlike general-purpose marketplaces, LolabMart has a clear geographical identity and a focused mission: supporting local entrepreneurship and making local products easier to access.

> **Our vision:** Give Lolab Valley's local marketplace a digital home.

## ✨ Key Features

| Module | Features |
|---|---|
| 🛍️ Customer | Registration, login, product browsing and search |
| 🛒 Shopping | Cart management and checkout |
| 📦 Orders | Order placement and order history |
| 🏪 Seller | Seller dashboard and product listings |
| 🛡️ Admin | Protected dashboard and marketplace overview |
| 📱 Interface | Responsive layout for mobile and desktop |

## 🧺 Marketplace Categories

- 🌱 Local Produce
- 🧶 Handmade Crafts
- 🍯 Food Products
- 🧵 Clothing & Textiles
- 📦 Other locally offered products

All listings are intended for products genuinely offered by sellers from Lolab Valley.

## 🎨 Project Identity

| Element | Identity |
|---|---|
| Project | LolabMart |
| Tagline | Your Valley. Your Marketplace. |
| Location | Lolab Valley, Kupwara |
| Primary colour | Natural Forest Green |
| Secondary colour | Warm Cream |
| Mission | Support local sellers and entrepreneurship |

## 🧰 Technology Stack

**Backend**
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF

**Frontend**
- HTML5
- CSS3
- JavaScript

**Database**
- PostgreSQL
- SQLite for local development

**Deployment**
- Gunicorn
- Render

## 📁 Project Structure

```text
lolabmart/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── products.html
│   ├── product_detail.html
│   ├── register.html
│   ├── login.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   ├── seller_dashboard.html
│   ├── create_product.html
│   └── admin_dashboard.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/lolabmart.git
```

### 2. Open the project directory

```bash
cd lolabmart
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Set the following variables in your environment:

```env
SECRET_KEY=your-secure-secret-key
DATABASE_URL=sqlite:///lolabmart.db
```

For production, use PostgreSQL and a securely generated secret key.

### 5. Run the application

```bash
python app.py
```

### 6. Open the website

```text
http://127.0.0.1:5000
```

## 🔐 Security

- Password hashing through Werkzeug.
- Session-based authentication.
- Role-based access for customers, sellers and administrators.
- CSRF protection for forms.
- Seller ownership checks for product management.
- Server-side stock validation during checkout.

## 🚀 Future Roadmap

- [ ] Verified Lolab Valley seller profiles.
- [ ] Secure product image uploads.
- [ ] Online payment integration.
- [ ] Order tracking and delivery management.
- [ ] Customer reviews and ratings.
- [ ] Seller analytics dashboard.
- [ ] Improved admin moderation tools.
- [ ] Authentic Lolab Valley photography and branding.

## ⚠️ Current Project Limitations

- Online payment processing is not yet implemented.
- Delivery arrangements require separate confirmation.
- Production deployment requires secure environment configuration.
- Database migrations and administrator provisioning should be configured before production use.

## 🤝 Project Philosophy

LolabMart is built around one simple principle:

**Local sellers deserve a dedicated digital marketplace.**

The platform is exclusively focused on Lolab Valley and aims to help its local businesses reach more customers.

---

<div align="center">

### 🍃 LOLABMART

**Your Valley. Your Marketplace.**

*Built with a vision to support Lolab Valley.*

</div>
