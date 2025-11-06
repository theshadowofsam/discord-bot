from discord import Message
from multiprocessing import Queue
import datetime
import os

class _Msg():
    def __init__(self, message: Message):
        self.id         =   f'{message.id}'
        self.author     =   f'{message.author}'
        self.author_id  =   f'{message.author.id}'
        self.content    =   f'{message.content}'
        self.guild      =   f'{message.guild.name}'
        self.guild_id   =   f'{message.guild.id}'
        self.channel    =   f'{message.channel.name}'
        self.channel_id =   f'{message.channel.id}'
        self.timestamp  =   f'{message.created_at}'
        self.sysTime    =   f'{datetime.datetime.now()}'
        self.text       =   ''


class _MsgHandler():
    def constructWrite(self, message: _Msg):
        message.text    +=  f'ID: {message.id}\n'
        message.text    +=  f'Guild\\Channel: {message.guild}\\{message.channel}, {message.guild_id}\\{message.channel_id}\n'
        message.text    +=  f'Author: {message.author}\n'
        message.text    +=  f'Content: {message.content}\n'
        message.text    +=  f'Timestamp: {message.timestamp}\n'
        message.text    +=  f'Systime: {message.sysTime}\n'
        message.text    +=  f'\n'
        return message.text


class WriteThread():
    def __init__(self, dir, file):
        self.queue_     =   Queue(maxsize=0)
        self.handler    =   _MsgHandler()
        self.running    =   True
        self.Dir = dir
        self.File = file

    def emplace(self, message):
        self.queue_.put_nowait(message)
        return 0

    def writeFile(self, message: _Msg):
        p_ = self.Dir + message.guild + '\\' + message.channel + "\\"
        toLog = self.handler.constructWrite(message)
        try:
            with open(p_ + self.File, "a", encoding='utf-8') as fd:
                fd.write(toLog)
        except FileNotFoundError as e:
            os.makedirs(p_, exist_ok=True)
            with open(p_ + self.File, "a", encoding='utf-8') as fd:
                fd.write(toLog)

    def close(self):
        with open("C:\\temp\\JesterMk2\\log.txt", "a", encoding='utf-8') as fd:
            fd.write(
                f"Bot Closed!\n"
                f"Systime: {datetime.datetime.now()}\n"
                f"\n"
            )
        return 0

    def logMsg(self, message):
        if message == 'CODE_STOP':
            self.running = False
            self.close()
            return 0
        self.writeFile(message)
        return 0

    def run(self):
        while self.running:
            self.logMsg(self.queue_.get(block=True))
        return 0