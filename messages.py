msg_search_result = "🔍 <b>Результаты поиска по вашему запросу:</b>"

msg_add_data = 'Скачайте и заполните таблицу "template.csv" данными, затем отправьте таблицу боту для добавления данных в базу.\n' + \
               'Ознакомтесь с примером валидного заполнения таблицы в файле "example.csv"'


msg_accept_add_data = '❕ Убедитесь в том, что все данные верны и расположены правильным образом.\n' + \
                      '❕ Отправте боту изображение коктейля для сохранения данных базу.\n' + \
                      '❕ Если вы заметили, что данные некорректны, отправьте боте команду /cancel для отмены.'

msg_start_command = "<b>Помощник начинающего бармена.</b>\nОтправьте боту название коктейля (на англ.) либо входящий в коктейль ингридиент. Получите детальную информацию, состав и инструкцию приготовления"

def msg_cocktail_params(data: list[dict], msg_type="Параметры коктейля"):
    cocktail_names = '🍸 <b>'
    text = ''
    for item in data:

        if 'название коктейля' in item['param'].lower():
            for value in item['data']:
                if value['value']:
                    cocktail_names += f"{value['value']}, "
            continue

        flag = True
        # text += f"🔹 <b>{item['param']}:</b>\n"
        for value in item['data']:
            if value['value']:
                if flag:
                    text += f"🔹 <b>{item['param']}:</b>\n"
                    flag = False
                if value['volume']:
                    text += f"<i>⇨ {value['value']}</i> --- {value['volume']}\n"
                else:
                    text += f"<i>⇨ {value['value']}</i>\n"
        #####

    cocktail_names = cocktail_names.rstrip(', ')
    cocktail_names += '</b>'
    cocktail_names += "\n\n"

    return cocktail_names + f"<b>❇️ {msg_type}</b>\n\n" + text


def msg_cocktail_ingredients_cooking(data, cocktail_name, msg_type):
    cocktail_names = f'🍸 <b>{cocktail_name}</b>\n\n'
    text = ''

    for item in data:
        try:
            if item['data'][0]['value']:
                text += f"🔹 <b>{item['param']}:</b>\n"
            else:
                continue
        except IndexError:
            pass

        for value in item['data']:
            if value['value']:
                value['value'] = value['value'].replace('\n', '\n⇨ ')
                if value['volume']:
                    text += f"<i>⇨ {value['value']}</i> --- {value['volume']}\n"
                else:
                    text += f"<i>⇨ {value['value']}</i>\n"
        #####
        text += '\n'

    return cocktail_names + f"<b>❇️ {msg_type}</b>\n\n" + text
