# Introduction

## Abstract

A small project demonstrating the capabilities of blockchain technology.

## Prerequisites

Create a new fork of this project on you Github repository.

## Start the Development Environment

1. Click on the button <button style="background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;"><> Code <span data-component="trailingVisual" class="prc-Button-Visual-2epfX prc-Button-VisualWrap-Db-eB"><svg aria-hidden="true" focusable="false" class="octicon octicon-triangle-down" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" style="display: inline-block; user-select: none; vertical-align: text-bottom; overflow: visible;"><path d="m4.427 7.427 3.396 3.396a.25.25 0 0 0 .354 0l3.396-3.396A.25.25 0 0 0 11.396 7H4.604a.25.25 0 0 0-.177.427Z"></path></svg></span></button>
2. Click on the Codespaces Tab
3. Click on <button style="background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Create codespace on main</button>
4. Wait for everything to be installed properly before going to the next part.

>Following commands will be executed behind the scene:

```shell
pipx install algokit
git clone https://github.com/algorandfoundation/algokit-utils-py.git
cd algokit-utils-py
pip install .
cd ..
```

### Verify installation

1. `$ algokit doctor`
2. `$ gh codespace ports`

> Everything should be installed properly except `poetry`. Port 4001, 4002, 5443, 8980 should be public.

## Algokit

### Whats is Algokit

AlgoKit compromises of a number of components that make it the one-stop shop tool for developers building on the Algorand network.

### Explore the blockchain

Use the command `algokit explore`
It will open a new page with the Algorand Explorer "lora".
Anything you do on your local environment will be displayed here.

> You can also see in real time what's going on the blockchain by switching to MainNet.

## Workshop

### Create a standalone file

`$  touch workshop.py`

### Environment configuration

We will stay in localnet for this introduction.

```python
def client_configuration():
    config = get_default_localnet_config("algod")
    client = get_algod_client(config)
    return client
```




### Account Creation

```python
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
```

### Import from the utils files

```python
from utils import client_configuration, account_creation
```

### Usage

We usually use Alice, Bob and Charlie as users to illustrate blockchain documentation.

```python
    client = client_configuration()
    
    alice = account_creation(client, "ALICE", funds=100_000_000)
    bob = account_creation(client, "BOB")
    charly = account_creation(client, "CHARLY")
```

## Resources

[Install AlgoKit](https://github.com/algorandfoundation/algokit-cli/blob/main/README.md#install)

[Quick Start Tutorial](https://github.com/algorandfoundation/algokit-cli/blob/main/docs/tutorials/intro.md)

[Documentation](https://github.com/algorandfoundation/algokit-cli/blob/main/docs/algokit.md)

[Algokit Utils](https://algorandfoundation.github.io/algokit-utils-py/html/index.html)

[Algorand Sdk](https://py-algorand-sdk.readthedocs.io/en/latest/)

[Transactions](https://developer.algorand.org/docs/get-details/transactions/transactions/)