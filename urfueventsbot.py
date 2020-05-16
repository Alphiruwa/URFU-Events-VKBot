#! /usr/bin/env python
# -*- coding: utf-8 -*-

import vk_api
import pymysql
import time
import json

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

vk = vk_api.VkApi(token='199645f330de1d079a2c0602dac55163c593fd9106d4873265c3b5f31221f4f58eef5ec0c6b6838a01e93', api_version=5.95)

db = pymysql.connect('localhost', 'unodoscuattro', 'unodoscuattro', 'urfuevents')
db.autocommit(True)

def id_is_not_exist(db, userid):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_users WHERE id='+str(userid))
    check = cur.fetchall()
    if check == (): return True
    return False

def get_user_status(db,userid):
    cur = db.cursor()
    cur.execute('SELECT status FROM urfuevents_users WHERE id='+str(userid))
    userstatus = cur.fetchall()[0][0]
    return userstatus

def get_user_info(db, userid):  
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_users WHERE id='+str(userid))
    userdata = cur.fetchall()[0]
    userfio = userdata[1]
    usergroup = userdata[2]
    userspeciality =userdata[3]
    userinfo = [userfio, usergroup, userspeciality]
    return userinfo

def get_user_team(db, userid):
    cur = db.cursor()
    cur.execute('SELECT team FROM urfuevents_users WHERE id='+str(userid))
    userteam = cur.fetchall()[0][0]
    return userteam

def get_teams(db):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_teams WHERE 1')
    teams = cur.fetchall()
    teamlist = 'Чтобы присоединиться к команде, отправь её номер в ответ!\n\n'
    for team in teams:
    	teamlist += '\n\n' + str(team[0]) + '. ' + team[1] + ' [' + str(team[5]) + '/' + str(team[6]) + '] \n' 
    	teamlist += 'Мероприятие: ' + team[2] + '\n'
    	leaderinfo = get_user_info(db, team[4])
    	teamlist += 'Капитан: ' + leaderinfo[0] + ' (' + leaderinfo[1] + '; ' + leaderinfo[2] + ') vk.com/id' + team[4] + '\n'
    	teamlist += 'Требования к участникам: ' + team[3]
    return teamlist

def get_events(db):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_events WHERE 1')
    events = cur.fetchall()
    eventlist = 'Чтобы добавить в этот список своё мероприятие, свяжись с администрацией!\n\n'
    for event in events:
        eventlist += str(event[0]) + '. ' + event[1] + ' — ' + event[2] + '\n'
    return eventlist

def change_user_status(db, userid, value):
    cur = db.cursor()
    cur.execute('UPDATE urfuevents_users SET status = "'+value+'" WHERE id='+str(userid))
    
def change_user_info(db, userid, column, value):
    cur = db.cursor()
    cur.execute('UPDATE urfuevents_users SET '+column+' = "'+value+'" WHERE id='+str(userid))
	

def reset_info(db, userid):
    cur = db.cursor()
    cur.execute('UPDATE urfuevents_users SET fio="" WHERE id='+str(userid))
    cur.execute('UPDATE urfuevents_users SET studygroup="" WHERE id='+str(userid))
    cur.execute('UPDATE urfuevents_users SET speciality="" WHERE id='+str(userid))
    cur.execute('UPDATE urfuevents_users SET status = "register1" WHERE id='+str(userid))

startmessage0 = 'Прежде чем найти команду на мероприятия, расскажи немного о себе!'
startmessage1 = 'Для начала введи свои фамилию, имя и отчество! Эти данные нужны для того, чтобы капитан команды мог записать тебя на мероприятие!'
startmessage2 = 'Отлично, теперь назови свою академическую группу, например: "РИ-190012"'
startmessage3 = 'И последний шаг: назови своё направление и курс, например: "Программная Инженерия, 1 курс"'
startmessage4 = 'Регистрация завершена!'
mainbutton0_1 = 'Найти команду'
mainbutton0_2 = 'Покинуть команду'
mainbutton1 = 'Организовать свою команду'
mainbutton2 = 'Доступные мероприятия'
mainbutton3 = 'Обновить информацию о себе'
unknownmessage = 'Я плохо понимаю человеческий, давай действовать по инструкции!'
resetmessage = 'Твои данные были успешно сброшены! Теперь давай заполним их заново!'
    
