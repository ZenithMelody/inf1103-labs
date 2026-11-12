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
    DiscountStrategy,
    NoDiscount,
    PercentageDiscount,
    BulkDiscount,
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

def expect_value_error(action, label: str) -> str:
    # runs action() and checks that it raises ValueError; returns the message
    try:
        action()
    except ValueError as error:
        print(f"Rejected {label}: {error}")
        return str(error)
    raise AssertionError(f"{label} should have raised ValueError")

# ---------- baseline carried over from Lab 8 ----------

def test_order_total_without_discount() -> None:
    order = make_order_of_250()
    order.display_information()
    assert order.calculate_total() == 250.00

# ---------- section 2: Strategy ----------

def test_each_strategy_applies_its_own_rule() -> None:
    assert NoDiscount().apply(250.0) == 250.0
    assert PercentageDiscount(10).apply(250.0) == 225.0
    assert BulkDiscount(200, 20).apply(250.0) == 230.0
    assert BulkDiscount(200, 20).apply(200.0) == 180.0    # exactly on the threshold counts
    assert BulkDiscount(200, 20).apply(199.99) == 199.99  # below it, no discount
    print(f"NoDiscount on 250.00:             {NoDiscount().apply(250.0):.2f}")
    print(f"PercentageDiscount(10) on 250.00: {PercentageDiscount(10).apply(250.0):.2f}")
    print(f"BulkDiscount(200, 20) on 250.00:  {BulkDiscount(200, 20).apply(250.0):.2f}")


def test_discount_strategy_is_abstract() -> None:
    try:
        DiscountStrategy()
    except TypeError as error:
        print(f"DiscountStrategy cannot be instantiated: {error}")
    else:
        raise AssertionError("DiscountStrategy should be abstract")
    expect_value_error(lambda: PercentageDiscount(150), "percentage 150")
    expect_value_error(lambda: BulkDiscount(200, -20), "bulk amount -20")


TESTS = [
    test_order_total_without_discount,
    test_each_strategy_applies_its_own_rule,
    test_discount_strategy_is_abstract,
]


def main() -> None:
    for test in TESTS:
        print(f"\n=== {test.__name__} ===")
        test()
        print("PASS")
    print(f"\nAll {len(TESTS)} tests passed.")


if __name__ == "__main__":
    main()