import os
import algosdk
import algokit_utils
from utils import client_configuration, indexer_configuration, account_creation, display_info

if __name__ == "__main__":
    algod_client = client_configuration()
    indexer_client = indexer_configuration()
    print(algod_client.block_info(0))
    print(indexer_client.health())

    alice = account_creation(algod_client, "ALICE", funds=100_000_000)
    bob = account_creation(algod_client, "BOB")
    charly = account_creation(algod_client, "CHARLY")
    
    print("Alice Create a Token")

    create_asa_txn =  algosdk.transaction.AssetCreateTxn(
    sender=alice.address,
    sp=algod_client.suggested_params(),
    total=15,
    decimals=0,
    default_frozen=False,
    unit_name="PY-CL-FD", # 8 Max
    asset_name="Proof of Attendance Py-Clermont",
    url="https://pyclermont.org/",
    note="Hello Clermont",
    )
    create_asa_signed = create_asa_txn.sign(alice.private_key)
    create_asa_tx_id = algod_client.send_transaction(create_asa_signed)
    res = algosdk.transaction.wait_for_confirmation(algod_client, create_asa_tx_id, 4)
    asset_id = res["asset-index"]

    print("BOB Buy 1 Token at 10 Algo from Alice\n")
    atc = algosdk.atomic_transaction_composer.AtomicTransactionComposer()

    opt_in_asa = algosdk.transaction.AssetOptInTxn(
        sender=bob.address,
        sp=algod_client.suggested_params(),
        index= asset_id
    )

    pay_alice = algosdk.transaction.PaymentTxn(
        sender=bob.address,
        sp=algod_client.suggested_params(),
        receiver=alice.address,
        amt=10_000_000, # Micro Algo
    )

    send_asa = algosdk.transaction.AssetTransferTxn(
        sender=alice.address,
        sp=algod_client.suggested_params(),
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

    atc.execute(algod_client, 4)

    price = 10_000_000

    display_info(algod_client, ["ALICE", "BOB"])

    print("Alice Create a smart contract")
    # compile the smart contract

    os.system("algokit compile py --out-dir ./app app.py")
    os.system("algokit generate client app/DigitalMarketplace.arc32.json --output client.py")

    from client import DigitalMarketplaceClient,Composer
    app_client = DigitalMarketplaceClient(
        algod_client,
        creator=alice,
        indexer_client=indexer_client
    )

    app_client.create_create_application(asset_id=asset_id, unitary_price=price)
    app_id = app_client.app_id
    
    display_info(algod_client, ["ALICE"])
    print(f"App {app_id} deployed with address {app_client.app_address}")

    sp = algod_client.suggested_params()
    sp.fee = sp.min_fee # extra_fee
    mbr_pay_txn = algosdk.transaction.PaymentTxn(
        sender=alice.address,
        sp=sp,
        receiver=app_client.app_address,
        amt=200_000, #0,1 account creation + 0,1 Hold ASA
    )

    app_client.opt_in_to_asset(
        mbr_pay=algosdk.atomic_transaction_composer.TransactionWithSigner(mbr_pay_txn, signer=alice.signer),
        transaction_parameters=algokit_utils.TransactionParameters(
            # The asset ID must be declared for the Algorand Virtual Machine (AVM) to use it
            foreign_assets=[asset_id]
        )
    )
    

    print(f"App can now Hold ASA-ID= {algod_client.account_info(app_client.app_address)['assets']}")

    print("Alice send ASAs to the App")
    algod_client.send_transaction(algosdk.transaction.AssetTransferTxn(
        sender=alice.address,
        sp=algod_client.suggested_params(),
        amt=10,
        receiver=app_client.app_address,
        index=asset_id
    ).sign(alice.private_key))
    print(f"Hold ASA-ID= {algod_client.account_info(app_client.app_address)['assets']}")

    amount_to_buy = 2
    print("Charly buy {amount_to_buy} token")
    sp = algod_client.suggested_params()
    sp.fee = sp.min_fee # extra_fee

    opt_in_asa = algosdk.transaction.AssetOptInTxn(
        sender=charly.address,
        sp=algod_client.suggested_params(),
        index= asset_id
    )
    opt_in_tws = algosdk.atomic_transaction_composer.TransactionWithSigner(opt_in_asa, charly.signer)

    buyer_payment_txn = algosdk.transaction.PaymentTxn(
        sender=charly.address,
        sp=sp,
        receiver=app_client.app_address,
        amt=amount_to_buy * app_client.get_global_state().unitary_price, # Micro Algo
    )

    atc = algosdk.atomic_transaction_composer.AtomicTransactionComposer()
    atc.add_transaction(opt_in_tws)
    
    app_client_composer = Composer(app_client=app_client.app_client, atc=atc)
    buy_txn = app_client_composer.buy(
        buyer_txn=algosdk.atomic_transaction_composer.TransactionWithSigner(
            txn=buyer_payment_txn, signer=charly.signer),
            quantity=2,
            transaction_parameters=algokit_utils.TransactionParameters(
            sender=charly.address,
            signer=charly.signer,
            # Inform the AVM that the transaction uses this asset
            foreign_assets=[asset_id],
        ),
    ).build()

    buy_txn.execute(algod_client, wait_rounds=4)

    display_info(algod_client, ["CHARLY"])

    print("Alice delete the app and get ASA and Algo back")

    sp = algod_client.suggested_params()
    sp.fee = 3*sp.min_fee 

    # Delete the smart contract application
    app_client.delete_delete_application(
        transaction_parameters=algokit_utils.TransactionParameters(
            # Tell the AVM that the transaction involves this asset
            foreign_assets=[asset_id],
            suggested_params=sp,
        )
    )
    
    display_info(algod_client, ["ALICE","BOB","CHARLY"])