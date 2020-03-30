from django.contrib.auth.models import User

from coindesk import rpc_pb2 as ln
from coindesk.models import Profile
from coindesk.utils.lnd_helper import get_ln_stub


class SignatureBackend(object):

    def authenticate(self, request, signature, csrf_token, username=None):
        stub = get_ln_stub()
        print(stub.GetInfo(ln.GetInfoRequest()))

        verifymessage_resp = stub.VerifyMessage(ln.VerifyMessageRequest(msg=bytes(csrf_token, 'utf-8'), signature=signature))
        # verifymessage_resp = stub.VerifyMessage(ln.VerifyMessageRequest(msg=bytearray(csrf_token, encoding='utf-8'), signature=signature))

        if not verifymessage_resp.valid:
            print("Invalid signature")
            return None

        pubkey = verifymessage_resp.pubkey
        # Try fetching an existing profile
        try:
            profile = Profile.objects.get(identity_pubkey=pubkey)
            return profile.user
        except Profile.DoesNotExist:
            # Create a new profile if they provided a username
            if 3 < len(username) < 36:
                user = User(username=username)
                user.save()
                profile, created = Profile.objects.get_or_create(
                    user=user,
                    identity_pubkey=pubkey)
                assert created is True
                # TODO Auth them in
            else:
                raise Exception("No username provided")
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
