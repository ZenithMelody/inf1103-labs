# github project repo: https://github.com/ZenithMelody/inf1103-labs/tree/main

import json
import os
from abc import ABC, abstractmethod
from typing import Any

FILENAME: str = "inventory.json"

# supplier of products -> ASSOCIATION with Product (no ownership)
class Supplier:
 
    def __init__(self, supplier_id: str, name: str, contact_email: str) -> None:
        self._supplier_id: str = supplier_id
        self.name: str = name
        self.contact_email: str = contact_email
 
    @property
    def supplier_id(self) -> str:
        return self._supplier_id
 
    def display_information(self) -> None:
        print(
            f"Supplier ID: {self._supplier_id} | Name: {self.name} | "
            f"Email: {self.contact_email}"
        )
 
    def to_dict(self) -> dict[str, str]:
        return {
            "id": self._supplier_id,
            "name": self.name,
            "contact_email": self.contact_email,
        }
 
    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Supplier":
        return cls(data["id"], data["name"], data["contact_email"])

# for JSON saved by Lab 7 (no supplier field)
UNKNOWN_SUPPLIER_DATA: dict[str, str] = {"id": "S000", "name": "Unknown Supplier", "contact_email": "n/a"}

# represents & manages an individual product unit
class Product(ABC):

    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier) -> None:
        self._product_id: str = product_id
        self.name: str = name
        self._price: float = float(price)
        self._stock: int = int(stock)
        self.supplier: Supplier = supplier  # association: a reference, not ownership

    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def price(self) -> float:
        return self._price

    @property
    def stock(self) -> int:
        return self._stock

    def update_stock(self, new_stock: int) -> None:
        if new_stock < 0:
            raise ValueError("Stock quantity cannot be negative.")
        self._stock = new_stock

    def display_information(self) -> None:
        print(
            f"ID: {self._product_id} | Name: {self.name} | "
            f"Price: ${self._price:.2f} | Stock: {self._stock} | "
            f"Supplier: {self.supplier.name}"
        )

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass

    # a JSON record mixes strings, numbers and a nested supplier record, hence Any
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self._product_id,
            "name": self.name,
            "price": self._price,
            "stock": self._stock,
            "supplier": self.supplier.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], supplier: Supplier) -> "Product":
        prod_type = data.get("type", "physical").lower()
        if prod_type == "physical":
            return PhysicalProduct(
                product_id=data["id"],
                name=data["name"],
                price=data["price"],
                stock=data["stock"],
                supplier=supplier,
                weight=data.get("weight", 1.0),
            )
        elif prod_type == "digital":
            return DigitalProduct(
                product_id=data["id"],
                name=data["name"],
                price=data["price"],
                stock=data["stock"],
                supplier=supplier,
                download_size=data.get("download_size", 100.0),
            )
        else:
            raise ValueError(f"Unknown product type identifier: {prod_type}")

# products that can be shipped physically
class CanBeShipped(ABC):

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass

# physical item that needs storage and shipping
class PhysicalProduct(Product, CanBeShipped):

    SHIPPING_RATE_PER_KG: float = 5.00  # base calculation rule

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self._weight: float = float(weight)

    @property
    def weight(self) -> float:
        return self._weight

    def get_fulfilment_info(self) -> str:
        return "Requires physical packaging and courier shipping."

    def calculate_shipping_cost(self) -> float:
        return self._weight * self.SHIPPING_RATE_PER_KG

    def display_information(self) -> None:
        super().display_information()
        print(
            f"   -> Type: Physical | Weight: {self._weight:.2f} kg | "
            f"Shipping Cost: ${self.calculate_shipping_cost():.2f} | "
            f"Fulfilment: {self.get_fulfilment_info()}"
        )

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["type"] = "physical"
        data["weight"] = self._weight
        return data

# virtual product delivered digitally
class DigitalProduct(Product):

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, download_size: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self._download_size: float = float(download_size)

    @property
    def download_size(self) -> float:
        return self._download_size

    def get_fulfilment_info(self) -> str:
        return "Delivered digitally via direct download link."

    def display_information(self) -> None:
        super().display_information()
        print(
            f"   -> Type: Digital  | Download Size: {self._download_size:.2f} MB | "
            f"Fulfilment: {self.get_fulfilment_info()}"
        )

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["type"] = "digital"
        data["download_size"] = self._download_size
        return data

