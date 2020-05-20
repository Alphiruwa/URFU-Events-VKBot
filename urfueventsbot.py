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

# Стандартные сообщения, чтобы потом не вводить их вручную 
startmessage0 = 'Прежде чем найти команду на мероприятия, расскажи немного о себе!'
startmessage1 = 'Для начала введи свои фамилию, имя и отчество! Эти данные нужны для того, чтобы капитан команды мог записать тебя на мероприятие!'
startmessage2 = 'Отлично, теперь назови свою академическую группу, например: "РИ-190012"'
startmessage3 = 'И последний шаг: назови своё направление и курс, например: "Программная Инженерия, 1 курс"'
startmessage4 = 'Регистрация завершена!'
mainbutton0 = 'Информация о себе'
mainbutton0_1 = 'Открыть список команд'
mainbutton0_2 = 'Покинуть команду'
mainbutton1 = 'Организовать свою команду'
disband_team_button = 'Распустить команду'
# mainbutton2 = 'Доступные мероприятия'
mainbutton3 = 'Обновить информацию о себе'
backbutton = 'Вернуться назад'
unknownmessage = 'Я плохо понимаю человеческий, давай действовать по инструкции!'
resetmessage = 'Твои данные были успешно сброшены! Теперь давай заполним их заново!'

# Все вспомогательные функции, которые используются в боте
def id_is_not_exist(db, userid):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_users WHERE id='+str(userid))
    check = cur.fetchall()
    if check == (): return True
    return False
    
def team_is_exist(db,team):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_teams WHERE name="'+team+'"')
    team = cur.fetchall()
    if team == (): return False
    return True

def is_user_leader_of_team(db, userid):
    team = get_user_team_info(db, id)
    if team[3] == str(userid): return True
    return False
    
def disband_team(db, userid):
    team = get_user_team(db, userid)
    cur = db.cursor()
    cur.execute('SELECT id FROM urfuevents_users WHERE team ="'+team+'"')
    members = cur.fetchall()
    for userid in members:
        delete_user_team(db, userid[0])
    cur.execute('DELETE FROM `urfuevents_teams` WHERE name="'+team+'"')    

def get_team_members_count(db, team):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_teams WHERE name="'+team+'"')
    team = cur.fetchall()[0]
    count = team[4]
    maxcount = team[5]
    memberscount = [count, maxcount]
    return memberscount

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
    userteam = cur.fetchall()
    if userteam == ():
        return ''
    return userteam[0][0]
    
def delete_user_team(db, userid):
    cur = db.cursor()
    cur.execute('UPDATE urfuevents_users SET team = "" WHERE id="'+str(userid)+'"')

def get_user_team_info(db, userid):
    cur = db.cursor()
    team_name = get_user_team(db, userid)
    cur.execute('SELECT * FROM urfuevents_teams WHERE name ="'+team_name+'"')
    team = cur.fetchall()[0]
    return team

def show_user_team_info(db, userid):
    team_name = get_user_team(db, userid)
    if team_name != '':
        update_members_count(db, team_name)
        cur = db.cursor()
        cur.execute('SELECT * FROM urfuevents_teams WHERE name ="'+team_name+'"')
        team = cur.fetchall()[0]
        team_info = '\n\n — Команда: ' + team[0] + ' [' + str(team[4]) + '/' + str(team[5]) + '] \n' 
        team_info += '— Мероприятие: ' +  team[1] + ' (' + team[6] +')' '\n'
        leader = get_user_info(db, team[3])
        team_info += '— Капитан: ' + leader[0] + ' (' + leader[1] + '; ' + leader[2] + ') https://vk.com/id' + team[3] + '\n'
        team_info += '— Требования к участникам: ' + team[2] 
        cur.execute('SELECT * FROM urfuevents_users WHERE team ="'+team_name+'"')
        team_members = cur.fetchall()
        team_info += '\n\n — Состав команды:\n'
        i = 0
        for member in team_members:
            i+=1
            team_info += str(i) +'. ' + member[1] + ' (' + member[2] + '; ' + member[3] + ') https://vk.com/id' + member[0] + '\n'
        return team_info
    else: return '\n\n— Вы не состоите в команде'

