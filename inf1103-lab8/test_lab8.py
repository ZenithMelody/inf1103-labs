# Lab 8 tests. Run with: python test_lab8.py
# Each test prints its output (for evidence) and asserts the expected relationship.

import importlib.util
import inspect
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
Order = lab.Order
OrderLine = lab.OrderLine


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
    inventory_b.display_all_products()

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


def test_composition() -> None:
    physical, digital = make_products()

    order = Order("O001")
    order.add_order_line(physical, 2)  # 2 x 200.00
    order.add_order_line(digital, 3)   # 3 x 50.00
    order.display_information()
    assert order.calculate_total() == 550.00

    # predict first: same Product in two Orders -> two OrderLines, one Product
    other_order = Order("O002")
    other_order.add_order_line(physical, 1)
    line_a = order.order_lines[0]
    line_b = other_order.order_lines[0]
    print(f"OrderLine ids: {id(line_a)} and {id(line_b)} -> same object? {line_a is line_b}")
    print(f"Product ids:   {id(line_a.product)} and {id(line_b.product)} "
          f"-> same object? {line_a.product is line_b.product}")
    assert line_a is not line_b
    assert line_a.product is line_b.product is physical

    # lines are removed through the Order, and only affect that Order
    assert order.remove_order_line("P100")
    assert not order.remove_order_line("P100")
    assert order.calculate_total() == 150.00
    assert other_order.calculate_total() == 200.00

    # the copy from the property cannot be used to change the Order's lines
    other_order.order_lines.clear()
    assert len(other_order.order_lines) == 1

    # the OrderLines go with the Order; the Product does not
    del order, other_order, line_a, line_b
    physical.display_information()
    assert physical.name == "Monitor"


def test_order_rejects_invalid_quantity() -> None:
    physical, _ = make_products()
    order = Order("O003")
    for bad_quantity in (0, -1):
        try:
            order.add_order_line(physical, bad_quantity)
        except ValueError as error:
            print(f"Rejected quantity {bad_quantity}: {error}")
        else:
            raise AssertionError("quantity should have been rejected")
    assert order.order_lines == []


def test_type_hints_present() -> None:
    # every parameter and return value of every method is annotated
    missing = []
    for cls in (Supplier, Product, PhysicalProduct, DigitalProduct, lab.CanBeShipped,
                Inventory, OrderLine, Order):
        for name, member in vars(cls).items():
            if name.startswith("__") and name != "__init__":
                continue  # generated by Python, e.g. __annotate_func__
            function = member.fget if isinstance(member, property) else member
            function = getattr(function, "__func__", function)
            if not inspect.isfunction(function):
                continue
            signature = inspect.signature(function)
            if signature.return_annotation is inspect.Signature.empty:
                missing.append(f"{cls.__name__}.{name} return")
            for parameter in signature.parameters.values():
                if parameter.name not in ("self", "cls") and parameter.annotation is inspect.Parameter.empty:
                    missing.append(f"{cls.__name__}.{name}({parameter.name})")
    assert not missing, missing

    # the types chosen in the design
    print("Inventory.products ->", inspect.signature(Inventory.products.fget).return_annotation)
    print("Inventory.find_product ->", inspect.signature(Inventory.find_product).return_annotation)
    print("Order.order_lines ->", inspect.signature(Order.order_lines.fget).return_annotation)
    print("Order.add_order_line ->", inspect.signature(Order.add_order_line))
    assert inspect.signature(Product.__init__).parameters["supplier"].annotation is Supplier
    assert inspect.signature(Inventory.products.fget).return_annotation == list[Product]
    assert inspect.signature(Inventory.find_product).return_annotation == (Product | None)
    assert inspect.signature(Order.order_lines.fget).return_annotation == list[OrderLine]


def test_empty_order_total_is_a_float() -> None:
    total = Order("O004").calculate_total()
    assert total == 0.0 and type(total) is float


# section 6.2: written against Product only, it never asks which subclass it was given
def show_product_details(product: Product) -> None:
    product.display_information()
    print(product.get_fulfilment_info())


def test_substitutability() -> None:
    physical, digital = make_products()
    show_product_details(physical)
    show_product_details(digital)

    # both types go through the Inventory's normal operations
    inventory = Inventory()
    assert inventory.add_product(physical)
    assert inventory.add_product(digital)
    assert inventory.find_product("P100") is physical
    assert inventory.find_product("D100") is digital
    inventory.display_all_products()
    assert inventory.remove_product("D100") is digital
    assert inventory.products == [physical]


def test_subclasses_preserve_product_expectations() -> None:
    # section 6.3: update_stock means the same thing on every Product
    for product in make_products():
        product.update_stock(5)
        assert product.stock == 5
        product.update_stock(0)  # zero is valid for the parent, so for subclasses too
        assert product.stock == 0
        try:
            product.update_stock(-1)
        except ValueError:
            pass
        else:
            raise AssertionError("negative stock should be rejected")
        assert product.stock == 0
        assert isinstance(product.get_fulfilment_info(), str)


def test_polymorphism() -> None:
    physical, digital = make_products()
    inventory = Inventory()
    inventory.add_product(physical)
    inventory.add_product(digital)

    expected = {
        "P100": "Requires physical packaging and courier shipping.",
        "D100": "Delivered digitally via direct download link.",
    }

    # one loop, no isinstance(): each object supplies its own implementation
    for product in inventory.products:
        product.display_information()
        print(product.get_fulfilment_info())
        assert product.get_fulfilment_info() == expected[product.product_id]


def test_physical_product_implements_can_be_shipped() -> None:
    physical, _ = make_products()
    assert isinstance(physical, lab.CanBeShipped)
    assert physical.calculate_shipping_cost() == 20.00


TESTS = [
    test_association,
    test_aggregation,
    test_inventory_collection_is_encapsulated,
    test_composition,
    test_order_rejects_invalid_quantity,
    test_empty_order_total_is_a_float,
    test_type_hints_present,
    test_substitutability,
    test_subclasses_preserve_product_expectations,
    test_polymorphism,
    test_physical_product_implements_can_be_shipped,
]


def main() -> None:
    for test in TESTS:
        print(f"\n=== {test.__name__} ===")
        test()
        print("PASS")
    print(f"\nAll {len(TESTS)} tests passed.")


if __name__ == "__main__":
    main()
