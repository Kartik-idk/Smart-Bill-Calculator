"""
ABC DIGITAL Bill Generator with Warranty Tracking & EMI Financing
=================================================================
A production-grade, mathematically exact Command-Line Billing & Invoicing
system built with Python's standard library.

Key Features:
- Exact banking rounding using `decimal.Decimal` (ROUND_HALF_UP).
- Dynamic receipt formatting preventing table overflow.
- Per-item warranty generation and expiry tracking.
- EMI calculation with annual interest rates and monthly installments.
- Resilient terminal input validation handling EOF and keyboard interrupts.
"""

import calendar
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import sys


GST_RATE = 0.18
MINIMUM_EMI_AMOUNT = 5000
EMI_TERMS = (3, 6, 9, 12)
COMPANY_NAME = "ABC DIGITAL"
COMPANY_GST_NUMBER = "27ABCDE1234F1Z5"
COMPANY_LOCATION = "MG Road, Bengaluru, Karnataka - 560001"
BILL_WIDTH = 128
TOTAL_LABEL_WIDTH = BILL_WIDTH - 15
SELLER_BILLS_FOLDER = Path(__file__).resolve().parent / "invoices"


def get_positive_number(prompt):
    """Return a positive numeric value entered by the user."""
    while True:
        try:
            raw = input(prompt).strip()
            if not raw:
                print("Input cannot be empty. Please enter a number.")
                continue
            value = float(raw)
            if value > 0:
                return value
            print("Please enter a value greater than zero.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled.")
            sys.exit(0)


def get_warranty_months():
    """Return a warranty period in whole months; zero means no warranty."""
    while True:
        try:
            raw = input("Enter warranty period in months (0 for no warranty): ").strip()
            if not raw:
                print("Input cannot be empty. Enter 0 if no warranty.")
                continue
            months = int(raw)
            if months >= 0:
                return months
            print("Warranty period cannot be negative.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled.")
            sys.exit(0)


def get_discount():
    """Return a valid discount percentage between 0 and 100."""
    while True:
        try:
            raw = input("Enter discount percentage (0 if none): ").strip()
            if not raw:
                return 0.0
            discount = float(raw)
            if 0 <= discount <= 100:
                return discount
            print("Discount must be between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled.")
            sys.exit(0)


def get_non_negative_number(prompt):
    """Return a non-negative number entered by the user."""
    while True:
        try:
            raw = input(prompt).strip()
            if not raw:
                print("Input cannot be empty. Please enter zero or a positive number.")
                continue
            value = float(raw)
            if value >= 0:
                return value
            print("Please enter zero or a positive number.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled.")
            sys.exit(0)


def get_emi_months():
    """Return one of the supported EMI durations (3, 6, 9, or 12 months)."""
    while True:
        try:
            raw = input("Choose EMI duration (3, 6, 9, or 12 months): ").strip()
            if not raw:
                print("Please select one of 3, 6, 9, or 12.")
                continue
            months = int(raw)
            if months in EMI_TERMS:
                return months
            print("Please choose 3, 6, 9, or 12 months.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled.")
            sys.exit(0)