def get_teams(db):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_teams WHERE 1')
    teams = cur.fetchall()
    if teams == (): return 'В настоящий момент список команд пуст!'
    else:
        teamlist = 'Чтобы присоединиться к выбранной команде, отправь её название!\n\n'
        i = 0
        for team in teams:
            update_members_count(db, team[0])
            if team[4] == 0: 
                cur = db.cursor()
                cur.execute('DELETE FROM `urfuevents_teams` WHERE name="'+team[0]+'"') 
                cur.close()
            else:
                i+=1
                teamlist += '\n\n' + str(i) + '. ' + team[0] + ' [' + str(team[4]) + '/' + str(team[5]) + '] \n' 
                teamlist += '— Мероприятие: ' +  team[1] + ' (' + team[6] +')' '\n'
                leaderinfo = get_user_info(db, team[3])
                teamlist += '— Капитан: ' + leaderinfo[0] + ' (' + leaderinfo[1] + '; ' + leaderinfo[2] + ') https://vk.com/id' + team[3] + '\n'
                teamlist += '— Требования к участникам: ' + team[2]
        if teamlist == 'Чтобы присоединиться к выбранной команде, отправь её название!\n\n':
            return 'В настоящий момент список команд пуст!'
        return teamlist

#def get_events(db):
#    cur = db.cursor()
#    cur.execute('SELECT * FROM urfuevents_events WHERE 1')
#    events = cur.fetchall()
#    eventlist = '(Чтобы добавить в этот список своё мероприятие, свяжись с администрацией)\n\n'
#    for event in events:
#        eventlist += str(event[0]) + '. ' + event[1] + ' — ' + event[2] + '\n'
#    return eventlist

def change_user_status(db, userid, value):
    cur = db.cursor()
    cur.execute('UPDATE urfuevents_users SET status = "'+value+'" WHERE id='+str(userid))
    
def change_user_info(db, userid, column, value):
    cur = db.cursor()
    cur.execute('UPDATE urfuevents_users SET '+column+' = "'+value+'" WHERE id='+str(userid))
	
def update_members_count(db, team):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_users WHERE team ="'+team+'"')
    team_members = cur.fetchall()
    if team_members == (): count = 0
    else: count = len(team_members)
    cur.execute('UPDATE urfuevents_teams SET members = '+str(count)+' WHERE name="'+team+'"')

def reset_info(db, userid):
    cur = db.cursor()
    cur.execute('UPDATE urfuevents_users SET fio="" WHERE id='+str(userid))
    cur.execute('UPDATE urfuevents_users SET studygroup="" WHERE id='+str(userid))
    cur.execute('UPDATE urfuevents_users SET speciality="" WHERE id='+str(userid))
    cur.execute('UPDATE urfuevents_users SET status = "register1" WHERE id='+str(userid))
  
# Клавиатура пользователя  
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
    'one_time': True,
    'buttons':
    [
        [get_button(label=mainbutton0, color='primary')],
        [get_button(label=mainbutton0_1, color='positive')],
        [get_button(label=mainbutton1, color='positive')],
#       [get_button(label=mainbutton2, color='positive')],
        [get_button(label=mainbutton3, color='primary')]
    ]
}
keyboard_main2 = {
    'one_time': True,
    'buttons':
    [
        [get_button(label=mainbutton0, color='primary')],
        [get_button(label=mainbutton0_1, color='positive')],
        [get_button(label=mainbutton1, color='positive')],
#       [get_button(label=mainbutton2, color='positive')],
        [get_button(label=mainbutton0_2, color='negative')],
        [get_button(label=mainbutton3, color='primary')]
    ]
}

keyboard_leader = {
    'one_time': True,
    'buttons':
    [
        [get_button(label=mainbutton0, color='primary')],
        [get_button(label=mainbutton0_1, color='positive')],
        [get_button(label=mainbutton1, color='positive')],
#       [get_button(label=mainbutton2, color='positive')],
        [get_button(label=mainbutton0_2, color='negative')],
        [get_button(label=disband_team_button, color='negative')],
        [get_button(label=mainbutton3, color='primary')]
    ]
}

back_key = {
    'one_time': True,
    'buttons':
    [
        [get_button(label=backbutton, color='primary')]
    ]
}
keyboard_main1 = json.dumps(keyboard_main1, ensure_ascii=False).encode('utf-8')
keyboard_main1 = str(keyboard_main1.decode('utf-8'))
keyboard_main2 = json.dumps(keyboard_main2, ensure_ascii=False).encode('utf-8')
keyboard_main2 = str(keyboard_main2.decode('utf-8'))
keyboard_leader = json.dumps(keyboard_leader, ensure_ascii=False).encode('utf-8')
keyboard_leader = str(keyboard_leader.decode('utf-8'))
back_key = json.dumps(back_key, ensure_ascii=False).encode('utf-8')
back_key = str(back_key.decode('utf-8'))

