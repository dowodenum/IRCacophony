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
# use debug = True and give a debugger nickname if you want
# a message each time a sound is triggered.

import asyncio
import bottom
import json
import simpleaudio as sa

with open('sounds.json', 'r') as file:
    sounds = json.load(file)
file.close()

host = 'your.server.here'
port = 6697
ssl = True
username = 'listenbot'  # The name of the bot that listens
irc_password = ""
channel = "#spamsounds"

listento = 'listenbot'  # The name of the bot being listened to (can be the same as username, for use w/ bouncers)
delimiter = ""

debug = False
debugger = "dowodenum"

bot = bottom.Client(host=host, port=port, ssl=ssl)


@bot.on('CLIENT_CONNECT')
async def connect(**kwargs):
    bot.send("NICK", nick=username)
    bot.send("USER", user=username, realname='')
    if irc_password is not None:
        bot.send("PASS", password=irc_password)

    done, pending = await asyncio.wait(
        [bot.wait("RPL_ENDOFMOTD"),
            bot.wait("ERR_NOMOTD")],
        loop=bot.loop,
        return_when=asyncio.FIRST_COMPLETED
    )
    bot.send("JOIN", channel=channel)


@bot.on('PRIVMSG')
def respond(nick, target, message, **kwargs):
    if target == channel:
        if nick == listento:
            if delimiter is not None:
                if delimiter in message:
                    msg_split = message.split(delimiter)
            else:
                msg_split = [message] + [" "]
            for key in sounds.keys():
                if key in msg_split[0]:
                    if debug:
                        debug_output = "Triggered by: " + msg_split[0][:-1] + '- ' + "Playing " + sounds[key]
                        bot.send("PRIVMSG", target=debugger, message=debug_output)
                    wave_obj = sa.WaveObject.from_wave_file("./sounds/" + sounds[key])
                    play_obj = wave_obj.play()
                    play_obj.wait_done()


bot.loop.create_task(bot.connect())
bot.loop.run_forever()
