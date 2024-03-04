import sys
import os
import hashlib
import webbrowser
import pyperclip
import configparser
import sqlite3
import qrcode
import io
import button_icons
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from eth_account import Account
from eth_account.signers.local import LocalAccount
from typing import Optional
from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import geth_poa_middleware, construct_sign_and_send_raw_middleware

version = '0.0.1'

config_file_path = 'conf/config.txt'

if not os.path.exists(config_file_path):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'hashed_password': '',
        'first_time': 'true',
        'account': 1,
    }

    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

    config.read(config_file_path)

    config_password = config['DEFAULT']['hashed_password']
    first_time = config['DEFAULT']['first_time']
else:
    config = configparser.ConfigParser()
    config.read(config_file_path)

    config_password = config['DEFAULT']['hashed_password']
    first_time = config['DEFAULT']['first_time']

binance_testnet_rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
web3 = Web3(Web3.HTTPProvider(binance_testnet_rpc_url))

web3.middleware_onion.inject(geth_poa_middleware, layer=0)
web3.eth.account.enable_unaudited_hdwallet_features()

current_account = f'Account'


# функция для создания транзакции
def build_txn(from_address: str, to_address: str, amount: float) -> dict[str, int | str]:
    # цена газа
    gas_price = web3.eth.gas_price

    # число подтверждённых транзакций отправителя
    nonce = web3.eth.get_transaction_count(from_address)
    # сколько газа может потребоваться
    gas = 2_000_000

    txn = {
        'from': from_address,
        'to': to_address,
        'value': int(web3.to_wei(amount, 'ether')),
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': gas
    }
    return txn


def make_a_transaction(from_address, to_address, amount, private_key):
    transaction = build_txn(from_address, to_address, amount)

    # подписываем транзакцию с приватным ключом
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

    # Отправка транзакции
    txn_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    # получаем хеш транзакции
    # Можно посмотреть статус тут https://testnet.bscscan.com/
    return txn_hash


class WalletMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_pre_start()

    def init_pre_start(self):
        uic.loadUi('ui/prestart.ui', self)
        self.setFixedSize(400, 600)
        self.errorLine.hide()
        self.toNextStage.clicked.connect(self.password_check)
        if first_time == "false":
            self.welcome.setText('<html><head/><body><p align="center">Добро пожаловать!</p>'
                                 '<p align="center">Напишите пароль для входа в кошелёк.</p></body></html>')

    def password_check(self):
        password = self.passwordEnter.text()
        hashed_password = hashlib.sha256(str(password).encode("utf-8")).hexdigest()
        if hashed_password == config_password:
            self.init_key_start()
        elif not config_password:
            config['DEFAULT']['hashed_password'] = hashed_password
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)
            self.init_key_start()
        else:
            self.errorLine.show()

    def init_key_start(self):
        uic.loadUi('ui/privstartwithmanager.ui', self)
        self.setFixedSize(400, 600)
        self.continueWith.clicked.connect(self.key_check)
        self.addAccount.clicked.connect(self.add_account)
        self.delAccount.clicked.connect(self.delete_account)
        self.makeNewBtn.clicked.connect(self.make_new_account)
        self.accountListWidget.itemSelectionChanged.connect(self.show_account)
        config['DEFAULT']['first_time'] = 'false'
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

        # Создаем подключение к базе данных
        self.conn = sqlite3.connect('db/accounts.db')
        self.cursor = self.conn.cursor()

        # Создаем таблицу, если её нет
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                deleted INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

        # Загружаем аккаунты из базы данных
        self.load_accounts()

    def load_accounts(self):
        self.accountListWidget.clear()
        self.cursor.execute('SELECT * FROM accounts WHERE deleted = 0')
        accounts = self.cursor.fetchall()
        for account in accounts:
            item = QListWidgetItem(f'Account: {account[0]}, Private Key: {account[1]}')
            self.accountListWidget.addItem(item)

    def add_account(self):
        key = self.keyEnter.text()

        if key and len(key) == 64:
            # Ищем удаленные аккаунты
            self.cursor.execute('SELECT id FROM accounts WHERE deleted = 1 LIMIT 1')
            deleted_account = self.cursor.fetchone()

            if deleted_account:
                account_id = deleted_account[0]
                # Восстанавливаем удаленный аккаунт
                self.cursor.execute('UPDATE accounts SET key = ?, deleted = 0 WHERE id = ?', (key, account_id))
            else:
                # Создаем новый аккаунт
                self.cursor.execute('INSERT INTO accounts (key) VALUES (?)', (key,))

            self.conn.commit()

            # Обновляем список аккаунтов
            self.load_accounts()

            # Очищаем поле ввода
            self.keyEnter.clear()

    def delete_account(self):
        selected_items = self.accountListWidget.selectedItems()
        for selected_item in selected_items:
            # Извлекаем ID аккаунта из текста и устанавливаем флаг "удален"
            account_id = selected_item.text().split(',')[0].split(':')[-1].strip()
            self.cursor.execute('UPDATE accounts SET deleted = 1 WHERE id = ?', (account_id,))
            self.conn.commit()

        # Обновляем список аккаунтов
        self.load_accounts()

    def show_account(self):
        selected_items = self.accountListWidget.selectedItems()
        if selected_items:
            account_info = selected_items[0].text()
            # Извлекаем "key" из текста
            self.private_key = '0x' + account_info.split('Private Key: ')[1]
            current_account = f'Account + {account_info.split(',')[0].split(':')[-1].strip()}'

    def make_new_account(self):
        new_acc = web3.eth.account.create()
        key = web3.to_hex(new_acc.key)[2:]
        self.cursor.execute('SELECT id FROM accounts WHERE deleted = 1 LIMIT 1')
        deleted_account = self.cursor.fetchone()
        if deleted_account:
            account_id = deleted_account[0]
            self.cursor.execute('UPDATE accounts SET key = ?, deleted = 0 WHERE id = ?', (key, account_id))
        else:
            self.cursor.execute('INSERT INTO accounts (key) VALUES (?)', (key,))

        self.conn.commit()

        # Обновляем список аккаунтов
        self.load_accounts()

    def key_check(self):
        self.goToAcc()

    def goToAcc(self):
        account: LocalAccount = Account.from_key(self.private_key)
        web3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
        self.my_address = account.address
        self.checksum = web3.to_checksum_address(self.my_address)
        self.balance = web3.eth.get_balance(self.checksum)
        self.init_main_ui()

    def init_main_ui(self):
        uic.loadUi('ui/main.ui', self)
        self.update_main_wallet_info()
        self.setFixedSize(400, 600)
        self.changeAccBtn.clicked.connect(self.change_account)
        self.sendButton.clicked.connect(self.sendwindow_open)
        self.receiveButton.clicked.connect(self.receivewindow_open)
        self.infoButton.clicked.connect(self.open_wallet_url)
        self.settingsButton.clicked.connect(self.open_settings)

    def change_account(self):
        config['DEFAULT']['private_key'] = ''
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
        self.init_key_start()

    def update_main_wallet_info(self):
        self.checksum = web3.to_checksum_address(self.my_address)
        self.balance = web3.eth.get_balance(self.checksum)
        self.balanceLabel.setText(f"{web3.from_wei(self.balance, 'ether')} BNB")
        self.addressLabel.setText(f"{current_account}")

    def open_settings(self):
        pass

    def open_wallet_url(self):
        webbrowser.open(f"https://testnet.bscscan.com/address/{self.my_address}", new=2)

    def sendwindow_open(self):
        uic.loadUi('ui/send.ui', self)
        self.setFixedSize(400, 600)
        self.checksum = web3.to_checksum_address(self.my_address)
        self.balance = web3.eth.get_balance(self.checksum)
        self.errorLine.hide()
        self.backButton.clicked.connect(self.init_main_ui)
        self.all.clicked.connect(self.set_all_amount)
        self.addressBalance.setText(f"Баланс: {web3.from_wei(self.balance, 'ether')} BNB")
        self.toNextStage.clicked.connect(self.send_crypto)

    def set_all_amount(self):
        self.amount.setText(str(web3.from_wei(self.balance, 'ether')))

    def send_crypto(self):
        self.errorLine.setStyleSheet('border-radius: 10px; '
                                     'min-height: 20px; '
                                     'min-width: 20px; '
                                     'background-color: rgb(255, 0, 0);')
        self.errorLine.setText("Ошибка")
        receiver_address = self.receiverAddress.text()
        amount = float(self.amount.text())
        if receiver_address == '' or not web3.is_address(receiver_address):
            self.errorLine.setText("Неверно указан адрес!")
            self.errorLine.show()
        elif not 0 < amount <= float(web3.from_wei(self.balance, 'ether')):
            self.errorLine.setText("Неверно указана сумма!")
            self.errorLine.show()
        else:
            try:
                if make_a_transaction(self.my_address, receiver_address, amount, self.private_key):
                    self.errorLine.setStyleSheet('border-radius: 10px; '
                                                 'min-height: 20px; '
                                                 'min-width: 20px; '
                                                 'background-color: rgb(0, 255, 0);')
                    self.errorLine.setText("Успешная транзакция!")
                    self.errorLine.show()
                    print(make_a_transaction, web3.eth.gas_price)
            except ValueError:
                self.errorLine.setText("Ошибка транзакции")
                self.errorLine.show()

    def receivewindow_open(self):
        uic.loadUi('ui/receive.ui', self)
        self.setFixedSize(400, 600)
        self.generate_qr()
        self.address.setText(f"{self.my_address[:24]} {self.my_address[24:]}")
        self.address.setWordWrap(True)
        self.toCopyboard.clicked.connect(self.to_copyboard)
        self.backButton.clicked.connect(self.init_main_ui)

    def generate_qr(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=1,
        )
        qr.add_data(self.my_address)
        qr.make(fit=True)

        img = qr.make_image(fill_color="white", back_color=(42, 42, 42))
        img.save('qr/qr.png')
        pixmap = QPixmap('qr/qr.png')
        self.qrcode.setPixmap(pixmap)

    def to_copyboard(self):
        pyperclip.copy(self.my_address)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = WalletMainWindow()
    sys.excepthook = except_hook
    w.show()
    sys.exit(app.exec())