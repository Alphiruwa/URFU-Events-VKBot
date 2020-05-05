import vk_api
import time
import json

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

vk = vk_api.VkApi(token='199645f330de1d079a2c0602dac55163c593fd9106d4873265c3b5f31221f4f58eef5ec0c6b6838a01e93', api_version=5.95)

startbutton = 'Начать'
startmessage0 = 'Прежде чем найти команду на мероприятия, расскажи немного о себе!'
startmessage1 = 'Для начала введи свои фамилию, имя и отчество! Эти данные нужны для того, чтобы капитан команды мог записать тебя на мероприятие!'
startmessage2 = 'Отлично, теперь назови свою академическую группу, например: "РИ-190012"!'
startmessage3 = 'И последний шаг: назови своё направление и курс, например: "Программная Инженерия, 1 курс"'
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

while True:
    messages = vk.method('messages.getConversations', {'offset':0, 'count':20, 'filter':'unread'})
    if messages['count'] > 0:
        id = messages['items'][0]['last_message']['from_id']
        body = messages['items'][0]['last_message']['text']
        if body.lower() == mainbutton0.lower():
            vk.method('messages.send', {'peer_id':id, 'message':'*список команд с мероприятиями и капитанами*', 'random_id':''})            
        elif body.lower() == mainbutton1.lower():
            vk.method('messages.send', {'peer_id':id, 'message':'*заполнение информации о команде т.е. выбор мероприятия и требования к участникам*', 'random_id':''}) 
        elif body.lower() == mainbutton2.lower():
            vk.method('messages.send', {'peer_id':id, 'message':'*список мероприятий с датами*', 'random_id':''})              
        elif body.lower() == mainbutton3.lower():
            vk.method('messages.send', {'peer_id':id, 'message':'*снова заполнение данных со старта*', 'random_id':''})
        else:
            vk.method('messages.send', {'peer_id':id, 'message':unknownmessage, 'random_id':''})        
    time.sleep(1)
 
