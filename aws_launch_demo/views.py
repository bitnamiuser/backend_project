from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .forms import AWSCredentials
from .credential_storage import (
    aws_credentials_required,
    save_credentials_for_request,
)


def capture_aws_credentials(request):
    """Capture, validate and store aws credentials."""
    if request.method == 'POST':
        form = AWSCredentials(request.POST)
        if form.is_valid():
            save_credentials_for_request(request, **form.cleaned_data)

            return HttpResponseRedirect(reverse('manage-instances'))
    else:
        form = AWSCredentials()

    return render(request, 'aws-credentials.html', dict(form=form))


@aws_credentials_required
def manage_wordpress_instances(request, conn):
    """Create and delete wordpress instances."""
    if request.method == 'POST':
        if 'run_instance' in request.POST:
            conn.run_instances('ami-b056dad0', security_groups=['wordpressdemo'])
        elif 'terminate_instance' in request.POST:
            conn.terminate_instances([request.POST['instance_id']])

        return HttpResponseRedirect(reverse('manage-instances'))

    # We're interested in the list of all instances, regardless of which
    # reservation they belong to.
    reservations = conn.get_all_instances()
    instances = []
    map(instances.extend, [r.instances for r in reservations])

    # Return JSON if it was requested, otherwise render the template.
    if request.META.get('HTTP_ACCEPT') == 'application/json':
        data = {
            'instances': [
                dict(id=i.id, state=i.state, dns=i.public_dns_name) for i in instances
            ],
        }
        return JsonResponse(data)

    return render(request, 'aws-instances.html', dict(instances=instances))