# AGGREGATION with Product: holds references, but does not create or own them
class Inventory:

    def __init__(self) -> None:
        self._products: list[Product] = []

    @property
    def products(self) -> list[Product]:
        # a copy, so the collection itself can only change through Inventory methods
        return list(self._products)

    def add_product(self, product: Product) -> bool:

        # apends a new Product object if no duplicate ID exists
        if self.find_product(product.product_id):
            return False
        self._products.append(product)
        return True

    def remove_product(self, product_id: str) -> Product | None:

        # removes only the reference; the Product itself lives on and is handed back
        product = self.find_product(product_id)
        if product:
            self._products.remove(product)
        return product

    def find_product(self, product_id: str) -> Product | None:

        # find product by ID
        for prod in self._products:
            if prod.product_id.upper() == product_id.upper():
                return prod
        return None

    def display_all_products(self) -> None:

        # display all products stored in inventory
        print("\nCurrent Inventory")
        print("-" * 45)
        if not self._products:
            print("Inventory stack is currently empty.")
        else:
            for prod in self._products:
                prod.display_information()
        print("-" * 45 + "\n")

    def load_from_file(self, filename: str) -> None:

        # load products from JSON file 
        self._products = []
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    raw_data = json.load(f)
                # one Supplier object per supplier ID, shared by its products
                suppliers: dict[str, Supplier] = {}
                for item in raw_data:
                    sup_data = item.get("supplier", UNKNOWN_SUPPLIER_DATA)
                    if sup_data["id"] not in suppliers:
                        suppliers[sup_data["id"]] = Supplier.from_dict(sup_data)
                    self._products.append(Product.from_dict(item, suppliers[sup_data["id"]]))
                print(f"{filename} found.")
                print("Inventory loaded successfully.\n")
            except Exception as e:
                print(f"Malfunction loading inventory data: {e}\n")
                self._products = []
        else:
            print(f"{filename} not found. Initializing default inventory.\n")

        if not self._products:
            hardware_supplier = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.com")
            software_supplier = Supplier("S002", "SoftWorks Digital", "support@softworks.com")
            default_items = [
                PhysicalProduct("P001", "Laptop", 1200.00, 15, hardware_supplier, 2.10),
                PhysicalProduct("P002", "Mouse", 25.50, 40, hardware_supplier, 0.12),
                PhysicalProduct("P003", "Keyboard", 45.00, 25, hardware_supplier, 0.85),
                DigitalProduct("D001", "System OS Pro", 149.99, 100, software_supplier, 4500.0),
            ]
            for prod in default_items:
                self.add_product(prod)

    def save_to_file(self, filename: str) -> None:

        # save/write inventory state to JSON file
        print("Saving inventory...")
        try:
            data = [prod.to_dict() for prod in self._products]
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Inventory saved successfully to {filename}.\n")
        except Exception as e:
            print(f"Unappeased friction during save operation: {e}\n")

# one product and quantity within an Order
# ASSOCIATION with Product (refers to it, does not own it)
# only Order should create these: an OrderLine has no meaning outside its Order
class OrderLine:

    def __init__(self, product: Product, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Order quantity must be greater than zero.")
        self.product: Product = product
        self.quantity: int = quantity

    def calculate_subtotal(self) -> float:
        return self.product.price * self.quantity

    def display_information(self) -> None:
        print(
            f"{self.product.product_id} | {self.product.name} | "
            f"Qty: {self.quantity} | Subtotal: ${self.calculate_subtotal():.2f}"
        )

# COMPOSITION with OrderLine: creates and manages its lines, which go when it goes
# STRATEGY pattern: one class per way of discounting an order total
class DiscountStrategy(ABC):

    @abstractmethod
    def apply(self, total: float) -> float:
        pass

# the default: the total is left unchanged
class NoDiscount(DiscountStrategy):

    def apply(self, total: float) -> float:
        return total

# e.g. PercentageDiscount(10) takes 10% off
class PercentageDiscount(DiscountStrategy):

    def __init__(self, percentage: float) -> None:
        if not 0 <= percentage <= 100:
            raise ValueError("Discount percentage must be between 0 and 100.")
        self.percentage: float = percentage

    def apply(self, total: float) -> float:
        return total * (1 - self.percentage / 100)

# e.g. BulkDiscount(200, 20) takes 20 off any total of 200 or more
class BulkDiscount(DiscountStrategy):

    def __init__(self, threshold: float, amount: float) -> None:
        if threshold < 0 or amount < 0:
            raise ValueError("Discount threshold and amount cannot be negative.")
        self.threshold: float = threshold
        self.amount: float = amount

    def apply(self, total: float) -> float:
        if total >= self.threshold:
            return total - self.amount
        return total
        
class Order:

    def __init__(self, order_id: str) -> None:
        self.order_id: str = order_id
        self._order_lines: list[OrderLine] = []

    @property
    def order_lines(self) -> list[OrderLine]:
        # a copy, so lines can only be added or removed through Order methods
        return list(self._order_lines)

    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)
        self._order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        for order_line in self._order_lines:
            if order_line.product.product_id.upper() == product_id.upper():
                self._order_lines.remove(order_line)
                return True
        return False

    def calculate_total(self) -> float:
        return sum((line.calculate_subtotal() for line in self._order_lines), 0.0)

    def display_information(self) -> None:
        print(f"Order ID: {self.order_id}")
        for order_line in self._order_lines:
            order_line.display_information()
        print(f"Total: ${self.calculate_total():.2f}")

