from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.manage_wordpress_instances, name='manage-instances'),
    url(r'^credentials/$', views.capture_aws_credentials, name='aws-credentials'),
]
