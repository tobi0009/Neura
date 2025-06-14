## 🤖 Neura AI Assistant Platform

Neura is a Django-powered backend for creating smart assistants that respond to WhatsApp messages using a custom knowledge base. It uses semantic search to find the most relevant answers and falls back to Gemini for generative replies when necessary. Built as a side project, Neura focuses on simplicity, private use, and learning.

---

## 🚀 Features

- **Knowledge Base:** Upload and manage knowledge entries per assistant.
- **Semantic Search:** Fast, relevant answers using vector embeddings.
- **Gemini LLM Fallback:** Uses Google Gemini for generative answers when knowledge base is insufficient.
- **WhatsApp Integration:** Webhook for Twilio WhatsApp, setup instructions, and group support.
- **User Authentication:** JWT-based registration, login, password reset, and email verification.
- **Admin Dashboard:** Powerful Django admin for assistants and knowledge entries.
- **REST API:** Fully documented endpoints for all operations.
- **Media Support:** Upload avatars for assistants.
- **Testing:** Comprehensive test suite for endpoints and logic.

---

## 🏗️ Project Structure

```
neura/
├── assistants/         # Assistant models, views, admin, semantic search, Gemini integration
├── userauth/           # User registration, login, password reset, email verification
├── whatsapp/           # WhatsApp webhook and setup instructions
├── neura/              # Django project settings, URLs, WSGI/ASGI
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## ⚡ Quickstart

**1. Clone the Repository**

```bash
git clone https://github.com/OnatadeTobi/neura.git
cd neura
```

**2. Install Dependencies**

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**3. Environment Variables**

Create a `.env` file in the project root with the following keys:

```
SECRET_KEY=your-django-secret
DEBUG=True
DB_NAME=your_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=your_from_email
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SOCIAL_AUTH_PASSWORD=your_social_auth_password
```

**4. Database Setup**

```bash
python manage.py migrate
```

**5. Create Superuser**

```bash
python manage.py createsuperuser
```

**6. Run the Server**

```bash
python manage.py runserver
```

---

## 🗄️ Database Choice

**PostgreSQL is the default database for Neura.**

- **Why PostgreSQL?**  
  Neura uses Django's `ArrayField` for efficient storage and querying of vector embeddings and other array data. `ArrayField` is only supported by PostgreSQL, making it the best choice for features like semantic search and storing embeddings natively.

- **Alternative (SQLite or other DBs):**  
  If you want to use Django's default SQLite database (or another DB that doesn't support `ArrayField`), you must change all `ArrayField` usages in your models to `JSONField`.  
  > **Note:** `JSONField` is supported by both PostgreSQL and SQLite (Django 3.1+), but you may lose some performance and advanced querying capabilities for arrays.

- **How to switch:**  
  1. Replace the `ArrayField` fields in the assistants models with `JSONField`.
  2. Run migrations:  
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```
  3. Update any code that relies on array-specific queries to use JSON-compatible logic.

- **PostgreSQL Setup:**  
  Make sure you have a running PostgreSQL instance and your `.env` is configured as shown in the Quickstart section.

---

## 🛠️ Usage

### **Assistant Management**

- Create assistants via the API or Django admin.
- Upload knowledge base entries for each assistant.
- Assign unique tag names for WhatsApp mentions.

### **WhatsApp Integration**

- Send a message to your Twilio WhatsApp number.
- Mention the assistant using `@tag_name: your question`.
- The assistant replies using semantic search or Gemini fallback.

### **API Authentication**

- Register and login to obtain JWT tokens.
- Use `Authorization: Bearer <token>` for authenticated endpoints.

---

## 📚 API Endpoints

### **Auth**

- `POST /api/auth/register/` — Register user
- `POST /api/auth/login/` — Login user
- `POST /api/auth/verify-email/` — Verify email with OTP
- `POST /api/auth/password-reset/` — Request password reset
- `POST /api/auth/set-new-password/` — Set new password

### **Assistants**

- `GET/POST /api/assistants/` — List/create assistants
- `GET/PUT/DELETE /api/assistants/<id>/` — Assistant detail/update/delete

### **Knowledge Base**

- `GET/POST /api/assistants/knowledge/?assistant=<id>` — List/create entries
- `GET/PUT/DELETE /api/assistants/knowledge/<id>/` — Entry detail/update/delete

### **Answer Query**

- `GET /api/assistants/answer/?query=...&assistant_id=...` — Get answer from assistant

### **WhatsApp**

- `GET /api/whatsapp/setup/<assistant_id>/` — Get WhatsApp setup instructions
- `POST /api/whatsapp/webhook/` — Twilio webhook for WhatsApp messages

---

## 🧪 Running Tests

```bash
python manage.py test assistants.tests
```

---

## 🖥️ Admin Dashboard

- Visit `/admin/` and login with your superuser credentials.
- Manage users, assistants, and knowledge base entries.
- View avatars, knowledge entry counts, and more.

---

## 📝 Example WhatsApp Usage

**1. Send a message to your Twilio WhatsApp number**  
**2. Send a message:** `@your_tag_name: What do you know about me?`  
**3. The assistant will reply based on your knowledge base or Gemini.**

---

## 🧩 Extending

- Add new platforms by extending the `Assistant` model and webhook logic.
- Integrate more LLMs or embedding models as needed.

---

## 🛡️ Security Notes

- Never commit your `.env` file or secrets.
- Use HTTPS and secure your Twilio webhook endpoint in production.
- Set `DEBUG=False` in production.

---

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue to discuss your ideas.

---

## 🙏 Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Twilio](https://www.twilio.com/)
- [Google Gemini](https://ai.google.dev/)
- [Sentence Transformers](https://www.sbert.net/)
