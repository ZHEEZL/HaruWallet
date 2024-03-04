import sys
import webbrowser
import io
import button_icons
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize, Qt
from PyQt5 import uic, pyrcc
from eth_account import Account
from eth_account.signers.local import LocalAccount
from typing import Optional
from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import geth_poa_middleware

version = '0.0.1'

binance_testnet_rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
web3 = Web3(Web3.HTTPProvider(binance_testnet_rpc_url))

web3.middleware_onion.inject(geth_poa_middleware, layer=0)
web3.eth.account.enable_unaudited_hdwallet_features()

my_address = "0xf5Fb2ec9E68A71A6678a2FC966735595713455f7"
checksum = web3.to_checksum_address(my_address)
balance = web3.eth.get_balance(checksum)
receiver_address = ''


class WalletSendWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('send.ui', self)
        self.backButton.clicked.connect(self.mainWindowOpen)
        self.update_wallet_info()

    def update_wallet_info(self):
        self.addressBalance.setText(f"Баланс: {web3.from_wei(balance, 'ether')} BNB")

    # функция для создания транзакции
    def build_txn(self, web3: Web3, from_address: str, to_address: str, amount: float) -> dict[str, int | str]:
        # цена газа
        gas_price = web3.eth.gas_price

        # число подтверждённых транзакций отправителя
        nonce = web3.eth.get_transaction_count(from_address)

        gas = 2_000_000

        txn = {
            'from': from_address,
            'to': to_address,
            'value': int(web3.to_wei(amount, 'ether')),
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas
        }
        # сколько газа может потребоваться
        print(f'Примерный газ: {web3.eth.gas_price}')
        print("Вы уверены? Y/n")
        if input() == 'Y':
            gas = web3.eth.estimate_gas(txn)
            return txn
        else:
            sys.exit()

    def make_a_transaction(self):
        transaction = self.build_txn(
            web3=web3,
            from_address=my_address,
            to_address=receiver_address,
            amount=0.1
        )

        # подписываем транзакцию с приватным ключом
        # signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

        # Отправка транзакции
        # txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # получаем хеш транзакции
        # Можно посмотреть статус тут https://testnet.bscscan.com/

    private_key = '0x' + 'de82f6bdca833f9f610e49059b530b50d87ef9f63ea4a454be0480662c141191'
    assert private_key is not None, "You must set PRIVATE_KEY environment variable"

    def mainWindowOpen(self):
        self.hide()
        self.window = WalletMainWindow()
        self.window.show()


class WalletMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.update_wallet_info()
        self.infoButton.clicked.connect(self.openWalletURL)
        self.setFixedSize(400, 600)
        self.sendButton.clicked.connect(self.sendWindowOpen)

    def update_wallet_info(self):
        self.balanceLabel.setText(f"{web3.from_wei(balance, 'ether')} BNB")
        self.addressLabel.setText(f"{my_address}")

    def openWalletURL(self):
        webbrowser.open(f"https://testnet.bscscan.com/address/{my_address}", new=2)

    def sendWindowOpen(self):
        self.hide()
        self.window = WalletSendWindow()
        self.window.show()



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = WalletMainWindow()
    sys.excepthook = except_hook
    w.show()
    sys.exit(app.exec())
