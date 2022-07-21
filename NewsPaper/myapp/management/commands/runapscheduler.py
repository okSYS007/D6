import logging

from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from myapp.models import CategorySubscribers, User, Post

from datetime import date, timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

 
logger = logging.getLogger(__name__)
 
def sendWeekMail():

    startDay = date.today()+timedelta(days=-date.today().weekday())  #monday
    #startDay = date(2022, 7, 11)
    subscribersId = CategorySubscribers.objects.values('subscribers', 'category').order_by('subscribers')
    subsID = 0
    #Комментарий боли. Очень долго сидел с этой задачей т.к. НЕ ХОТЕЛ делать запросы в бд через цикл =(
    for subsData in subscribersId:
        #если это тот же пользователь
        if subsID != subsData['subscribers']:

            subsID = subsData['subscribers']
            SubsUser = User.objects.get(id = subsID)
            
            subsCategorys = subscribersId.filter(subscribers = subsID).values_list('category', flat=True)

            weekPosts = Post.objects.filter(creation_date__gt = startDay, category__in = subsCategorys)
    
            postInfo = []

            for post in weekPosts:
                postInfo.append(
                    {
                        'title': post.post_title,
                        'postUrl': str(post.id)
                    }
                )
               
            html_content = render_to_string( 
                'week_mailing.html',
                {
                    'userName': SubsUser.username,
                    'postInfo': postInfo
                }
            )
            msg = EmailMultiAlternatives(
                subject='Еженедельная рассылка',
                body='Новости за неделю', 
                from_email='ViacheslavDan803@gmail.com',
                to=[SubsUser.email] 
            )
            msg.attach_alternative(html_content, "text/html") 

            msg.send()

# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        scheduler.add_job(
            sendWeekMail,
            trigger=CronTrigger(day_of_week ="mon", hour="01", minute="00"),  # =) 01. что б не мешать работе delete_old_job_executions
            id="sendWeekMail", 
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'sendWeekMail'.")
 
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")