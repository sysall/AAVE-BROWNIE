from brownie import network, config, accounts

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONNEMENTS = ["mainnet-fork","mainnet-fork-dev"]

def get_account(index=None, id=None):
    if id:
        return accounts.load(id)
    
    if index:
        return accounts[index]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONNEMENTS:
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])