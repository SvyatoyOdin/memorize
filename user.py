import json
import datetime
import random
from telegram_api import Bot
from log import append_bot_operation_data
from json import JSONDecodeError



class User:

    def __init__(self, bot: Bot) -> None:
        updates = bot.get_updates()["result"]
        self.__time_send_message = datetime.datetime.now()
        self.__time_of_last_saved_message: int = updates[-1]["message"]["date"] if updates else 0
        self.__bot = bot

    @staticmethod
    def is_time_to_sleep() -> bool:
        """if time more the 11:00 hour or less 10:00, then funciot returns False,
         else retunrs True"""
        return datetime.datetime.now().hour < 10

    @staticmethod
    def get_sentence_and_value() -> tuple[str, str, int] | None:
        """returns sentence and value with their index from file json"""
        try:
            with open("sentences_to_remember.json", "r") as file:
                sentences_to_remember = json.load(file)["learning"]
                if sentences_to_remember:
                    num = len(sentences_to_remember)
                    index = random.randrange(0, num) if num else 0
                    sentence: str = sentences_to_remember[index][0][0]
                    value: str = sentences_to_remember[index][0][1]
                    return sentence, value, index
        except FileNotFoundError:
            pass

    def answer_right(self, index: int) -> None:
        self.__time_send_message = datetime.datetime.now() + datetime.timedelta(hours=1)
        hour_and_minute = self.__time_send_message.strftime("%H:%M")

        with open("sentences_to_remember.json", "r") as file:
            sentences_to_remember = json.load(file)
            count = sentences_to_remember["learning"][index][-1]["count"] + 1
            if count == 15:
                sentence, value = sentences_to_remember["queue"].pop(0)
                sentences_to_remember["learning"][index] = [(sentence, value), {"count": 0}]
                self.__bot.send_message(f"you has learned sentence\nNext messge sending time: <b>{hour_and_minute}</b>",
                                      parse_mode="HTML")
            else:
                sentences_to_remember["learning"][index][-1]["count"] = count
                self.__bot.send_message(f"Right, still {15 - count} times\nNext messge sending time: <b>{hour_and_minute}</b>",
                                      parse_mode="HTML")
  
        with open("sentences_to_remember.json", "w") as file:
            json.dump(sentences_to_remember, file, ensure_ascii=False, indent=4)
            
    def answer_wrong(self, index: int) -> None:
        with open("sentences_to_remember.json", "r") as file:
            sentences_to_remember = json.load(file)
            sentences_to_remember["learning"][index][-1]["count"] = 0

        with open("sentences_to_remember.json", "w") as file:
            json.dump(sentences_to_remember, file)

        self.__bot.send_message("Wrong, try again")

    def check_user_answer(self, index: int, value) -> None:
        while True:
            new_message = self.user_has_sent_a_new_massage()
            if new_message:
                text_of_the_message: str = new_message["message"]["text"]
                message_id: int = new_message["message"]["message_id"]

                if text_of_the_message.lower() == value.lower():
                    self.answer_right(index)
                    self.__bot.delete_message(message_id=message_id)
                    break
                else:
                    self.answer_wrong(index)
                    self.__bot.delete_message(message_id=message_id)


    def is_time_sending_message(self) -> bool:
        return self.__time_send_message <= datetime.datetime.now() 

    def ask_for_sentence_value(self) -> None:
        """ if time currently more, than time send message,
          then bot is asking user the sentence value"""
        if self.is_time_sending_message():
            sentence__value__index = self.get_sentence_and_value()

            if sentence__value__index:
                sentence, value, index = sentence__value__index

                self.__bot.send_message(f"What value is this sentence:\n<b>{sentence}</b>", parse_mode="HTML")
                self.check_user_answer(index, value)

    def user_has_sent_a_new_massage(self) -> dict | None:
        """if user has sent a new message, then function returns dict 
        with data of the last message else return None"""
        updates: dict = self.__bot.get_updates()["result"]
        if updates:
            time_of_the_last_message: int = updates[-1]["message"]["date"]
            text_of_the_last_message: str = updates[-1]["message"]["text"]

            if self.__time_of_last_saved_message < time_of_the_last_message:
                self.__time_of_last_saved_message = time_of_the_last_message
                append_bot_operation_data("BOT HAS GOT MESSAGE", text_of_the_last_message)
                return updates[-1]

    def get_a_new_sentence(self) -> tuple[str, str, int] | None:
        """"returns sentence, its value and message id"""
        while True:
            new_message = self.user_has_sent_a_new_massage()
            if new_message:
                message_text = new_message["message"]["text"]
                if " : " in message_text:
                    sentence,value = message_text.split(" : ")
                    return sentence, value, new_message["message"]["message_id"]
                else:
                    self.__bot.send_message("incorrect entry format, must be so: sentance <b>:</b> value", parse_mode="HTML")
                    break

    def append_a_new_sentence(self) -> None:
        """"append to file a new sentence to remember"""
        self.__bot.send_message("you can add a sentence")
        sentence__value__message_id = self.get_a_new_sentence()
        if sentence__value__message_id:
            sentence, value, message_id = sentence__value__message_id
            try:
                with open("sentences_to_remember.json", "r") as file:
                    sentence_to_remember: dict = json.load(file)
            except (FileNotFoundError, JSONDecodeError):
                sentence_to_remember = {}

            with open("sentences_to_remember.json", "w") as file:
                if sentence_to_remember:
                    if 5 >= len(sentence_to_remember["learning"]):
                        sentence_to_remember["learning"].append([(sentence, value), {"count": 0}])
                    else:
                        sentence_to_remember["queue"].append((sentence, value))

                    json.dump(sentence_to_remember, file, ensure_ascii=False, indent=4)
                else:
                    sentence_to_remember = {"learning": [((sentence, value), {"count": 0})], "queue": []}
                    json.dump(sentence_to_remember, file, ensure_ascii=False, indent=4)

            self.__bot.send_message("new sentence has been appended")
            self.__bot.delete_message(message_id=message_id)

            append_bot_operation_data("HAS ADD A NEW SENTENCE", f"sentence: {sentence}, value: {value}")
            print(f"HAS ADD A NEW SENTENCE, sentence: {sentence}, value: {value}")

    @staticmethod
    def check_for_availability_of_sentence(message_text: str) -> tuple[dict, str, int] | None:
        """if sentence is a available, then function returns tuple[sentences_to_remember, cloumn, index]
        or else it returns None"""
        with open("sentences_to_remember.json", "r") as file:
            sentences_to_remember: dict = json.load(file)       

        index = 0
        for sentences in sentences_to_remember["learning"]:
            if sentences[0][0].lower() == message_text.lower():
                return sentences_to_remember, "learning", index
            index += 1

        index = 0
        for sentences in sentences_to_remember["queue"]:
            if sentences[0].lower() == message_text.lower():
                return sentences_to_remember, "queue", index
            index += 0 

    def change_sentence_to_remember(self) -> None:
        self.__bot.send_message("write down sentence wich you wants to change")

        while True:
            new_message = self.user_has_sent_a_new_massage()
            if new_message:
                message_text: str = new_message["message"]["text"]
                sentences_to_remember__colomn__index = self.check_for_availability_of_sentence(message_text)

                if sentences_to_remember__colomn__index:
                    self.__bot.send_message("write down sentences value")
                    while True:
                        new_message = self.user_has_sent_a_new_massage()
                        if new_message:
                            sentences_to_remember, colomn, index = sentences_to_remember__colomn__index
                            sentences_to_remember[colomn][index][0]: str = new_message["message"]["text"]

                            if colomn == "learning":
                                sentences_to_remember[colomn][index][1]["count"] = 0
                                sentences_to_remember[colomn][index][0][1]: str = new_message["message"]["text"]
                            else:
                                sentences_to_remember[colomn][index][0]: str = new_message["message"]["text"]

                        
                            with open("sentences_to_remember.json", "w") as file:
                                json.dump(sentences_to_remember, file)

                            self.__bot.send_message(f"sentence has been chenged")
                            break
                    
                else:
                   self.__bot.send_message(f"sentence:\n{message_text}\n has not been found")
                   break
 
                        
    def delete_sentence(self) -> None:
       self.__bot.send_message("write down sentence wich you want to delete") 
       while True:
           new_message = self.user_has_sent_a_new_massage()
           if new_message:
               message_text = new_message["message"]["text"] 
               sentences_to_remember__colomn__index = self.check_for_availability_of_sentence(message_text)
               if sentences_to_remember__colomn__index:
                  sentences_to_remember, colomn, index = sentences_to_remember__colomn__index
                  sentence = sentences_to_remember[colomn].pop(index)

                  with open("sentences_to_remember.json", "w") as file:
                      json.dump(sentences_to_remember, file)      
                  self.__bot.send_message(f"sentence:\n{sentence}\nhas been deleted", parse_mode="HTML")
                  break
               else:
                   self.__bot.send_message(f"sentence:\n{message_text}\n has not been found")
                   break

                



                
            

            




