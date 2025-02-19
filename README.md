# TP 1

Pour commencer, il faut tout créer un fichier python.

```console
touch txn.py
```

## Import

```python
import algokit_utils as au
import algosdk as sdk
from utils import (
    account_creation,
    display_info,
)
```

## Choisir son réseau

[Algorand Client](https://algorandfoundation.github.io/algokit-utils-py/autoapi/algokit_utils/algorand/index.html#algokit_utils.algorand.AlgorandClient)
> Pour localnet `algorand = au.AlgorandClient.from_environment()`

### Verifier que le réseau est correctement initialisé

```python
    print(algorand.client.algod.block_info(0))
    print(algorand.client.indexer.health())
```

## Création des comptes

```python
    alice = account_creation(algorand, "ALICE", au.AlgoAmount(algo=10_000))
    bob = account_creation(algorand, "BOB", au.AlgoAmount(algo=100))
```

> Plus de details sur [Documentation algokit utils](https://algorandfoundation.github.io/algokit-utils-py/).

You can display the mnemonic associated with an account like this:
`sdk.mnemonic.from_private_key(alice.private_key)`

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
