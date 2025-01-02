from algokit_utils import (
    get_algod_client,
    get_default_localnet_config,
    get_account,
    Account,
    TransactionParameters,
    TransferParameters,
    transfer,
)

git 

def client_configuration():
    config = get_default_localnet_config("algod")
    client = get_algod_client(config)
    return client

def account_creation(client: AlgodClient, name: str, funds=0):
    account = get_account(client, name) if funds==0 else get_account(client, name, fund_with_algos=funds)
    info = client.account_info(account.address)
    print(f'Name\t\t: %s \nAddress\t\t: %s\nCreated Asset\t: %s\nAssets\t\t: %s\nAlgo\t\t: %.6f \n' % (name, account.address,info["created-assets"], info["assets"], info["amount"] / 1_000_000))
    return account

if __name__ == "__main__":
    client = client_configuration()
    alice = account_creation(client, "ALICE", funds=100_000_000)
    bob = account_creation(client, "BOB")
    charly = account_creation(client, "CHARLY")
