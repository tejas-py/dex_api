from clients import connection
from tinyman.v1.client import TinymanTestnetClient


# connect to the indexer
indexer_client = connection.connect_indexer()


# return the assets information
def assets_wallet(wallet):
    response = indexer_client.account_info(wallet)
    total_assets = response['account']['assets']

    asset_list = []
    for wallet_asset_info in total_assets:
        one_asset_info = indexer_client.asset_info(wallet_asset_info.get('asset-id'))
        params = one_asset_info['asset']['params']
        asset = {
            "amount": wallet_asset_info.get('amount'),
            "id": wallet_asset_info.get('asset-id'),
            "frozen": wallet_asset_info.get('is-frozen'),
            "name": params.get('name'),
            "unitName": params.get('unit-name'),
            "creator": params.get('creator'),
            "decimals": params.get('decimals'),
            "url": params.get('url')
        }

        asset_list.append(asset)

    return asset_list


# return the price of the pool
def pool_price(algod_client, asset1, asset2, asset1_name, asset2_name, wallet_address):

    client = TinymanTestnetClient(algod_client=algod_client, user_address=wallet_address)

    # Declare assets
    asset = {
        "asset-1": {
            'asset_name': asset1_name,
            'asset_id': asset1
        },
        "asset-2": {
            'asset_name': asset2_name,
            'asset_id': asset2
        }
    }

    # define the swapping assets
    asset_1 = client.fetch_asset(asset["asset-1"]['asset_id'])
    asset_2 = client.fetch_asset(asset["asset-2"]['asset_id'])

    # Fetch the pool we will work with
    pool = client.fetch_pool(asset_1, asset_2)
    quote = pool.fetch_fixed_input_swap_quote(asset_2(1_000_000), slippage=0.01)

    return str(quote)
