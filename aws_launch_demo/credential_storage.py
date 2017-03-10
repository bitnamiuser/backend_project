from functools import wraps

from boto.ec2 import connect_to_region

from django.http import HttpResponseRedirect


def save_credentials_for_request(request, access_key, secret_key):
    """Save creds for re-use.

    Currently this saves to the session table, which is not ideal - but it's an
    easy solution for a demo without requiring user auth and models.

    This function is abstracted here to be replaceable.
    """
    request.session['aws_access_key'] = access_key
    request.session['aws_secret_key'] = secret_key


def aws_credentials_required(view_func):
    """Decorate views requiring aws credentials adding aws connection to args"""
    @wraps(view_func)
    def wrapper(request):
        if ("aws_access_key" not in request.session or
            "aws_secret_key" not in request.session):
            return HttpResponseRedirect('/credentials/')

        # If the credentials are present, pass a valid connection
        # to the view.
        conn = connect_to_region(
            'us-west-2',
            aws_access_key_id=request.session['aws_access_key'],
            aws_secret_access_key=request.session['aws_secret_key'])

        return view_func(request, conn)
    return wrapper
