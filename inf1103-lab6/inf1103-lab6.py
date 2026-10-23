import json
import os

FILENAME = "inventory.json"


class Product:
    # represents & manages an individual product unit

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
        # modify internal stock quantity
        if new_stock < 0:
            raise ValueError("Stock quantity cannot be negative.")
        self._stock = new_stock

    def display_information(self) -> None:
        # display details of this individual product
        print(
            f"ID: {self._product_id} | Name: {self.name} | "
            f"Price: ${self._price:.2f} | Stock: {self._stock}"
        )

    def to_dict(self) -> dict:
        return {
            "id": self._product_id,
            "name": self.name,
            "price": self._price,
            "stock": self._stock,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            product_id=data["id"],
            name=data["name"],
            price=data["price"],
            stock=data["stock"],
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