from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


ITEMS_PER_PAGE = 10  # Keyboard button limit on "page"


async def build_keyboard_with_pagination(cocktails_array: list[dict], page: int = 0) -> InlineKeyboardMarkup:
    """Build inline keyboard with pagination"""

    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_page_items = cocktails_array[start_idx:end_idx]

    keyboard = InlineKeyboardBuilder()

    # Add buttons
    for item in current_page_items:
        button_name = f"🍸 {item['name']}"
        if len(button_name) > 48:
            button_name = f"{button_name[:48]}..."

        keyboard.add(
            InlineKeyboardButton(
                text=button_name,
                callback_data=f"item_{item['id']}"
            )
        )

    navigation_buttons = []

    # Button "Back" (if current page not first)
    if page > 0:
        navigation_buttons.append(
            types.InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_page")
        )

    # Button "Next" (if current page not last)
    if end_idx < len(cocktails_array):
        navigation_buttons.append(
            types.InlineKeyboardButton(text="Далее ➡️", callback_data="next_page")
        )

    # Arrange elements
    keyboard.adjust(1)  # One element per row
    if navigation_buttons:
        keyboard.row(*navigation_buttons)
    return keyboard.as_markup()


async def build_keyboard_cocktail(cocktail_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❇️ Состав", callback_data=f"ingre_{str(cocktail_id)}")
    builder.button(text="❇️ Приготовление и подача", callback_data=f"instruct_{str(cocktail_id)}")

    builder.adjust(1)

    return builder.as_markup()
