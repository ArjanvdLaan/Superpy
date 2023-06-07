# Imports
import argparse
import helper

# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"


# Your code below this line.
def main():
    pass

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
    parser_add_product.add_argument(
        "quantity", type=str, help="Quantity of the product"
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
    parser_set_date = subparsers.add_parser("set-date", help="Set the current date")
    parser_set_date.add_argument(
        "date", type=str, help="Date to set (YYYY-MM-DD)"
    )


    args = parser.parse_args()

    if args.command == "advance-time":
        helper.advance_time(args.days)
    elif args.command == "set-date":
        helper.set_date(args.date)
    elif args.command == "add-product":
        helper.add_product(args)
    elif args.command == "sell-product":
        helper.sell_product(args)
    elif args.command == "list-products":
        helper.list_products()
    elif args.command == "list-inventory":
        helper.list_inventory()
    elif args.command == "report":
        start_date = args.start_date
        end_date = args.end_date
        revenue, profit = helper.calculate_revenue_profit(start_date, end_date)
        print(f"Revenue from {start_date} to {end_date}: ${revenue}")
        print(f"Profit from {start_date} to {end_date}: ${profit}")
    elif args.command == "export-inventory":
        filename = args.filename
        helper.export_inventory(filename)
    elif args.command == "check-expiration":
        helper.check_expiration()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
