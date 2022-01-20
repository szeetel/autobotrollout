import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import datetime


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def alarm(context: CallbackContext) -> None:
    wednesday = 2
    friday = 4
    test_date = datetime.datetime.today()
    wed_delta = wednesday - test_date.weekday()
    fri_delta = friday - test_date.weekday()
    if wed_delta <= 0:
        wed_delta += 7
    if fri_delta <= 0:
        fri_delta += 7
    wed_res = test_date + datetime.timedelta(wed_delta)
    fri_res = test_date + datetime.timedelta(fri_delta)
    """Send the alarm message."""
    job = context.job
    q = '*BOXING TRAINING* @ DS8'
    answers = ['Wednesday 1900-2100 ' + str(wed_res)[:10], 'Friday 1900-2100 ' + str(fri_res)[:10]]
    context.bot.send_poll(job.context, question=q, options=answers, is_anonymous=False, allows_multiple_answers=True)


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)


def main() -> None:
    """Run bot."""
    updater = Updater("5047545312:AAF4oy9ZHPI8ebNvN2E6eCErvAQFvY9LUHs")
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()