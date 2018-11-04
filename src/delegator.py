'''
NEO CityOfZurich Delegator Smart Contract

Authors: Michele Federici
Email: michele@federici.tech
Version: 1.0
Date: 03 November 2018
License: MIT

# Build-test
neo> build src/delegator.py test 0710 01 True True 0 registerProvider ['KYC1',b'db28f711893ada23f513d86e6c0ce195b578d116']
neo> build src/delegator.py test 0710 01 True True 0 delegateVerify ['KYC1']
# Build
neo> build src/delegator.py
# Deploy
neo> import contract src/delegator.avm 0710 07 True True 0
neo> contract search ICO1
# Invoke
neo> testinvoke 50b57d93fe256f78196e9c28d7fe5674c140a8d3 registerProvider ['KYC1',b'db28f711893ada23f513d86e6c0ce195b578d116']
neo> testinvoke 50b57d93fe256f78196e9c28d7fe5674c140a8d3 delegateVerify ['KYC1']
'''

from boa.interop.Neo.Runtime import Notify, CheckWitness
from boa.interop.Neo.Storage import Get, Put, Delete, GetContext
from boa.interop.Neo.App import DynamicAppCall
from boa.interop.System.ExecutionEngine import GetCallingScriptHash

OWNER = b'#\xba\'\x03\xc52c\xe8\xd6\xe5"\xdc2 39\xdc\xd8\xee\xe9'

ARG_ERROR = 'Wrong number of arguments'
INVALID_OPERATION = 'Invalid operation'
INVALID_ADDRESS = 'Invalid address'
MISSING_PROVIDER_NAME = 'Provider name not provided'
ILLEGAL_CALL = 'Illegal call'
ALREADY_EXISTING_PROVIDER = 'Provider already exists'
UNEXISTING_PROVIDER = 'Unexisting provider'

def Main(op, args):
    context = GetContext()

    if op == 'registerProvider':
        if len(args) == 2:
            return register_provider(context, args)
        else:
            Notify(ARG_ERROR)
            return False
    elif op == 'delegateVerify':
        if len(args) == 1:
            wallet = GetCallingScriptHash()
            return delegate_verify(context, wallet, args)
        else:
            Notify(ARG_ERROR)
            return False
    else:
        Notify(INVALID_OPERATION)
        return False

def register_provider(context, args):
    if not CheckWitness(OWNER):
        Notify(ILLEGAL_CALL)
        return False

    name = args[0]
    provider = args[1]

    if not name:
        Notify(MISSING_PROVIDER_NAME)
        return False

    if len(provider) != 20:
        Notify(INVALID_ADDRESS)
        return False

    if Get(context, name):
        Notify(ALREADY_EXISTING_PROVIDER)
        return False

    Notify(['[REGISTER-PROVIDER] name:', name, 'provider:', provider])

    Put(context, name, provider)

    return True

def delegate_verify(context, wallet, args):
    name = args[0]
    provider = Get(context, name)

    if not provider:
        Notify(UNEXISTING_PROVIDER)
        return False

    Notify(['[DELEGATE-VERIFY] caller:', wallet, 'provider', provider])

    result = DynamicAppCall(provider, 'verifyClaim', [wallet])
    if not result:
        Notify('[DELEGATE-VERIFY] access denied')
        return False

    return True