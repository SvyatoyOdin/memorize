import os
from dotenv import load_dotenv
from log import append_bot_operation_data, append_exception_data
from telegram_api import Bot
from user import User


load_dotenv()
URL = f'https://api.telegram.org/bot{os.getenv("token")}'
CHAT_ID = int(os.getenv("chat_id"))


def main():
    bot = Bot(url=URL, chat_id=CHAT_ID)
    user = User(bot=bot)
    
    commands = [
        {"add": "add a new sentence"},
        {"delete": "delete a sentence"},
        {"change": "change sentence"}
        ]
    bot.set_my_commands(commands)

    while True:
        if not user.is_time_to_sleep():
            user.ask_for_sentence_value()

        new_message = user.user_has_sent_a_new_massage()
        if new_message:
            message_text = new_message["message"]["text"]
            if message_text == "/add":
                user.append_a_new_sentence()
            elif message_text == "/change":
                user.change_sentence_to_remember()
            elif message_text == "/delete":
                user.delete_sentence()
            else:
                bot.send_message("I don't understand")


if __name__ == '__main__':
    try:
        append_bot_operation_data("BOT STARTED")
        main()
        append_bot_operation_data("BOT HAS STOPPED SUCCESSFUL")
    except KeyboardInterrupt:
        append_bot_operation_data("BOT HAS STOPPED SUCCESSFUL")
    except BaseException as ex:
        exception_number = append_exception_data(ex)
        append_bot_operation_data(type_data="BOT HAS STOPPED UNSUCCESSFUL",
                                  data=f"{ex.__str__()}; EXCEPTION NUMBER - {exception_number}")
