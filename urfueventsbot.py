#! /usr/bin/env python
# -*- coding: utf-8 -*-

import vk_api
import pymysql
import time
import json

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

vk = vk_api.VkApi(token='--', api_version=5.95)

db = pymysql.connect('localhost', 'unodoscuattro', 'unodoscuattro', 'urfuevents')
db.autocommit(True)
# db: urfuevents_users, urfuevents_teams
# urfuevents_users: id | fio | studygroup | speciality | team | status
# urfuevents_teams: name | event | requierements | captain_id | members | total | event_date

# Клавиши меню 
info_button = 'Информация о себе'
team_list_button = 'Открыть список команд'
team_leave_button = 'Покинуть свою команду'
team_create_button = 'Организовать свою команду'
team_disband_button = 'Распустить свою команду'
team_user_kick_button = 'Исключить участника из команды'
team_chat_button = 'Написать сообщение команде'
user_search_button = 'Найти пользователя'
reset_info_button = 'Обновить информацию о себе'
back_button = 'Вернуться назад'

unknown_message = 'Я плохо понимаю человеческий, давай действовать по инструкции!'

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
keyboard_without_team = {
    'one_time': True,
    'buttons':
    [
        [get_button(label=info_button, color='primary')],
        [get_button(label=team_list_button, color='positive')],
        [get_button(label=team_create_button, color='positive')],
        [get_button(label=user_search_button, color='primary')],
        [get_button(label=reset_info_button, color='primary')]
    ]
}
keyboard_with_team = {
    'one_time': True,
    'buttons':
    [
        [get_button(label=info_button, color='primary')],
        [get_button(label=team_chat_button, color='positive')],
        [get_button(label=team_list_button, color='positive')],
        [get_button(label=team_leave_button, color='negative')],
        [get_button(label=user_search_button, color='primary')],        
        [get_button(label=reset_info_button, color='primary')]
    ]
}

keyboard_leader = {
    'one_time': True,
    'buttons':
    [
        [get_button(label=info_button, color='primary')],
        [get_button(label=team_chat_button, color='positive')],
        [get_button(label=team_list_button, color='positive')],
        [get_button(label=team_user_kick_button, color='negative')],        
        [get_button(label=team_leave_button, color='negative')],
        [get_button(label=team_disband_button, color='negative')],
        [get_button(label=user_search_button, color='primary')],        
        [get_button(label=reset_info_button, color='primary')]
    ]
}

back_key = {
    'one_time': True,
    'buttons':
    [
        [get_button(label=back_button, color='primary')]
    ]
}

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
    if team == '' or team == (): return False
    if team[3] == str(userid): return True
    return False
    
def send_message_to_team(db, team, message):
    if team != '':
        cur = db.cursor()
        cur.execute('SELECT id FROM urfuevents_users WHERE team ="'+team+'"')
        members = cur.fetchall()
        for userid in members:
            vk.method('messages.send', {'peer_id':userid[0], 'message':message, 'random_id':''}) 
    
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
    team = cur.fetchall()
    if team != ():
    	return team[0]
    else: return ()

def show_user_profile(db, userid):
    user_info = get_user_info(db,userid)
    info = '— Анкета: ' + user_info[0] + ' (' + user_info[1] + '; ' + user_info[2] + ')'
    info += show_user_team_info(db,userid)
    return info

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
    else: return '\n\n— Команды не найдено'

def get_teams(db):
    cur = db.cursor()
    cur.execute('SELECT * FROM urfuevents_teams WHERE 1')
    teams = cur.fetchall()   
    if teams == (): return 'В настоящий момент список команд пуст!'
    for team in teams:
        update_members_count(db, team[0]) 
    teamlist = 'Чтобы присоединиться к выбранной команде, отправь её название!\n\n'
    cur.execute('SELECT * FROM urfuevents_teams WHERE 1')
    teams = cur.fetchall()
    i = 0
    for team in teams:
        update_members_count(db, team[0])
        if team[4] == 0: 
            cur = db.cursor()
            cur.execute('DELETE FROM `urfuevents_teams` WHERE name="'+team[0]+'"') 
            cur.close()
        else:
            if team[4] < team[5]:
                i+=1
                teamlist += '\n\n' + str(i) + '. ' + team[0] + ' [' + str(team[4]) + '/' + str(team[5]) + '] \n' 
                teamlist += '— Мероприятие: ' +  team[1] + ' (' + team[6] +')' '\n'
                leaderinfo = get_user_info(db, team[3])
                teamlist += '— Капитан: ' + leaderinfo[0] + ' (' + leaderinfo[1] + '; ' + leaderinfo[2] + ') https://vk.com/id' + team[3] + '\n'
                teamlist += '— Требования к участникам: ' + team[2]
    if teamlist == 'Чтобы присоединиться к выбранной команде, отправь её название!\n\n':
        return 'В настоящий момент список команд пуст!'
    return teamlist

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
  
