"""
Unit and Integration Tests for ABC DIGITAL Bill Generator (bill_generator.py)
"""

from datetime import datetime, timedelta
import io
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import bill_generator


class TestBillTotalsAndCalculations(unittest.TestCase):
    def test_calculate_bill_totals_standard(self):
        items = [
            {"name": "Laptop", "quantity": 1, "price": 50000.0, "warranty_months": 12},
            {"name": "Mouse", "quantity": 2, "price": 1000.0, "warranty_months": 6},
        ]
        # Subtotal = 50000 + 2000 = 52000.00
        # Discount 10% = 5200.00
        # Taxable = 46800.00
        # GST 18% = 8424.00
        # Grand Total = 55224.00
        totals = bill_generator.calculate_bill_totals(items, 10.0)
        self.assertEqual(totals["subtotal"], 52000.0)
        self.assertEqual(totals["discount_amount"], 5200.0)
        self.assertEqual(totals["gst_amount"], 8424.0)
        self.assertEqual(totals["grand_total"], 55224.0)

    def test_calculate_bill_totals_zero_discount(self):
        items = [{"name": "Item A", "quantity": 1, "price": 100.0}]
        # Subtotal: 100.0, Disc: 0.0, Taxable: 100.0, GST: 18.0, Total: 118.0
        totals = bill_generator.calculate_bill_totals(items, 0.0)
        self.assertEqual(totals["subtotal"], 100.0)
        self.assertEqual(totals["discount_amount"], 0.0)
        self.assertEqual(totals["gst_amount"], 18.0)
        self.assertEqual(totals["grand_total"], 118.0)

    def test_calculate_bill_totals_full_discount(self):
        items = [{"name": "Promo Item", "quantity": 1, "price": 100.0}]
        totals = bill_generator.calculate_bill_totals(items, 100.0)
        self.assertEqual(totals["subtotal"], 100.0)
        self.assertEqual(totals["discount_amount"], 100.0)
        self.assertEqual(totals["gst_amount"], 0.0)
        self.assertEqual(totals["grand_total"], 0.0)

    def test_calculate_bill_totals_decimal_rounding(self):
        # 3 items at 19.99 = 59.97
        # 5% discount = 2.9985 -> rounded to 3.00
        # Taxable = 56.97
        # GST 18% = 10.2546 -> rounded to 10.25
        # Grand Total = 67.22
        items = [{"name": "Item", "quantity": 3, "price": 19.99}]
        totals = bill_generator.calculate_bill_totals(items, 5.0)
        self.assertEqual(totals["subtotal"], 59.97)
        self.assertEqual(totals["discount_amount"], 3.00)
        self.assertEqual(totals["gst_amount"], 10.25)
        self.assertEqual(totals["grand_total"], 67.22)


class TestAddMonthsAndDates(unittest.TestCase):
    def test_add_months_within_year(self):
        dt = datetime(2026, 1, 15, 10, 30)
        res = bill_generator.add_months(dt, 6)
        self.assertEqual(res, datetime(2026, 7, 15, 10, 30))

    def test_add_months_across_years(self):
        dt = datetime(2026, 11, 20, 14, 0)
        res = bill_generator.add_months(dt, 4)
        self.assertEqual(res, datetime(2027, 3, 20, 14, 0))

    def test_add_months_end_of_month(self):
        dt = datetime(2026, 1, 31, 12, 0)
        res = bill_generator.add_months(dt, 1)
        # February has 28 days in 2026
        self.assertEqual(res, datetime(2026, 2, 28, 12, 0))


class TestPaymentAndEMICalculations(unittest.TestCase):
    def test_payment_below_minimum_emi(self):
        f = io.StringIO()
        with redirect_stdout(f):
            plan = bill_generator.get_payment_details(4999.0)
        self.assertEqual(plan["method"], "Full Payment")
        self.assertIn("EMI is available for bills of Rs. 5,000.00 and above.", f.getvalue())

    @patch("builtins.input", side_effect=["1"])
    def test_payment_full_payment_choice(self, _mock_input):
        with redirect_stdout(io.StringIO()):
            plan = bill_generator.get_payment_details(10000.0)
        self.assertEqual(plan["method"], "Full Payment")

    @patch("builtins.input", side_effect=["2", "6", "12"])
    def test_payment_emi_calculation(self, _mock_input):
        # Grand total = 60000
        # Duration = 6 months
        # Interest rate = 12% annual
        # Interest = 60000 * 12 * 6 / 1200 = 3600.00
        # Total payable = 63600.00
        # Monthly installment = 63600 / 6 = 10600.00
        with redirect_stdout(io.StringIO()):
            plan = bill_generator.get_payment_details(60000.0)
        self.assertEqual(plan["method"], "EMI")
        self.assertEqual(plan["months"], 6)
        self.assertEqual(plan["annual_interest_rate"], 12.0)
        self.assertEqual(plan["interest_amount"], 3600.0)
        self.assertEqual(plan["total_emi_payable"], 63600.0)
        self.assertEqual(plan["monthly_installment"], 10600.0)


