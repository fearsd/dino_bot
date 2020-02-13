import telebot
import time
from config import Config


config = Config()

bot = telebot.TeleBot(config.token)

reports = []
greeting = 'Привет! Этот бот служит для того, чтобы собрать все баг-репорты от Dino 3d. Убедительная просьба, писать свой отзыв в одном сообщении. От вас требуется: описание проблемы, тип устройства(ноутбук/ПК/Мак), кол-во ОЗУ, название браузера, ссылку на скриншот(lightshot, imgur) консоли f12 (опционально) '

@bot.message_handler(commands=['start', 'info'])
def start_message(message):
    bot.send_message(message.chat.id, greeting)

@bot.message_handler(commands=['read_feedback'])
def read_feedback(message):
    answer = ''
    if message.chat.id != config.admin_id:
        bot.send_message(message.chat.id, 'Access denied')
    else:
        try:
            for report in reports:
                one_rep = '<b>От кого:</b> @{} \n<b>Дата:</b> {} \n<b>Сообщение:</b> {} \n\n'.format(report['user_name'], time.strftime("%D %H:%M:%S", time.localtime(report['date'])), report['report_mess'])
                answer = answer + one_rep
            bot.send_message(config.admin_id, answer, parse_mode='HTML')
            reports.clear()
        except telebot.apihelper.ApiException:
            bot.send_message(config.admin_id, 'Пока нет новых баг репортов')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Команды бота: \n/info - Информация о боте \n/read_feedback - читает новые баг-репорты(доступна только админу) \n/help - помощь')


@bot.message_handler(content_types=['text', 'sticker', 'photo', 'voice', 'video_note', 'document'])
def accept_report(message):
    if message.content_type == 'text':
        bot.send_message(message.chat.id, 'Спасибо!')
        bot.send_message(config.admin_id, 'Новый баг репорт')
        reports.append({'user_name': message.from_user.username, 'date': message.date, 'report_mess': message.text})
    else:
        bot.send_message(message.chat.id, 'poshel nafig')

    

bot.polling(none_stop=True)