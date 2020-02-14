import telebot
import time
from config import Config

config = Config()
bot = telebot.TeleBot(config.token)
reports = {}

class Message:
    # contains methods that return string of message

    def greeting(self):
        greeting = 'Привет! Этот бот служит для того, чтобы собрать все баг-репорты от Dino 3d.'
        return greeting

    def helping(self):
        mess = 'Команды бота: \n/info - Информация о боте \n/read_feedback - читает новые баг-репорты(доступна только админу) \n/send_feedback - отправляет новый баг-репорт \n/help - помощь'
        return mess

class Report:
    def __init__(self, id, username, date, text):
        self.id = id # this need for method which will ban user for not appropriate behaviour
        self.username = username
        self.date = date
        self.text = text
        self.photo = None
    
    def get_id(self):
        return self.id
    
    def get_username(self):
        return self.username
    
    def get_date(self):
        return self.date
    
    def get_text(self):
        return self.text

    def get_photo(self):
        return self.photo
    

messages = Message()


@bot.message_handler(commands=['start', 'info'])
def start_message(message):
    bot.send_message(message.chat.id, messages.greeting())

@bot.message_handler(commands=['read_feedback'])
def read_feedback(message):
    if message.chat.id != config.admin_id:
        bot.send_message(message.chat.id, 'Access denied')
    else:
        if bool(reports):
            for report, value in reports.items():
                caption = '<b>От кого:</b> @{} \n<b>Дата:</b> {} \n<b>Сообщение:</b> {} \n\n'.format( value.get_username(), time.strftime("%D %H:%M:%S", time.localtime(value.get_date())), value.get_text())
                bot.send_photo(config.admin_id, value.get_photo(), parse_mode='HTML', caption=caption)
            reports.clear()
        else:
            bot.send_message(config.admin_id, 'Пока нет новых баг репортов')

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, messages.helping())


@bot.message_handler(commands=['send_feedback'], content_types=['text', 'sticker', 'photo', 'voice', 'video_note', 'document'])
def accept_report(message):
    if message.chat.id not in reports.keys():
        msg = bot.reply_to(message, 'Отправьте описание вашей ошибки. В сообщении должно быть тип вашего компа(ПК, ноутбук, Мак), ваш браузер(хром, сафари и т.д)')
        bot.register_next_step_handler(msg, process_description_step)
    else:
        bot.send_message(message.chat.id, 'Пока ваш багрепорт не прочитают, вы не сможете отправить новый')
        return

def process_description_step(message):
    if not message.content_type == 'text':
        msg = bot.reply_to(message, 'Должен быть текст, а не иное. Отправьте описание вашей ошибки')
        bot.register_next_step_handler(msg, process_description_step)
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    date = message.date
    text = message.text

    report = Report(user_id, username, date, text)
    reports[chat_id] = report
    msg = bot.reply_to(message, 'Хорошо. Отправьте фото вашей консоли(она открывается при нажатии на кнопку f12)')

    bot.register_next_step_handler(msg, process_photo_step)
    
def process_photo_step(message):
    if not message.content_type == 'photo':
        msg = bot.reply_to(message, 'Должно быть фото, а не иное. Отправьте фото')
        bot.register_next_step_handler(msg, process_photo_step)
        return
    photo = message.photo[-1].file_id
    report = reports[message.chat.id]
    report.photo = photo
    bot.send_message(message.chat.id, 'Спасибо за ваш багрепорт!')
    bot.send_message(config.admin_id, 'Новый багрепорт!')

    

bot.polling(none_stop=True)