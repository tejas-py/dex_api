from tinyman.v1.client import TinymanTestnetClient


# opt-in asset function
def optin_asset(algod, address):
    # connect to Tiny-Man Client
    client = TinymanTestnetClient(algod_client=algod, user_address=address)

    # check if the account is opted into Tiny-Man and optin if necessary
    try:
        print('Account not opted into app, opting in now..')
        optin_transaction_group = client.prepare_app_optin_transactions()
        return str(optin_transaction_group)
    except Exception as Error:
        return 'Error !', Error


# assets swap
def swap_asset(algod, address, asset1, asset2, asset1_name, asset2_name, swap_amount):
    # connect to Tiny-Man Client
    client = TinymanTestnetClient(algod_client=algod, user_address=address)

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
    print('{} per {}: {}'.format(asset["asset-1"]['asset_name'],
                                 asset["asset-2"]['asset_name'],
                                 quote.price))

    print('{} per {} (worst case): {}'.format(asset["asset-1"]['asset_name'],
                                              asset["asset-2"]['asset_name'],
                                              quote.price_with_slippage))

    # We only want to sell if Asset_2 is > 180 Asset_2 (It's testnet!)
    try:
        print(f'Swapping {quote.amount_in} to {quote.amount_out_with_slippage}')
        try:
            # Prepare a transaction group
            swap_transaction_group = pool.prepare_swap_transactions_from_quote(quote)
        except Exception as swap_transaction_group:
            return 'Error !', swap_transaction_group

    except Exception as swap_transaction_group:
        return 'Error !', swap_transaction_group

    return str(swap_transaction_group)


# redeem swapped assets
def redeem_asset(algod, address, asset1, asset2):
    # connect to Tiny-Man Client
    client = TinymanTestnetClient(algod_client=algod, user_address=address)
    pool = client.fetch_pool(asset1, asset2)

    # Check if any excess remaining after the swap
    excess = pool.fetch_excess_amounts()
    if asset1 in excess:
        amount = excess[asset1]
        print(f'Excess: {amount}')
        # We might just let the excess accumulate rather than redeeming if its < 1 TinyUSDC
        try:
            redeem_transaction_group = pool.prepare_redeem_transactions(amount)
        except Exception as redeem_transaction_group:
            return 'Error !', redeem_transaction_group
    else:
        return f"Error in redeeming {asset1}"

    return redeem_transaction_group
