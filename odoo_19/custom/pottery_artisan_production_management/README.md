# 🏺 Village Pottery & Artisan Production Management System

## Project Overview

The **Village Pottery & Artisan Production Management System** is a comprehensive Odoo 19 custom module designed to digitally manage and streamline the complete pottery production and business workflow.

The system connects traditional village pottery production with modern business management. It helps manage artisans, pottery products, raw materials, kilns, production processes, quality checks, recovery processes, customer orders, payments, deliveries, settlements, reports, and customer-facing website operations.

The project provides both:

* **Backend Management System** for administrators and employees.
* **Customer Website** for browsing pottery products, placing orders, and tracking orders.

---

# 📌 Project Information

| Item                 | Details                                                |
| -------------------- | ------------------------------------------------------ |
| **Project Name**     | Village Pottery & Artisan Production Management System |
| **Platform**         | Odoo 19                                                |
| **Backend Language** | Python                                                 |
| **Database**         | PostgreSQL                                             |
| **Frontend**         | XML, QWeb, HTML, CSS                                   |
| **Module Type**      | Custom Odoo Module                                     |
| **Project Category** | Production & Business Management                       |
| **Database Name**    | `artisan_db`                                           |

---

# 🎯 Project Objective

The main objective of this project is to create a centralized system for managing the complete lifecycle of pottery production.

The system helps users to:

* Manage village artisans and their production activities.
* Manage pottery products and raw materials.
* Track raw material consumption during production.
* Manage kiln availability and capacity.
* Control the complete production workflow.
* Perform quality inspections.
* Handle rejected quantities and recovery processes.
* Manage customer orders and payments.
* Manage deliveries and settlements.
* Generate professional reports.
* Provide customers with an online pottery website.
* Allow customers to track their orders.

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │   CUSTOMER WEBSITE  │
                    └──────────┬──────────┘
                               │
                Browse / Order / Track Order
                               │
                               ▼
                    ┌─────────────────────┐
                    │  CUSTOMER ORDERS   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     PRODUCTION      │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
        Raw Materials       Artisans           Kilns
                               │
                               ▼
                    ┌─────────────────────┐
                    │   QUALITY CHECK     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ RECOVERY PROCESS    │
                    │   (If Required)    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      DELIVERY       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      PAYMENT        │
                    └─────────────────────┘
```

---

# 📦 Main Modules and Features

## 👨‍🎨 1. Artisan Management

The Artisan Management module manages information related to village artisans.

### Features

* Artisan profile management.
* Contact information.
* Artisan code generation.
* Skill tracking.
* Experience tracking.
* Active and inactive artisan management.
* Production assignment.

---

## 🏺 2. Pottery Product Management

This module manages all pottery products available for production and customer orders.

### Features

* Product code generation.
* Product name and type.
* Selling price.
* Product cost.
* Active/inactive products.
* Raw material requirements.
* Product-wise material quantity configuration.

---

## 🧱 3. Raw Material Management

The Raw Material module manages materials required for pottery production.

### Features

* Raw material information.
* Available quantity tracking.
* Unit and unit cost.
* Material cost calculation.
* Stock validation during production.

---

## 🔥 4. Kiln Management

The Kiln Management module manages pottery kilns used during the production process.

### Features

* Kiln reference generation.
* Kiln type management.
* Capacity management.
* Kiln availability tracking.
* Maintenance status.
* In-use status validation.
* Production capacity validation.

### Kiln Types

* Traditional
* Wood
* Gas
* Electric

---

# ⚙️ 5. Production Management

Production Management is the core functionality of the system.

### Production Workflow

```text
DRAFT
  ↓
IN PRODUCTION
  ↓
DRYING
  ↓
IN KILN
  ↓
QUALITY CHECK
  ↓
