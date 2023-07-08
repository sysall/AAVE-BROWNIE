from brownie import config, config, network, interface
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

# 0.1
amount = Web3.toWei(0.1, "ether")

def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    # ABI
    # Address
    lending_pool = get_lending_pool()
    # print(lending_pool)
    # we need to approve another contract to use our token
    # Approve sendind out ERC20 tokens
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    # Deposit function
    print("Depositing...")
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")
    # how much to borrow : The maximum amount that can be borrowed will always be less than the collateral (liquidation threshold 80%)
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow DAI!")
    # DAI in term of ETH using chainlink price feed
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    # We multiply by 0.95 as a buffer to make sure our health factor is better
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.95)
    # borrowable_eth -> borrowable_dai * 95%
    print(f"we are going to borrow {amount_dai_to_borrow} DAI...")
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(dai_address,Web3.toWei(amount_dai_to_borrow, "ether"), 1, 0, account.address, {"from":account})
    borrow_tx.wait(1)
    print("Some DAI token has been borrowed!")
    get_borrowable_data(lending_pool, account)
    # Repaying
    repay_all(amount, lending_pool, account)
    print("You just deposit, borrow and repayed with Aave, Brownie, Chainlink")

def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account}
    )
    repay_tx.wait(1)
    print("Repayed!")




def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price_feed = interface.IAggregatorV3(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1] # 538604410154329
    converted_latest_price = Web3.fromWei(latest_price, "ether") # 0.000538604410154329
    print(f"The DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price)

def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_factor
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))



def approve_erc20(amount, spender, erc20_address, account):
    # ABI
    # Address
    print("Approving ERC20 token...")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved")
    return tx

def  get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    # Address
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool

