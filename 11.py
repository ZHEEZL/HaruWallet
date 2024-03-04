import sys
import webbrowser
import hashlib
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5 import uic
from web3 import Web3
from web3.middleware import geth_poa_middleware

binance_testnet_rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
web3 = Web3(Web3.HTTPProvider(binance_testnet_rpc_url))

web3.middleware_onion.inject(geth_poa_middleware, layer=0)
web3.eth.account.enable_unaudited_hdwallet_features()

my_address = "0xf5Fb2ec9E68A71A6678a2FC966735595713455f7"
checksum = web3.to_checksum_address(my_address)
balance = web3.eth.get_balance(checksum)
receiver_address = ''
amount = 1.56644
f = int(web3.to_wei(amount, 'ether'))
print(f)
import qrcode
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=6,
    border=1,
)
qr.add_data("0xf5Fb2ec9E68A71A6678a2FC086735595713455f7")
qr.make(fit=True)

img = qr.make_image(fill_color="white", back_color=(42, 42, 42))
img.save('test1.png')
i = QLabel
i.setWordWrap(True)
i.text()
print(hashlib.sha256('123'.encode("utf-8")).hexdigest())
print(de82f6bdca833f9f610e49059b530b50d87ef9f63ea4a454be0480662c141191)
7f7834b2266be977ab8a5f2772e05075a25ee600b9d01ea679b54e22312a002e