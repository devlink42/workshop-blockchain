import os
from utils import client_configuration, indexer_configuration, account_creation, display_info
import algokit_utils
import algosdk, base64
from Cryptodome.Hash import SHA512

if __name__ == "__main__":
    algod_client = client_configuration()
    indexer_client = indexer_configuration()

    print(algod_client.block_info(0))
    print(indexer_client.health())

    alice = account_creation(algod_client, "ALICE", funds=100_000_000)
    bob = account_creation(algod_client, "BOB")
    charly = account_creation(algod_client, "CHARLY")

    print("Alice Create a Token")
    
    if len(algod_client.account_info(alice.address)["created-assets"]) == 0:
        create_asa =  algosdk.transaction.AssetCreateTxn(
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
        create_asa_signed = create_asa.sign(alice.private_key)
        create_asa_tx_id = algod_client.send_transaction(create_asa_signed)
        res = algosdk.transaction.wait_for_confirmation(algod_client, create_asa_tx_id, 4)
        asset_id = res["asset-index"]
    else:
        asset_id = algod_client.account_info(alice.address)["created-assets"][0]["index"]
    print("Asset ID:", asset_id)

    print("BOB Buy 1 Token at 10 Algo from Alice\n")
    if len(algod_client.account_info(bob.address)["assets"]) == 0:
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

    # if len(algod_client.account_info(alice.address)["created-apps"]) == 0:
    #     with open("app/DigitalMarketplace.approval.teal", "r") as f:
    #         approval_program = f.read()
    #     with open("app/DigitalMarketplace.clear.teal", "r") as f:
    #         clear_program = f.read()

    #     approval_result = algod_client.compile(approval_program)
    #     approval_binary = base64.b64decode(approval_result["result"])

    #     clear_result = algod_client.compile(clear_program)
    #     clear_binary = base64.b64decode(clear_result["result"])
    #     # Native conversion
    #     asset_id_bytes = asset_id.to_bytes(4, 'big')  # Convert asset_id to 4 bytes in big-endian order
    #     single_zero_byte = b'\x00'  # Single zero byte
    #     price_bytes = price.to_bytes(8, 'big', signed=False)  # Convert price to 8 bytes, big-endian (int representation)

    #     # Combine into desired list
    #     result = [asset_id_bytes, single_zero_byte, price_bytes]
    #     local_ints = 0
    #     local_bytes = 0
    #     global_ints = 2 # number of integer values
    #     global_bytes = 0 #number of byte slices values
    #     global_schema = algosdk.transaction.StateSchema(global_ints, global_bytes)
    #     local_schema = algosdk.transaction.StateSchema(local_ints, local_bytes)
        
    #     # Method signature
    #     hash = SHA512.new(truncate="256")
    #     hash.update("create_application(asset,uint64)void".encode("utf-8"))
    #     selector = hash.digest()[:4]

    #     algokit_utils.TransactionParameters()
    #     app_create_txn = algosdk.transaction.ApplicationCreateTxn(
    #         alice.address,
    #         sp=algod_client.suggested_params(),
    #         on_complete=algosdk.transaction.OnComplete.NoOpOC,
    #         approval_program=approval_binary,
    #         clear_program=clear_binary,
    #         global_schema=global_schema,
    #         local_schema=local_schema,
    #         app_args=[selector, (0).to_bytes(1, 'big'), (price).to_bytes(8, 'big')],
    #         foreign_assets=[asset_id]
    #     )
    #     signed_create_txn = app_create_txn.sign(alice.private_key)
    #     txid = algod_client.send_transaction(signed_create_txn)
    #     result = algosdk.transaction.wait_for_confirmation(algod_client, txid, 4)
    #     app_id = result["application-index"]
    # else:
    #     app_id = algod_client.account_info(alice.address)["created-apps"][0]["id"]


    # generate the client 
    # `algokit generate client app/DigitalMarketplace.arc32.json --output client.py`

    os.system("algokit generate client app/DigitalMarketplace.arc32.json --output client.py")
    
    from client import DigitalMarketplaceClient,Composer
    app_client = DigitalMarketplaceClient(
        algod_client,
        creator=alice,
        indexer_client=indexer_client
    )
    if len(algod_client.account_info(alice.address)["created-apps"]) == 0:

        app_client.create_create_application(asset_id=asset_id, unitary_price=price)
        app_id = app_client.app_id
    else:
        app_id = algod_client.account_info(alice.address)["created-apps"][0]["id"]
        app_client.app_id = app_id
    
    
    display_info(algod_client, ["ALICE"])
    print(f"App {app_id} deployed with address {app_client.app_address}")

    if len(algod_client.account_info(app_client.app_address)["assets"]) == 0:
        sp = algod_client.suggested_params()
        sp.fee = sp.min_fee # extra_fee
        mbr_pay_txn = algosdk.transaction.PaymentTxn(
            sender=alice.address,
            sp=sp,
            receiver=app_client.app_address,
            amt=200_000, #0,1 account creation + 0,1 Hold ASA
        )

        result = app_client.opt_in_to_asset(
            mbr_pay=algosdk.atomic_transaction_composer.TransactionWithSigner(mbr_pay_txn, signer=alice.signer),
            transaction_parameters=algokit_utils.TransactionParameters(
                # The asset ID must be declared for the Algorand Virtual Machine (AVM) to use it
                foreign_assets=[asset_id]
            )
        )
        
        print("Transaction confirmed {result.confirmed_round}")

        print(f"App can now Hold ASA-ID= {algod_client.account_info(app_client.app_address)['assets']}")
    if algod_client.account_info(app_client.app_address)["assets"][0]["amount"] == 0:
        print("Alice send ASAs to the App")
        algod_client.send_transaction(algosdk.transaction.AssetTransferTxn(
            sender=alice.address,
            sp=algod_client.suggested_params(),
            amt=10,
            receiver=app_client.app_address,
            index=asset_id
        ).sign(alice.private_key))
        print(f"Hold ASA-ID= {algod_client.account_info(app_client.app_address)['assets']}")

    

    if len(algod_client.account_info(charly.address)["assets"]) == 0:
        sp = algod_client.suggested_params()
        sp.fee = sp.min_fee # extra_fee
        amount_to_buy = 2

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

        buy_txn.execute(algod_client, 4)

    display_info(algod_client, ["CHARLY"])

    sp = algod_client.suggested_params()
    sp.fee = 3*sp.min_fee 

    # Delete the smart contract application
    result = app_client.delete_delete_application(
        transaction_parameters=algokit_utils.TransactionParameters(
            # Tell the AVM that the transaction involves this asset
            foreign_assets=[asset_id],
            suggested_params=sp,
        )
    )
    
    display_info(algod_client, ["ALICE","BOB","CHARLY"])