# Само тело бота
while True:
    messages = vk.method('messages.getConversations', {'offset':0, 'count':20, 'filter':'unread'})
    if messages['count'] > 0:
        id = messages['items'][0]['last_message']['from_id']
        body = messages['items'][0]['last_message']['text'].replace('"', "").replace("'","")
        
        if id_is_not_exist(db, id):
            cur = db.cursor()
            cur.execute('INSERT INTO urfuevents_users SET id = '+str(id)+', fio = "", studygroup = "", speciality = "", team = "", status = ""')
            cur.close()
 	
        user_status = get_user_status(db, id)
        
        user_team = get_user_team(db, id)
        if user_team == '': keyboard = keyboard_main1
        else: 
            if is_user_leader_of_team(db, id):
                keyboard = keyboard_leader
            else: keyboard = keyboard_main2
 
        # Регистрация
        if user_status == '':
            vk.method('messages.send', {'peer_id':id, 'message':startmessage0, 'random_id':''})
            change_user_status(db, id, 'register1')
            vk.method('messages.send', {'peer_id':id, 'message':startmessage1, 'random_id':''})
        if user_status == 'register1':
            if body == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:
                change_user_info(db, id, 'fio', body)
                change_user_status(db, id, 'register2')
                vk.method('messages.send', {'peer_id':id, 'message':startmessage2, 'random_id':''})  
        if user_status == 'register2':
            if body == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                change_user_info(db, id, 'studygroup', body)
                change_user_status(db, id, 'register3')
                vk.method('messages.send', {'peer_id':id, 'message':startmessage3, 'random_id':''})
        if user_status == 'register3':
            if body == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                change_user_info(db, id, 'speciality', body)
                change_user_status(db, id, 'main_page')
                vk.method('messages.send', {'peer_id':id, 'message':startmessage4, 'keyboard': keyboard, 'random_id':''})
         
        # Главное меню
        if user_status == 'main_page':                   
            if body.lower() == mainbutton0_1.lower():
                vk.method('messages.send', {'peer_id':id, 'message':get_teams(db), 'keyboard': back_key, 'random_id':''}) 
                change_user_status(db, id, 'team_select')
            elif body.lower() == mainbutton0.lower():
                user_info = get_user_info(db, id)
                info = '— Ваша анкета: ' + user_info[0] + ' (' + user_info[1] + '; ' + user_info[2] + ')'
                info += show_user_team_info(db,id)
                vk.method('messages.send', {'peer_id':id, 'message':info, 'keyboard': keyboard, 'random_id':''}) 
            elif body.lower() == mainbutton0_2.lower():
                team = get_user_team(db, id) 
                delete_user_team(db, id)  
                count = get_team_members_count(db, team)
                if count[0] == 0:
                    cur = db.cursor()
                    cur.execute('DELETE FROM `urfuevents_teams` WHERE name="'+team+'"')
                    cur.close()
                vk.method('messages.send', {'peer_id':id, 'message':'Теперь ты снова без команды!', 'keyboard': keyboard_main1, 'random_id':''})
            elif body.lower() == disband_team_button.lower():
                if is_user_leader_of_team(db, id):
                    disband_team(db, id)
                    vk.method('messages.send', {'peer_id':id, 'message':'Команда была распущена.', 'keyboard': keyboard_main1, 'random_id':''}) 
                else:
                    vk.method('messages.send', {'peer_id':id, 'message':'Только лидер команды может распустить её!', 'keyboard': keyboard, 'random_id':''}) 
            elif body.lower() == backbutton.lower():
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''})
            elif body.lower() == mainbutton1.lower():
                change_user_status(db, id, 'team_creating_1')
                vk.method('messages.send', {'peer_id':id, 'message':'Придумай название своей команде!', 'keyboard': back_key, 'random_id':''}) 