class TestCreateBillAndFormatting(unittest.TestCase):
    def setUp(self):
        self.fixed_dt = datetime(2026, 8, 2, 0, 50, 51)
        self.items = [
            {
                "name": "Asus Laptop",
                "quantity": 1.0,
                "price": 68000.0,
                "warranty_months": 24,
            },
            {
                "name": "Acer Mouse",
                "quantity": 1.0,
                "price": 1200.0,
                "warranty_months": 0,
            },
        ]

    def test_create_bill_full_payment(self):
        bill_text, inv_no, warranties = bill_generator.create_bill(
            customer_name="Kartik",
            customer_id="CUST-001",
            telephone_number="9876543210",
            items=self.items,
            discount_percent=10.0,
            generated_at=self.fixed_dt,
            payment_details={"method": "Full Payment"},
        )

        self.assertIn("ABC DIGITAL", bill_text)
        self.assertIn("TAX INVOICE", bill_text)
        self.assertIn("Customer ID : CUST-001", bill_text)
        self.assertIn("Customer    : Kartik", bill_text)
        self.assertIn("Telephone   : 9876543210", bill_text)
        self.assertIn("Asus Laptop", bill_text)
        self.assertIn("Acer Mouse", bill_text)
        self.assertIn("24 month(s)", bill_text)
        self.assertIn("No Warranty", bill_text)
        self.assertIn("Subtotal:", bill_text)
        self.assertIn("69200.00", bill_text)
        self.assertIn("Discount:", bill_text)
        self.assertIn("6920.00", bill_text)
        self.assertIn("GST (18%):", bill_text)
        self.assertIn("11210.40", bill_text)
        self.assertIn("GRAND TOTAL:", bill_text)
        self.assertIn("73490.40", bill_text)
        self.assertIn("Payment Method: Full Payment", bill_text)

        # Warranty verification
        self.assertEqual(len(warranties), 1)
        w = warranties[0]
        self.assertEqual(w["product_name"], "Asus Laptop")
        self.assertEqual(w["customer_name"], "Kartik")
        self.assertEqual(w["warranty_months"], 24)
        self.assertTrue(w["warranty_id"].endswith("-01"))

    def test_create_bill_long_product_name_truncation(self):
        long_name_items = [
            {
                "name": "Very Long Product Description Exceeding Twenty Characters",
                "quantity": 1.0,
                "price": 500.0,
                "warranty_months": 0,
            }
        ]
        bill_text, _, _ = bill_generator.create_bill(
            customer_name="Test",
            customer_id="N/A",
            telephone_number="N/A",
            items=long_name_items,
            discount_percent=0.0,
            generated_at=self.fixed_dt,
        )
        self.assertIn("Very Long Product...", bill_text)

    def test_create_bill_emi_formatting(self):
        emi_plan = {
            "method": "EMI",
            "months": 6,
            "annual_interest_rate": 10.0,
            "interest_amount": 500.0,
            "total_emi_payable": 10500.0,
            "monthly_installment": 1750.0,
        }
        bill_text, _, _ = bill_generator.create_bill(
            customer_name="Test",
            customer_id="N/A",
            telephone_number="N/A",
            items=[{"name": "Item", "quantity": 1, "price": 10000, "warranty_months": 0}],
            discount_percent=0.0,
            generated_at=self.fixed_dt,
            payment_details=emi_plan,
        )
        self.assertIn("Payment Method: EMI", bill_text)
        self.assertIn("EMI Duration: 6 months", bill_text)
        self.assertIn("Annual Interest Rate: 10.00%", bill_text)
        self.assertIn("Total Interest: Rs. 500.00", bill_text)
        self.assertIn("Total EMI Payable: Rs. 10500.00", bill_text)
        self.assertIn("Monthly Installment: Rs. 1750.00", bill_text)


class TestWarrantyStatus(unittest.TestCase):
    def test_check_warranty_status_active(self):
        future_date = datetime.now() + timedelta(days=180)
        records = [
            {
                "warranty_id": "WARR-100-01",
                "product_name": "Laptop",
                "customer_name": "Alice",
                "customer_id": "C-1",
                "telephone_number": "12345",
                "invoice_number": "INV-100",
                "expiry_date": future_date,
            }
        ]
        f = io.StringIO()
        with patch("builtins.input", return_value="WARR-100-01"), redirect_stdout(f):
            bill_generator.check_warranty_status(records)
        output = f.getvalue()
        self.assertIn("WARRANTY STATUS", output)
        self.assertIn("Status      : Active", output)
        self.assertIn("Product     : Laptop", output)

    def test_check_warranty_status_expired(self):
        past_date = datetime.now() - timedelta(days=10)
        records = [
            {
                "warranty_id": "WARR-200-01",
                "product_name": "Headphones",
                "customer_name": "Bob",
                "customer_id": "C-2",
                "telephone_number": "54321",
                "invoice_number": "INV-200",
                "expiry_date": past_date,
            }
        ]
        f = io.StringIO()
        with patch("builtins.input", return_value="WARR-200-01"), redirect_stdout(f):
            bill_generator.check_warranty_status(records)
        output = f.getvalue()
        self.assertIn("Status      : Expired", output)

    def test_check_warranty_status_not_found(self):
        records = [{"warranty_id": "WARR-1", "expiry_date": datetime.now()}]
        f = io.StringIO()
        with patch("builtins.input", return_value="UNKNOWN-ID"), redirect_stdout(f):
            bill_generator.check_warranty_status(records)
        self.assertIn("Warranty ID not found.", f.getvalue())

    def test_check_warranty_status_empty_records(self):
        f = io.StringIO()
        with redirect_stdout(f):
            bill_generator.check_warranty_status([])
        self.assertIn("No warranty records have been generated", f.getvalue())


