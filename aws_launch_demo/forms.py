from django import forms

from boto.ec2 import connect_to_region
from boto.exception import EC2ResponseError


class AWSCredentials(forms.Form):

    access_key = forms.CharField()
    # Don't want browsers saving secret keys.
    secret_key = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        """Verify provided credentials."""
        cleaned_data = super(AWSCredentials, self).clean()

        try:
            conn = connect_to_region(
                'us-west-2',
                aws_access_key_id=cleaned_data['access_key'],
                aws_secret_access_key=cleaned_data['secret_key'])

            # Validate the credentials by attempting to create a secgroup
            wordpress = conn.create_security_group('wordpressdemo', 'Access to frontend http')
            wordpress.authorize(ip_protocol='tcp', from_port=80, to_port=80, cidr_ip='0.0.0.0/0')
        except EC2ResponseError as e:
            # An Duplicate error here means the creds could be used to attempt
            # the secgroup creation.
            if e.error_code not in ('InvalidPermission.Duplicate', 'InvalidGroup.Duplicate'):
                raise forms.ValidationError(
                    "There was an error connecting to EC2 with these credentials: "
                    "%(error_code)s - %(error_message)s",
                    params=dict(error_code=e.error_code, error_message=e.error_message),
                    code=e.error_code)

        return cleaned_data
