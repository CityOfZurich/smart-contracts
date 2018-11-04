'''
NEO CityOfZurich Provider Smart Contract

Authors: Michele Federici
Email: michele@federici.tech
Version: 1.0
Date: 03 November 2018
License: MIT

# Build-test
neo> build src/provider.py test 0710 01 True True 0 registerDelegator [b'50b57d93fe256f78196e9c28d7fe5674c140a8d3','ICO1']
neo> build src/provider.py test 0710 01 True True 0 registerWallet [b'#\xba\'\x03\xc52c\xe8\xd6\xe5"\xdc2 39\xdc\xd8\xee\xe9']
# Build
neo> build src/provider.py
# Deploy
neo> import contract src/provider.avm 0710 01 True True 0
neo> contract search KYC1
# Invoke
neo> testinvoke 22c5868efc9ebbc90e4bd6087ff3c97b72ed7b97 registerDelegator [b'50b57d93fe256f78196e9c28d7fe5674c140a8d3','ICO1']
neo> testinvoke 22c5868efc9ebbc90e4bd6087ff3c97b72ed7b97 registerWallet [b'#\xba\'\x03\xc52c\xe8\xd6\xe5"\xdc2 39\xdc\xd8\xee\xe9']
# Notes:
The verifyClaim method can't be tested independently because it checks the invoker address
'''

from boa.interop.Neo.Runtime import Notify, CheckWitness
from boa.interop.Neo.Storage import Get, Put, Delete, GetContext
from boa.interop.System.ExecutionEngine import GetEntryScriptHash

OWNER = b'#\xba\'\x03\xc52c\xe8\xd6\xe5"\xdc2 39\xdc\xd8\xee\xe9'

ARG_ERROR = 'Wrong number of arguments'
INVALID_OPERATION = 'Invalid operation'
INVALID_ADDRESS = 'Invalid address'
MISSING_DELEGATOR_NAME = 'Delegator name not provided'
ALREADY_EXISTING_DELEGATOR = 'Delegator already exists'
ALREADY_EXISTING_WALLET = 'Wallet already exists'
UNEXISTING_DELEGATOR = 'Unexisting delegator'
UNEXISTING_WALLET = 'Unexisting wallet'
ILLEGAL_CALL = 'Illegal call'

def Main(op, args):
    context = GetContext()

    if op == 'registerDelegator':
        if len(args) == 2:
            return register_delegator(context, args)
        else:
            Notify(ARG_ERROR)
            return False
    elif op == 'registerWallet':
        if len(args) == 1:
            return register_wallet(context, args)
        else:
            Notify(ARG_ERROR)
            return False
    elif op == 'verifyClaim':
        if len(args) == 1:
            delegator = GetEntryScriptHash()
            return verify_claim(context, delegator, args)
        else:
            Notify(ARG_ERROR)
            return False
    else:
        Notify(INVALID_OPERATION)
        return False

def register_delegator(context, args):
    if not CheckWitness(OWNER):
        Notify(ILLEGAL_CALL)
        return False

    delegator = args[0]
    name = args[1]

    if len(delegator) != 20:
        Notify(INVALID_ADDRESS)
        return False

    if not name:
        Notify(MISSING_DELEGATOR_NAME)
        return False

    if Get(context, delegator):
        Notify(ALREADY_EXISTING_DELEGATOR)
        return False

    Notify(['[REGISTER-DELEGATOR] delegator:', delegator, 'name:', name])

    Put(context, delegator, name)

    return True

def register_wallet(context, args):
    if not CheckWitness(OWNER):
        Notify(ILLEGAL_CALL)
        return False

    wallet = args[0]

    if len(wallet) != 20:
        Notify(INVALID_ADDRESS)
        return False

    if Get(context, wallet):
        Notify(ALREADY_EXISTING_WALLET)
        return False

    Notify(['[REGISTER-WALLET] wallet:', wallet])

    Put(context, wallet, True)

    return True

def verify_claim(context, delegator, args):
    holder = args[0]

    if len(holder) != 20:
        Notify(INVALID_ADDRESS)
        return False

    if not Get(context, delegator):
        Notify(UNEXISTING_DELEGATOR)
        return False

    if not Get(context, holder):
        Notify(UNEXISTING_WALLET)
        return False
    
    Notify(['[VERIFY-CLAIM] holder:', holder, 'delegator', delegator])

    return True