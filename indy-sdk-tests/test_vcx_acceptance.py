import pytest
from utils import payment_initializer
from vcx.api.vcx_init import vcx_init
from vcx.api.wallet import Wallet
from vcx.common import mint_tokens

# import logging
# logging.basicConfig(level=0)
# logging.basicConfig( level=logging.DEBUG)
# logging.getLogger().setLevel(0)


@pytest.mark.asyncio
async def test_vcx_mint_token():
    config = './config.json'
    library = 'libnullpay.so'
    initializer = 'nullpay_init'
    await payment_initializer(library, initializer)

    """ Mint tokens to send """
    # Create the connection to before processing the credential
    await vcx_init(config)

    # Mint tokens and store in wallet
    mint_tokens()  # three addresses and 1000 tokens each - puts stuff in wallet only...

    tkn = await Wallet.get_token_info(0)
    print("Token info %s " % tkn)
    address = await Wallet.create_payment_address()
    # Send tokens - test for EN-479
    rec = await Wallet.send_tokens(0, 50000000000, address.decode('utf-8'))
    tkn2 = await Wallet.get_token_info(0)
    print("============")
    print(tkn2)
