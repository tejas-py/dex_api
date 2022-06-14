from algosdk.future.transaction import ApplicationNoOpTxn, PaymentTxn, AssetTransferTxn
from tinyman.utils import TransactionGroup
from .contracts import get_pool_logicsig
from tinyman.v1.client import TinymanTestnetClient
from clients import connection


def prepare_swap_transactions(validator_app_id, asset1_id, asset2_id, liquidity_asset_id, asset_in_id, asset_in_amount,
                              asset_out_amount, swap_type, sender, suggested_params):
    pool_logicsig = get_pool_logicsig(validator_app_id, asset1_id, asset2_id)
    pool_address = pool_logicsig.address()

    swap_types = {
        'fixed-input': 'fi',
        'fixed-output': 'fo',
    }

    asset_out_id = asset2_id if asset_in_id == asset1_id else asset1_id

    txns = [
        PaymentTxn(
            sender=sender,
            sp=suggested_params,
            receiver=pool_address,
            amt=2000,
            note='fee',
        ),
        ApplicationNoOpTxn(
            sender=pool_address,
            sp=suggested_params,
            index=validator_app_id,
            app_args=['swap', swap_types[swap_type]],
            accounts=[sender],
            foreign_assets=[asset1_id, liquidity_asset_id] if asset2_id == 0 else [asset1_id, asset2_id, liquidity_asset_id],
        ),
        AssetTransferTxn(
            sender=sender,
            sp=suggested_params,
            receiver=pool_address,
            amt=int(asset_in_amount),
            index=asset_in_id,
        ) if asset_in_id != 0  else PaymentTxn(
            sender=sender,
            sp=suggested_params,
            receiver=pool_address,
            amt=int(asset_in_amount),
        ),
        AssetTransferTxn(
            sender=pool_address,
            sp=suggested_params,
            receiver=sender,
            amt=int(asset_out_amount),
            index=asset_out_id,
        ) if asset_out_id != 0 else PaymentTxn(
            sender=pool_address,
            sp=suggested_params,
            receiver=sender,
            amt=int(asset_out_amount),
        ),
    ]

    txn_group = TransactionGroup(txns)

    # Signing the logic sign transaction
    txn_group.sign_with_logicisg(pool_logicsig)

    # taking out all the transaction from the tiny man object
    algodtransaction = txn_group.transactions
    unsign_txn = [algodtransaction[0], algodtransaction[2]]

    # taking out all the signed transaction from the tiny man object
    signedTransactions = txn_group.signed_transactions
    sign_txn = [signedTransactions[1], signedTransactions[3]]

    total_txns = [unsign_txn, sign_txn]

    return total_txns
