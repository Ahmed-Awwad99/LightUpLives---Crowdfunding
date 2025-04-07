from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        print("token: ",str(user.pk) + str(timestamp) + str(user.get_email_field_name))
        return (
            str(user.pk) + str(timestamp) + str(user.get_email_field_name)
        )
    
account_token = AccountActivationTokenGenerator()