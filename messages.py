msg_search_result = "🔍 <b>Результаты поиска по вашему запросу:</b>"


def msg_cocktail_params(data: list[dict]):
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
                text += f"<i>⇨ {value['value']}</i>\n\n"
        #####

    cocktail_names = cocktail_names.rstrip(', ')
    cocktail_names += '</b>'
    cocktail_names += "\n\n"

    return cocktail_names + "<b>❇️ Параметры коктейля</b>\n\n" + text


def msg_cocktail_ingredients_cooking(data, cocktail_name, msg_type):
    cocktail_names = f'🍸 <b>{cocktail_name}</b>\n\n'
    text = ''

    for item in data:
        if item['data'][0]['value']:
            text += f"🔹 <b>{item['param']}:</b>\n"
        else:
            continue

        for value in item['data']:
            if value['value']:
                if value['volume']:
                    text += f"<i>⇨ {value['value']}</i> --- {value['volume']}\n"
                else:
                    text += f"<i>⇨ {value['value']}</i>\n"
        #####
        text += '\n'

    return cocktail_names + f"<b>❇️ {msg_type}</b>\n\n" + text
