import algokit_utils
import algosdk, base64
import os

if not(os.path.exists("client.py")):
    os.system("algokit compile py --out-dir ./app app.py")
    os.system("algokit generate client app/DigitalMarketplace.arc32.json --output client.py")
from client import DigitalMarketplaceClient
## This is for example only.
## The following is unsafe to do in codespace and should be done on local machine.

if __name__ == "__main__":
    print("deploy_testnet") 
    config_client = algokit_utils.get_algonode_config(network="testnet", token="",config="algod")
    algod_client = algokit_utils.get_algod_client(config=config_client)

    config_indexer = algokit_utils.get_algonode_config(network="testnet", token="",config="indexer")
    indexer_client = algokit_utils.get_indexer_client(config=config_indexer)
    print(algod_client.block_info(0))
    print(indexer_client.health())


    if not(os.path.exists(".env")):
        private_key, address = algosdk.account.generate_account()
        with open(".env", "w") as file:
            file.write(algosdk.mnemonic.from_private_key(private_key))

    with open(".env", "r") as file:
        mnemonic = file.read()

    alice = algokit_utils.models.Account(private_key=algosdk.mnemonic.to_private_key(mnemonic))

    app_client = DigitalMarketplaceClient(
        algod_client,
        creator=alice,
        indexer_client=indexer_client
    )
    
    
    ## We need to fund the account here.
    ## algokit explore
    ## Switch network to testnet
    ## Install a wallet (like lute)
    ## Connect your account by entering the mnemonic in your .env
    ## go to to get some free Test net Algo (Only need one)
    ## https://lora.algokit.io/testnet/fund
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
        print("Transaction confirmed {result.confirmed_round}")
        asset_id = res["asset-index"]
    else:
        asset_id = algod_client.account_info(alice.address)["created-assets"][0]["index"]
    print("Asset ID:", asset_id)

    price = 100_000
    if len(algod_client.account_info(alice.address)["created-apps"]) == 0:
        app_client.create_create_application(asset_id=asset_id, unitary_price=price)
        app_id = app_client.app_id
    else:
        app_id = algod_client.account_info(alice.address)["created-apps"][0]["id"]
        app_client.app_id = app_id


    if len(algod_client.account_info(app_client.app_address)["assets"]) == 0:
        sp = algod_client.suggested_params()
        sp.fee = 2 * sp.min_fee # extra_fee
        sp.flat_fee = True
        mbr_pay_txn = algosdk.transaction.PaymentTxn(
            sender=alice.address,
            sp=sp,
            receiver=app_client.app_address,
            amt=200_000, #0,1 account creation + 0,1 Hold ASA
        )

        result = app_client.opt_in_to_asset(
            mbr_pay=algosdk.atomic_transaction_composer.TransactionWithSigner(mbr_pay_txn, signer=alice.signer),
            transaction_parameters=algokit_utils.TransactionParameters(
                foreign_assets=[asset_id]
            )
        )
        
        print(f"Transaction confirmed {result.confirmed_round}")

    if algod_client.account_info(app_client.app_address)["assets"][0]["amount"] == 0:
        print("Alice send ASAs to the App")
        result = algod_client.send_transaction(algosdk.transaction.AssetTransferTxn(
            sender=alice.address,
            sp=algod_client.suggested_params(),
            amt=10,
            receiver=app_client.app_address,
            index=asset_id
        ).sign(alice.private_key))
        print("Transaction confirmed {result.confirmed_round}")
        print(f"Hold ASA-ID= {algod_client.account_info(app_client.app_address)['assets']}")

    sp = algod_client.suggested_params()
    sp.fee = 3*sp.min_fee 
    sp.flat_fee = True
    # Delete the smart contract application
    app_client.delete_delete_application(
        transaction_parameters=algokit_utils.TransactionParameters(
            # Tell the AVM that the transaction involves this asset
            foreign_assets=[asset_id],
            suggested_params=sp,
        )
    )
    
