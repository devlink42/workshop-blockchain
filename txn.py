import algokit_utils as au
import algosdk as sdk
from utils import (
    account_creation,
    display_info,
)

if __name__ == "__main__":
    algorand = au.AlgorandClient.from_environment()

    print(algorand.client.algod.block_info(0))
    print(algorand.client.indexer.health())

    alice = account_creation(algorand, "ALICE", au.AlgoAmount(algo=10_000))
    bob = account_creation(algorand, "BOB", au.AlgoAmount(algo=100))

    # print(sdk.mnemonic.from_private_key(alice.private_key))

    pay_txn = algorand.create_transaction.payment(
        au.PaymentParams(
            sender=alice.address,
            receiver=bob.address,
            amount=au.AlgoAmount(algo=1)
        )
    )
    pay_txn_signed = pay_txn.sign(alice.private_key)

    tx_id = algorand.client.algod.send_transaction(pay_txn_signed)

    res = sdk.transaction.wait_for_confirmation(
        algod_client=algorand.client.algod,
        txid=tx_id
        )
    print('Transaction confirmed'
          f'{res}')

    # display_info(algorand, ["ALICE", "BOB"])

    payback_txn = algorand.send.payment(
        au.PaymentParams(
            sender=bob.address,
            signer=bob.signer,
            receiver=alice.address,
            amount=au.AlgoAmount(algo=1)
        )
    )

    print('Transaction confirmed, round: '
          f'{payback_txn.confirmation["confirmed-round"]}')
