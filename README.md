# TP 1

## Création des comptes

```python
import os
import algosdk
import algokit_utils
from utils import client_configuration, indexer_configuration, account_creation, display_info

if __name__ == "__main__":
    algod_client = client_configuration()

    print(algod_client.block_info(0))
    if not (os.path.exists(".env")):
        alice = account_creation(algod_client, "ALICE", funds=100_000_000)
        with open(".env", "w") as file:
            file.write(algosdk.mnemonic.from_private_key(alice.private_key))
    with open(".env", "r") as file:
        mnemonic = file.read()
    alice = algokit_utils.models.Account(private_key=algosdk.mnemonic.to_private_key(mnemonic))
    bob = account_creation(algod_client, "BOB")
```

> Plus de details sur [Documentation algokit utils](https://algorandfoundation.github.io/algokit-utils-py/).

## Création d'un payment d'alice vers Bob de 1 Algo

[PaymentTxn](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/transaction.html#algosdk.transaction.PaymentTxn)
`pay_txn = algosdk.transaction.PaymentTxn(..)`

## Signature de la transaction

[Transaction](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/transaction.html#algosdk.transaction.Transaction)
`pay_txn_signed = pay_txn.sign(..)`

## Envoi de la transaction

[Send](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/v2client/algod.html#algosdk.v2client.algod.AlgodClient.send_transactions)
`tx_id = algod_client.send_transaction(..)`

[Wait for Confirmation](https://py-algorand-sdk.readthedocs.io/en/latest/algosdk/transaction.html#algosdk.transaction.wait_for_confirmation)
`res = algosdk.transaction.wait_for_confirmation(..)`

## Afficher le résultat

`print(res)`

## Visualiser sur l'explorer

Ouvrir l'explorer depuis le terminal:
`algokit explore`
