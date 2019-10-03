"""Example of sending transactions.
Before running this script ensure that `cryptocurrency-advanced` service is enabled.
"""

from typing import Tuple
import time
import requests
from exonum_client import ExonumClient, ModuleManager, MessageGenerator
from exonum_client.crypto import KeyPair, PublicKey

from examples.protobuf import cryptocurrency_advanced_protobuf_provider


def run() -> None:
    """This example creates two wallets (for Alice and Bob) and performs several
    transactions between these wallets."""
    protobuf_provider = cryptocurrency_advanced_protobuf_provider()

    client = ExonumClient(hostname="127.0.0.1", public_api_port=8080, private_api_port=8081)
    client.set_protobuf_provider(protobuf_provider)

    with client.protobuf_loader() as loader:
        # Load and compile proto files:
        loader.load_main_proto_files()
        loader.load_service_proto_files(0, "cryptocurrency-advanced")

        instance_id = get_cryptocurrency_instance_id(client)

        cryptocurrency_message_generator = MessageGenerator(instance_id, "cryptocurrency-advanced", "cryptocurrency")

        alice_keypair = create_wallet(client, cryptocurrency_message_generator, "Alice")
        bob_keypair = create_wallet(client, cryptocurrency_message_generator, "Bob")

        alice_balance = get_balance(client, alice_keypair.public_key)
        bob_balance = get_balance(client, bob_keypair.public_key)
        print("Created the wallets for Alice and Bob. Balance:")
        print(f" Alice => {alice_balance}")
        print(f" Bob => {bob_balance}")

        amount = 10
        alice_balance, bob_balance = transfer(
            client, cryptocurrency_message_generator, alice_keypair, bob_keypair.public_key, amount
        )

        print(f"Transferred {amount} tokens from Alice's wallet to Bob's one")
        print(f" Alice => {alice_balance}")
        print(f" Bob => {bob_balance}")

        amount = 25
        bob_balance, alice_balance = transfer(
            client, cryptocurrency_message_generator, bob_keypair, alice_keypair.public_key, amount
        )

        print(f"Transferred {amount} tokens from Bob's wallet to Alice's one")
        print(f" Alice => {alice_balance}")
        print(f" Bob => {bob_balance}")


def get_cryptocurrency_instance_id(_client: ExonumClient) -> int:
    """Returns cryptocurrency service id."""
    # For 0.12 it's a constant.
    return 128


def create_wallet(client: ExonumClient, message_generator: MessageGenerator, name: str) -> KeyPair:
    """Creates a wallet with the given name and returns a KeyPair for it."""
    key_pair = KeyPair.generate()

    # Load the "service.proto" from the Cryptocurrency service:
    cryptocurrency_module = ModuleManager.import_service_module("cryptocurrency-advanced", "cryptocurrency")

    # Create a Protobuf message:
    create_wallet_message = cryptocurrency_module.CreateWallet()
    create_wallet_message.name = name

    # Convert the Protobuf message to an Exonum message and sign it:
    create_wallet_tx = message_generator.create_message(create_wallet_message)
    create_wallet_tx.sign(key_pair)

    # Send the transaction to Exonum:
    response = client.send_transaction(create_wallet_tx)
    ensure_status_code(response)
    tx_hash = response.json()["tx_hash"]

    # Wait for new blocks:
    # with client.create_subscriber() as subscriber:
    # subscriber.wait_for_new_block()
    # subscriber.wait_for_new_block()

    # If node is launched via `dry-run`, subscriber will not work because of the
    # CORS configuration. This issue is fixed on the `dynamic_services` branch
    # already.
    time.sleep(1)

    ensure_transaction_success(client, tx_hash)

    print(f"Successfully created wallet with name '{name}'")

    return key_pair


def transfer(
    client: ExonumClient, message_generator: MessageGenerator, from_keypair: KeyPair, to_key: PublicKey, amount: int
) -> Tuple[int, int]:
    """This example transfers tokens from one wallet to the other one and
    returns the balances of these wallets."""

    cryptocurrency_module = ModuleManager.import_service_module("cryptocurrency-advanced", "cryptocurrency")
    # Note that since we are using the Cryptocurrency module,
    # we need to load helpers from this module and not from the main module:
    helpers_module = ModuleManager.import_service_module("cryptocurrency-advanced", "helpers")

    transfer_message = cryptocurrency_module.Transfer()
    transfer_message.to.CopyFrom(helpers_module.PublicKey(data=to_key.value))
    transfer_message.amount = amount
    transfer_message.seed = Seed.get_seed()

    transfer_tx = message_generator.create_message(transfer_message)
    transfer_tx.sign(from_keypair)

    response = client.send_transaction(transfer_tx)
    ensure_status_code(response)
    tx_hash = response.json()["tx_hash"]

    # Wait for new blocks:

    # with client.create_subscriber() as subscriber:
    # subscriber.wait_for_new_block()
    # subscriber.wait_for_new_block()

    # If node is launched via `dry-run`, subscriber will not work because of the
    # CORS configuration. This issue is fixed on the `dynamic_services` branch
    # already.
    time.sleep(1)

    ensure_transaction_success(client, tx_hash)

    from_balance = get_balance(client, from_keypair.public_key)
    to_balance = get_balance(client, to_key)

    return from_balance, to_balance


def get_balance(client: ExonumClient, key: PublicKey) -> int:
    """The example returns the balance of the wallet."""

    # Call the /wallets/info endpoint to retrieve the balance:
    wallet_info = client.get_service("cryptocurrency", "v1/wallets/info?pub_key={}".format(key.hex()))
    ensure_status_code(wallet_info)
    balance = wallet_info.json()["wallet_proof"]["to_wallet"]["entries"][0]["value"]["balance"]

    return balance


def ensure_status_code(response: requests.Response) -> None:
    """Raises an error if the status code is not 200."""
    if response.status_code != 200:
        raise RuntimeError(f"Received non-ok response: {response.content}")


def ensure_transaction_success(client: ExonumClient, tx_hash: str) -> None:
    """Checks that the transaction is committed and the status is success."""
    tx_info_response = client.get_tx_info(tx_hash)
    ensure_status_code(tx_info_response)

    tx_info = tx_info_response.json()
    if not (tx_info["type"] == "committed" and tx_info["status"]["type"] == "success"):
        raise RuntimeError(f"Error occured during transaction execution: {tx_info}")


class Seed:
    """Class that creates a new seed for each call."""

    seed = 1

    @classmethod
    def get_seed(cls) -> int:
        """Returns a new seed."""
        old_seed = cls.seed
        cls.seed += 1
        return old_seed


if __name__ == "__main__":
    run()
