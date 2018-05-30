from charms.reactive import (
    when_all,
    when_any,
    when_not,
    toggle_flag,
    clear_flag,
)
from charms.reactive.relations import endpoint_from_name

from charms import layer


@when_any('config.changed.credentials')
def update_creds():
    clear_flag('charm.azure.creds.set')


@when_not('charm.azure.creds.set')
def get_creds():
    toggle_flag('charm.azure.creds.set', layer.azure.get_credentials())


@when_all('snap.installed.google-cloud-sdk',
          'charm.azure.creds.set')
@when_not('endpoint.azure.requests-pending')
def no_requests():
    layer.azure.cleanup()
    layer.status.active('ready')


@when_all('snap.installed.google-cloud-sdk',
          'charm.azure.creds.set',
          'endpoint.azure.requests-pending')
def handle_requests():
    azure = endpoint_from_name('azure')
    for request in azure.requests:
        layer.status.maintenance('granting request for {}'.format(
            request.unit_name))
        if not request.has_credentials:
            creds = layer.azure.create_account_key(
                request.model_uuid,
                request.application_name,
                request.relation_id)
            request.set_credentials(creds)
        if request.instance_labels:
            layer.azure.label_instance(
                request.instance,
                request.zone,
                request.instance_labels)
        if request.requested_instance_inspection:
            layer.azure.enable_instance_inspection(
                request.model_uuid,
                request.application_name)
        if request.requested_network_management:
            layer.azure.enable_network_management(
                request.model_uuid,
                request.application_name)
        if request.requested_security_management:
            layer.azure.enable_security_management(
                request.model_uuid,
                request.application_name)
        if request.requested_block_storage_management:
            layer.azure.enable_block_storage_management(
                request.model_uuid,
                request.application_name)
        if request.requested_dns_management:
            layer.azure.enable_dns_management(
                request.model_uuid,
                request.application_name)
        if request.requested_object_storage_access:
            layer.azure.enable_object_storage_access(
                request.model_uuid,
                request.application_name)
        if request.requested_object_storage_management:
            layer.azure.enable_object_storage_management(
                request.model_uuid,
                request.application_name)
        layer.azure.log('Finished request for {}'.format(request.unit_name))
    azure.mark_completed()