import requests
import time


class Bot:
    """this class works with telegram API """
    def __init__(self, url: str, chat_id: int) -> None:
        self.url = url
        self.chat_id = chat_id

    def get_updates(self) -> dict:
        """returns messages data for last 24 hour"""
        response = requests.get(f"{self.url}/getUpdates")
        if response.status_code == 429:
            self.send_message("bot going to rest for 15 minut")
            time.sleep(900)
        elif response.status_code != 200:
            raise Exception(f"status code - {response.status_code}")
        time.sleep(1.5)
        return response.json()

    def send_message(self, text: str, parse_mode: str = None) -> None:
        """send message to user"""
        data = {"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode}
        requests.post(f"{self.url}/sendMessage", data=data)

    def delete_message(self, message_id: int) -> None:
        """"delete message user"""
        data = {"chat_id": self.chat_id, "message_id": message_id}
        requests.get(f"{self.url}/deleteMessage", data=data)

    def set_my_commands(self, commands: list[dict[str, str]]) -> None:
        """set commands for all
        commands format have to be:[
         ["command": "description"],
         ["command": "description"]j
         ]"""
        
        data = {"commands": []}

        for i in commands:
            for command, description in i.items():
                data["commands"].append({"command": command, "description": description})

        requests.post(f"{self.url}/setMyCommands", json=data)

    
