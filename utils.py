from typing import List
from algokit_utils import (
    get_algod_client,
    get_default_localnet_config,
    get_account,
    get_indexer_client
)
from algosdk.v2client.algod import AlgodClient


def client_configuration():
    config = get_default_localnet_config("algod")
    client = get_algod_client(config)
    return client

def indexer_configuration():
    config = get_default_localnet_config("indexer")
    client = get_indexer_client(config)
    return client


def account_creation(client: AlgodClient, name: str, funds=0):
    account = get_account(client, name) if funds == 0 else get_account(
        client, name, fund_with_algos=funds)
    info = client.account_info(account.address)

    print(f'Name\t\t: %s \n'
          f'Address\t\t: %s\n'
          f'Created Asset\t: %s\n'
          f'Assets\t\t: %s\n'
          f'Algo\t\t: %.6f' %
          (name, account.address, info["created-assets"], info["assets"], info["amount"] / 1_000_000))
    if len(info["created-apps"]) > 0:
        print(f'Created-Apps\t: %s \n' % info["created-apps"][0]["id"])
    print("")
    return account


def get_asa_id(ptx):
    if isinstance(ptx, dict) and "asset-index" in ptx and isinstance(ptx["asset-index"], int):
        return ptx["asset-index"]
    else:
        raise ValueError("Unexpected response from pending_transaction_info")


def display_info(client: AlgodClient, names: List[str]):
    for name in names:
        account_creation(client, name)
