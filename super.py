# Imports
import argparse
import csv
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table

# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"


# Your code below this line.
def main():
    pass


# File paths
BOUGHT_FILE = "bought.csv"
SOLD_FILE = "sold.csv"
TIME_FILE = "time.txt"


def initialize_time():
    # Initialize time to today's date
    current_time = datetime.now().strftime("%Y-%m-%d")
    with open(TIME_FILE, "w") as file:
        file.write(current_time)


def advance_time(days):
    # Read current time from file
    with open(TIME_FILE, "r") as file:
        current_time = datetime.strptime(file.read().strip(), "%Y-%m-%d")

    # Calculate new time by advancing days
    new_time = current_time + timedelta(days=days)

    # Save new time to file
    with open(TIME_FILE, "w") as file:
        file.write(new_time.strftime("%Y-%m-%d"))

    print(
        f'Time advanced by {days} days. Current date: {new_time.strftime("%Y-%m-%d")}'
    )


def add_product(args):
    product_name = args.product_name
    buy_date = args.buy_date
    buy_price = args.buy_price
    expiration_date = args.expiration_date

    # Generate unique ID for the product
    product_id = get_next_id(BOUGHT_FILE)

    # Append product data to bought.csv
    with open(BOUGHT_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [product_id, product_name, buy_date, buy_price, expiration_date]
        )

    print("Product added successfully.")


