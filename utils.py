from algokit_utils import (
    get_algod_client,
    get_default_localnet_config,
    get_account,
)
from algosdk.v2client.algod import AlgodClient


def client_configuration():
    config = get_default_localnet_config("algod")
    client = get_algod_client(config)
    return client


def account_creation(client: AlgodClient, name: str, funds=0):
    account = get_account(client, name) if funds == 0 else get_account(client, name, fund_with_algos=funds)
    info = client.account_info(account.address)
    print(f'Name\t\t: %s \n'
      f'Address\t\t: %s\n'
      f'Created Asset\t: %s\n'
      f'Assets\t\t: %s\n'
      f'Algo\t\t: %.6f \n' % 
      (name, account.address, info["created-assets"], info["assets"], info["amount"] / 1_000_000))    
    return account
