from algosdk.future.transaction import *
from tinyman.v1.client import TinymanTestnetClient


# opt-in asset function
def optin_asset(algod_client, address):
    # connect to Tiny-Man Client
    client = TinymanTestnetClient(algod_client=algod_client, user_address=address)

    # check if the account is opted into Tiny-Man and optin if necessary
    try:
        print('Account not opted into app, opting in now..')

        optin_transaction_group = client.prepare_app_optin_transactions()

        txn_grp = [
            {'txn': encoding.msgpack_encode(optin_transaction_group)}
        ]

        return txn_grp

    except Exception as Error:
        return 'Error !', Error


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


# assets swap
def swap_asset(algod_client, address, asset1, asset2, asset1_name, asset2_name, swap_amount):
    # connect to Tiny-Man Client
    client = TinymanTestnetClient(algod_client=algod_client, user_address=address)

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
    print(pool.asset1_price)

    # Get a quote for a swap of 1 asset_2 to Asset_1 with 1% slippage tolerance
    quote = pool.fetch_fixed_input_swap_quote(asset_2(swap_amount), slippage=0.01)

    # We only want to sell if Asset_2 is > 180 Asset_2 (It's testnet!)
    try:
        print(f'Swapping {quote.amount_in} to {quote.amount_out_with_slippage}')
        try:
            # Prepare a transaction group
            transaction_group = pool.prepare_swap_transactions_from_quote(quote)

            # splitting the signed and unsigned transactions
            unsignedTxn = transaction_group[0]
            singedTxn = transaction_group[1]

            # unsigned transactions
            unsign_encoded = {
                'txn1': encoding.msgpack_encode(unsignedTxn[0]),
                "txn2": encoding.msgpack_encode(unsignedTxn[1])
            }

            # signed transactions
            sign_encoded = {
                "stxn1": encoding.msgpack_encode(singedTxn[0]),
                "stxn2": encoding.msgpack_encode(singedTxn[1])
            }

            # total group of transactions
            total_txns = {
                "unsigned_txn": unsign_encoded,
                "signed_txn": sign_encoded
            }

            return total_txns

        except Exception as small_error:
            return 'Error !', small_error

    except Exception as Error:
        return 'Error !', Error


# remaining assets in the pool
def remaining_assets(algod_client, address, asset1, asset1_name,  asset2, asset2_name):

    # connect to Tiny-Man Client
    client = TinymanTestnetClient(algod_client=algod_client, user_address=address)

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

    pool = client.fetch_pool(asset_1, asset_2)

    # Check if any excess remaining after the swap
    excess = pool.fetch_excess_amounts()

    return str(excess)


# redeem swapped assets
def redeem_asset(algod_client, address, asset1, asset1_name,  asset2, asset2_name):
    # connect to Tiny-Man Client
    client = TinymanTestnetClient(algod_client=algod_client, user_address=address)

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

    pool = client.fetch_pool(asset_1, asset_2)

    # Check if any excess remaining after the swap
    excess = pool.fetch_excess_amounts()

    if asset_1 in excess:
        amount = excess[asset_1]
        print(f'Excess: {amount}')

        # We might just let the excess accumulate rather than redeeming if its < 1 TinyUSDC
        try:
            redeem_transaction_group = pool.prepare_redeem_transactions(amount)

            # splitting the signed and unsigned transactions
            unsignedTxn = redeem_transaction_group[0]
            singedTxn = redeem_transaction_group[1]

            # unsigned transactions
            unsign_encoded = {
                'txn1': encoding.msgpack_encode(unsignedTxn[0])
            }

            # signed transactions
            sign_encoded = {
                "stxn1": encoding.msgpack_encode(singedTxn[0]),
                "stxn2": encoding.msgpack_encode(singedTxn[1])
            }

            # total group of transactions
            total_txns = {
                "unsigned_txn": unsign_encoded,
                "signed_txn": sign_encoded
            }

            return total_txns

        except Exception as txn_error:
            return 'Transaction Error !', txn_error

    else:
        return f"No Excess remaining for , {asset2_name} to {asset1_name}"