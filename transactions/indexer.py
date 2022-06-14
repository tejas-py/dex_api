from clients import connection


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

