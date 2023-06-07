# Imports
import csv
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table


# File paths
BOUGHT_FILE = "bought.csv"
SOLD_FILE = "sold.csv"
TIME_FILE = "time.txt"


def advance_time(days):
    current_time = load_current_time()

    new_time = current_time + timedelta(days=days)

    update_time_in_csv(BOUGHT_FILE, current_time, new_time)
    update_time_in_csv(SOLD_FILE, current_time, new_time)

    save_current_time(new_time)

    print(
        f'Time advanced by {days} days. Current date: {new_time.strftime("%Y-%m-%d")}'
    )


def set_date(date):
    new_time = datetime.strptime(date, "%Y-%m-%d")
    current_time = load_current_time()

    update_time_in_csv(BOUGHT_FILE, current_time, new_time)
    update_time_in_csv(SOLD_FILE, current_time, new_time)

    save_current_time(new_time)

    print(f"Current date set to: {new_time.strftime('%Y-%m-%d')}")


def update_time_in_csv(filename, current_time, new_time):
    rows = []
    with open(filename, "r") as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            rows.append(row)

    for row in rows:
        date_index = 2 if current_time.strftime("%Y-%m-%d") in row else 3
        row[date_index] = new_time.strftime("%Y-%m-%d")

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def load_current_time():
    with open(TIME_FILE, "r") as file:
        return datetime.strptime(file.read().strip(), "%Y-%m-%d")


def save_current_time(current_time):
    with open(TIME_FILE, "w") as file:
        file.write(current_time.strftime("%Y-%m-%d"))


def add_product(args):
    product_name = args.product_name
    buy_date = args.buy_date
    buy_price = args.buy_price
    expiration_date = args.expiration_date
    quantity = args.quantity

    # Generate unique ID for the product
    product_id = get_next_id(BOUGHT_FILE)

    # Append product data to bought.csv
    with open(BOUGHT_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [product_id, product_name, buy_date, buy_price, expiration_date, quantity]
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
            product_id, product_name, _, _, _, _ = row
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
            product_id, _, _, _, _, _ = row
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
            product_id, product_name, _, _, expiration_date, _ = row
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
            try:
                sell_price = float(sell_price)  # Convert sell_price to float
            except ValueError:
                continue  # Skip this row if sell_price cannot be converted to float

            if start_date <= sell_date <= end_date:
                buy_price = get_buy_price(bought_id)
                revenue += sell_price
                profit += sell_price - buy_price

    return revenue, profit


def get_buy_price(bought_id):
    with open(BOUGHT_FILE, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == str(bought_id):
                return float(row[3])
    return 0.0


def export_inventory(filename):
    inventory = {}
    with open(BOUGHT_FILE, "r") as bought_file:
        bought_reader = csv.reader(bought_file)
        next(bought_reader)  # Skip header row
        for row in bought_reader:
            product_id, product_name, _, _, expiration_date, quantity = row
            if product_id not in inventory:
                inventory[product_id] = [product_id, product_name, 0, expiration_date]

            inventory[product_id][2] += int(quantity)  # Increment quantity

    with open(SOLD_FILE, "r") as sold_file:
        sold_reader = csv.reader(sold_file)
        next(sold_reader)  # Skip header row
        for row in sold_reader:
            _, bought_id, _, _ = row
            if bought_id in inventory:
                inventory[bought_id][2] -= 1  # Decrement quantity

    data = list(inventory.values())

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Product ID", "Product Name", "Quantity", "Expiration Date"])
        writer.writerows(data)

    print(f"Inventory exported to {filename} successfully.")


def check_expiration():
    console = Console()

    current_time = load_current_time().date()  # Convert current_time to datetime.date
    threshold = current_time + timedelta(
        days=7
    )  # Define a threshold for expiration alert (e.g., 7 days)

    expired_products = []
    with open(BOUGHT_FILE, "r") as file:
        reader = csv.reader(file)
        header = next(reader)  # Get the header row

        # Find the index of the expiration date column
        expiration_date_index = header.index("expiration-date")

        for row in reader:
            product_name = row[1]  # Product name is at index 1
            expiration_date = datetime.strptime(
                row[expiration_date_index], "%Y-%m-%d"
            ).date()

            if expiration_date <= current_time:  # Compare with current time
                expired_products.append((product_name, expiration_date))
            elif current_time < expiration_date <= threshold:
                days_remaining = (expiration_date - current_time).days
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
