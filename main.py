# from web3 import Web3
#
# binance_testnet_rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
# web3 = Web3(Web3.HTTPProvider(binance_testnet_rpc_url))
# print(f"Is connected: {web3.is_connected()}")
# print(f"Gas Price: {web3.eth.gas_price / 1000000000} GWei")
# print(f"current block number: {web3.eth.get_block_number}")
# print(f"number of current chain is: {web3.eth.chain_id}")
#
# wallet_address = "0xf5Fb2ec9E68A71A6678a2FC966735595713455f7"
# checksum = web3.to_checksum_address(wallet_address)
# balance = web3.eth.get_balance(checksum)
# private_key = '0x' + '7f7834b2266be977ab8a5f2772e05075a25ee600b9d01ea679b54e22312a002e'
# print(f"The current amount of {wallet_address} == {web3.from_wei(balance, 'ether')} tBNB")
# print(int(web3.to_wei(105000, 'gwei')), web3.eth.gas_price)
# print(balance, web3.from_wei(balance, 'ether'))
# print(0.306933765 > float(web3.from_wei(balance, 'ether')))
# acc = web3.eth.account.from_key(private_key)
# print(acc.address)
count = 0
for i in '0xde82f6bdca833f9f610e49059b530b50d87ef9f63ea4a454be0480662c141191':
    count += 1
print(count)
acc = w3.eth.account.create();
print(f'private key={w3.to_hex(acc.key)}, account={acc.address}')