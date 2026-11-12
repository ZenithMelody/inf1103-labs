# Lab 9 tests. Run from the inf1103-lab9 folder with: python tests/test_lab9.py
# Each test prints its output (for evidence) and asserts the expected behaviour.

import sys
from pathlib import Path

# this file sits in tests/, so the lab folder is added to the import path first
LAB_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB_FOLDER))

from inf1103_lab9 import (
    Supplier,
    PhysicalProduct,
    DigitalProduct,
    Order,
)


# ---------- helpers ----------

def make_supplier() -> Supplier:
    return Supplier("S100", "Test Supplier", "test@supplier.com")


def make_order_of_250() -> Order:
    supplier = make_supplier()
    order = Order("O001")
    order.add_order_line(PhysicalProduct("P100", "Monitor", 200.00, 10, supplier, 4.0), 1)
    order.add_order_line(DigitalProduct("D100", "Antivirus", 50.00, 99, supplier, 300.0), 1)
    return order


# ---------- baseline carried over from Lab 8 ----------

def test_order_total_without_discount() -> None:
    order = make_order_of_250()
    order.display_information()
    assert order.calculate_total() == 250.00


TESTS = [
    test_order_total_without_discount,
]


def main() -> None:
    for test in TESTS:
        print(f"\n=== {test.__name__} ===")
        test()
        print("PASS")
    print(f"\nAll {len(TESTS)} tests passed.")


if __name__ == "__main__":
    main()