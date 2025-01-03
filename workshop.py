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
        decimals=0,
        default_frozen=False,
        # manager=alice.address,
        # reserve=None,
        # freeze=None,
        # clawback=None,
        unit_name="PY-CL-FD", # 8 Max
        asset_name="Proof of Attendance Py-Clermont",
        url="https://pyclermont.org/",
        # metadata_hash=None,
        note="Hello Clermont",
        # lease=None,
        # rekey_to=None,
        )
        create_asa_signed = create_asa.sign(alice.private_key)
        create_asa_tx_id = client.send_transaction(create_asa_signed)
        res = algosdk.transaction.wait_for_confirmation(client, create_asa_tx_id, 4)
        asset_id = res["asset-index"]
    else:
        asset_id = client.account_info(alice.address)["created-assets"][0]["index"]
    print("Asset ID:", asset_id)

    atc = algosdk.atomic_transaction_composer.AtomicTransactionComposer()

    opt_in_asa = algosdk.transaction.AssetOptInTxn(
        sender=bob.address,
        sp=client.suggested_params(),
        index= asset_id
    )

    pay_alice = algosdk.transaction.PaymentTxn(
        sender=bob.address,
        sp=client.suggested_params(),
        receiver=alice.address,
        amt=10_000_000, # Micro Algo
    )

    send_asa = algosdk.transaction.AssetTransferTxn(
        sender=alice.address,
        sp=client.suggested_params(),
        amt=1,
        receiver=bob.address,
        index=asset_id
    )

    opt_in_tws = algosdk.atomic_transaction_composer.TransactionWithSigner(opt_in_asa, bob.signer)
    pay_alice_tws = algosdk.atomic_transaction_composer.TransactionWithSigner(pay_alice, bob.signer)
    send_asa_tws = algosdk.atomic_transaction_composer.TransactionWithSigner(send_asa, alice.signer)

    atc.add_transaction(opt_in_tws)
    atc.add_transaction(pay_alice_tws)
    atc.add_transaction(send_asa_tws)

    atc.execute(client, 4)
