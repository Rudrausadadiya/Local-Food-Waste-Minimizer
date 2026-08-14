# Local Food Waste Minimizer

A production-grade, full-stack application designed to rescue surplus food from local businesses and redistribute it to nearby customers and non-profit organizations (NGOs) before it expires.

---

## 🌟 Overview & Features

- **Multi-Role Portals**:
  - **Vendors**: Manage inventory, publish discounted marketplace listings, track orders, counter-verify claim codes, and handle NGO donation requests.
  - **Customers**: Search and reserve surplus food within a 15 km radius, view scannable QR claim codes, manage orders, and track pickup timers.
  - **NGOs**: Browse and claim free surplus food donations from approved vendors, manage distribution pickups, and track community impact.
  - **Platform Admins**: Approve business registrations (Vendors & NGOs), monitor system listings, manage platform users, and review cross-module analytics.
- **Geofencing & Privacy Isolation**: Haversine 15.0 km radius enforcement; absolute data isolation ensuring Vendors and NGOs access only their own business credentials and data.
- **Real-Time Analytics & Data Quality**: Cross-module KPI aggregations, automated anomaly detection (negative stock, orphaned orders, unlinked reservations), report generation, and dataset exports.

---

## 🏗️ Technical Architecture

- **Backend**: Django 5 REST Framework (Python 3.13), PostgreSQL, Celery/Redis background task queues.
  - Layered Architecture: `Models → Repositories → Services → Views → Serializers`.
- **Frontend**: React 18 (Vite, Tailwind CSS, Framer Motion), Zustand, TanStack React Query, React Hook Form + Zod, Lucide React icons.
  - Optimized Bundle Splitting: Heavy vendor libraries (`recharts`, `leaflet`, `framer-motion`) split into dedicated manual chunks.

---

## 🚀 Quick Setup Instructions

For step-by-step installation, environment setup, and execution commands, refer to the individual component guides:

- **[Backend Setup & API Guide](backend/README.md)**
- **[Frontend Setup & Development Guide](frontend/README.md)**

---

## 📋 Architectural Decisions & Scope Notes

- **Analytics Module**: `DashboardService`, `DataQualityService`, `DatasetService`, and `ReportService` run real ORM queries across orders, inventory, and reservations.
- **Notification Providers**:
  - **Email**: Integrated using Django's built-in mail framework (`send_mail()`), defaulting to `django.core.mail.backends.console.EmailBackend` for zero-config local development.
  - **Webhooks**: Performs real HTTP POST requests via `requests.post()` with status verification.
  - **SMS & Push Notifications**: Intentionally remain simulated with docstrings and provider classes (`SMSProvider`, `PushProvider`) designed for seamless drop-in replacement upon configuring paid Twilio/FCM accounts.

  @
  confirmed pickups are not showing in the impact page 