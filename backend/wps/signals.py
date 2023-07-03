import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Permit

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Permit)
def permit_post_save(sender, instance, created, **kwargs):
    """
        Create PDF for the permit if not already created.
        Send e-mail if created.
    """

    if created:
        # Send email
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            settings.CHANNEL_NAME_PERMITS, {
                'type': 'email_new_permit',
                'data': {
                    'submitted_on': instance.submitted_on.strftime('%d.%m.%Y %H:%M'),
                    'submitted_by': {
                        'name': instance.submitted_by.full_name,
                        'email': instance.submitted_by.email
                    },
                    'operator_name': instance.operator_name
                }
            })

    if not instance.pdf:
        # send task to worker
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            settings.CHANNEL_NAME_PERMITS, {'type': 'create_pdf', 'data': {'obj_id': instance.id}})
