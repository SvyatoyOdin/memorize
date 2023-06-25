#  Program for memorizing 

## You need this program if:
You want to learn a language or memorize your friend’s birthday or anything else you want
to remember, you probably need this program.

## How this program works:
You add that you want to remember, in the format: "sentence : values", examples: brother’s birthday : 24 March, or 节目 : program. The program will send messages every hour(short of 12 hours and up to 10:00 hour) with a question: what mean is this sentence: sentence wich you added. You must answer correctly 15 times in a row, otherwise the score will be reduced to 0. If you answer correctly 15 times in a row, this sentence will be deleted. The program has 2 list of offers, 1 (learning) from which are randomly taken sentences that will be sent, 2 (queue) that are waiting for their turn. In the first list only 5 sentences, if the sentence is deleted, it will be replaced from the second list 

## What you need to start useing this program:
Program only for one person. In addition, it is necessary to create a telegram bot so that the program can have an interface. After you create your bot, you need to take its marker and paste it into the file. env (you need to create .env in the program folder), the same thing you should know your telegram chat_id and paste it into the file . env also.

### how must look file .env:
```
token=<<YOUR TOKEN>>
chat_id=<<YOUR CHAT ID>>
```


