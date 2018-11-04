"""NEO Identity Token Smart Contract

Authors: Ben Wolf
Email: benjamin.wolf@swisscom.com
Version: 1.0
Date: 03 November 2018
License: MIT

Based on NFT Template of Splyse

Example test using neo-local:
neo> build src/identity_token.py test 0710 05 True True False name []

Compile and import with neo-python using neo-local:
neo> build src/identity_token.py
neo> import contract src/identity_token.avm 0710 05 True True False

Example invocation
neo> testinvoke {this_contract_hash} mintToken ['destination_wallet_address', 'claims']
neo> testinvoke {this_contract_hash} tokensOfOwner ['your_wallet_address', 1]
"""

from boa.builtins import concat
from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.App import DynamicAppCall
from boa.interop.Neo.Blockchain import GetContract
from boa.interop.Neo.Iterator import IterNext, IterKey, IterValue
from boa.interop.Neo.Runtime import (CheckWitness, GetTrigger, Log,
                                     Notify, Serialize)
from boa.interop.Neo.Storage import GetContext, Get, Put, Delete, Find
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.System.ExecutionEngine import (GetCallingScriptHash,
                                                GetEntryScriptHash,
                                                GetExecutingScriptHash)

# This is the script hash of the address for the owner of the contract
# This can be found in ``neo-python`` with the wallet open,
# use ``wallet`` command
# TOKEN_CONTRACT_OWNER = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
# TOKEN_CONTRACT_OWNER = b'\x0f&\x1f\xe5\xc5,k\x01\xa4{\xbd\x02\xbdM\xd3?\xf1\x88\xc9\xde'
TOKEN_CONTRACT_OWNER = b'#\xba\'\x03\xc52c\xe8\xd6\xe5"\xdc2 39\xdc\xd8\xee\xe9'
TOKEN_NAME = 'Identity Token'
TOKEN_SYMBOL = 'IDK'
TOKEN_CIRC_KEY = b'in_circulation'

# Smart Contract Event Notifications
OnMint = RegisterAction('mint', 'addr_to')
OnIDKMint = RegisterAction('NFTmint', 'addr_to')

# common errors
ARG_ERROR = 'incorrect arg length'
INVALID_ADDRESS_ERROR = 'invalid address'
PERMISSION_ERROR = 'incorrect permission'
TOKEN_DNE_ERROR = 'token does not exist'


def Main(operation, args):
    """Entry point to the program

    :param str operation: The name of the operation to perform
    :param list args: A list of arguments along with the operation
    :return: The result of the operation
    :rtype: bytearray

    Token operations:
    - name(): returns name of token
    - symbol(): returns token symbol
    - claims(): returns a holders claim

    TOKEN_CONTRACT_OWNER operations:
        - mintToken(owner, claims): create a new NFT token with the specified properties
        and URI and send it to the specified owner
    """
    # The trigger determines whether this smart contract is being run
    # in 'verification' mode or 'application'
    trigger = GetTrigger()

    # 'Verification' mode is used when trying to spend assets
    # (eg NEO, Gas) on behalf of this contract's address
    if trigger == Verification():

        # if the script that sent this is the owner, we allow the spend
        if CheckWitness(TOKEN_CONTRACT_OWNER):
            return True

    elif trigger == Application():

        ctx = GetContext()

        if operation == 'name':
            return TOKEN_NAME

        elif operation == 'symbol':
            return TOKEN_SYMBOL

        elif operation == 'claims':
            t_owner = GetCallingScriptHash()
            token = Get(ctx, t_owner)

            if len(token) == b'\x00':
                token = b'\x01'  # token id's cannot go below 1

            claims = Get(ctx, concat('claims/', token))
            if claims:
                return claims

            Notify(TOKEN_DNE_ERROR)
            return False

        # Administrative operations
        if operation == 'mintToken':
            if CheckWitness(TOKEN_CONTRACT_OWNER):
                if len(args) == 2:
                    return do_mint_token(ctx, args)

                Notify(ARG_ERROR)
                return False
            else:
                Notify(PERMISSION_ERROR)
                return False

        Notify('unknown operation')

    return False


def do_mint_token(ctx, args):
    """Mints a new NFT token; stores it's properties, URI info, and
    owner on the blockchain; updates the totalSupply

    :param StorageContext ctx: current store context
    :param list args:
        0: byte[] t_owner: token owner
        1: byte[] t_claims: token's claims
    :return: mint success
    :rtype: bool
    """
    t_id = Get(ctx, TOKEN_CIRC_KEY)
    # the int 0 is represented as b'' in neo-boa, this caused bugs
    # throughout my code
    # This is the reason why token id's start at 1 instead
    t_id += 1

    # this should never already exist
    if len(Get(ctx, t_id)) == 20:
        Notify('token already exists')
        return False

    t_owner = args[0]
    if len(t_owner) != 20:
        Notify(INVALID_ADDRESS_ERROR)
        return False

    t_claims = args[1]
    if len(t_claims) == b'\x00':
        Notify('missing claims data string')
        return False

    token_amount = Get(ctx, t_owner)
    Notify(token_amount)
    if token_amount > 0:
        Notify('address already has an identity token')
        return False

    Put(ctx, t_id, t_owner)  # update token's owner
    Put(ctx, concat('claims/', t_id), t_claims)
    add_token_to_owners_list(ctx, t_owner, t_id)
    Put(ctx, TOKEN_CIRC_KEY, t_id)  # update total supply

    # Log this minting event
    OnMint(t_owner)
    OnIDKMint(t_owner)
    return True


def add_token_to_owners_list(ctx, t_owner, t_id):
    """Adds a token to the owner's list of tokens

    :param StorageContext ctx: current store context
    :param byte[] t_owner: token owner (could be either a smart
        contract or a wallet address)
    :param bytes t_id: token ID
    :return: successfully added token to owner's list
    :rtype: bool
    """
    length = Get(ctx, t_owner)  # number of tokens the owner has
    Put(ctx, concat(t_owner, t_id), t_id)  # store owner's new token
    length += 1  # increment the owner's balance
    Put(ctx, t_owner, length)  # store owner's new balance
    Log("added token to owner's list and incremented owner's balance")
    return True