def sell_product(args):
    bought_id = args.bought_id
    sell_date = args.sell_date
    sell_price = args.sell_price

    # Check if the bought product exists
    if not product_exists(bought_id, BOUGHT_FILE):
        print(f"Product with ID {bought_id} does not exist.")
        return

    # Generate unique ID for the sold product
    sold_id = get_next_id(SOLD_FILE)

    # Append sold product data to sold.csv
    with open(SOLD_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([sold_id, bought_id, sell_date, sell_price])

    print("Product sold successfully.")


def product_exists(product_id, file_path):
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(product_id):
                return True
    return False


def get_next_id(file_path):
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        rows = list(reader)
        if rows:
            last_id = rows[-1][0]
            try:
                return int(last_id) + 1
            except ValueError:
                # Handle the case where the last ID is not a valid integer
                print(f"Invalid ID found in {file_path}. Generating a new ID.")
                return len(rows) + 1
        else:
            return 1


def list_products():
    console = Console()

    with open(BOUGHT_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row

        table = Table(title="Available Products")
        table.add_column("Product ID", justify="right")
        table.add_column("Product Name")

        for row in reader:
            product_id, product_name, _, _, _ = row
            table.add_row(product_id, product_name)

        console.print(table)


def list_inventory():
    console = Console()

    inventory = {}
    with open(BOUGHT_FILE, "r") as bought_file, open(SOLD_FILE, "r") as sold_file:
        bought_reader = csv.reader(bought_file)
        sold_reader = csv.reader(sold_file)

        next(bought_reader)  # Skip header row in bought.csv
        next(sold_reader)  # Skip header row in sold.csv

        for row in bought_reader:
            product_id, _, _, _, _ = row
            if product_id not in inventory:
                inventory[product_id] = 1
            else:
                inventory[product_id] += 1

        for row in sold_reader:
            _, bought_id, _, _ = row
            if bought_id in inventory:
                inventory[bought_id] -= 1

    table = Table(title="Inventory")
    table.add_column("Product ID", justify="right")
    table.add_column("Product Name")
    table.add_column("Quantity", justify="right")
    table.add_column("Expiration Date")

    with open(BOUGHT_FILE, "r") as bought_file:
        reader = csv.reader(bought_file)
        next(reader)  # Skip header row

        for row in reader:
            product_id, product_name, _, _, expiration_date = row
            quantity = inventory.get(product_id, 0)
            table.add_row(product_id, product_name, str(quantity), expiration_date)

    console.print(table)


def calculate_revenue_profit(start_date, end_date):
    revenue = 0
    profit = 0

    with open(SOLD_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            _, bought_id, sell_date, sell_price = row
            if start_date <= sell_date <= end_date:
                buy_price = get_buy_price(bought_id)
                revenue += float(sell_price)
                profit += float(sell_price) - float(buy_price)

    return revenue, profit


def get_buy_price(bought_id):
    with open(BOUGHT_FILE, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(bought_id):
                return row[3]
    return 0


def export_inventory(filename):
    inventory = {}
    with open(BOUGHT_FILE, "r") as bought_file:
        bought_reader = csv.reader(bought_file)
        next(bought_reader)  # Skip header row
        for row in bought_reader:
            product_id, product_name, _, _, expiration_date = row
            if product_id not in inventory:
                inventory[product_id] = [product_id, product_name, 0, expiration_date]

    with open(SOLD_FILE, "r") as sold_file:
        sold_reader = csv.reader(sold_file)
        next(sold_reader)  # Skip header row
        for row in sold_reader:
            _, bought_id, _, _ = row
            if bought_id in inventory:
                inventory[bought_id][2] += 1

    data = list(inventory.values())

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Product ID", "Product Name", "Quantity", "Expiration Date"])
        writer.writerows(data)

    print(f"Inventory exported to {filename} successfully.")


def check_expiration():
    console = Console()

    today = datetime.now().date()
    threshold = today + timedelta(
        days=7
    )  # Define a threshold for expiration alert (e.g., 7 days)

    expired_products = []
    with open(BOUGHT_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row

        for row in reader:
            _, product_name, _, _, expiration_date = row
            expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()

            if expiration_date <= today:
                expired_products.append((product_name, expiration_date))
            elif today < expiration_date <= threshold:
                days_remaining = (expiration_date - today).days
                console.print(
                    f"Product '{product_name}' will expire in {days_remaining} days."
                )

    if expired_products:
        table = Table(title="Expired Products")
        table.add_column("Product Name")
        table.add_column("Expiration Date")

        for product_name, expiration_date in expired_products:
            table.add_row(product_name, str(expiration_date))

        console.print(table)
    else:
        console.print("No expired products found.")


def main():
    parser = argparse.ArgumentParser(
        prog="SuperPy", description="Supermarket inventory management tool"
    )

    subparsers = parser.add_subparsers(dest="command")

    parser_advance_time = subparsers.add_parser(
        "advance-time", help="Advance time by specified days"
    )
    parser_advance_time.add_argument("days", type=int, help="Number of days to advance")

    parser_add_product = subparsers.add_parser("add-product", help="Add a new product")
    parser_add_product.add_argument(
        "product_name", type=str, help="Name of the product"
    )
    parser_add_product.add_argument(
        "buy_date", type=str, help="Date the product was bought (YYYY-MM-DD)"
    )
    parser_add_product.add_argument(
        "buy_price", type=float, help="Price at which the product was bought"
    )
    parser_add_product.add_argument(
        "expiration_date", type=str, help="Expiration date of the product (YYYY-MM-DD)"
    )

    parser_sell_product = subparsers.add_parser("sell-product", help="Sell a product")
    parser_sell_product.add_argument(
        "bought_id", type=int, help="ID of the product being sold"
    )
    parser_sell_product.add_argument(
        "sell_date", type=str, help="Date the product was sold (YYYY-MM-DD)"
    )
    parser_sell_product.add_argument(
        "sell_price", type=float, help="Price at which the product was sold"
    )

    subparsers.add_parser("list-products", help="List all available products")

    subparsers.add_parser("list-inventory", help="List the inventory")

    parser_report = subparsers.add_parser(
        "report", help="Generate revenue and profit report"
    )
    parser_report.add_argument(
        "start_date", type=str, help="Start date of the report (YYYY-MM-DD)"
    )
    parser_report.add_argument(
        "end_date", type=str, help="End date of the report (YYYY-MM-DD)"
    )

    parser_export_inventory = subparsers.add_parser(
        "export-inventory", help="Export inventory to a CSV file"
    )
    parser_export_inventory.add_argument(
        "filename", type=str, help="Name of the CSV file to export inventory"
    )
    parser_check_expiration = subparsers.add_parser(
        "check-expiration", help="Check product expiration"
    )

    args = parser.parse_args()

    if args.command == "advance-time":
        advance_time(args.days)
    elif args.command == "add-product":
        add_product(args)
    elif args.command == "sell-product":
        sell_product(args)
    elif args.command == "list-products":
        list_products()
    elif args.command == "list-inventory":
        list_inventory()
    elif args.command == "report":
        start_date = args.start_date
        end_date = args.end_date
        revenue, profit = calculate_revenue_profit(start_date, end_date)
        print(f"Revenue from {start_date} to {end_date}: ${revenue}")
        print(f"Profit from {start_date} to {end_date}: ${profit}")
    elif args.command == "export-inventory":
        filename = args.filename
        export_inventory(filename)
    elif args.command == "check-expiration":
        check_expiration()
    else:
        parser.print_help()


if __name__ == "__main__":
    initialize_time()
    main()
