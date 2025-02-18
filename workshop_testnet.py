import algokit_utils as au
import algokit_utils.transactions.transaction_composer as att
import algosdk
import os

if not (os.path.exists("client.py")):
    os.system("algokit compile py --out-dir ./app app.py")
    os.system("algokit generate client app/DigitalMarketplace.arc32.json --output client.py")
import client as cl
# This is for example only.
# The following is unsafe to do in codespace and should be done on local machine.


def ai(address):
    return (address)


if __name__ == "__main__":
    print("deploy_testnet")

    algorand = au.AlgorandClient.testnet()
    algod_client = algorand.client.algod
    indexer_client = algorand.client.indexer
    print(algod_client.block_info(0))
    print(indexer_client.health())

    if not (os.path.exists(".env")):
        private_key, address = algosdk.account.generate_account()
        with open(".env", "w") as file:
            file.write(algosdk.mnemonic.from_private_key(private_key))

    with open(".env", "r") as file:
        mnemonic = file.read()

    alice = algorand.account.from_mnemonic(mnemonic=mnemonic)

    factory = algorand.client.get_typed_app_factory(
        cl.DigitalMarketplaceFactory, default_sender=alice.address
    )
    # We need to fund the account here.
    # algokit explore
    # Switch network to testnet
    # Install a wallet (like lute)
    # Connect your account by entering the mnemonic in your .env
    # go to to get some free Test net Algo (Only need one)
    # https://lora.algokit.io/testnet/fund

    if len(ai(alice.address)["created-assets"]) == 0:
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
    else:
        asset_id = ai(alice.address)["created-assets"][0]["index"]
    print("Asset ID:", asset_id)

    price = au.AlgoAmount(micro_algo=100_000)
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

        result = ac.send.opt_in_to_asset(
            cl.OptInToAssetArgs(
                mbr_pay=att.TransactionWithSigner(mbr_pay_txn, alice.signer)
            ),
            au.CommonAppCallParams(
                asset_references=[asset_id]
            )
        )

        print(f"Transaction confirmed {result.confirmation['confirmed-round']}")

        print(
            f"App can now Hold ASA-ID= {
                ai(ac.app_address)['assets']
            }"
        )

    if ai(ac.app_address)["assets"][0]["amount"] == 0:
        print("Alice send ASAs to the App")
        result = algorand.send.asset_transfer(
            au.AssetTransferParams(
                sender=alice.address,
                signer=alice.signer,
                amount=10,
                receiver=ac.app_address,
                asset_id=asset_id
            )
        )
        print(f"Transaction confirmed {result.confirmation['confirmed-round']}")
        print(f"Hold ASA-ID= {ai(ac.app_address)['assets']}")

    ac.send.delete.delete_application(
        au.CommonAppCallParams(
            asset_references=[asset_id],
            extra_fee=au.AlgoAmount(micro_algo=3*sp.min_fee)
        )
    )
