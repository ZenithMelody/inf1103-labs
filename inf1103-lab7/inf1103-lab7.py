# github project repo: https://github.com/ZenithMelody/inf1103-labs/tree/main

import json
import os
from abc import ABC, abstractmethod

FILENAME = "inventory.json"

# represents & manages an individual product unit
class Product(ABC):

    def __init__(self, product_id: str, name: str, price: float, stock: int):
        self._product_id = product_id
        self.name = name
        self._price = float(price)
        self._stock = int(stock)

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
            f"Price: ${self._price:.2f} | Stock: {self._stock}"
        )

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass

# products that can be shipped physically
class CanBeShipped(ABC):

    @abstractmethod
    def calculate_shipping_cost(self) -> float:
        pass

# physical item that needs storage and shipping
class PhysicalProduct(Product):

    SHIPPING_RATE_PER_KG = 5.00  # base calculation rule

    def __init__(self, product_id: str, name: str, price: float, stock: int, weight: float):
        super().__init__(product_id, name, price, stock)
        self._weight = float(weight)

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

# virtual product delivered digitally
class DigitalProduct(Product):

    def __init__(self, product_id: str, name: str, price: float, stock: int, download_size: float):
        super().__init__(product_id, name, price, stock)
        self._download_size = float(download_size)

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

class Inventory:
    #  manage collection of Product objects

    def __init__(self):
        self._products = []

    def add_product(self, product: Product) -> bool:

        # apends a new Product object if no duplicate ID exists
        if self.search_product(product.product_id):
            return False
        self._products.append(product)
        return True

    def search_product(self, product_id: str) -> Product | None:
        
        # search product by ID
        for prod in self._products:
            if prod.product_id.upper() == product_id.upper():
                return prod
        return None

    def display_all(self) -> None:

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
                    for item in raw_data:
                        self._products.append(Product.from_dict(item))
                print(f"{filename} found.")
                print("Inventory loaded successfully.\n")
            except Exception as e:
                print(f"Malfunction loading inventory data: {e}\n")
                self._products = []
        else:
            print(f"{filename} not found. Initializing default inventory.\n")

        if not self._products:
            default_items = [
                Product("P001", "Laptop", 1200.00, 15),
                Product("P002", "Mouse", 25.50, 40),
                Product("P003", "Keyboard", 45.00, 25),
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

def display_menu():
    print("---------- MENU ----------")
    print("1. Display All Products")
    print("2. Add Product")
    print("3. Update Stock")
    print("4. Search Product")
    print("5. Save Inventory")
    print("6. Exit")
    print("--------------------------")


def main():
    print("=" * 45)
    print("INVENTORY MANAGEMENT SYSTEM")
    print("=" * 45 + "\n")

    inventory = Inventory()
    inventory.load_from_file(FILENAME)

    while True:
        display_menu()
        option = input("\nEnter option: ").strip()

        if option == "1":
            inventory.display_all()

        elif option == "2":
            print("\nAdd New Product")
            prod_id = input("Product ID: ").strip()
            if inventory.search_product(prod_id):
                print("Error: Product ID already exists in data-stack.\n")
                continue

            name = input("Product Name: ").strip()
            try:
                price = float(input("Price: "))
                stock = int(input("Stock Quantity: "))
                new_prod = Product(prod_id, name, price, stock)
                inventory.add_product(new_prod)
                print("\nProduct added successfully!\n")
            except ValueError as e:
                print(f"Data type mismatch or invalid value: {e}\n")

        elif option == "3":
            print("\nUpdate Stock")
            prod_id = input("Enter Product ID to update: ").strip()
            prod = inventory.search_product(prod_id)
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
            prod = inventory.search_product(prod_id)
            if prod:
                print("\nProduct Found")
                print("-" * 45)
                prod.display_information()
                print("-" * 45 + "\n")
            else:
                print("\nProduct not found.\n")

        elif option == "5":
            inventory.save_to_file(FILENAME)

        elif option == "6":
            print("\nSaving inventory before exit...")
            inventory.save_to_file(FILENAME)
            print("Thank you for using Inventory Management System.")
            print("Program terminated.")
            break
        else:
            print("Invalid input. Please enter an option from 1 to 6.\n")

if __name__ == "__main__":
    main()