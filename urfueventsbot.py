#! /usr/bin/env python
# -*- coding: utf-8 -*-

import vk_api
import pymysql
import time
import json

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

vk = vk_api.VkApi(token='199645f330de1d079a2c0602dac55163c593fd9106d4873265c3b5f31221f4f58eef5ec0c6b6838a01e93', api_version=5.95)

db = pymysql.connect('localhost', 'unodoscuattro', 'unodoscuattro', 'urfuevents')

def get_user_status(db,userid):
    cur = db.cursor()
    cur.execute('SELECT status FROM urfuevents_users WHERE id='+str(userid))
    userstatus = cur.fetchall()
    return userstatus

def get_user_info(db, userid):  
    cur = db.cursor()
    cur.execute('SELECT fio FROM urfuevents_users WHERE id='+str(userid))
    userfio = cur.fetchall()
    cur.execute('SELECT studygroup FROM urfuevents_users WHERE id='+str(userid))
    usergroup = cur.fetchall()
    cur.execute('SELECT speciality FROM urfuevents_users WHERE id='+str(userid))
    userspeciality = cur.fetchall()
    userinfo = [userfio, usergroup, userspeciality]
    return userinfo

def get_user_team(db, userid):
    cur = db.cursor()
    cur.execute('SELECT team FROM urfuevents_users WHERE id='+str(userid))
    userteam = cur.fetchall()
    return userteam

def get_teams(db):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_teams WHERE 1')
    teams = cur.fetchall()
    teamlist = 'Чтобы присоединиться к команде, отправь её номер в ответ!\n'
    for team in teams:
        teamlist += team
        teamlist += '\n'
    return teamlist

def get_events(db):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_events WHERE 1')
    events = cur.fetchall()
    eventlist = 'Чтобы добавить в этот список своё мероприятие, свяжись с администрацией!\n'
    for event in events:
        eventlist += event
        eventlist += '\n'
    return eventlist

def reset_info(db, id):
    cur = db.cursor()

startmessage0 = 'Прежде чем найти команду на мероприятия, расскажи немного о себе!'
startmessage1 = 'Для начала введи свои фамилию, имя и отчество! Эти данные нужны для того, чтобы капитан команды мог записать тебя на мероприятие!'
startmessage2 = 'Отлично, теперь назови свою академическую группу, например: "РИ-190012"'
startmessage3 = 'И последний шаг: назови своё направление и курс, например: "Программная Инженерия, 1 курс"'
startmessage4 = 'Регистрация завершена!'
mainbutton0 = 'Найти команду'
mainbutton1 = 'Организовать свою команду'
mainbutton2 = 'Доступные мероприятия'
mainbutton3 = 'Обновить информацию о себе'
unknownmessage = 'Я плохо понимаю человеческий, давай действовать по инструкции!'
    
def get_button(label, color, payload=""):
    return {
        'action': {
            'type': 'text',
            'payload': json.dumps(payload),
            'label': label,
        },
        'color': color
    }

keyboard = {
    'one_time': False,
    'buttons':
    [
        [get_button(label=mainbutton0, color='positive')],
        [get_button(label=mainbutton1, color='positive')],
        [get_button(label=mainbutton2, color='positive')],
        [get_button(label=mainbutton3, color='primary')]
    ]
}
keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

while True:
    messages = vk.method('messages.getConversations', {'offset':0, 'count':20, 'filter':'unread'})
    if messages['count'] > 0:
        id = messages['items'][0]['last_message']['from_id']
        body = messages['items'][0]['last_message']['text']

        user_info = get_user_info(db, id)
        user_status = get_user_status(db, id)
        user_team = get_user_team(db, id)
        
        if user_status == '':
            if user_info[0] == '':
                vk.method('messages.send', {'peer_id':id, 'message':startmessage0, 'random_id':''})
                vk.method('messages.send', {'peer_id':id, 'message':startmessage1, 'random_id':''})
            if user_info[1] == '' and user_info[0] != '':
                vk.method('messages.send', {'peer_id':id, 'message':startmessage2, 'random_id':''})
            if user_info[2] == '' and user_info[1] != '' and user_info[0] != '':
                vk.method('messages.send', {'peer_id':id, 'message':startmessage3, 'random_id':''})
            if user_info[0] != '' and user_info[1] != '' and user_info[2] != '':
                vk.method('messages.send', {'peer_id':id, 'message':startmessage4, 'keyboard': keyboard, 'random_id':''})
            
        if user_status != '':               
            if body.lower() == mainbutton0.lower():
                vk.method('messages.send', {'peer_id':id, 'message':get_teams(db), 'random_id':''})            
            elif body.lower() == mainbutton1.lower():
                vk.method('messages.send', {'peer_id':id, 'message':'*заполнение информации о команде т.е. выбор мероприятия и требования к участникам*', 'random_id':''}) 
            elif body.lower() == mainbutton2.lower():
                vk.method('messages.send', {'peer_id':id, 'message':get_events(db), 'random_id':''})              
            elif body.lower() == mainbutton3.lower():
                vk.method('messages.send', {'peer_id':id, 'message':'*снова заполнение данных со старта*', 'random_id':''})
            else:
                 vk.method('messages.send', {'peer_id':id, 'message':unknownmessage, 'random_id':''})

    time.sleep(1)
