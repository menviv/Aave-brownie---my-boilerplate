from scripts.helpful_scripts import get_account
from brownie import interface, network, config


def main():
    get_weth()


def get_weth():
    pass
    """
    Mints WETH by depositing ETH
    """
    # ABI
    # Address
    account = get_account()
    address = config["networks"][network.show_active()]["weth_token"]
    weth = interface.IWeth(address)  ### ABI to use
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx
