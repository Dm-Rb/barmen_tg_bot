from aiogram.types import Message, FSInputFile
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import search_controller, data_controller
from keyboards import build_keyboard_with_pagination
from messages import msg_search_result, msg_add_data, msg_cocktail_params, msg_accept_add_data, msg_start_command
from aiogram.types.input_media_document import InputMediaDocument
import os
from io import BytesIO, TextIOWrapper


router = Router()


class PaginationState(StatesGroup):
    viewing_list = State()


class UploadFileState(StatesGroup):
    process_uploading = State()


@router.message(Command("start"))
async def start(message: Message):
    await message.answer(text=msg_start_command, parse_mode='HTML')


@router.message(Command("add"))
async def add_new(message: Message, bot: Bot):
    media = [
        InputMediaDocument(
            media=FSInputFile(os.path.join('files', 'template.csv')),
            caption="Шаблон с таблицей"
        ),
        InputMediaDocument(
            media=FSInputFile(os.path.join('files', "example.csv")),
            caption="Пример заполнения"
        )
    ]
    await message.answer(text=msg_add_data)
    await bot.send_media_group(chat_id=message.chat.id, media=media)


@router.message(Command("show_all"))
async def start(message: Message, state: FSMContext):
    cocktails_array = []
    for k, v in search_controller.cash_display_cocktail_names.items():
        cocktails_array.append(
            {
                'name': v,
                'id': k
            }
        )
    if cocktails_array:
        await state.set_state(PaginationState.viewing_list)
        await state.update_data(current_page=0, items=cocktails_array)  # Сохраняем в FSM)
        await message.answer(
            text=msg_search_result,
            parse_mode="HTML",
            reply_markup=await build_keyboard_with_pagination(cocktails_array)  # Shows pagination
        )


@router.message(StateFilter(UploadFileState.process_uploading), Command("cancel"))
async def cancel(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    current_i = int(data.get('current_i', 0))
    items = data.get('items', None)
    if not items:
        await state.clear()
        return
    # обновляем хранилище состояния
    await state.update_data(current_i=current_i + 1, items=items)
    await processing_new_cocktail(state, bot, message.chat.id)


@router.message(F.text)
async def handle_user_message(message: Message, state: FSMContext):
    cocktails_array: list = await search_controller.get_cocktail_names_by_user_query(message.text)

    if cocktails_array:
        await state.set_state(PaginationState.viewing_list)
        await state.update_data(current_page=0, items=cocktails_array)  # Сохраняем в FSM)
        await message.answer(
            text=msg_search_result,
            parse_mode="HTML",
            reply_markup=await build_keyboard_with_pagination(cocktails_array)  # Shows pagination
        )
    else:
        await message.answer(
            text=msg_search_result + f"\n\n<i>По вашему запросу ничего не найдено</i> 🤷 ️",
            parse_mode="HTML",
        )


@router.message(F.document)
async def handle_user_message(message: Message, bot: Bot, state: FSMContext):
    # проверяем, что это csv
    if not message.document.file_name or not message.document.file_name.endswith('.csv'):
        return  # пропускаем, если не CSV

    # скачиваем файл в память (передаём file_id, а не Document)
    file_in_memory = BytesIO()
    await bot.download(
        message.document.file_id,
        destination=file_in_memory
    )
    file_in_memory.seek(0)  # переводим курсор в начало

    # читаем csv через csv.dictreader
    text_io = TextIOWrapper(file_in_memory, encoding='utf-8')
    try:
        new_cocktails_array = data_controller.preparing_csv_file(text_io)
        await state.set_state(UploadFileState.process_uploading)
        await state.update_data(current_i=0, items=new_cocktails_array)

    except Exception as _ex:
        await message.answer(text=f'Ошибка чтения файла: {_ex}')
    await processing_new_cocktail(state, bot, message.chat.id)


@router.message(StateFilter(UploadFileState.process_uploading), F.photo)
async def save_new_cocktail(message: Message, state: FSMContext, bot: Bot):
    photo = message.photo[-1]
    file_in_memory = BytesIO()
    await bot.download(photo.file_id, destination=file_in_memory)
    file_in_memory.seek(0)
    photo_data = file_in_memory.getvalue()
    data = await state.get_data()
    current_i = int(data.get('current_i', 0))
    items = data.get('items', None)
    if not items:
        await state.clear()
        return
    if current_i > len(items) - 1:
        await state.clear()
        return
    cocktail_data = items[current_i]
    # обновляем хранилище состояния
    await state.update_data(current_i=current_i + 1, items=items)
    try:
        await data_controller.add_new_cocktail_to_database(cocktail_data, photo_data)
        await bot.send_message(chat_id=message.chat.id, text='🟢 Данные сохранены', parse_mode='HTML')
    except Exception as _ex:
        await bot.send_message(chat_id=message.chat.id, text=f'🔴 Данные НЕ сохранены, ошибка: {_ex}', parse_mode='HTML')

    await processing_new_cocktail(state, bot, message.chat.id)
    if current_i == len(items) - 1:
        await state.clear()
        search_controller.update_caches()
        return


@router.message(StateFilter(UploadFileState.process_uploading))
async def processing_new_cocktail(state: FSMContext, bot: Bot, chat_id):
    data = await state.get_data()

    current_i = int(data.get('current_i', 0))
    items = data.get('items', None)

    if not items:
        await bot.send_message(chat_id=chat_id, text='Список данных из таблицы пуст.')
        await state.clear()
        return
    if current_i > len(items) - 1:
        await state.clear()
        search_controller.update_caches()
        return
    message = msg_cocktail_params(items[current_i], 'Вся информация')
    message += '\n\n' + msg_accept_add_data
    await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
