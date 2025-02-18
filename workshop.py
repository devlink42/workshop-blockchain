import os
import algosdk
import algokit_utils as au
import algokit_utils.transactions.transaction_composer as att

from utils import (
    account_creation,
    display_info,
)


if __name__ == "__main__":
    algorand = au.AlgorandClient.from_environment()

    algod_client = algorand.client.algod
    indexer_client = algorand.client.indexer

    print(algod_client.block_info(0))
    print(indexer_client.health())

    alice = account_creation(algorand, "ALICE", au.AlgoAmount(algo=10000))
    with open(".env", "w") as file:
        file.write(algosdk.mnemonic.from_private_key(alice.private_key))
    bob = account_creation(algorand, "BOB", au.AlgoAmount(algo=100))
    charly = account_creation(algorand, "CHARLY", au.AlgoAmount(algo=100))

    print("Alice Create a Token")
    result = algorand.send.asset_create(
        au.AssetCreateParams(
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
        au.AssetOptInParams(
            sender=bob.address,
            signer=bob.signer,
            asset_id=asset_id
        )
    )
    composer.add_payment(
        au.PaymentParams(
            sender=bob.address,
            signer=bob.signer,
            receiver=alice.address,
            amount=au.AlgoAmount(algo=10),
        )
    )
    composer.add_asset_transfer(
        au.AssetTransferParams(
            sender=alice.address,
            signer=alice.signer,
            receiver=bob.address,
            amount=1,
            asset_id=asset_id,
        )
    )

    result = composer.send()

    price = au.AlgoAmount(algo=10)

    display_info(algorand, ["ALICE", "BOB"])

    print("Alice Create a smart contract")
    # compile the smart contract

    os.system("algokit compile py --out-dir ./app app.py")
    os.system(
        "algokit generate client app/DigitalMarketplace.arc32.json --output client.py"
    )
    import client as cl

    factory = algorand.client.get_typed_app_factory(
        cl.DigitalMarketplaceFactory, default_sender=alice.address
    )

    result, _ = factory.send.create.create_application(
        cl.CreateApplicationArgs(
            asset_id=asset_id, unitary_price=price.micro_algo
        )
    )
    app_id = result.app_id
    ac = factory.get_app_client_by_id(app_id, default_sender=alice.address)

    display_info(algorand, ["ALICE"])
    print(f"App {app_id} deployed with address {ac.app_address}")

    sp = algorand.get_suggested_params()

    mbr_pay_txn = algorand.create_transaction.payment(
        au.PaymentParams(
            sender=alice.address,
            receiver=ac.app_address,
            amount=au.AlgoAmount(algo=0.2),
            extra_fee=au.AlgoAmount(micro_algo=sp.min_fee)
        )
    )

    ac.send.opt_in_to_asset(
        cl.OptInToAssetArgs(
            mbr_pay=att.TransactionWithSigner(mbr_pay_txn, alice.signer)
        ),
        au.CommonAppCallParams(
            asset_references=[asset_id]
        )
    )

    print(
        f"App can now Hold ASA-ID= {
            algod_client.account_info(ac.app_address)['assets']
        }"
    )

    print("Alice send ASAs to the App")
    algorand.send.asset_transfer(
        au.AssetTransferParams(
            sender=alice.address,
            signer=alice.signer,
            amount=10,
            receiver=ac.app_address,
            asset_id=asset_id
        )
    )
    print(f"Hold ASA-ID= {algod_client.account_info(ac.app_address)['assets']}")

    amt_to_buy = 2
    print(f"Charly buy {amt_to_buy} token")
    composer = algorand.new_group()
    composer.add_asset_opt_in(
        au.AssetOptInParams(
            sender=charly.address,
            signer=charly.signer,
            asset_id=asset_id
        )
    )
    buyer_payment_txn = algorand.create_transaction.payment(
        au.PaymentParams(
            sender=charly.address,
            receiver=ac.app_address,
            amount=au.AlgoAmount(
                micro_algo=amt_to_buy*ac.state.global_state.unitary_price
            ),
            extra_fee=au.AlgoAmount(micro_algo=sp.min_fee)
        )
    )
    atc = au.AtomicTransactionComposer()
    composer.add_app_call_method_call(
        ac.params.buy(
            cl.BuyArgs(
                buyer_txn=att.TransactionWithSigner(
                    txn=buyer_payment_txn,
                    signer=charly.signer
                ),
                quantity=2
            ),
            au.CommonAppCallParams(
                sender=charly.address,
                signer=charly.signer,
                # Inform the AVM that the transaction uses this asset
                asset_references=[asset_id],
            )
        )
    )
    composer.send()

    display_info(algorand, ["CHARLY"])

    print("Alice delete the app and get ASA and Algo back")
    # Delete the smart contract

    ac.send.delete.delete_application(
        au.CommonAppCallParams(
            # Tell the AVM that the transaction involves this asset
            asset_references=[asset_id],
            extra_fee=au.AlgoAmount(micro_algo=3*sp.min_fee)
        )
    )

    display_info(algorand, ["ALICE", "BOB", "CHARLY"])