def get_payment_details(grand_total):
    """Collect a full-payment or EMI plan for the completed bill using Decimal precision."""
    if grand_total < MINIMUM_EMI_AMOUNT:
        print(
            f"\nEMI is available for bills of Rs. {MINIMUM_EMI_AMOUNT:,.2f} and above."
        )
        return {"method": "Full Payment"}

    while True:
        try:
            print("\nPayment options")
            print("1. Full Payment")
            print("2. EMI")
            choice = input("Choose payment option (1-2): ").strip()

            if choice == "1":
                return {"method": "Full Payment"}

            if choice == "2":
                months = get_emi_months()
                annual_interest_rate = get_non_negative_number(
                    "Enter annual interest rate (%): "
                )
                gt_dec = Decimal(str(round(grand_total, 2)))
                rate_dec = Decimal(str(annual_interest_rate))
                months_dec = Decimal(str(months))

                interest_amount = (gt_dec * rate_dec * months_dec / Decimal("1200")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                total_emi_payable = (gt_dec + interest_amount).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                monthly_installment = (total_emi_payable / months_dec).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

                return {
                    "method": "EMI",
                    "months": months,
                    "annual_interest_rate": float(annual_interest_rate),
                    "interest_amount": float(interest_amount),
                    "total_emi_payable": float(total_emi_payable),
                    "monthly_installment": float(monthly_installment),
                }

            print("Invalid choice. Please select 1 or 2.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled.")
            sys.exit(0)


def get_customer_details():
    """Collect customer information for a new bill."""
    try:
        print("\nEnter customer details")
        customer_name = input("Customer name: ").strip() or "Walk-in Customer"
        customer_id = input("Customer ID: ").strip() or "N/A"
        telephone_number = input("Telephone number: ").strip() or "N/A"
        return customer_name, customer_id, telephone_number
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperation cancelled.")
        sys.exit(0)


def add_months(date_value, months):
    """Return a date/time moved forward by a number of calendar months."""
    month_index = date_value.month - 1 + months
    year = date_value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(date_value.day, calendar.monthrange(year, month)[1])
    return date_value.replace(year=year, month=month, day=day)


def calculate_bill_totals(items, discount_percent):
    """Calculate subtotal, discount, GST, and grand total using exact Decimal arithmetic."""
    subtotal = sum(
        (Decimal(str(item["quantity"])) * Decimal(str(item["price"])) for item in items),
        Decimal("0.00"),
    )
    disc_pct = Decimal(str(discount_percent))
    discount_amount = (subtotal * disc_pct / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    taxable_amount = subtotal - discount_amount
    gst_rate = Decimal(str(GST_RATE))
    gst_amount = (taxable_amount * gst_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    grand_total = (taxable_amount + gst_amount).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return {
        "subtotal": float(subtotal),
        "discount_amount": float(discount_amount),
        "gst_amount": float(gst_amount),
        "grand_total": float(grand_total),
    }


def create_bill(
    customer_name,
    customer_id,
    telephone_number,
    items,
    discount_percent,
    generated_at=None,
    payment_details=None,
):
    """Create a formatted bill and the warranty records for eligible products."""
    totals = calculate_bill_totals(items, discount_percent)
    subtotal = totals["subtotal"]
    discount_amount = totals["discount_amount"]
    gst_amount = totals["gst_amount"]
    grand_total = totals["grand_total"]
    payment_details = payment_details or {"method": "Full Payment"}

    bill_time = generated_at or datetime.now()
    invoice_number = bill_time.strftime("%Y%m%d%H%M%S%f")
    warranty_records = []

    for position, item in enumerate(items, start=1):
        warranty_months = item["warranty_months"]
        if warranty_months > 0:
            warranty_id = f"{invoice_number}-{position:02d}"
            expiry_date = add_months(bill_time, warranty_months)
            item["warranty_id"] = warranty_id
            item["expiry_date"] = expiry_date
            warranty_records.append(
                {
                    "warranty_id": warranty_id,
                    "product_name": item["name"],
                    "customer_name": customer_name,
                    "customer_id": customer_id,
                    "telephone_number": telephone_number,
                    "invoice_number": invoice_number,
                    "warranty_months": warranty_months,
                    "expiry_date": expiry_date,
                }
            )
        else:
            item["warranty_id"] = "N/A"
            item["expiry_date"] = None

    lines = [
        "\n" + "=" * BILL_WIDTH,
        f"{COMPANY_NAME:^{BILL_WIDTH}}",
        f"{COMPANY_LOCATION:^{BILL_WIDTH}}",
        f"GSTIN: {COMPANY_GST_NUMBER}".center(BILL_WIDTH),
        "TAX INVOICE".center(BILL_WIDTH),
        "=" * BILL_WIDTH,
        f"Invoice No. : {invoice_number}",
        f"Date & Time : {bill_time.strftime('%d-%m-%Y %I:%M %p')}",
        f"Customer ID : {customer_id}",
        f"Customer    : {customer_name}",
        f"Telephone   : {telephone_number}",
        "-" * BILL_WIDTH,
        f"{'Product':<20} | {'Qty':>8} | {'Price':>12} | {'Total':>13} | "
        f"{'Warranty':>14} | {'Expiry Date & Time':>20} | {'Warranty ID':>23}",
        "-" * BILL_WIDTH,
    ]

    for item in items:
        item_qty = Decimal(str(item["quantity"]))
        item_price = Decimal(str(item["price"]))
        item_total = float((item_qty * item_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        warranty_text = (
            f"{item['warranty_months']} month(s)"
            if item["warranty_months"] > 0
            else "No Warranty"
        )
        expiry_text = (
            item["expiry_date"].strftime("%d-%m-%Y %I:%M %p")
            if item["expiry_date"]
            else "-"
        )
        # Prevent table overflow by truncating overly long names cleanly
        product_display = item["name"]
        if len(product_display) > 20:
            product_display = product_display[:17] + "..."

        lines.append(
            f"{product_display:<20} | {item['quantity']:>8.2f} | "
            f"{item['price']:>12.2f} | {item_total:>13.2f} | "
            f"{warranty_text:>14} | {expiry_text:>20} | "
            f"{item['warranty_id']:>23}"
        )

    lines.extend(
        [
            "-" * BILL_WIDTH,
            f"{'Subtotal:':>{TOTAL_LABEL_WIDTH}} Rs. {subtotal:>10.2f}",
            f"{'Discount:':>{TOTAL_LABEL_WIDTH}} Rs. {discount_amount:>10.2f}",
            f"{'GST (18%):':>{TOTAL_LABEL_WIDTH}} Rs. {gst_amount:>10.2f}",
            "=" * BILL_WIDTH,
            f"{'GRAND TOTAL:':>{TOTAL_LABEL_WIDTH}} Rs. {grand_total:>10.2f}",
            "=" * BILL_WIDTH,
            f"Payment Method: {payment_details['method']}",
        ]
    )

    if payment_details["method"] == "EMI":
        lines.extend(
            [
                f"EMI Duration: {payment_details['months']} months",
                f"Annual Interest Rate: {payment_details['annual_interest_rate']:.2f}%",
                f"Total Interest: Rs. {payment_details['interest_amount']:.2f}",
                f"Total EMI Payable: Rs. {payment_details['total_emi_payable']:.2f}",
                f"Monthly Installment: Rs. {payment_details['monthly_installment']:.2f}",
            ]
        )

    lines.extend(
        [
            "=" * BILL_WIDTH,
            "Thank you for shopping with ABC DIGITAL!".center(BILL_WIDTH),
            "=" * BILL_WIDTH,
        ]
    )
    return "\n".join(lines), invoice_number, warranty_records


def check_warranty_status(warranty_records):
    """Find a warranty from this session and display its current status."""
    if not warranty_records:
        print("\nNo warranty records have been generated in this session yet.")
        return

    try:
        warranty_id = input("Enter warranty ID: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperation cancelled.")
        return

    record = next(
        (item for item in warranty_records if item["warranty_id"] == warranty_id),
        None,
    )

    if record is None:
        print("Warranty ID not found.")
        return

    status = "Active" if datetime.now() <= record["expiry_date"] else "Expired"
    print("\n" + "=" * 45)
    print("             WARRANTY STATUS")
    print("=" * 45)
    print(f"Warranty ID : {record['warranty_id']}")
    print(f"Product     : {record['product_name']}")
    print(f"Customer    : {record['customer_name']} ({record['customer_id']})")
    print(f"Telephone   : {record['telephone_number']}")
    print(f"Invoice No. : {record['invoice_number']}")
    print(f"Expiry Date : {record['expiry_date'].strftime('%d-%m-%Y')}")
    print(f"Status      : {status}")
    print("=" * 45)


def save_bill_to_archive(bill_text, invoice_number):
    """Save a bill directly in the invoices folder."""
    invoices_folder = SELLER_BILLS_FOLDER
    invoices_folder.mkdir(parents=True, exist_ok=True)
    bill_path = invoices_folder / f"bill_{invoice_number}.txt"
    bill_path.write_text(bill_text, encoding="utf-8")
    return bill_path


def main():
    print("=" * 45)
    print(" WELCOME TO ABC DIGITAL BILL GENERATOR")
    print("=" * 45)

    customer_name = None
    customer_id = None
    telephone_number = None
    items = []
    warranty_records = []

    while True:
        try:
            print("\n1. Add product")
            print("2. Generate bill")
            print("3. Check warranty status")
            print("4. Exit")
            choice = input("Enter your choice (1-4): ").strip()

            if choice == "1":
                if customer_name is None:
                    customer_name, customer_id, telephone_number = get_customer_details()

                product_name = input("Enter product name: ").strip()
                if not product_name:
                    print("Product name cannot be empty.")
                    continue

                quantity = get_positive_number("Enter quantity: ")
                price = get_positive_number("Enter price per unit: ")
                warranty_months = get_warranty_months()
                items.append(
                    {
                        "name": product_name,
                        "quantity": quantity,
                        "price": price,
                        "warranty_months": warranty_months,
                    }
                )
                print(f"{product_name} added successfully.")

            elif choice == "2":
                if not items:
                    print("No products added. Please add at least one product.")
                    continue

                discount = get_discount()
                totals = calculate_bill_totals(items, discount)
                payment_details = get_payment_details(totals["grand_total"])
                bill_text, invoice_number, new_warranty_records = create_bill(
                    customer_name,
                    customer_id,
                    telephone_number,
                    items,
                    discount,
                    payment_details=payment_details,
                )
                warranty_records.extend(new_warranty_records)
                print(bill_text)

                bill_path = save_bill_to_archive(bill_text, invoice_number)
                print(f"\nBill archived for seller at: {bill_path}")

                # Keep warranty records for checks, but begin a fresh customer bill.
                customer_name = None
                customer_id = None
                telephone_number = None
                items = []

            elif choice == "3":
                check_warranty_status(warranty_records)

            elif choice == "4":
                print("Thank you for using ABC DIGITAL Bill Generator!")
                break

            else:
                print("Invalid choice. Please select a number from 1 to 4.")

        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled. Thank you!")
            break


if __name__ == "__main__":
    main()
