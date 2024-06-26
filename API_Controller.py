from flask import Flask, request, jsonify
from flask_cors import CORS
from clients import connection as algod_client
from transactions import indexer, exchange

app = Flask(__name__)

# define the CORS
CORS(app)
cors = CORS(app, resources={
    r"/*": {
        "origin": "*"
    }
})

# connect to the algorand client
algod_client = algod_client.algo_conn()


# list the assets in the wallet
@app.route('/assets_in_wallet/<wallet_address>')
def asset_wallet(wallet_address):
    total_assets = indexer.assets_wallet(wallet_address)
    return jsonify(total_assets)


# price of the assets in the pool
@app.route('/pool_price', methods=['POST'])
def price_of_pool():
    # get the details
    asset_id = request.get_json()

    # asset that has to be converted to
    asset1 = int(asset_id['asset1'])
    asset1_name = asset_id['asset1_name']

    # asset that we want to be converted
    asset2 = int(asset_id['asset2'])
    asset2_name = asset_id['asset2_name']

    wallet_address = asset_id['wallet_address']

    price = exchange.pool_price(algod_client, asset1, asset2, asset1_name, asset2_name, wallet_address)
    final_price = price[9:]

    return jsonify(final_price)


# Opt-in the Assets
@app.route('/optin_asset', methods=['POST'])
def optin():
    # get the details
    account = request.get_json()
    address = account['wallet_address']

    optin_transaction = exchange.optin_asset(algod_client, address)
    return jsonify(optin_transaction)


# Swap Assets
@app.route('/swap_assets', methods=['POST'])
def swapping():
    # get the details
    asset_info = request.get_json()
    address = asset_info['wallet_address']

    # asset that is converted to
    asset1 = int(asset_info['asset1'])
    asset1_name = asset_info['asset1_name']

    # asset that is to be converted
    asset2 = int(asset_info['asset2'])
    asset2_name = asset_info['asset2_name']

    swap_amount = asset_info['amount']

    swap_transaction = exchange.swap_asset(algod_client, address,
                                           asset1, asset2, asset1_name, asset2_name, swap_amount)
    return jsonify(swap_transaction)


# remaining assets in pool
@app.route('/remaining_redeem', methods=['POST'])
def pool_excess():
    # get the details
    redeem_info = request.get_json()
    address = redeem_info['wallet_address']

    # asset that is converted to
    asset1 = int(redeem_info['asset1'])
    asset1_name = redeem_info['asset1_name']

    # asset that is to be converted
    asset2 = int(redeem_info['asset2'])
    asset2_name = redeem_info['asset2_name']

    remaining_amt = exchange.remaining_assets(algod_client, address, asset1, asset1_name, asset2, asset2_name)
    return remaining_amt


# Redeem Asset
@app.route('/redeem_asset', methods=['POST'])
def redeem():
    # get the details
    redeem_info = request.get_json()
    address = redeem_info['wallet_address']

    # asset that is converted to
    asset1 = int(redeem_info['asset1'])
    asset1_name = redeem_info['asset1_name']

    # asset that is to be converted
    asset2 = int(redeem_info['asset2'])
    asset2_name = redeem_info['asset2_name']

    redeem_transaction = exchange.redeem_asset(algod_client, address, asset1, asset1_name, asset2, asset2_name)
    return jsonify(redeem_transaction)


# running the API
if __name__ == "__main__":
    app.run(debug=True, port=2000)
