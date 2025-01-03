from algokit_utils import (
    Account,
    TransactionParameters,
    TransferParameters,
    transfer,
)
from utils import client_configuration, account_creation
import algosdk

if __name__ == "__main__":
    client = client_configuration()
    alice = account_creation(client, "ALICE", funds=100_000_000)
    bob = account_creation(client, "BOB")
    charly = account_creation(client, "CHARLY")

    if len(client.account_info(alice.address)["created-assets"]) == 0:
        create_asa =  algosdk.transaction.AssetCreateTxn(
        sender=alice.address,
        sp=client.suggested_params(),
        total=15,
        decimal=0,
        default_frozen=False,
        manager=alice.address,
        reserve=None,
        freeze=None,
        clawback=None,
        unit_name="PY-CL-FD", # 8 Max
        asset_name="Proof of Attendance Py-Clermont",
        url="https://pyclermont.org/",
        metadata_hash=None,
        note="Hello Clermont",
        lease=None,
        rekey_to=None,
        )
        create_asa_signed = create_asa.sign(alice.private_key)
        client.send_transaction(create_asa_signed)
        
