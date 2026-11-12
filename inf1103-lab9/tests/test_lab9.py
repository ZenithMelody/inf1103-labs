# Lab 9 tests. Run from the inf1103-lab9 folder with: python tests/test_lab9.py
# Each test prints its output (for evidence) and asserts the expected behaviour.

import inspect
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
    StudentDiscount,
    DISCOUNT_CHOICES,
    ProductFactory,
)

# ---------- helpers ----------

def make_supplier() -> Supplier:
    return Supplier("S100", "Test Supplier", "test@supplier.com")


def make_order_of_250(discount: DiscountStrategy | None = None) -> Order:
    supplier = make_supplier()
    order = Order("O001", discount)
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
    assert StudentDiscount().apply(200.0) == 190.0
    print(f"NoDiscount on 250.00:             {NoDiscount().apply(250.0):.2f}")
    print(f"PercentageDiscount(10) on 250.00: {PercentageDiscount(10).apply(250.0):.2f}")
    print(f"BulkDiscount(200, 20) on 250.00:  {BulkDiscount(200, 20).apply(250.0):.2f}")
    print(f"StudentDiscount on 200.00:        {StudentDiscount().apply(200.0):.2f}")

def test_discount_strategy_is_abstract() -> None:
    try:
        DiscountStrategy()
    except TypeError as error:
        print(f"DiscountStrategy cannot be instantiated: {error}")
    else:
        raise AssertionError("DiscountStrategy should be abstract")
    expect_value_error(lambda: PercentageDiscount(150), "percentage 150")
    expect_value_error(lambda: BulkDiscount(200, -20), "bulk amount -20")

def test_order_defaults_to_no_discount() -> None:
    order = make_order_of_250()
    assert isinstance(order.discount, NoDiscount)
    assert order.calculate_total() == 250.00
    print(f"No strategy given -> {type(order.discount).__name__}, total {order.calculate_total():.2f}")


def test_set_discount_changes_strategy_on_existing_order() -> None:
    # predict first (2.3): the lines add up to 250
    order = make_order_of_250(BulkDiscount(200, 20))
    print(f"BulkDiscount(200, 20):  {order.calculate_total():.2f}")
    assert order.calculate_total() == 230.00

    order.set_discount(PercentageDiscount(10))
    print(f"PercentageDiscount(10): {order.calculate_total():.2f}")
    assert order.calculate_total() == 225.00


def test_order_has_no_discount_if_elif_logic() -> None:
    source = inspect.getsource(Order.calculate_total)
    print(source)
    assert "if " not in source and "elif" not in source
    assert "self.discount.apply(" in source


def test_two_orders_can_share_one_strategy() -> None:
    # predict first (2.4): does the Order own its strategy, or just use it?
    shared = PercentageDiscount(10)
    order_a = make_order_of_250(shared)
    order_b = make_order_of_250(shared)
    print(f"Same strategy object in both orders? {order_a.discount is order_b.discount}")
    assert order_a.discount is order_b.discount is shared

    del order_a
    print(f"After deleting one order, the other still totals {order_b.calculate_total():.2f}")
    assert order_b.calculate_total() == 225.00

def test_new_strategy_needs_no_change_to_order() -> None:
    # predict first (2.1): a strategy Order has never seen, defined here in the test file
    class HalfPriceDiscount(DiscountStrategy):
        def apply(self, total: float) -> float:
            return total / 2

    order = make_order_of_250(HalfPriceDiscount())
    print(f"HalfPriceDiscount, written outside the program: {order.calculate_total():.2f}")
    assert order.calculate_total() == 125.00

    order.set_discount(StudentDiscount())
    print(f"StudentDiscount:                                {order.calculate_total():.2f}")
    assert order.calculate_total() == 237.50


def test_discount_menu_offers_only_strategies() -> None:
    for key, (label, strategy) in DISCOUNT_CHOICES.items():
        print(f"{key}. {label} -> {type(strategy).__name__}")
        assert isinstance(strategy, DiscountStrategy)
    assert any(isinstance(strategy, StudentDiscount) for _, strategy in DISCOUNT_CHOICES.values())

# ---------- section 3: Factory ----------

def test_factory_creates_the_right_product_types() -> None:
    supplier = make_supplier()
    physical = ProductFactory.create("physical", "P100", "Monitor", 200.00, 10, supplier, weight=4.0)
    digital = ProductFactory.create("digital", "D100", "Antivirus", 50.00, 99, supplier,
                                    download_size=300.0)
    assert type(physical) is PhysicalProduct and physical.weight == 4.0
    assert type(digital) is DigitalProduct and digital.download_size == 300.0
    assert physical.supplier is supplier and digital.supplier is supplier

    # the caller only uses methods every Product has
    for product in (physical, digital):
        product.display_information()
        print(product.get_fulfilment_info())


def test_factory_rejects_unknown_product_type() -> None:
    # predict first (3.2)
    message = expect_value_error(
        lambda: ProductFactory.create("service", "S001", "Installation", 30.00, 5, make_supplier()),
        "product type 'service'",
    )
    assert message == "Unknown product type: service"


TESTS = [
    test_order_total_without_discount,
    test_each_strategy_applies_its_own_rule,
    test_discount_strategy_is_abstract,
    test_order_defaults_to_no_discount,
    test_set_discount_changes_strategy_on_existing_order,
    test_order_has_no_discount_if_elif_logic,
    test_two_orders_can_share_one_strategy,
    test_new_strategy_needs_no_change_to_order,
    test_discount_menu_offers_only_strategies,
    test_factory_creates_the_right_product_types,
    test_factory_rejects_unknown_product_type,
]


def main() -> None:
    for test in TESTS:
        print(f"\n=== {test.__name__} ===")
        test()
        print("PASS")
    print(f"\nAll {len(TESTS)} tests passed.")


if __name__ == "__main__":
    main()