def get_button(label, color, payload=""):
    return {
        'action': {
            'type': 'text',
            'payload': json.dumps(payload),
            'label': label,
        },
        'color': color
    }

keyboard_main1 = {
    'one_time': False,
    'buttons':
    [
        [get_button(label=mainbutton0_1, color='positive')],
        [get_button(label=mainbutton1, color='positive')],
        [get_button(label=mainbutton2, color='positive')],
        [get_button(label=mainbutton3, color='primary')]
    ]
}
keyboard_main2 = {
    'one_time': True,
    'buttons':
    [
        [get_button(label=mainbutton0_2, color='negative')],
        [get_button(label=mainbutton1, color='positive')],
        [get_button(label=mainbutton2, color='positive')],
        [get_button(label=mainbutton3, color='primary')]
    ]
}
back_key = {
    'one_time': True,
    'buttons':
    [
        [get_button(label='Вернуться обратно', color='primary')]
    ]
}
keyboard_main1 = json.dumps(keyboard_main1, ensure_ascii=False).encode('utf-8')
keyboard_main1 = str(keyboard_main1.decode('utf-8'))

while True:
    messages = vk.method('messages.getConversations', {'offset':0, 'count':20, 'filter':'unread'})
    if messages['count'] > 0:
        id = messages['items'][0]['last_message']['from_id']
        body = messages['items'][0]['last_message']['text']
        
        if id_is_not_exist(db, id):
            cur = db.cursor()
            cur.execute('INSERT INTO urfuevents_users SET id = '+str(id)+', fio = "", studygroup = "", speciality = "", team = "", status = ""')
            cur.close()
 	
        user_info = get_user_info(db, id)
        user_status = get_user_status(db, id)
        user_team = get_user_team(db, id)
	 
 
        # Регистрация
        if user_status == '':
            vk.method('messages.send', {'peer_id':id, 'message':startmessage0, 'random_id':''})
            change_user_status(db, id, 'register1')
            vk.method('messages.send', {'peer_id':id, 'message':startmessage1, 'random_id':''})
        if user_status == 'register1':
            change_user_info(db, id, 'fio', body)
            change_user_status(db, id, 'register2')
            vk.method('messages.send', {'peer_id':id, 'message':startmessage2, 'random_id':''})  
        if user_status == 'register2':
            change_user_info(db, id, 'studygroup', body)
            change_user_status(db, id, 'register3')
            vk.method('messages.send', {'peer_id':id, 'message':startmessage3, 'random_id':''})
        if user_status == 'register3':
            change_user_info(db, id, 'speciality', body)
            change_user_status(db, id, 'mainpage')
            vk.method('messages.send', {'peer_id':id, 'message':startmessage4, 'keyboard': keyboard_main1, 'random_id':''})
         
        # Главное меню
        if user_status == 'mainpage':               
            if body.lower() == mainbutton0_1.lower():
                vk.method('messages.send', {'peer_id':id, 'message':get_teams(db), 'random_id':''})            
            elif body.lower() == mainbutton1.lower():
                vk.method('messages.send', {'peer_id':id, 'message':'*заполнение информации о команде т.е. выбор мероприятия и требования к участникам*', 'random_id':''}) 
            elif body.lower() == mainbutton2.lower():
                vk.method('messages.send', {'peer_id':id, 'message':get_events(db), 'random_id':''})              
            elif body.lower() == mainbutton3.lower():
                vk.method('messages.send', {'peer_id':id, 'message':resetmessage, 'random_id':''})
                reset_info(db,id)
                vk.method('messages.send', {'peer_id':id, 'message':startmessage1, 'random_id':''})
            else:
                 vk.method('messages.send', {'peer_id':id, 'message':unknownmessage, 'random_id':''})

    time.sleep(1)
