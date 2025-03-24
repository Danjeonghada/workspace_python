# pip install python-telegram-bot==13.11

API_KEY = '7958231340:AAEXkxZvSYkv-SX-5Aqf7FbVQV-TkGAc-kM'
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters, CommandHandler
import os
import time
updater = Updater(token=API_KEY, use_context=True)

def fn_start(update, context):
    # 키보드 버튼
    keyboard = [
        [InlineKeyboardButton('button 1', callback_data='1')]
       ,[InlineKeyboardButton('button 2', callback_data='2')]
       ,[InlineKeyboardButton('button 3', callback_data='3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('choose one option:', reply_markup=reply_markup)


def fn_button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'행운의 로또 번호 {query.data}개:')

def echo(update, context):
    user_id = update.effective_chat.id
    user_msg = update.message.text
    context.bot.send_message(chat_id=user_id, text=user_msg)

def diary(update, context):
    user_id = update.effective_chat.id
    user_msg = update.message.text
    with open('my_diary.txt', 'a', encoding='utf-8') as f:
        f.write(user_msg.replace('/diary', '').strip())
        f.write('\n')
    context.bot.send_message(chat_id=user_id, text='다이어리 작성.')

def save_photo(update, context):
    # 1. 폴더 체크
    img_dir = './myimg'
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    # 2. 저장 이름
    filename = time.strftime('%Y%m%d%H%M%S') + '.png'
    img_path = os.path.join(img_dir, filename)
    # 3. 저장
    photo_id = update.message.photo[-1].file_id
    photo_file = context.bot.getFile(photo_id)
    photo_file.download(img_path)
    update.message.reply_text('photo saved')

def get_photo(update, context):
    img_path = ('./고래상어/0.png')
    user_id = update.effective_chat.id
    context.bot.send_photo(chat_id=user_id, photo=open(img_path, 'rb'))


# 로또 출력

# 사진 가져오기
updater.dispatcher.add_handler(CommandHandler('face', get_photo))

# 버튼
start_handler = CommandHandler('start', fn_start)
updater.dispatcher.add_handler(start_handler)
updater.dispatcher.add_handler(CallbackQueryHandler(fn_button))

# 사진 저장 기능 추가
photo_handler = MessageHandler(Filters.photo, save_photo)
updater.dispatcher.add_handler(photo_handler)

# 다이어리 기능 추가
diary_handler = CommandHandler('diary', diary)
updater.dispatcher.add_handler(diary_handler)

# 응답 함수 등록
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
updater.dispatcher.add_handler(echo_handler)
print("bot 스타트")
updater.start_polling()
updater.idle()