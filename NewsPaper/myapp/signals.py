from django.db.models.signals import post_delete, post_init
from django.dispatch import receiver # импортируем нужный декоратор
from django.core.mail import mail_managers, EmailMultiAlternatives 
from .models import Appointment

from django.template.loader import render_to_string
 
@receiver(post_delete, sender=Appointment)
def notify_managers_appointment_del(sender, instance, created, **kwargs):
   
    subject = f'Ув. {instance.userName}, Новость удаленна! '
 
    mail_managers(
        subject=subject,
        message=instance.text,
    )

@receiver(post_init, sender=Appointment)
def notify_followers_appointment_add(sender, instance, **kwargs):

    html_content = render_to_string( 
        'appointment_created.html',
        {
            'appointment': instance,
        }
    )

    msg = EmailMultiAlternatives(
        subject=f'{instance.title}',
        body=instance.text, #  это то же, что и message
        from_email='ViacheslavDan803@gmail.com',
        to=[instance.email], # это то же, что и recipients_list
    )
    msg.attach_alternative(html_content, "text/html") # добавляем html

    msg.send() # отсылаем