def prompt_supplier() -> Supplier:
    supplier_id = input("Supplier ID: ").strip()
    name = input("Supplier Name: ").strip()
    email = input("Supplier Email: ").strip()
    return Supplier(supplier_id, name, email)


def create_order(inventory: Inventory) -> Order | None:
    order_id = input("Order ID: ").strip()
    order = Order(order_id)

    while True:
        prod_id = input("Product ID to order (blank to finish): ").strip()
        if not prod_id:
            break
        prod = inventory.find_product(prod_id)
        if not prod:
            print("Product not found.")
            continue
        try:
            order.add_order_line(prod, int(input(f"Quantity of {prod.name}: ")))
        except ValueError as e:
            print(f"Invalid quantity: {e}")

    if not order.order_lines:
        print("No order lines added. Order discarded.\n")
        return None
    return order


def display_menu() -> None:
    print("---------- MENU ----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Remove Product")
    print("6. Create Order")
    print("7. Display Orders")
    print("8. Save Inventory")
    print("9. Exit")
    print("--------------------------")


def main() -> None:
    print("=" * 45)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 45 + "\n")

    inventory = Inventory()
    inventory.load_from_file(FILENAME)
    orders: list[Order] = []  # kept for this session only

    while True:
        display_menu()
        option = input("\nEnter option: ").strip()

        if option == "1":
            inventory.display_all_products()

        elif option == "2":
            print("\nAdd New Product")
            prod_id = input("Product ID: ").strip()
            if inventory.find_product(prod_id):
                print("Error: Product ID already exists in data-stack.\n")
                continue

            print("Select Product Type:")
            print("1. Physical Product")
            print("2. Digital Product")
            type_choice = input("Enter choice (1 or 2): ").strip()

            if type_choice not in ("1", "2"):
                print("Invalid product type selected. Operation aborted.\n")
                continue

            name = input("Product Name: ").strip()
            try:
                price = float(input("Price: "))
                stock = int(input("Stock Quantity: "))
                supplier = prompt_supplier()

                if type_choice == "1":
                    weight = float(input("Weight (kg): "))
                    new_prod = PhysicalProduct(prod_id, name, price, stock, supplier, weight)
                else:
                    download_size = float(input("Download Size (MB): "))
                    new_prod = DigitalProduct(prod_id, name, price, stock, supplier, download_size)

                inventory.add_product(new_prod)
                print("\nProduct added successfully!\n")
            except ValueError as e:
                print(f"Data type mismatch or invalid value: {e}\n")

        elif option == "3":
            print("\nUpdate Stock")
            prod_id = input("Enter Product ID to update: ").strip()
            prod = inventory.find_product(prod_id)
            if prod:
                try:
                    new_stock = int(input(f"Enter new stock for {prod.name}: "))
                    prod.update_stock(new_stock)
                    print("Stock updated successfully!\n")
                except ValueError:
                    print("Invalid stock entry. Operation aborted.\n")
            else:
                print("Product not found.\n")

        elif option == "4":
            print("\nSearch Product")
            prod_id = input("Enter Product ID: ").strip()
            prod = inventory.find_product(prod_id)
            if prod:
                print("\nProduct Found")
                print("-" * 45)
                prod.display_information()
                print("-" * 45 + "\n")
            else:
                print("\nProduct not found.\n")

        elif option == "5":
            print("\nRemove Product")
            prod_id = input("Enter Product ID to remove: ").strip()
            prod = inventory.remove_product(prod_id)
            if prod:
                print(f"{prod.name} removed from inventory.\n")
            else:
                print("Product not found.\n")

        elif option == "6":
            print("\nCreate Order")
            order = create_order(inventory)
            if order:
                orders.append(order)
                print("\nOrder created!")
                order.display_information()
                print()

        elif option == "7":
            print("\nOrders")
            print("-" * 45)
            if not orders:
                print("No orders created yet.")
            for order in orders:
                order.display_information()
            print("-" * 45 + "\n")

        elif option == "8":
            inventory.save_to_file(FILENAME)

        elif option == "9":
            print("\nSaving inventory before exit...")
            inventory.save_to_file(FILENAME)
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid input. Please enter an option from 1 to 9.\n")

if __name__ == "__main__":
    main()