# BorrowBox Backend

A single-file FastAPI backend for the BorrowBox rent/buy marketplace.
Everything lives in `main.py` on purpose — simple functions, no
service/repository layers, easy to explain in a viva.

## Stack

- **FastAPI** + **Uvicorn** — web framework / server
- **MongoDB Atlas** (via PyMongo) — application data (`users`, `products`,
  `transactions`, `categories`)
- **Cloudinary** — image storage (only image URLs are stored in MongoDB)
- **JWT** (`python-jose`) — authentication
- **bcrypt** (`passlib`) — password hashing

## 1. Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Environment variables

Copy `.env.example` to `.env` and fill in your real values:

```bash
cp .env.example .env
```

You'll need:

- A free **MongoDB Atlas** cluster → connection string for `MONGO_URI`
- A free **Cloudinary** account → cloud name, API key, API secret
- Any long random string for `JWT_SECRET_KEY`

## 3. Run locally

```bash
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Interactive docs (Swagger UI)
are automatically available at `http://localhost:8000/docs` — useful
for testing endpoints without the frontend.

## 4. Categories

On startup, if the `categories` collection is empty, it's automatically
seeded with: Property, Furniture, Electronics, Vehicles, Gaming,
Cameras, Appliances, Tools, Sports, Study, Other.

## 5. Deploying to Render

1. Push this repo to GitHub.
2. On Render, create a new **Web Service** pointing at the `backend/` folder.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add the same environment variables from `.env` in Render's dashboard.

Then update `BorrowBox_API_BASE` in the frontend (see `frontend/app.js`,
or set `window.BorrowBox_API_BASE` before `app.js` loads) to your Render URL.

## API summary

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/auth/register | - | Create an account |
| POST | /api/auth/login | - | Log in, get JWT |
| GET | /api/auth/me | any | Current user |
| GET | /api/categories | - | List categories |
| POST | /api/upload | seller | Upload image to Cloudinary |
| POST | /api/products | seller | Create listing |
| GET | /api/products | - | Browse/search listings |
| GET | /api/products/{id} | - | Listing details |
| PUT | /api/products/{id} | seller (owner) | Edit listing |
| DELETE | /api/products/{id} | seller (owner) | Deactivate listing |
| GET | /api/seller/products | seller | My listings |
| GET | /api/seller/transactions | seller | Transactions on my listings |
| POST | /api/transactions/buy | customer | Buy a listing |
| POST | /api/transactions/rent | customer | Rent a listing |
| GET | /api/transactions/my | customer | My transactions |
| PUT | /api/transactions/{id}/status | seller (owner) | Approve/cancel/complete |

Prices are always read from the database, never trusted from the client.
Real payments are not implemented — transactions start as `pending` and
the seller approves/cancels/completes them manually.
# borrowbox
# borrowbox
# borrowbox
# borrowbox
# borrowbox
# borrowbox
# borrowbox
# borrowbox
# borrowbox
# borrowbox
# borrowbox
# borrowbox-backend
# borrowbox-backend
# borrowbox-backend