COMPLETED
```

### Features

* Automatic production reference generation.
* Product selection.
* Artisan assignment.
* Customer order linking.
* Planned quantity management.
* Produced quantity tracking.
* Rejected quantity tracking.
* Passed quantity calculation.
* Wastage percentage calculation.
* Final good quantity calculation.
* Material cost calculation.
* Labour cost management.
* Total production cost calculation.
* Raw material consumption validation.

---

# ☀️ 6. Drying Management

The system manages the drying stage of pottery production.

### Features

* Drying start date.
* Expected drying days.
* Expected drying completion date.
* Drying notes.
* Validation before moving to the kiln stage.

---

# 🔍 7. Quality Management

The Quality Management module ensures that produced pottery meets the required quality standards.

### Features

* Automatic quality check creation.
* Inspector assignment.
* Quality check date.
* Passed quantity.
* Rejected quantity.
* Quality status.
* Production completion validation.

---

# 🔄 8. Recovery Management

If the required production quantity is not achieved, the system supports a recovery process.

### Recovery Workflow

```text
Quality Result
      ↓
Pending Quantity Detected
      ↓
Recovery Required
      ↓
Start Recovery
      ↓
Recovery Quality Check
      ↓
Recovery Completed
```

### Features

* Automatic pending quantity calculation.
* Recovery requirement detection.
* Recovery quantity management.
* Recovery status tracking.
* Recovery passed quantity.
* Final good quantity calculation.

---

# 🛒 9. Customer Order Management

The system manages customer pottery orders.

### Features

* Automatic order reference generation.
* Customer selection.
* Multiple order lines.
* Product selection.
* Quantity management.
* Unit price.
* Subtotal calculation.
* Total quantity calculation.
* Total amount calculation.
* Order status tracking.

---

# 💳 10. Payment Management

The system tracks customer payment status.

### Payment Status

* Unpaid
* Partially Paid
* Paid

### Features

* Payment amount tracking.
* Automatic payment status calculation.
* Partial payment support.
* Payment verification before final delivery.

---

# 🚚 11. Delivery Management

The Delivery Management module controls the final delivery process.

### Delivery Workflow

```text
DRAFT
  ↓
READY
  ↓
IN TRANSIT
  ↓
DELIVERED
```

### Features

* Delivery reference generation.
* Customer order linking.
* Delivery quantity validation.
* Vehicle number management.
* Delivery status tracking.
* Customer payment verification.
* Production settlement verification.
* Delivery notification emails.

---

# 💰 12. Artisan Settlement Management

The system manages settlements related to completed production work.

### Features

* Production-based settlement.
* Settlement amount management.
* Payment status.
* Settlement verification before final delivery.

---

# 📊 13. Reports

The project includes professional reports for business analysis and documentation.

### Available Reports

* Production PDF Report.
* Production XLSX Report.
* Production cost information.
* Raw material details.
* Quality details.
* Production summary.

---

# 🌐 14. Customer Website

The project includes a customer-facing pottery website.

The website allows customers to interact with the pottery business without accessing the Odoo backend.

### Website Features

* Professional pottery home page.
* Product collection.
* Product browsing.
* Product order form.
* Customer order creation.
* Order success page.
* Order tracking.
* Payment status display.
* Production and delivery progress tracking.
* Contact page.

---

# 🌍 Website URLs

## 🏠 Home Page

```text
http://localhost:10511/pottery
```

## 🏺 Collection

```text
http://localhost:10511/pottery/collection
```

## 🛒 Place Order

```text
http://localhost:10511/pottery/order
```

## 🔎 Track Order

```text
http://localhost:10511/pottery/track-order
```

---

# 🔎 Order Tracking Flow

Customers can track their pottery order using:

* Order Reference.
* Customer Email Address.

### Tracking Flow

```text
Customer
   ↓
Enter Order Reference
   ↓
Enter Email
   ↓
System Validates Order
   ↓
