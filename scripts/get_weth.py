from scripts.helpful_scripts import get_account
from brownie import interface, config, network

def main():
    get_weth()

# Deposing ETH into the WETH contract will mint you WETH token
def get_weth():
    """
    MINT WETH BY DEPOSING ETH we will need the ABI and the address lets work with interface to get ABI & Address
    """

    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10**18})
    tx.wait(1)
    print("Depositing.... You will receive 0.1 WETH")
    return tx
