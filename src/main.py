from transaction_and_key_generator import generate_mock_transactions_and_keys
from chain_generator import generate_chain
from tests.chain_checker import check_chain
from utilities.display_chain import display_chain_info


def run_suite():
    # Adjust parameters here:
    transactions_filename = "mock_transactions.json"
    number_of_cars = 5
    transactions_per_car = 10

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

if __name__ == "__main__":
    # Generates mock transactions, books them into the chain and tests chain continuity
    run_suite()