# Настройка клавиатуры, которую требует ВК 
keyboard_without_team = json.dumps(keyboard_without_team, ensure_ascii=False).encode('utf-8')
keyboard_without_team = str(keyboard_without_team.decode('utf-8'))
keyboard_with_team = json.dumps(keyboard_with_team, ensure_ascii=False).encode('utf-8')
keyboard_with_team = str(keyboard_with_team.decode('utf-8'))
keyboard_leader = json.dumps(keyboard_leader, ensure_ascii=False).encode('utf-8')
keyboard_leader = str(keyboard_leader.decode('utf-8'))
back_key = json.dumps(back_key, ensure_ascii=False).encode('utf-8')
back_key = str(back_key.decode('utf-8'))

# Сам бот
while True:
    messages = vk.method('messages.getConversations', {'offset':0, 'count':20, 'filter':'unread'})
    if messages['count'] > 0:
        id = messages['items'][0]['last_message']['from_id']
        body = messages['items'][0]['last_message']['text'].replace('"','').replace("'",'').replace('\\','')
        
        if id_is_not_exist(db, id):
            cur = db.cursor()
            cur.execute('INSERT INTO urfuevents_users SET id = '+str(id)+', fio = "", studygroup = "", speciality = "", team = "", status = ""')
            cur.close()
 	
        user_status = get_user_status(db, id)
        
        user_team = get_user_team(db, id)
        if user_team == '': keyboard = keyboard_without_team
        else: 
            if is_user_leader_of_team(db, id):
                keyboard = keyboard_leader
            else: keyboard = keyboard_with_team
 
        # Регистрация
        if user_status == '':
            vk.method('messages.send', {'peer_id':id, 'message':'Прежде чем найти команду на мероприятия, расскажи немного о себе!', 'random_id':''})
            change_user_status(db, id, 'register1')
            vk.method('messages.send', {'peer_id':id, 'message':'Для начала введи свои фамилию, имя и отчество! Эти данные нужны для того, чтобы капитан команды мог записать тебя на мероприятие!', 'random_id':''})
        if user_status == 'register1':
            if body.replace(' ','') == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:
                change_user_info(db, id, 'fio', body)
                change_user_status(db, id, 'register2')
                vk.method('messages.send', {'peer_id':id, 'message':'Отлично, теперь назови свою академическую группу, например: "РИ-190012"', 'random_id':''})  
        if user_status == 'register2':
            if body.replace(' ','') == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                change_user_info(db, id, 'studygroup', body)
                change_user_status(db, id, 'register3')
                vk.method('messages.send', {'peer_id':id, 'message':'И последний шаг: назови своё направление и курс, например: "Программная Инженерия, 1 курс"', 'random_id':''})
        if user_status == 'register3':
            if body.replace(' ','') == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                change_user_info(db, id, 'speciality', body)
                change_user_status(db, id, 'main_page')
                vk.method('messages.send', {'peer_id':id, 'message':'Регистрация завершена!', 'keyboard': keyboard, 'random_id':''})
         
        # Главное меню
        if user_status == 'main_page':                   
            if body.lower() == team_list_button.lower():
                vk.method('messages.send', {'peer_id':id, 'message':get_teams(db), 'keyboard': back_key, 'random_id':''}) 
                change_user_status(db, id, 'team_select')
            elif body.lower() == info_button.lower():
                info = show_user_profile(db,id)
                vk.method('messages.send', {'peer_id':id, 'message':info, 'keyboard': keyboard, 'random_id':''}) 
            elif body.lower() == team_chat_button.lower():
                change_user_status(db, id, 'team_chat')
                vk.method('messages.send', {'peer_id':id, 'message':'Теперь твои сообщения будут отправляться всей команде!', 'keyboard': back_key, 'random_id':''}) 
            elif body.lower() == team_user_kick_button.lower():
                if is_user_leader_of_team:
                    change_user_status(db, id, 'removing_user')
                    vk.method('messages.send', {'peer_id':id, 'message':'Введите ФИО участника, которого хотите исключить!', 'keyboard': back_key, 'random_id':''})             
                else: 
                    vk.method('messages.send', {'peer_id':id, 'message':'Только лидер команды может исключить её участника', 'keyboard': keyboard, 'random_id':''})
            elif body.lower() == team_leave_button.lower():
                team = get_user_team(db, id) 
                delete_user_team(db, id)  
                user_info = get_user_info(db, id)
                message = 'Участник покинул команду! :( \n - ' + user_info[0] + ' (' + user_info[1] + '; ' + user_info[2] + ') https://vk.com/id' + str(id)
                send_message_to_team(db, team, message)
                vk.method('messages.send', {'peer_id':id, 'message':'Теперь ты снова без команды!', 'keyboard': keyboard_without_team, 'random_id':''})
            elif body.lower() == team_disband_button.lower():
                if is_user_leader_of_team(db, id):
                    send_message_to_team(db, user_team, 'Лидер вашей команды распустил состав!')
                    disband_team(db, id)
                    vk.method('messages.send', {'peer_id':id, 'message':'Команда была распущена.', 'keyboard': keyboard_without_team, 'random_id':''}) 
                else:
                    vk.method('messages.send', {'peer_id':id, 'message':'Только лидер команды может распустить её!', 'keyboard': keyboard, 'random_id':''}) 
            elif body.lower() == back_button.lower():
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''})
            elif body.lower() == team_create_button.lower():
                change_user_status(db, id, 'team_creating_1')
                vk.method('messages.send', {'peer_id':id, 'message':'Придумай название своей команде!', 'keyboard': back_key, 'random_id':''})  
            elif body.lower() == user_search_button.lower():
                change_user_status(db, id, 'user_search')
                vk.method('messages.send', {'peer_id':id, 'message':'Введи ФИО пользователя, которого хочешь найти!', 'keyboard': back_key, 'random_id':''})                 
            elif body.lower() == reset_info_button.lower():
                vk.method('messages.send', {'peer_id':id, 'message':'Твои данные были успешно сброшены! Теперь давай заполним их заново!', 'random_id':''})
                reset_info(db,id)
                vk.method('messages.send', {'peer_id':id, 'message':'Для начала введи свои фамилию, имя и отчество! Эти данные нужны для того, чтобы капитан команды мог записать тебя на мероприятие!', 'random_id':''})
            else: vk.method('messages.send', {'peer_id':id, 'message':unknown_message, 'keyboard': keyboard, 'random_id':''}) 
                 
        # Выбор команды
        if user_status == 'team_select':
            if body.lower() == back_button.lower():
                change_user_status(db, id, 'main_page')
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
            elif team_is_exist(db, body):
                count = get_team_members_count(db, body)
                if count[0] >= count[1]:
                    vk.method('messages.send', {'peer_id':id, 'message':'Команда, к которой ты хочешь присоединиться, заполнена!', 'keyboard': back_key, 'random_id':''})    
                else:
                    user_info = get_user_info(db, id)             
                    if user_team != '':
                        message = 'Участник покинул команду! :( \n - ' + user_info[0] + ' (' + user_info[1] + '; ' + user_info[2] + ') https://vk.com/id' + str(id)
                        send_message_to_team(db, user_team, message)
                    message = 'Новый участник присоединился к команде! :) \n + ' + user_info[0] + ' (' + user_info[1] + '; ' + user_info[2] + ') https://vk.com/id' + str(id)
                    send_message_to_team(db, body, message)
                    cur = db.cursor()              
                    cur.execute('UPDATE urfuevents_users SET team = "'+body+'" WHERE id='+str(id))
                    cur.close()               
                    change_user_status(db, id, 'main_page')                
                    vk.method('messages.send', {'peer_id':id, 'message':'Ты успешно присоединился к команде '+body+'!\nОбязательно свяжись с участниками команды для уточнения всех подробностей!', 'keyboard': keyboard_with_team, 'random_id':''}) 
                    vk.method('messages.send', {'peer_id':id, 'message':show_user_team_info(db, id), 'random_id':''})
            else: 
                vk.method('messages.send', {'peer_id':id, 'message':'Названной тобой команды не существует! Возможно, ты неправильно написал её название?', 'keyboard': back_key, 'random_id':''})
        
        # Чат команды
        if user_status == 'team_chat':
            if body.lower() == back_button.lower():
                change_user_status(db, id, 'main_page')
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
            else:
                user_info = get_user_info(db, id)
                message = '— Чат «' + user_team + '» \n' + user_info[0] + ': ' + body
                vk.method('messages.send', {'peer_id':id, 'message':'Твоё сообщение увидят все участники команды!', 'keyboard':back_key, 'random_id':''})
                send_message_to_team(db, user_team, message)
        
        # Создание команды
        if user_status == 'team_creating_1':
            if body.replace(' ','') == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                if body.lower() == back_button.lower():
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
            if body.replace(' ','') == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                if body.lower() == back_button.lower():
                    change_user_status(db, id, 'main_page')
                    disband_team(db, id)
                    vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
                else:
                    team = get_user_team(db,id)
                    cur = db.cursor()
                    cur.execute('UPDATE urfuevents_teams SET event = "'+body+'" WHERE name="'+team+'"')
                    cur.close()
                    change_user_status(db,id,'team_creating_3')       
                    vk.method('messages.send', {'peer_id':id, 'message':'Уточни дату мероприятия в формате день.месяц.год (напр. 01.09.2020)!', 'keyboard': back_key, 'random_id':''}) 
        if user_status == 'team_creating_3':
            if body.replace(' ','') == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:                
                if body.lower() == back_button.lower():
                    change_user_status(db, id, 'main_page')
                    disband_team(db, id)
                    vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
                else:
                    try:
                        validation_date = time.strptime(body, '%d.%m.%Y')
                        team = get_user_team(db,id)
                        cur = db.cursor()
                        cur.execute('UPDATE urfuevents_teams SET event_date = "'+body+'" WHERE name="'+team+'"')
                        cur.close()
                        change_user_status(db,id,'team_creating_4')
                        vk.method('messages.send', {'peer_id':id, 'message':'Сколько максимально участников должно быть в команде?', 'keyboard': back_key, 'random_id':''}) 
                    except ValueError:
                        vk.method('messages.send', {'peer_id':id, 'message':'Кажется, ты некорректно ввёл дату!', 'keyboard': back_key, 'random_id':''}) 
        if user_status == 'team_creating_4':
            if body.lower() == back_button.lower():
                change_user_status(db, id, 'main_page')
                disband_team(db, id)
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
            else:
                if body.isdigit():
                    if abs(int(body)) > 10:
                        vk.method('messages.send', {'peer_id':id, 'message':'К сожалению, в команде может быть не более 10 человек!', 'keyboard': back_key, 'random_id':''})
                    else:
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
            if body.replace(' ','') == '': 
                vk.method('messages.send', {'peer_id':id, 'message':'Ты должен ввести хоть что-нибудь! :(', 'random_id':''})  
            else:        
                if body.lower() == back_button.lower():
                    change_user_status(db, id, 'main_page')
                    disband_team(db, id)
                    vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''}) 
                else:
                    team = get_user_team(db,id)
                    cur = db.cursor()
                    cur.execute('UPDATE urfuevents_teams SET requierements = "'+body+'" WHERE name="'+team+'"')
                    cur.close()
                    change_user_status(db,id,'main_page')
                    vk.method('messages.send', {'peer_id':id, 'message':'Поздравляю, команда успешна создана! Осталось только дождаться новых участников!', 'keyboard': keyboard_leader, 'random_id':''})                     
        
        # Исключение участника из команды
        if user_status == 'removing_user':
            if body.lower() == back_button.lower():
                change_user_status(db, id, 'main_page')
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''})         
            else:
                cur = db.cursor()
                cur.execute('SELECT id FROM urfuevents_users WHERE fio ="'+body+'" AND team="'+user_team+'"')
                removingid = cur.fetchall()
                cur.close()
                if removingid == ():
                    vk.method('messages.send', {'peer_id':id, 'message':'В команде нет участника с такими данными!', 'keyboard': back_key, 'random_id':''}) 
                else:
                    removingid=removingid[0][0]
                    delete_user_team(db, removingid)
                    change_user_status(db, id, 'main_page')
                    vk.method('messages.send', {'peer_id':id, 'message':'Участник был исключен из команды!', 'keyboard': keyboard, 'random_id':''}) 
                    removing_info = get_user_info(db, removingid)
                    message = 'Участник был исключен из команды! :( \n - ' + removing_info[0] + ' (' + removing_info[1] + '; ' + removing_info[2] + ') https://vk.com/id' + str(removingid)
                    send_message_to_team(db, user_team, message)        
        
        # Поиск участника
        if user_status == 'user_search':
            if body.lower() == back_button.lower():
                change_user_status(db, id, 'main_page')
                vk.method('messages.send', {'peer_id':id, 'message':'Возвращаемся...', 'keyboard': keyboard, 'random_id':''})         
            else:
                cur = db.cursor()
                cur.execute('SELECT id FROM urfuevents_users WHERE fio ="'+body+'"')
                search_ids = cur.fetchall()
                cur.close()
                if search_ids == ():
                    vk.method('messages.send', {'peer_id':id, 'message':'К сожалению, такого пользователя не существует! Попробуем по-другому?', 'keyboard': back_key, 'random_id':''})
                else:
                    search_results = 'Вот, что мне удалось найти: \n\n'
                    for search_id in search_ids[0]:
                        search_results+='\n\n'+show_user_profile(db,search_id)
                    vk.method('messages.send', {'peer_id':id, 'message':search_results, 'keyboard':back_key, 'random_id':''})    
    time.sleep(1)
