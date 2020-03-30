import codecs
import os

import grpc

from coindesk import settings
from coindesk import rpc_pb2_grpc as lnrpc


def get_ln_stub():
    def metadata_callback(context, callback):
        # for more info see grpc docs
        callback([('macaroon', macaroon)], None)

    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'
    # Lnd admin macaroon is at ~/.lnd/data/chain/bitcoin/simnet/admin.macaroon on Linux and
    # ~/Library/Application Support/Lnd/data/chain/bitcoin/simnet/admin.macaroon on Mac
    with open(os.path.expanduser(settings.MACAROON_PATH), 'rb') as f:
        macaroon_bytes = f.read()
        macaroon = codecs.encode(macaroon_bytes, 'hex')
    cert = open(settings.CERT_PATH, 'rb').read()
    creds = grpc.ssl_channel_credentials(cert)

    # now build meta data credentials
    auth_creds = grpc.metadata_call_credentials(metadata_callback)

    # combine the cert credentials and the macaroon auth credentials
    # such that every call is properly encrypted and authenticated
    combined_creds = grpc.composite_channel_credentials(creds, auth_creds)

    # channel = grpc.secure_channel(settings.LND_RPCHOST, creds)
    channel = grpc.secure_channel(settings.LND_RPCHOST, combined_creds)
    # stub.GetInfo(ln.GetInfoRequest(), metadata=[('macaroon', macaroon)])
    stub = lnrpc.LightningStub(channel)

    return stub
