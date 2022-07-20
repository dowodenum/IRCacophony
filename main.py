###
# Kopyleft 2022 SirVo. All right unreserved.
###

# A framework for triggering sounds via IRC.
# Intended for use with valcanobacon/BoostBots

# Audio:
# Put WAV files in ./sounds/
# Define trigger words and filenames in ./sounds.json

# IRC:
# Give a host, port, SSL, password, username yadda yadda
# for the bot which will listen for trigger words.
# define debugger nicks in debuggers dict, and
# whether they're enabled/disabled, to receive
# a message when the bot initially connects, and
# each time a sound is triggered.

import asyncio
import bottom
import json
import simpleaudio as sa

with open('sounds.json', 'r') as file:
    sounds = json.load(file)
file.close()

host = 'my.l33t.vps'
port = 6969
ssl = False
username = 'bot'  # The name of the bot that listens
irc_password = ""
channel = "#testinshit"

listento = 'bot'  # The name of the bot being listened to (can be the same as above)
delimiter = "[podcast name]"

debuggers = {
    "SirVo": True,
    "SirVo2": False
}

bot = bottom.Client(host=host, port=port, ssl=ssl)


@bot.on('CLIENT_CONNECT')
async def connect(**kwargs):
    bot.send("NICK", nick=username)
    bot.send("USER", user=username, realname='')
    if irc_password is not None:
        bot.send("PASS", password=irc_password)

    _, pending = await asyncio.wait(
        [
            bot.wait("RPL_ENDOFMOTD"),
            bot.wait("ERR_NOMOTD")
        ],
        loop=bot.loop,
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel whichever waiter's event didn't come in.
    for future in pending:
        future.cancel()

    bot.send("JOIN", channel=channel)
    for debugger, isdebugging in debuggers.items():
        if isdebugging:
            bot.send("PRIVMSG", target=debugger, message="IRCacophony connected")


@bot.on("CLIENT_DISCONNECT")
async def reconnect(**kwargs):
    await asyncio.sleep(2, loop=bot.loop)
    bot.loop.create_task(bot.connect())

@bot.on("PING")
def keepalive(message, **kwargs):
    bot.send("PONG", message=message)

@bot.on('PRIVMSG')
def message(nick, target, message, **kwargs):
    if target == channel:
        if nick == listento:
            if delimiter is not None:
                if delimiter in message:
                    msg_split = message.split(delimiter)
                else:
                    return
            else:
                msg_split = [message] + [" "]
            for key in sounds.keys():
                if key in msg_split[0]:
                    for debugger, isdebugging in debuggers.items():
                        if isdebugging:
                            debug_output = "Triggered by: " + msg_split[0] + '- ' + "Playing " + sounds[key]
                            bot.send("PRIVMSG", target=debugger, message=debug_output)

                    wave_obj = sa.WaveObject.from_wave_file("./sounds/" + sounds[key])
                    play_obj = wave_obj.play()
                    play_obj.wait_done()


bot.loop.run_until_complete(bot.connect())
bot.loop.run_forever()
