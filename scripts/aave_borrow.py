from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from brownie import interface, network, config, interface
from web3 import Web3

# 0.1
# amount = 100000000000000000
amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()
    lending_pool = get_lending_pool()
    print(lending_pool)
    # Approve sending out ERC20 tokens
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)
    print("Depositeds...")
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("Let's borrow some DAI!")
    # Need to get the conversion rate from DAI --- > Eth
    dai_eth_price = get_asset_price(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    # Calculates amount dai to borrow
    amount_dai_to_borrow = (1 / dai_eth_price) * (borrowable_eth * 0.75)
    print(f"We are going to borrow: {amount_dai_to_borrow}")
    # Let's borrow
    dai_address = config["networks"][network.show_active()]["dai_token_address"]
    print(f"dai_address: {dai_address}")
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("We borrowed some DAI!")
    get_borrowable_data(lending_pool, account)
    print("Repaying the DAI back")
    repay_all(amount, lending_pool, account)
    print("Getting account data again: ")
    get_borrowable_data(lending_pool, account)
    print("You just deposited, borrowed and repayed with Aave, Brownie and Chainlink!")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        amount,
        lending_pool,
        config["networks"][network.show_active()]["dai_token_address"],
        account,
    )
    tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token_address"],
        amount,
        1,
        account,
        {"from": account},
    )
    tx.wait(1)
    print(f"Repaid! {amount}")


def get_asset_price(price_feed_address):
    # ABI
    # Address
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    dai_eth_price_feed_converted = Web3.fromWei(latest_price, "ether")
    print(f"latest_price: {dai_eth_price_feed_converted}")
    print(f"latest price as float: {float(dai_eth_price_feed_converted)}")
    return float(dai_eth_price_feed_converted)


def get_borrowable_data(lending_pool, account):
    (
        totalCollateralETH,
        totalDebtETH,
        availableBorrowsETH,
        currentLiquidationThreshold,
        ltv,
        healthFactor,
    ) = lending_pool.getUserAccountData(account)
    totalCollateralETH = Web3.fromWei(totalCollateralETH, "ether")
    print(f"totalCollateralETH: {totalCollateralETH}")
    totalDebtETH = Web3.fromWei(totalDebtETH, "ether")
    print(f"totalDebtETH: {totalDebtETH}")
    availableBorrowsETH = Web3.fromWei(availableBorrowsETH, "ether")
    print(f"availableBorrowsETH: {availableBorrowsETH}")
    print(f"healthFactor: {healthFactor}")
    return (float(availableBorrowsETH), float(totalDebtETH))


def approve_erc20(amount, spender, erc_address, account):
    print("approving ERC20 token...")
    erc20 = interface.IERC20(erc_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("approved!")
    return tx
    # ABI
    # Address


def get_lending_pool():
    # Address
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