Display Order Details
```

The customer can view:

* Order reference.
* Order date.
* Customer details.
* Payment status.
* Order status.
* Production progress.
* Delivery progress.
* Ordered products.
* Total amount.

---

# 🔐 Security

The system includes access control and security management.

### Security Features

* Model access rights.
* User access restrictions.
* Controlled backend operations.
* Public website routes with controlled record access.
* `sudo()` access used for authorized website operations.

---

# 🔄 Automated Features

The project includes several automated business operations.

### Automation Examples

* Automatic sequence generation.
* Automatic raw material line creation.
* Automatic raw material consumption.
* Automatic cost calculation.
* Automatic passed quantity calculation.
* Automatic wastage calculation.
* Automatic final good quantity calculation.
* Automatic payment status calculation.
* Automatic production delay checking.
* Automatic kiln availability updates.

---

# ⏰ Scheduled Actions

The system supports automated scheduled operations.

### Production Delay Check

The scheduled action identifies productions that remain in progress beyond the expected time period.

Delayed productions are automatically marked for management attention.

---

# 🧮 Important Business Validations

The system contains multiple validations to ensure correct business operations.

### Production

* Planned quantity must be greater than zero.
* Produced quantity cannot be negative.
* Rejected quantity cannot exceed produced quantity.
* Labour cost cannot be negative.

### Kiln

* Kiln capacity must support production quantity.
* Kilns under maintenance cannot be assigned.
* Inactive kilns cannot be assigned.
* Busy kilns cannot be used by another active production.

### Delivery

* Delivery quantity must be greater than zero.
* Delivery quantity cannot exceed the available order quantity.
* Only confirmed orders can proceed for delivery.
* Payment must be completed before final delivery.

### Recovery

* Recovery quantity cannot exceed pending quantity.
* Recovery passed quantity cannot exceed recovery quantity.

---

# 🛠️ Technology Stack

```text
Odoo 19
│
├── Python
├── PostgreSQL
├── XML
├── QWeb
├── HTML
├── CSS
└── JavaScript
```

---

# 📁 Module Structure

```text
pottery_artisan_production_management/
│
├── __init__.py
├── __manifest__.py
│
├── models/
│   ├── artisan_information.py
│   ├── pottery_product_information.py
│   ├── raw_material_information.py
│   ├── production_information.py
│   ├── kiln_information.py
│   ├── quality_information.py
│   ├── customer_order_information.py
│   ├── delivery_information.py
│   └── settlement_information.py
│
├── views/
│
├── controllers/
│
├── wizard/
│
├── reports/
│
├── security/
│
├── data/
│
├── static/
│
└── README.md
```

---

# ▶️ How to Run the Project

## Step 1: Open Terminal

Open the terminal in your Odoo project environment.

## Step 2: Go to the Odoo Directory

```text
/home/bambus/odoo/workspace/odoo_19
```

## Step 3: Run the Odoo Server

Use the appropriate Odoo configuration and database.

```bash
./odoo-bin -c odoo.conf -d artisan_db
```

## Step 4: Open Odoo

Open the browser and visit:

```text
http://localhost:10511
```

## Step 5: Open the Pottery Website

```text
http://localhost:10511/pottery
```

---

# 🔄 Complete Business Workflow

```text
CUSTOMER ORDER
       ↓
ORDER CONFIRMATION
       ↓
PRODUCTION PLANNING
       ↓
RAW MATERIAL VALIDATION
       ↓
PRODUCTION STARTED
       ↓
DRYING
       ↓
KILN PROCESS
       ↓
QUALITY CHECK
       ↓
RECOVERY (IF REQUIRED)
       ↓
PRODUCTION COMPLETED
       ↓
DELIVERY READY
       ↓
IN TRANSIT
       ↓
PAYMENT VERIFIED
       ↓
DELIVERED
```

---

# 🌟 Key Highlights

⭐ Complete pottery production lifecycle management.

⭐ Traditional artisan business combined with modern technology.

⭐ Customer-facing website integration.

⭐ Real-time order tracking.

⭐ Payment status tracking.

⭐ Production recovery management.

⭐ Kiln capacity and availability validation.

⭐ Automated calculations.

⭐ Professional PDF and XLSX reporting.

⭐ Email notifications.

⭐ Odoo ORM and workflow implementation.

---

# 🏺 Conclusion

The **Village Pottery & Artisan Production Management System** provides a complete digital solution for managing traditional pottery production and business operations.

The system integrates artisan management, production planning, raw materials, kilns, quality control, recovery, customer orders, payments, deliveries, settlements, reports, and a customer-facing website into one centralized Odoo platform.

This project demonstrates how traditional village-based artisan businesses can be supported and modernized using **Odoo 19 and modern business management technology**.

---

## 👩‍💻 Project Developer

**Project:** Village Pottery & Artisan Production Management System

**Platform:** Odoo 19

**Type:** Custom Odoo Module

**Year:** 2026
