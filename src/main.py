import sys
import argparse
from transaction_and_key_generator import generate_mock_transactions_and_keys
from chain_generator import generate_chain
from tests.chain_checker import check_chain
from utilities.display_chain import display_chain_info


def cli_parser():
    """Parse command line arguments for C-Chain parameters.
    
    Returns:
        dict: Parsed arguments with defaults
    """
    parser = argparse.ArgumentParser(
        description='C-Chain for V2X',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: python main.py -f transactions.json -c 50 -t 20'
    )
    
    parser.add_argument(
        '-f', '--filename',
        type=str,
        default='mock_transactions.json',
        help='Transaction output filename (default: mock_transactions.json)'
    )
    
    parser.add_argument(
        '-c', '--cars',
        type=int,
        default=100,
        help='Number of cars (default: 100)'
    )
    
    parser.add_argument(
        '-t', '--transactions',
        type=int,
        default=100,
        help='Number of transactions per car (default: 100)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    try:
        args = parser.parse_args()
        
        # Validate arguments
        if args.cars <= 0:
            raise ValueError("Number of cars must be positive integer")
        if args.transactions <= 0:
            raise ValueError("Number of transactions per car must be positive integer")
        
        return {
            'transactions_filename': args.filename,
            'number_of_cars': args.cars,
            'transactions_per_car': args.transactions,
            'verbose': args.verbose
        }
        
    except argparse.ArgumentError as e:
        print(f"Argument parsing error: {e}")
        print("Use -h or --help for usage information.")
        sys.exit(1)
    except ValueError as e:
        print(f"Invalid argument: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Parse command line arguments
        params = cli_parser()
        
        if params['verbose']:
            print("Parsed parameters:")
            print(f"  Transactions file: {params['transactions_filename']}")
            print(f"  Number of cars: {params['number_of_cars']}")
            print(f"  Transactions per car: {params['transactions_per_car']}")
            print()
        
        # Generates mock transactions, books them into a chain and tests chain continuity
        run_suite(
            transactions_filename=params['transactions_filename'], 
            number_of_cars=params['number_of_cars'], 
            transactions_per_car=params['transactions_per_car']
        )
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def run_suite(transactions_filename, number_of_cars, transactions_per_car):

    generate_mock_transactions_and_keys(transactions_filename=transactions_filename, number_of_cars=number_of_cars, transactions_per_car=transactions_per_car)
    print("\n" + "=" * 100)
    print("GENERATED MOCK TRANSACTIONS AND KEYS")
    print("=" * 100)
    
    generate_chain(transactions_filename=transactions_filename)
    
    print("\n" + "=" * 100)
    print("GENERATED CHAIN")
    print("=" * 100)
    print("\n" + "=" * 100)
    print("=" * 100)
    print("DISPLAY CHAIN START")
    print("=" * 100)
    print("=" * 100)
    
    display_chain_info()
    
    print("\n" + "=" * 100)
    print("=" * 100)
    print("DISPLAY CHAIN END")
    print("=" * 100)
    print("=" * 100)
    
    check_chain()
    
    print("\n" + "=" * 100)
    print("CHECKED CHAIN")
    print("=" * 100)