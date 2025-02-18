import os
import algokit_utils as au
import algokit_utils.transactions.transaction_composer as att

from utils import (
    account_creation,
    display_info,
)


def ai(address):
    return algod_client.account_info(address)


if __name__ == "__main__":
    algorand = au.AlgorandClient.from_environment()
    algod_client = algorand.client.algod
    indexer_client = algorand.client.indexer

    print(algod_client.block_info(0))
    print(indexer_client.health())

    alice = account_creation(algorand, "ALICE", au.AlgoAmount(algo=10000))
    bob = account_creation(algorand, "BOB", au.AlgoAmount(algo=100))
    charly = account_creation(algorand, "CHARLY", au.AlgoAmount(algo=100))

    print("Alice Create a Token")

    if len(ai(alice.address)["created-assets"]) == 0:
        result = algorand.send.asset_create(
            au.AssetCreateParams(
                sender=alice.address,
                signer=alice.signer,
                total=15,
                decimals=0,
                default_frozen=False,
                unit_name="PY-CL-FD",  # 8 Max
                asset_name="Proof of auendance Py-Clermont",
                url="https://pyclermont.org/",
                note="Hello Clermont",
            )
        )
        asset_id = result.confirmation["asset-index"]
    else:
        asset_id = ai(alice.address)["created-assets"][0]["index"]
    print("Asset ID:", asset_id)

    print("BOB Buy 1 Token at 10 Algo from Alice\n")
    if len(ai(bob.address)["assets"]) == 0:
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

    # if len(ai(alice.address)["created-apps"]) == 0:
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
    #     app_id = ai(alice.address)["created-apps"][0]["id"]

    # generate the client 
    # `algokit generate client app/DigitalMarketplace.arc32.json --output client.py`

    os.system("algokit generate client app/DigitalMarketplace.arc32.json --output client.py")
    import client as cl

    factory = algorand.client.get_typed_app_factory(
        cl.DigitalMarketplaceFactory, default_sender=alice.address
    )

    if len(ai(alice.address)["created-apps"]) == 0:
        result, _ = factory.send.create.create_application(
            cl.CreateApplicationArgs(
                asset_id=asset_id, unitary_price=price.micro_algo
            )
        )
        app_id = result.app_id
    else:
        app_id = ai(alice.address)["created-apps"][0]["id"]

    ac = factory.get_app_client_by_id(app_id, default_sender=alice.address)

    display_info(algorand, ["ALICE"])
    print(f"App {app_id} deployed with address {ac.app_address}")

    sp = algorand.get_suggested_params()

    if len(ai(ac.app_address)["assets"]) == 0:
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
                ai(ac.app_address)['assets']
            }"
        )
    if ai(ac.app_address)["assets"][0]["amount"] == 0:
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
        print(f"Hold ASA-ID= {ai(ac.app_address)['assets']}")

    if len(ai(charly.address)["assets"]) == 0:
        amt_to_buy = 2

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
            asset_references=[asset_id],
            extra_fee=au.AlgoAmount(micro_algo=3*sp.min_fee)
        )
    )

    display_info(algorand, ["ALICE", "BOB", "CHARLY"])
