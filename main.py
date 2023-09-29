#!/usr/bin/env python

import uiautomator2 as u2
from datetime import datetime
import threading
import time

d = u2.connect()

# Global variables
notifiy_message = """
Welocme，這裡是 %s 的家
我是最喜歡跟大家聊天的 %s 
⁽⁽⁽٩(๑˃̶͈̀ ᗨ ˂̶͈́)۶⁾⁾

DotDot 是一個小小小朋友，可能會犯一些小錯誤～
希望大家多多寬待♡(>ᴗ•)
現在時間是: %s
"""

welcome_message = """
ʕº̫͡ºʔ boo, Hi %s
Welcome Welcome 
這裡是 %s 的家，希望你會喜歡%s～～
"""

bot_name = 'DotDot'

## Global settings
records = dict()
message_queue = list()
manager_lock = False

def message_manager():
  global manager_lock
  global message_queue
  if manager_lock == True:
    return
  manager_lock = True
  try:
    msg = message_queue[0]

    send_msg( msg )
    del message_queue[0]
    manager_lock = False
    # check the message queue
    
    if len(message_queue) > 0:
      return message_manager()
  except:
    manager_lock = False

def notifiy_msg( hostname, botname ):
  # Get the current date and time
  now = datetime.now()
  # Format it as per your requirement
  formatted_date = now.strftime("%Y/%m/%d %H:%M:%S")
  return notifiy_message % (hostname, botname, formatted_date)

def welcome_msg( guestname, hostname, nickname ):
  return welcome_message % (guestname, hostname, nickname)

def send_msg( msg ):
  d.xpath('//*[@resource-id="com.wave.waveradio:id/commentEditText"]').click()
  d.send_keys(msg, clear=True)
  d.xpath('//*[@resource-id="com.wave.waveradio:id/sendButton"]').click()

def notify_5minute(hostname, botname):
  global message_queue
  while True:
    print("Send notification")
    msg = notifiy_msg(hostname, botname)
    message_queue.append(msg)
    message_manager()
    time.sleep(300)

def detect_guests(hostname, nickname):
  global message_queue
  while True:
    res = d.xpath('//*[@resource-id="com.wave.waveradio:id/notifyContentTexView"]')
    guests = [v.text.replace(" joined.", "") for v in res.all()]
    now = datetime.now().timestamp()
    final_list = []
    for name in guests:
      if name not in records or records[name] - 300 > now:
        records[name] = now
        final_list.append(name)
    
    if len(final_list) > 0:
      finallist = ','.join(final_list)
      msg = welcome_msg(finallist, hostname, nickname)
      message_queue.append(msg)
      print('Who\'s joined:', final_list)
      message_manager()

def detect_close_btn():
  while True:
    closeBtn = d.xpath('//*[@resource-id="com.wave.waveradio:id/closeBtn"]')
    if closeBtn.exists:
      closeBtn.click()
    time.sleep(5)

if __name__ == '__main__':
  rh = d.xpath('//*[@resource-id="com.wave.waveradio:id/headerView"]//android.widget.TextView[@resource-id="com.wave.waveradio:id/nameTextView"]')
  if not rh.exists:
    raise Exception('Can not found the room host')

  host_name = rh.get_text()
  nick_name = '把拔' if host_name == 'NodeDot' else host_name
  

  notify_every_5minute = threading.Thread(target=notify_5minute, args=(host_name, bot_name))
  notify_every_5minute.start()

  detect_new_guest = threading.Thread(target=detect_guests, args=(host_name, nick_name))
  detect_new_guest.start()