import web3
from web3 import Web3
from solc import compile_standard
import json

ROPSTEN_URL = 'https://ropsten.infura.io/v3/4c4f3a5e3ca64dddadba2d5492de64eb'
keys = {"0x930D1A60D902867eDEC6225c663b86a2AC41eB8A":"8a0fbdc25fae3453f1b2c23fbc97e36c77879c46a51b64f7750997c281e29182", "0x5F2b764fA558aE25394BDa0E966d190f0274bd9d" : "9f8027d7d0baa25bca213de1c14916a693144ed0b739b06d9a3c9e45c84ace92"}
keys_list = ["0x930D1A60D902867eDEC6225c663b86a2AC41eB8A","0x5F2b764fA558aE25394BDa0E966d190f0274bd9d"]
CONTRACT_ADDR = "0xbe6b03288d0ea8A574Ade9F29e88e1192261Ed61"

def valid_address(addr):
	return Web3.isAddress(addr)
def read_file(filename):
	f = open(filename, "r")
	r = ""
	for i in f.readlines():
		r+=i
	return r
def compile_contract():
	contract = read_file("Shipping.sol")
	compiled_sol = compile_standard({"language": "Solidity","sources": {"Shipping.sol" :{"content":contract}}, "settings":{"outputSelection": {"*": {"*": ["metadata", "evm.bytecode", "evm.bytecode.sourceMap"]}}}})
	bytecode = compiled_sol['contracts']['Shipping.sol']['Shipping']['evm']['bytecode']['object']
	abi = compiled_sol['contracts']['Shipping.sol']['Shipping']['evm']['abi']['object']
	return contract,bytecode,abi
def generate_contract(filename, eth_acct):
	abi = json.loads(read_file("abi"))
	contract = eth_acct.eth.contract(address=CONTRACT_ADDR, abi=abi)
	return contract
def get_connection():
	return Web3(Web3.HTTPProvider(ROPSTEN_URL))
def get_contract(eth_acct):
	return generate_contract("abi",eth_acct)
def build_function_trans(addr,key,conn,contract_func,*args,value=0):
	conn.eth.defaultAccount = addr
	transaction_count = conn.eth.getTransactionCount(addr)
	transaction = contract_func(*args).buildTransaction({"value":value})
	transaction["nonce"]=transaction_count
	signed = conn.eth.account.signTransaction(transaction, key)
	return signed
def execute_signed_trans(conn,signed,msg="waiting for receipt..."):
	signed_txn = conn.eth.sendRawTransaction(signed.rawTransaction)
	print(msg)
	conn.eth.waitForTransactionReceipt(signed_txn)
	receipt = conn.eth.getTransactionReceipt(signed_txn)
	return receipt
def signup_driver(addr,key,conn,contract,*args):
	signup_func = contract.functions.signup_to_drive
	transaction = build_function_trans(addr,key,conn,
									   signup_func,*args)
	receipt = execute_signed_trans(conn,transaction)
	return receipt
def update_driver_status(addr, key, conn, contract, status):
	func = contract.functions.unavailable_to_drive
	if(status):
		func = contract.functions.available_to_drive
	transaction = build_function_trans(addr,key,conn,func)
	receipt = execute_signed_trans(conn,transaction)
	return receipt
def driver_exists(contract, addr):
	return contract.functions.driverExists(addr).call()
def driver_available(contract, addr):
	return contract.functions.driverAvailable(addr).call()
def estimate_shipping(contract, lat_o, lon_o, lat_d, lon_d):
	return contract.functions.get_cost(lat_o, lon_o, lat_d, lon_d).call()
def shipment_exists(contract, address):
	return contract.functions.shipmentExists(address).call()
def get_shipment_driver(contract, address):
	return contract.functions.get_package_driver(address).call()
def get_shipment_status(contract, address):
	return contract.functions.get_shipment_status(address).call()
def get_driver_status(contract, address):
	return contract.functions.get_driver_status(address).call()

def get_driver_package(contract, address):
	return contract.functions.get_driver_package(address).call()
def get_driver_goal_long(contract, address):
	return contract.functions.get_driver_goal_long(address).call()
def get_driver_goal_lat(contract, address):
	return contract.functions.get_driver_goal_lat(address).call()

def ship_package(addr,key,conn,contract,*args):
	ship_func = contract.functions.ship_package
	value = estimate_shipping(contract, args[0], args[1], args[2], args[3])
	print(value)
	transaction = build_function_trans(addr,key,conn,
									   ship_func,*args, value=value)
	print(transaction)
	receipt = execute_signed_trans(conn,transaction)
	return receipt
def claim_package(addr,key,conn,contract):
	claim_func = contract.functions.claimPackage
	transaction = build_function_trans(addr,key,conn,
									   claim_func)
	receipt = execute_signed_trans(conn,transaction)
	return receipt
def dropoff_package(addr,key,conn,contract):
	drop_func = contract.functions.dropoff
	transaction = build_function_trans(addr,key,conn,
									   drop_func)
	receipt = execute_signed_trans(conn,transaction)
	return receipt

#if __name__=="__main__":
#	print(valid_address(""))
#	w3 = get_connection()
#	contract = generate_contract("abi", w3)
#	signup_func = contract.functions.signup_to_drive
#	transaction = build_function_trans(keys_list[0],keys[keys_list[0]],w3,
#									   signup_func,1,1,c1,1,1,1)
#	receipt = execute_signed_trans(w3,transaction)
#	print(receipt)
#	print(driver_exists(contract, keys_list[0]))