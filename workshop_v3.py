import os
import algosdk
from algokit_utils import AlgorandClient, AlgoAmount, TransactionParameters
import algokit_utils.transactions.transaction_composer as att

from utils_v3 import (
    account_creation,
    display_info,
)


if __name__ == "__main__":
    algorand = AlgorandClient.from_environment()

    algod_client = algorand.client.algod
    indexer_client = algorand.client.indexer

    print(algod_client.block_info(0))
    print(indexer_client.health())

    if not (os.path.exists(".env")):
        alice = account_creation(algorand, "ALICE", AlgoAmount(algo=10000))
        with open(".env", "w") as file:
            file.write(algosdk.mnemonic.from_private_key(alice.private_key))
    with open(".env", "r") as file:
        mnemonic = file.read()
    alice = algorand.account.from_mnemonic(mnemonic=mnemonic)
    bob = account_creation(algorand, "BOB", AlgoAmount(algo=100))
    charly = account_creation(algorand, "CHARLY", AlgoAmount(algo=100))

    print("Alice Create a Token")
    result = algorand.send.asset_create(
        att.AssetCreateParams(
            sender=alice.address,
            signer=alice.signer,
            total=15,
            decimals=0,
            default_frozen=False,
            unit_name="PY-CL-FD",  # 8 Max
            asset_name="Proof of Attendance Py-Clermont",
            url="https://pyclermont.org/",
            note="Hello Clermont",
        )
    )
    asset_id = result.confirmation["asset-index"]

    print("BOB Buy 1 Token at 10 Algo from Alice\n")

    composer = algorand.new_group()

    composer.add_asset_opt_in(
        att.AssetOptInParams(
            sender=bob.address,
            signer=bob.signer,
            asset_id=asset_id
        )
    )
    composer.add_payment(
        att.PaymentParams(
            sender=bob.address,
            signer=bob.signer,
            receiver=alice.address,
            amount=AlgoAmount(algo=10),
        )
    )
    composer.add_asset_transfer(
        att.AssetTransferParams(
            sender=alice.address,
            signer=alice.signer,
            receiver=bob.address,
            amount=1,
            asset_id=asset_id,
        )
    )

    result = composer.send()

    price = AlgoAmount(algo=10)

    display_info(algorand, ["ALICE", "BOB"])

    print("Alice Create a smart contract")
    # compile the smart contract

    os.system("algokit compile py --out-dir ./app app.py")
    os.system(
        "algokit generate client app/DigitalMarketplace.arc32.json --output client.py"
    )
    with open("app/DigitalMarketplace.arc32.json", "r") as file:
        arc32_json = file.read()  # Read file content as string
    from client import DigitalMarketplaceClient, Composer
    # from algokit_utils.applications import AppClient, Arc32Contract
    app_client = DigitalMarketplaceClient(
        algod_client, signer=alice, indexer_client=indexer_client
    )
    
    app_client.create_create_application(
        asset_id=asset_id, unitary_price=price.micro_algo
    )
    app_id = app_client.app_id

    # app_client = AppClient.from_network(
    #     app_spec=Arc32Contract.from_json(arc32_json),
    #     algorand=algorand
    #     )

    # app_client = algorand.client.get_app_factory(
    #     app_spec=Arc32Contract.from_json(arc32_json),
    #     default_sender=alice.address,
    #     default_signer=alice.signer
    # ).deploy(

    # )
    # app_client = AppClient.from_network(
    #     app_spec=Arc32Contract.from_json(arc32_json),
    #     algorand=algorand,

    # )

    display_info(algorand, ["ALICE"])
    print(f"App {app_id} deployed with address {app_client.app_address}")


    sp = algorand.get_suggested_params()
    sp.flat_fee = True

    mbr_pay_txn = algorand.create_transaction.payment(
        att.PaymentParams(
            sender=alice.address,
            receiver=app_client.app_address,
            amount=AlgoAmount(algo=0.2),
            extra_fee=AlgoAmount(micro_algo=sp.min_fee)
        )
    )
    
    app_client.opt_in_to_asset(
        mbr_pay=att.TransactionWithSigner(mbr_pay_txn, alice.signer),
        transaction_parameters=TransactionParameters(
            # The asset ID must be declared for the Algorand Virtual Machine (AVM) to use it
            foreign_assets=[asset_id]
        )
    )

    print(
        f"App can now Hold ASA-ID= {
            algod_client.account_info(app_client.app_address)['assets']
        }"
    )

    print("Alice send ASAs to the App")
    algorand.send.asset_transfer(
        att.AssetTransferParams(
            sender=alice.address,
            signer=alice.signer,
            amount=10,
            receiver=app_client.app_address,
            asset_id=asset_id
        )
    )
    print(f"Hold ASA-ID= {algod_client.account_info(app_client.app_address)['assets']}")

    amt_to_buy = 2
    print(f"Charly buy {amt_to_buy} token")

    # composer = app_client.new_group()

    # composer.add_asset_opt_in(
    #     att.AssetOptInParams(
    #         sender=charly.address,
    #         signer=charly.signer,
    #         asset_id=asset_id
    #     )
    # )
    asset_opt_in = algorand.create_transaction.asset_opt_in(
        att.AssetOptInParams(
            sender=charly.address,
            asset_id=asset_id
        )
    )
    asset_opt_in_tws = att.TransactionWithSigner(
        txn=asset_opt_in,
        signer=charly.signer
    )
    buyer_payment_txn = algorand.create_transaction.payment(
        att.PaymentParams(
            sender=charly.address,
            receiver=app_client.app_address,
            amount=AlgoAmount(
                micro_algo=amt_to_buy*app_client.get_global_state().unitary_price
            ),
            extra_fee=AlgoAmount(micro_algo=sp.min_fee)
        )
    )

    atc = att.AtomicTransactionComposer()
    atc.add_transaction(asset_opt_in_tws)
    app_client_composer = Composer(
        app_client=app_client.app_client, atc=atc
    )
    buy_txn = app_client_composer.buy(
        buyer_txn=att.TransactionWithSigner(
            txn=buyer_payment_txn,
            signer=charly.signer
        ),
        quantity=2,
        transaction_parameters=TransactionParameters(
            sender=charly.address,
            signer=charly.signer,
            # Inform the AVM that the transaction uses this asset
            foreign_assets=[asset_id],
        ),
    ).build()

    buy_txn.execute(algod_client, wait_rounds=4)

    display_info(algorand, ["CHARLY"])

    print("Alice delete the app and get ASA and Algo back")

    algorand.send.app_call_method_call
    # Delete the smart contract 
    sp.fee = 3*sp.min_fee 
    sp.flat_fee = True
    app_client.delete_delete_application(
        transaction_parameters=TransactionParameters(
            # Tell the AVM that the transaction involves this asset
            foreign_assets=[asset_id],
            suggested_params=sp,
        )
    )

    display_info(algorand, ["ALICE", "BOB", "CHARLY"])
