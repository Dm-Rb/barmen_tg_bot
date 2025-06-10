from aiogram.types import Message
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import search_controller
from keyboards import build_keyboard_with_pagination
from messages import msg_search_result


router = Router()


class PaginationState(StatesGroup):
    viewing_list = State()  # Состояние просмотра списка


@router.message(Command("start"))
async def start(message: Message):
    await message.answer("добавить мессагу для команды start")


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

