# Business Management System (CRM/ERP)

A complete, production‑ready web‑based business management platform for service‑based companies. Manage customers, service jobs, inventory, finances, team performance, quotations, and reports from a single dashboard. **Live in production** at [Aquashine Limited](https://crm-erp-system.onrender.com).

## 🚀 Live Demo

🔗 **Production URL:** [https://crm-erp-system.onrender.com](https://crm-erp-system.onrender.com)  
*Login:* `admin` / `admin123` (demo credentials – please change after first login)

---

## ✨ Features

### Core Modules
- **Dashboard** – Real‑time business metrics and KPIs (unassigned jobs, pending payments, stock valuation, etc.)
- **Job / Service Management** – Full lifecycle: create, assign to technician, track status, close, and record payments
- **Customer Management** – Centralised database with type classification (Individual, Company, Reseller) and service history
- **Inventory Control** – Manage items and products, track stock levels, automatic deduction on job completion
- **Financial Tracking** – Record payments (Cash, Mpesa, Cheque, Bank Transfer), track revenue and pending balances
- **Team Management** – Technician database, assignment tracking, performance metrics

### Advanced Features
- **Project Management** – Track projects with status, budgets, and associated job cards
- **Service Calls** – Log and resolve customer service requests with priority levels
- **AMC Contracts** – Manage annual maintenance contracts and schedule service visits
- **Quotations** – Generate professional quotes with margin calculation (cost price, gross profit, margin %), convert to job card on approval
- **Reports** – Financial, stock, customer, technician, and job card reports with date filters
- **Export** – Excel (XLSX) and CSV export for job cards, customers, and inventory
- **PDF Generation** – Download job cards, quotations, invoices, financial and stock reports (via PDFShift API)
- **Planner / Scheduler** – Calendar view for events, tasks, and pending jobs
- **Audit Log** – Complete user action tracking (admin only)
- **Role‑Based Access Control** – Admin, Manager, Accounts, Projects, Sales – each with tailored permissions

### Recent Enhancements
- **SMS Notifications** – Automated messages (assignment, completion, payment) via Africa’s Talking API
- **Dynamic Footer** – Current year automatically updates across all pages
- **Production Cloud Deployment** – Hosted on **Render** with **TiDB Cloud** (MySQL‑compatible database)

---

## 🛠️ Tech Stack

| Category       | Technologies                                                                 |
|----------------|------------------------------------------------------------------------------|
| **Backend**    | Python 3.12, Flask, Waitress (production WSGI)                              |
| **Database**   | MySQL (TiDB Cloud Serverless – fully compatible)                            |
| **Frontend**   | Bootstrap 5, JavaScript (ES6), jQuery, DataTables, FullCalendar             |
| **APIs**       | PDFShift (PDF generation), Africa’s Talking (SMS)                           |
| **Deployment** | Render (web service), GitHub (CI/CD)                                        |
| **Libraries**  | openpyxl (Excel export), pdfkit, requests, mysql‑connector‑python           |

---

## 📦 Installation (Local Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/lemayian23/CRM-ERP-system.git
   cd CRM-ERP-system