#           elif body.lower() == mainbutton2.lower():
#                vk.method('messages.send', {'peer_id':id, 'message':get_events(db), 'keyboard': keyboard, 'random_id':''})             
            elif body.lower() == mainbutton3.lower():
                vk.method('messages.send', {'peer_id':id, 'message':resetmessage, 'random_id':''})
                reset_info(db,id)
                vk.method('messages.send', {'peer_id':id, 'message':startmessage1, 'random_id':''})
            else: vk.method('messages.send', {'peer_id':id, 'message':unknownmessage, 'keyboard': keyboard, 'random_id':''}) 
                 
        # Выбор команды
        if user_status == 'team_select':
            if body.lower() == backbutton.lower():
                change_user_status(db, id, 'main_page')
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
            elif team_is_exist(db, body):
                cur = db.cursor()
                cur.execute('UPDATE urfuevents_users SET team = "'+body+'" WHERE id='+str(id))
                cur.close()
                change_user_status(db, id, 'main_page')                
                vk.method('messages.send', {'peer_id':id, 'message':'Ты успешно присоединился к команде '+body+'!\nОбязательно свяжись с участниками команды для уточнения всех подробностей!', 'keyboard': keyboard_main2, 'random_id':''})   
                vk.method('messages.send', {'peer_id':id, 'message':show_user_team_info(db, id), 'random_id':''})
            else: vk.method('messages.send', {'peer_id':id, 'message':'Названной тобой команды не существует! Возможно, ты неправильно написал её название?', 'keyboard': back_key, 'random_id':''})
        
        # Создание команды
        if user_status == 'team_creating_1':
            if body == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                if body.lower() == backbutton.lower():
                    change_user_status(db, id, 'main_page')
                    vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''})         
                elif team_is_exist(db, body):
                    vk.method('messages.send', {'peer_id':id, 'message':'К сожалению, выбранное тобой название уже занято!', 'keyboard': back_key, 'random_id':''})
                else:
                    cur = db.cursor()
                    cur.execute('INSERT INTO urfuevents_teams SET name = "'+body+'", event = "", requierements = "", captain_id = "'+str(id)+'", members = 1, total=1, event_date = ""')
                    cur.execute('UPDATE urfuevents_users SET team = "'+body+'" WHERE id='+str(id))
                    cur.close()
                    change_user_status(db,id,'team_creating_2') 
                    vk.method('messages.send', {'peer_id':id, 'message':'Теперь напиши, на какое мероприятие ты хочешь собрать команду!', 'keyboard': back_key, 'random_id':''})                 
        if user_status == 'team_creating_2':
            if body == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                if body.lower() == backbutton.lower():
                    change_user_status(db, id, 'main_page')
                    vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
                else:
                    team = get_user_team(db,id)
                    cur = db.cursor()
                    cur.execute('UPDATE urfuevents_teams SET event = "'+body+'" WHERE name="'+team+'"')
                    cur.close()
                    change_user_status(db,id,'team_creating_3')       
                    vk.method('messages.send', {'peer_id':id, 'message':'Уточни дату мероприятия в формате день.месяц.год (напр. 01.09.2020)!', 'keyboard': back_key, 'random_id':''}) 
        if user_status == 'team_creating_3':
            if body.lower() == backbutton.lower():
                change_user_status(db, id, 'main_page')
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
            else:
                team = get_user_team(db,id)
                cur = db.cursor()
                cur.execute('UPDATE urfuevents_teams SET event_date = "'+body+'" WHERE name="'+team+'"')
                cur.close()
                change_user_status(db,id,'team_creating_4')
                vk.method('messages.send', {'peer_id':id, 'message':'Сколько максимально участников должно быть в команде?', 'keyboard': back_key, 'random_id':''}) 
        if user_status == 'team_creating_4':
            if body.lower() == backbutton.lower():
                change_user_status(db, id, 'main_page')
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
            else:
                if body.isdigit:
                    body = str(abs(int(body)))
                    team = get_user_team(db,id)
                    cur = db.cursor()
                    cur.execute('UPDATE urfuevents_teams SET total = '+body+' WHERE name="'+team+'"')
                    cur.close()
                    change_user_status(db,id,'team_creating_5')
                    vk.method('messages.send', {'peer_id':id, 'message':'Последний шаг. Напиши свои пожелания к будущим участникам!', 'keyboard': back_key, 'random_id':''})         
                else: 
                    vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести число!', 'keyboard': back_key, 'random_id':''}) 
        if user_status == 'team_creating_5':
            if body == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                if body.lower() == backbutton.lower():
                    change_user_status(db, id, 'main_page')
                    vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
                else:
                    team = get_user_team(db,id)
                    cur = db.cursor()
                    cur.execute('UPDATE urfuevents_teams SET requierements = "'+body+'" WHERE name="'+team+'"')
                    cur.close()
                    change_user_status(db,id,'main_page')
                    vk.method('messages.send', {'peer_id':id, 'message':'Поздравляю, команда успешна создана! Осталось только дождаться новых участников!', 'keyboard': keyboard_leader, 'random_id':''})                     
    
    
    time.sleep(1)
