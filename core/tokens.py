from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int


class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, pending_user, timestamp):
        # Используем username и email из PendingUser
        return f"{pending_user.username}{pending_user.email}{timestamp}"

    def make_token(self, pending_user):
        return self._make_token_with_timestamp(
            pending_user, self._num_seconds(self._now()), self.secret
        )

    def check_token(self, pending_user, token):
        if not (pending_user and token):
            return False
        try:
            ts_b36, _ = token.split("-")
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        if constant_time_compare(
            self._make_token_with_timestamp(pending_user, ts, self.secret),
            token,
        ):
            return True
        return False
