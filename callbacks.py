from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from handlers import PaginationState
from keyboards import build_keyboard_with_pagination, build_keyboard_cocktail
from database import data_controller, search_controller
from messages import msg_cocktail_params, msg_cocktail_ingredients_cooking


router = Router()


@router.callback_query(F.data.in_(["prev_page", "next_page"]), StateFilter(PaginationState.viewing_list))
async def handle_pagination(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 0)
    items = data.get("items", [])  # массив cocktails_array

    if callback.data == "prev_page":
        current_page = max(0, current_page - 1)  # не уходим ниже 0
    elif callback.data == "next_page":
        current_page += 1

    await state.update_data(current_page=current_page)

    keyboard = await build_keyboard_with_pagination(items, current_page)

    # редактируем сообщение (чтобы не создавать новое)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer() 

@router.callback_query(F.data.startswith('item_'))
async def handle_show_cocktail_details(callback: types.CallbackQuery):
    cocktail_id = int(callback.data.lstrip('item_'))
    if not cocktail_id:
        return

    cocktail_params = await data_controller.get_cocktail_params(cocktail_id)
    cocktail_img_bytes = await data_controller.get_cocktail_image(cocktail_id)

    # BufferedInputFile вместо InputFile
    input_file = types.BufferedInputFile(
        file=cocktail_img_bytes,
        filename="cocktail.jpg"
    )
    message = msg_cocktail_params(cocktail_params)
    await callback.message.answer_photo(
        photo=input_file,
        caption=message,
        parse_mode="HTML",
        reply_markup=await build_keyboard_cocktail(cocktail_id)
    )


@router.callback_query(F.data.startswith('ingre_'))
async def handle_show_cocktail_ingredients(callback: types.CallbackQuery):
    cocktail_id = int(callback.data.lstrip('ingre_:'))
    if not cocktail_id:
        return
    cocktail_ingredients = await data_controller.get_cocktail_ingredients(cocktail_id)
    cocktail_name = search_controller.cash_display_cocktail_names[cocktail_id]
    message = msg_cocktail_ingredients_cooking(cocktail_ingredients, cocktail_name, "Состав")
    await callback.message.answer(text=message, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith('instruct_'))
async def handle_show_instructions(callback: types.CallbackQuery, state: FSMContext):
    cocktail_id = int(callback.data.lstrip('instruct_:'))
    if not cocktail_id:
        return
    cooking_instructions = await data_controller.get_cocktail_cooking_instructions(cocktail_id)
    cocktail_name = search_controller.cash_display_cocktail_names[cocktail_id]
    message = msg_cocktail_ingredients_cooking(cooking_instructions, cocktail_name, "Приготовление и подача")

    await callback.message.answer(text=message, parse_mode="HTML")
    await callback.answer()
