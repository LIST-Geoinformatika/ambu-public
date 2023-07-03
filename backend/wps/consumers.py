import io
import logging
import os

from channels.generic.websocket import SyncConsumer
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import get_template
from xhtml2pdf import pisa

from .models import Permit

logger = logging.getLogger(__name__)


class PermitConsumer(SyncConsumer):

    def get_pdf_context_data(self, obj):
        abstraction_points = []
        discharge_points = []

        for ap in obj.abstraction_points.all():
            wc = ap.water_body
            abstraction_points.append({
                'id': ap.id,
                'coords': list(ap.geom.coords),
                'identifier': ap.identifier,
                'watercourse': {
                    'wb_code': wc.wb_code if wc else '-',
                    'name': wc.name if wc else '-'
                },
                'sub_basin': ap.subbasin.name if ap.subbasin else '-'
            })

        for dp in obj.discharge_points.all():
            wc = ap.water_body
            discharge_points.append({
                'id': dp.id,
                'coords': list(dp.geom.coords),
                'watercourse': {
                    'wb_code': wc.wb_code if wc else '-',
                    'name': wc.name if wc else '-'
                },
                'sub_basin': dp.subbasin.name if dp.subbasin else '-'
            })

        context = {
            'id': obj.id,
            'permit_uid': obj.uid,
            'submitted_by': {
                'full_name': obj.submitted_by.full_name,
                'email': obj.submitted_by.email
            },
            'operator_name': obj.operator_name,
            'validated_by': obj.validated_by.full_name if obj.validated_by else '-',
            'validated_on': obj.validated_on.strftime('%d.%m.%Y') if obj.validated_on else '-',
            'status': obj.status,
            'water_use_sector': obj.water_use_sector.name if obj.water_use_sector else '-',
            'nace_code': obj.nace_code.code if obj.nace_code else '-',
            'nace_description': obj.nace_code.description if obj.nace_code else '',
            'abstraction_points': abstraction_points,
            'discharge_points': discharge_points
        }

        return context

    def create_pdf(self, message):
        data = message['data']
        obj = Permit.objects.get(pk=data['obj_id'])

        # prepare output dir
        pdf_fname = 'permit.pdf'
        relative_path_pdf = os.path.join(str(obj.uid), pdf_fname)
        fpath = os.path.join(settings.DATA_DIR, relative_path_pdf)
        dirpath = os.path.dirname(fpath)

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        # define context dict for template
        context = self.get_pdf_context_data(obj)

        # render html template with defined context
        template = get_template('permit_pdf.html')
        html = template.render(context)
        result = io.BytesIO()

        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

        if pdf.err:
            return None

        with open(fpath, "wb") as f:
            f.write(result.getvalue())

        obj.pdf.name = relative_path_pdf
        obj.save()

    def email_permit_status_update(self, message):
        data = message['data']
        obj = Permit.objects.get(pk=data['obj_id'])

        # send e-mail
        subject = "Permit Application - status update"
        message = (
            "Permit application with UID: {} has been validated.\n\n"
            "Status: {}\n\nValidated on:{}\nValidated by: {}".format(
                str(obj.uid), obj.status.upper(), obj.validated_on.strftime('%d.%m.%Y'), obj.validated_by.full_name)
        )

        if obj.remark:
            message += ("\n\nRemark: {}".format(obj.remark))

        from_email = settings.DEFAULT_FROM_EMAIL

        try:
            send_mail(subject, message, from_email, [obj.submitted_by.email])
        except BadHeaderError:
            logger.error("E-mail sending failed. Invalid header found.")
            return None

    def email_new_permit(self, message):
        data = message['data']
        submitted_by = data['submitted_by']
        submitted_on = data['submitted_on']
        operator_name = data['operator_name']

        from_email = settings.DEFAULT_FROM_EMAIL

        # send e-mail
        subject_for_user = "AMBU - Water Permit Application"
        message_to_user = (
            "Dear {},\n\n"
            "Thank you for submitting your water permit request through our app. "
            "We have received your application and it will be reviewed by our team.\n"
            "You will receive an email notification once the permit is validated.\n\n"
            "Best regards,\nAMBU Team".format(submitted_by['name'])
        )

        subject_for_admin = "Water Permit Request - Review Required"
        message_to_admin = (
            "A water permit request has been submitted via WPS web app and requires your review.\n\n"
            "Submitted by: {full_name} ({email})\nOperator name: {operator}\n"
            "Submitted on: {dt}\nURL for review: -".format(
                full_name=submitted_by['name'],
                email=submitted_by['email'],
                operator=operator_name,
                dt=submitted_on
            )
        )

        try:
            # send mail to user
            send_mail(subject_for_user, message_to_user, from_email, [submitted_by['email']])
            # send mail to admin
            send_mail(subject_for_admin, message_to_admin, from_email, [settings.ADMIN_EMAIL])

        except BadHeaderError:
            logger.error("E-mail sending failed. Invalid header found.")
            return None
