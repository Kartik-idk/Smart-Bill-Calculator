# Smart Bill Calculator

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-26%20Passing-brightgreen.svg)]()
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20External-success.svg)]()
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP%208-informational.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-quality, mathematically exact Command-Line Billing, Warranty Tracking & Invoicing system written in Python. 

Built originally as a collegiate Python mini-project for **ABC DIGITAL** and engineered into a robust, single-source-of-truth architecture adhering to exact decimal rounding guarantees (`ROUND_HALF_UP`), per-product warranty life-cycle management, and flexible EMI financing.

---

## 📌 Problem Statement

Standard retail billing scripts often suffer from three critical flaws:
1. **IEEE 754 Floating-Point Drift:** Using native floats (`0.1 + 0.2 = 0.30000000000000004`) causes 1-cent/1-paisa discrepancies in retail taxation and interest accrual.
2. **Fragile Terminal Formatting:** Fixed-width tables distort and break layout borders when product descriptions exceed arbitrary character limits.
3. **Lack of Lifecycle Services:** Basic calculators discard post-sale metadata, omitting per-item warranty tracking, customer record association, and flexible financing options (EMI).

**Smart Bill Calculator** solves these issues in a single, coherent, self-contained implementation with exact banking arithmetic using Python's standard library `Decimal`, dynamic column truncation, and clean invoice archiving.

---

## ✨ Key Features

- **💰 Exact Banking Precision:** Powered by Python's `decimal.Decimal` with `ROUND_HALF_UP` rounding to eliminate precision loss across Subtotals, Discounts, 18% GST, and EMI interest.
- **🧾 Complete Tax Invoicing:** Generates formatted 128-column GST tax invoices containing business headers, GSTIN, customer information, line-item totals, and payment breakdowns.
- **🛡️ Warranty Tracking & Status Lookup:**
  - Assigns unique serialized Warranty IDs (`<InvoiceNo>-<ItemIndex>`) to eligible products.
  - Computes exact calendar expiry dates handling leap years and month-end boundaries.
  - Interactive lookup tool to verify active versus expired warranty status in real time.
- **💳 Flexible EMI Financing:**
  - Automated EMI qualification for invoices of Rs. 5,000.00 and above.
  - Supports 3, 6, 9, or 12-month terms with custom annual interest rate calculation and monthly installment breakdown.
- **🛡️ Bulletproof Input Validation:** Traps non-numeric inputs, negative amounts, out-of-range percentages, and terminal signals (`Ctrl+C`, `EOFError`) without unhandled stack traces.
- **💾 Organized Invoice Persistence:** Automatically archives generated invoices in UTF-8 plain text into an isolated `invoices/` directory.
- **⚡ Zero External Dependencies:** 100% standard library Python for instant execution on any system.

---

## 🖥️ Terminal Interface Preview

```
================================================================================================================================
                                                          ABC DIGITAL                                                           
                                             MG Road, Bengaluru, Karnataka - 560001                                             
                                                     GSTIN: 27ABCDE1234F1Z5                                                     
                                                          TAX INVOICE                                                           
================================================================================================================================
Invoice No. : 20261107142947396836
Date & Time : 07-11-2026 02:29 PM
Customer ID : CUST-042
Customer    : Kartik Pradhan
Telephone   : 9876543210
--------------------------------------------------------------------------------------------------------------------------------
Product              |      Qty |        Price |         Total |       Warranty |   Expiry Date & Time |             Warranty ID
--------------------------------------------------------------------------------------------------------------------------------
Asus ROG Gaming L... |     1.00 |     85000.00 |      85000.00 |    24 month(s) |  07-11-2028 02:29 PM | 20261107142947396836-01
Logitech MX Maste... |     1.00 |      8500.00 |       8500.00 |    12 month(s) |  07-11-2027 02:29 PM | 20261107142947396836-02
--------------------------------------------------------------------------------------------------------------------------------
                                                                                                        Subtotal: Rs.   93500.00
                                                                                                        Discount: Rs.    4675.00
                                                                                                       GST (18%): Rs.   15988.50
================================================================================================================================
                                                                                                     GRAND TOTAL: Rs.  104813.50
================================================================================================================================
Payment Method: Full Payment
================================================================================================================================
                                            Thank you for shopping with ABC DIGITAL!                                            
================================================================================================================================
```

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure Python 3.9 or newer is installed on your system:
```bash
python3 --version
```

### 2. Run the Application
Launch the canonical application entry point:
```bash
python3 bill_generator.py
```
Or use the Makefile shortcut:
```bash
make run
```

---

## 📖 Usage Guide

Upon startup, the application presents a clean interactive menu:

```
=============================================
 WELCOME TO ABC DIGITAL BILL GENERATOR
=============================================

1. Add product
2. Generate bill
3. Check warranty status
4. Exit
```

1. **Add product:** Prompts for Customer Details (Name, Customer ID, Telephone Number) on the first product, followed by Product Name, Quantity, Price, and Warranty period in months.
2. **Generate bill:** Validates that products have been entered, asks for discount percentage (0–100%), provides payment options (**Full Payment** or **EMI** with term and interest rate calculation), displays the formatted Tax Invoice, and archives it to `invoices/`.
3. **Check warranty status:** Allows entering a Warranty ID to instantly view the associated product, customer, invoice number, expiration date, and real-time status (**Active** or **Expired**).
4. **Exit:** Gracefully terminates the session.

---

## 🏗️ Project Architecture

The repository enforces a clean, single-source-of-truth structure without artificial packaging overhead or competing entry points:

```
Smart-Bill-Calculator/
├── bill_generator.py          # CANONICAL SOURCE OF TRUTH (Engine, Formatter, CLI, Storage)
├── tests/                     # Automated test suite
│   ├── __init__.py
│   └── test_bill_generator.py # 26 unit and integration tests
├── invoices/                  # Output directory for archived customer receipts
│   ├── bill_20260802005051.txt
│   └── bill_20260802005707.txt
├── .gitignore                 # Clean repository hygiene rules
├── LICENSE                    # MIT Open Source License
├── Makefile                   # Ergonomic developer shortcuts (run, test, clean)
└── README.md                  # Comprehensive project documentation
```

---

## 🧪 Automated Testing

The project includes 26 automated unit and integration tests covering calculation proofs, date arithmetic, EMI mathematics, formatting truncation, and interactive workflows.

Run all tests using the Makefile:
```bash
make test
```
Or directly with Python's built-in `unittest` runner:
```bash
python3 -m unittest discover tests -v
```

### Test Coverage Highlights
- ✅ **Mathematical Accuracy:** Decimal arithmetic verification for Subtotals, Discounts, 18% GST, and Grand Totals.
- ✅ **Boundary & Calendar Calculations:** Validates `add_months()` across calendar years and month-end dates (e.g. January 31 + 1 month = February 28).
- ✅ **Financing Proofs:** Tests EMI threshold enforcement (< Rs. 5,000 disabled), interest accrual, total payable amounts, and monthly installments.
- ✅ **Warranty Lifecycle:** Verifies active vs. expired status determination based on real-time clock comparison.
- ✅ **Formatting Resilience:** Ensures product names longer than 20 characters truncate gracefully with `...` without misaligning column borders.
- ✅ **Input Robustness:** Tests empty strings, negative values, and non-numeric retry handling.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