class TestStorageAndArchive(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_folder = bill_generator.SELLER_BILLS_FOLDER
        bill_generator.SELLER_BILLS_FOLDER = tempfile.Path(self.temp_dir) if hasattr(tempfile, "Path") else None
        from pathlib import Path
        bill_generator.SELLER_BILLS_FOLDER = Path(self.temp_dir)

    def tearDown(self):
        bill_generator.SELLER_BILLS_FOLDER = self.original_folder
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_bill_to_archive(self):
        saved_path = bill_generator.save_bill_to_archive("Test Bill Content", "20261107120000")
        self.assertTrue(saved_path.exists())
        self.assertEqual(saved_path.read_text(encoding="utf-8"), "Test Bill Content")
        self.assertEqual(saved_path.name, "bill_20261107120000.txt")


class TestInteractiveInputHandlers(unittest.TestCase):
    @patch("builtins.input", side_effect=["-5", "abc", "0", "42.50"])
    def test_get_positive_number(self, _mock_input):
        with redirect_stdout(io.StringIO()):
            res = bill_generator.get_positive_number("Enter: ")
        self.assertEqual(res, 42.50)

    @patch("builtins.input", side_effect=["-1", "xyz", "12"])
    def test_get_warranty_months(self, _mock_input):
        with redirect_stdout(io.StringIO()):
            res = bill_generator.get_warranty_months()
        self.assertEqual(res, 12)

    @patch("builtins.input", side_effect=["-10", "150", "15.5"])
    def test_get_discount(self, _mock_input):
        with redirect_stdout(io.StringIO()):
            res = bill_generator.get_discount()
        self.assertEqual(res, 15.5)

    @patch("builtins.input", side_effect=[""])
    def test_get_discount_blank_is_zero(self, _mock_input):
        res = bill_generator.get_discount()
        self.assertEqual(res, 0.0)

    @patch("builtins.input", side_effect=["4", "5", "6"])
    def test_get_emi_months(self, _mock_input):
        with redirect_stdout(io.StringIO()):
            res = bill_generator.get_emi_months()
        self.assertEqual(res, 6)

    @patch("builtins.input", side_effect=["Kartik", "K-123", "9999999999"])
    def test_get_customer_details(self, _mock_input):
        with redirect_stdout(io.StringIO()):
            name, cid, phone = bill_generator.get_customer_details()
        self.assertEqual(name, "Kartik")
        self.assertEqual(cid, "K-123")
        self.assertEqual(phone, "9999999999")

    @patch("builtins.input", side_effect=["", "", ""])
    def test_get_customer_details_defaults(self, _mock_input):
        with redirect_stdout(io.StringIO()):
            name, cid, phone = bill_generator.get_customer_details()
        self.assertEqual(name, "Walk-in Customer")
        self.assertEqual(cid, "N/A")
        self.assertEqual(phone, "N/A")

    @patch("builtins.input", side_effect=[
        "1",                    # 1. Add product
        "Kartik", "K-1", "9876",# customer details
        "Wireless Keyboard",    # product name
        "1",                    # qty
        "2500",                 # price
        "12",                   # warranty months
        "2",                    # 2. Generate bill
        "0",                    # discount %
        "4",                    # 4. Exit
    ])
    def test_main_workflow_full_simulation(self, _mock_input):
        with tempfile.TemporaryDirectory() as tmp_dir:
            from pathlib import Path
            orig = bill_generator.SELLER_BILLS_FOLDER
            bill_generator.SELLER_BILLS_FOLDER = Path(tmp_dir)
            f = io.StringIO()
            try:
                with redirect_stdout(f):
                    bill_generator.main()
                output = f.getvalue()
                self.assertIn("WELCOME TO ABC DIGITAL BILL GENERATOR", output)
                self.assertIn("Wireless Keyboard added successfully.", output)
                self.assertIn("TAX INVOICE", output)
                self.assertIn("Customer    : Kartik", output)
                self.assertIn("Bill archived for seller at:", output)
                self.assertIn("Thank you for using ABC DIGITAL Bill Generator!", output)
            finally:
                bill_generator.SELLER_BILLS_FOLDER = orig


if __name__ == "__main__":
    unittest.main()
