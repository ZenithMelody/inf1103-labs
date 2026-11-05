# Lab 8 tests. Run with: python test_lab8.py
# Each test prints its output (for evidence) and asserts the expected relationship.

import importlib.util
import sys
from pathlib import Path

# the program's file name has a hyphen, so a normal import statement cannot load it
_spec = importlib.util.spec_from_file_location(
    "inf1103_lab8", Path(__file__).with_name("inf1103-lab8.py")
)
lab = importlib.util.module_from_spec(_spec)
sys.modules["inf1103_lab8"] = lab
_spec.loader.exec_module(lab)

Supplier = lab.Supplier
Product = lab.Product
PhysicalProduct = lab.PhysicalProduct
DigitalProduct = lab.DigitalProduct
Inventory = lab.Inventory


def make_products() -> tuple[Product, Product]:
    supplier = Supplier("S100", "Test Supplier", "test@supplier.com")
    physical = PhysicalProduct("P100", "Monitor", 200.00, 10, supplier, 4.0)
    digital = DigitalProduct("D100", "Antivirus", 50.00, 99, supplier, 300.0)
    return physical, digital


def test_association() -> None:
    supplier = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.com")
    physical = PhysicalProduct("P001", "Laptop", 1200.00, 15, supplier, 2.10)
    digital = DigitalProduct("D001", "System OS Pro", 149.99, 100, supplier, 4500.0)

    print("Supplier information through each Product:")
    physical.supplier.display_information()
    digital.supplier.display_information()

    # one Supplier object is shared; the Product stores a reference, not a copy
    assert physical.supplier is supplier
    assert digital.supplier is supplier

    # predict first: del only removes this variable name, not the Supplier object
    del supplier
    print("After 'del supplier':")
    physical.supplier.display_information()
    digital.supplier.display_information()
    assert physical.supplier.name == "TechSource Pte Ltd"

    # and the other way round: the Supplier outlives its Products
    remaining_supplier = physical.supplier
    del physical, digital
    print("After deleting both products:")
    remaining_supplier.display_information()
    assert remaining_supplier.supplier_id == "S001"


def test_aggregation() -> None:
    # the Product exists before any Inventory does
    product, _ = make_products()
    inventory_a = Inventory()
    inventory_b = Inventory()

    assert inventory_a.add_product(product)
    assert inventory_a.find_product("P100") is product
    assert inventory_b.find_product("P100") is None

    # predict first: removing drops the reference, the Product still works
    removed = inventory_a.remove_product("P100")
    assert removed is product
    assert inventory_a.find_product("P100") is None
    assert inventory_a.products == []
    print("After removal from Inventory A, the Product still works:")
    product.update_stock(7)
    product.display_information()
    assert product.stock == 7

    # the very same object moves to another inventory
    assert inventory_b.add_product(product)
    assert inventory_b.find_product("P100") is product
    print("Now in Inventory B:")
    inventory_b.display_all()

    # emptying an inventory does not destroy its products either
    inventory_b.remove_product("P100")
    assert inventory_b.products == []
    assert product.name == "Monitor"

    # removing something that is not there is reported, not an error
    assert inventory_b.remove_product("NOPE") is None


def test_inventory_collection_is_encapsulated() -> None:
    product, _ = make_products()
    inventory = Inventory()
    inventory.add_product(product)
    inventory.products.clear()  # only clears the returned copy
    assert inventory.find_product("P100") is product


TESTS = [
    test_association,
    test_aggregation,
    test_inventory_collection_is_encapsulated,
]


def main() -> None:
    for test in TESTS:
        print(f"\n=== {test.__name__} ===")
        test()
        print("PASS")
    print(f"\nAll {len(TESTS)} tests passed.")


if __name__ == "__main__":
    main()
