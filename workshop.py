from algokit_utils import (
    Account,
    TransactionParameters,
    TransferParameters,
    transfer,
)
from utils import client_configuration, account_creation


if __name__ == "__main__":
    client = client_configuration()
    alice = account_creation(client, "ALICE", funds=100_000_000)
    bob = account_creation(client, "BOB")
    charly = account_creation(client, "CHARLY")
