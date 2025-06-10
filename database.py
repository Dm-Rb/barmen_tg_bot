import aiosqlite
from typing import List, Tuple, Optional, Any
import sqlite3
import re
import asyncio
import base64


class DataBase:

    def __init__(self, db_name: str):
        self.db_name = db_name
        self.connection: Optional[aiosqlite.Connection] = None
        self.cursor: Optional[aiosqlite.Cursor] = None

    async def __aenter__(self):
        self.connection = await aiosqlite.connect(self.db_name)
        self.cursor = await self.connection.cursor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            await self.connection.close()

    def _get_all_cocktail_names(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            sql = """
            SELECT en_cocktail_name, ru_cocktail_name, additional_name, id FROM cocktails;
            """

            return cursor.execute(sql).fetchall()

    def _get_all_ingredients(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            sql = """
            SELECT ingredient, id FROM ingredients;
            """

            return cursor.execute(sql).fetchall()

    async def _get_cocktail_base_info_by_id(self, cocktail_id: int) \
            -> List[Tuple[str, Any]]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            WITH cocktail_data AS (
                SELECT * FROM cocktails WHERE id = ?
            )
            SELECT 
                column_name, 
                column_value
            FROM (
                SELECT 'en_cocktail_name' AS column_name, en_cocktail_name AS column_value FROM cocktail_data
                UNION ALL SELECT 'ru_cocktail_name', ru_cocktail_name FROM cocktail_data
                UNION ALL SELECT 'additional_name', additional_name FROM cocktail_data
                UNION ALL SELECT 'strength', strength FROM cocktail_data
                UNION ALL SELECT 'total_volume', total_volume FROM cocktail_data
                UNION ALL SELECT 'cooking_level', cooking_level FROM cocktail_data
                UNION ALL SELECT 'type', type FROM cocktail_data
                UNION ALL SELECT 'bartender_guide_category', bartender_guide_category FROM cocktail_data
                UNION ALL SELECT 'seasonality', seasonality FROM cocktail_data
                UNION ALL SELECT 'color', color FROM cocktail_data
                UNION ALL SELECT 'tart_flavor', tart_flavor FROM cocktail_data
                UNION ALL SELECT 'sweet_flavor', sweet_flavor FROM cocktail_data
                UNION ALL SELECT 'bitter_flavor', bitter_flavor FROM cocktail_data
                UNION ALL SELECT 'salty_flavor', salty_flavor FROM cocktail_data
                UNION ALL SELECT 'descr_flavor', descr_flavor FROM cocktail_data
            )
            """
            await cursor.execute(sql, (cocktail_id,))
            response_data = await cursor.fetchall()
            return [tuple(row) for row in response_data]  # конвертим Row в tuple

    async def _get_related_ingredients_from_cocktails_table_by_cocktail_id(self, cocktail_id: int) \
            -> List[Tuple[str, Optional[str] or None]]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            WITH cocktail_data AS (
                SELECT * FROM cocktails WHERE id = ?
            )
            SELECT 
                column_name, 
                column_value
            FROM (
                SELECT 'flavoring' AS column_name, flavoring AS column_value FROM cocktail_data
                UNION ALL SELECT 'production_ice', production_ice FROM cocktail_data
                UNION ALL SELECT 'serving_ice', serving_ice FROM cocktail_data
                UNION ALL SELECT 'garnish_ingredients', garnish_ingredients FROM cocktail_data
            );
            """
            await cursor.execute(sql, (cocktail_id,))
            response_data = await cursor.fetchall()
            return [tuple(row) for row in response_data]

    async def _get_related_ingredients_from_ingredients_table_by_cocktail_id(self, cocktail_id: int) \
            -> List[Tuple[str, str or None]]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            SELECT ingredients.ingredient, relations_cocktail_ingredient.value
            FROM ingredients
            JOIN relations_cocktail_ingredient ON ingredients.id = relations_cocktail_ingredient.id_ingredient
            WHERE relations_cocktail_ingredient.id_cocktail = ?;
            """
            await cursor.execute(sql, (cocktail_id,))
            response_data = await cursor.fetchall()
            return [tuple(row) for row in response_data]

    async def _get_related_drinkware_from_drinkware_table_by_cocktail_id(self, cocktail_id: int) -> List[Tuple[str, ]]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            SELECT drinkware.ware  
            FROM drinkware 
            JOIN relations_cocktail_drinkware ON drinkware.id = relations_cocktail_drinkware.id_ware
            WHERE relations_cocktail_drinkware.id_cocktail = ?;
            """
            await cursor.execute(sql, (cocktail_id,))
            response_data = await cursor.fetchall()
            return [tuple(row) for row in response_data]

    async def _get_related_instructions_from_cocktails_table_by_cocktail_id(self, cocktail_id: int) \
            -> List[Tuple[str, ]]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            WITH cocktail_data AS (
                SELECT * FROM cocktails WHERE id = ?
            )
            SELECT 
                column_name, 
                column_value
            FROM (
                SELECT 'cooking_time' AS column_name, cooking_time AS column_value FROM cocktail_data
                UNION ALL SELECT 'prep_instructions', prep_instructions FROM cocktail_data
                UNION ALL SELECT 'serving_temperature', serving_temperature FROM cocktail_data
            );
            """
            await cursor.execute(sql, (cocktail_id,))
            response_data = await cursor.fetchall()
            return [tuple(row) for row in response_data]

    async def _get_related_methods_from_preparation_methods_table_by_cocktail_id(self, cocktail_id: int) \
            -> List[Tuple[str, ]]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            SELECT preparation_methods.method  
            FROM preparation_methods 
            JOIN relations_cocktail_method ON preparation_methods.id = relations_cocktail_method.id_method
            WHERE relations_cocktail_method.id_cocktail = ?;
            """
            await cursor.execute(sql, (cocktail_id,))
            response_data = await cursor.fetchall()
            return [tuple(row) for row in response_data]

    async def _get_related_inventory_from_necessary_inventory_table_by_cocktail_id(self, cocktail_id: int) \
            -> List[Tuple[str, ]]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            SELECT necessary_inventory.inventory  
            FROM necessary_inventory 
            JOIN relations_cocktail_inventory ON necessary_inventory.id = relations_cocktail_inventory.id_inventory
            WHERE relations_cocktail_inventory.id_cocktail = ?;
            """
            await cursor.execute(sql, (cocktail_id,))
            response_data = await cursor.fetchall()
            return [tuple(row) for row in response_data]

    async def _get_related_hardware_from_bar_hardware_table_by_cocktail_id(self, cocktail_id: int) -> List[Tuple[str, ]]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            SELECT bar_hardware.hardware  
            FROM bar_hardware 
            JOIN relations_cocktail_hardware ON bar_hardware.id = relations_cocktail_hardware.id_hardware
            WHERE relations_cocktail_hardware.id_cocktail = ?;
            """
            await cursor.execute(sql, (cocktail_id,))
            response_data = await cursor.fetchall()
            return [tuple(row) for row in response_data]

    async def _get_related_cocktail_names_by_ingredient_id(self, ingredient_id: int) -> List[int]:
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            SELECT cocktails.en_cocktail_name
            FROM relations_cocktail_ingredient
            JOIN cocktails ON relations_cocktail_ingredient.id_cocktail = cocktails.id
            WHERE relations_cocktail_ingredient.id_ingredient = ?;
            """
            await cursor.execute(sql, (ingredient_id,))
            response_data = await cursor.fetchall()
            return [row[0] for row in response_data]

    async def _get_related_img_base64_by_id_cocktail(self, id_cocktail: int):
        async with aiosqlite.connect(self.db_name) as conn:
            cursor = await conn.cursor()
            sql = """
            SELECT img_base64 FROM cocktail_imgs WHERE id_cocktail = ?;
            """
            await cursor.execute(sql, (id_cocktail,))
            response_data = await cursor.fetchone()

            return response_data


class DataInterfaces(DataBase):

    def __init__(self, db_path: str = "data.db"):
        super().__init__(db_path)
        self._cocktails_alias = {
            'en_cocktail_name': 'Название коктейля (en)',
            'ru_cocktail_name': 'Название коктейля (ru)',
            'additional_name': "Дополнительное название коктейля",
            'flavoring': 'Ароматизация коктейля',
            'production_ice': 'Лёд, используемый для приготовления',
            'serving_ice': 'Лёд для подачи в бокале',
            'garnish_ingredients': 'Состав украшения/гарнира',
            'cooking_time': 'Время приготовления',
            'serving_temperature': 'Температура подачи коктейля',
            'strength': 'Крепость коктейля',
            'total_volume': 'Общий объём коктейля',
            'cooking_level': 'Уровень сложности',
            'type': 'Принадлежность коктейля',
            'bartender_guide_category': 'Классификация по Учебнику Бармена',
            'seasonality': 'Сезонность',
            'color': 'Цвет коктейля',
            'tart_flavor': "Характеристика вкуса, кислый",
            'sweet_flavor': "Характеристика вкуса, сладкий",
            'bitter_flavor': "Характеристика вкуса, горький",
            'salty_flavor': "Характеристика вкуса, солёный",
            'descr_flavor': 'Описание вкуса и аромата',
            'prep_instructions': 'Пошаговая инструкция приготовления'
        }

    async def get_cocktail_params(self, id_cocktail: int) -> List[dict]:
        """Получить данные для блока 'Параметры коктейля' """
        result = []
        response_data = await self._get_cocktail_base_info_by_id(id_cocktail)
        for item in response_data:
            d = {
                'param': self._cocktails_alias[item[0]],
                'data': [{
                    'value': item[1],
                    'volume': None
                }]
            }
            result.append(d)
        return result

    async def get_cocktail_ingredients(self, cocktail_id: int) -> List[dict]:
        """Получить данные для блока 'Состав' """
        result = []

        ingredients = await self._get_related_ingredients_from_ingredients_table_by_cocktail_id(cocktail_id)
        result.append({
            'param': 'Ингредиенты',
            'data': [{'value': item[0], 'volume': item[1]} for item in ingredients]
        })

        cocktail_ingredients = await self._get_related_ingredients_from_cocktails_table_by_cocktail_id(cocktail_id)
        for item in cocktail_ingredients:
            d = {
                'param': self._cocktails_alias[item[0]],
                'data': [{
                    'value': item[1],
                    'volume': None
                }]
            }
            result.append(d)

        drinkware = await self._get_related_drinkware_from_drinkware_table_by_cocktail_id(cocktail_id)
        result.append({
            'param': 'Посуда для подачи (наименования согласно учебнику бармена)',
            'data': [{'value': item[0], 'volume': None} for item in drinkware]
        })
        return result

    async def get_cocktail_cooking_instructions(self, cocktail_id: int) -> List[dict]:
        """Получить данные для блока 'Приготовление и подача' """
        result = []

        instructions = await self._get_related_instructions_from_cocktails_table_by_cocktail_id(cocktail_id)
        response_data_cocktails_table = []
        for item in instructions:
            d = {
                'param': self._cocktails_alias[item[0]],
                'data': [{
                    'value': item[1].replace('\t', '') if item[1] else None,
                    'volume': None
                }]
            }
            response_data_cocktails_table.append(d)

        if response_data_cocktails_table:
            result.append(response_data_cocktails_table[0])

        methods = await self._get_related_methods_from_preparation_methods_table_by_cocktail_id(cocktail_id)
        result.append({
            'param': 'Методы и приёмы приготовления',
            'data': [{'value': item[0], 'volume': None} for item in methods]
        })

        inventory = await self._get_related_inventory_from_necessary_inventory_table_by_cocktail_id(cocktail_id)
        result.append({
            'param': 'Список необходимого инвентаря (наименования согласно учебнику бармена)',
            'data': [{'value': item[0], 'volume': None} for item in inventory]
        })

        hardware = await self._get_related_hardware_from_bar_hardware_table_by_cocktail_id(cocktail_id)
        result.append({
            'param': 'Список необходимого оборудования (наименования согласно учебнику бармена)',
            'data': [{'value': item[0], 'volume': None} for item in hardware]
        })

        if len(response_data_cocktails_table) > 1:
            result.extend(response_data_cocktails_table[1:])

        return result

    async def get_cocktail_image(self, cocktail_id):
        response = await self._get_related_img_base64_by_id_cocktail(cocktail_id)
        bs64_img = response[0]

        if isinstance(bs64_img, list):
            bs64_img = bs64_img[0]

        if isinstance(bs64_img, str) and bs64_img.startswith("data:image"):
            bs64_img = bs64_img.split(",")[1]

        try:
            image_bytes = base64.b64decode(bs64_img)
            return image_bytes
        except Exception as e:
            print(f"Ошибка декодирования Base64: {e}")
            return None
    def _get_cash_cocktail_names_id(self):
        result = {}
        response: list[tuple] = self._get_all_cocktail_names()
        [
            [result.setdefault(tuple_r[i], tuple_r[-1]) for i in range(len(tuple_r) - 1) if tuple_r[i]]
            for tuple_r in response
        ]
        return result

    def _get_cash_id_en_cocktail_names(self):
        # {id: en_cocktail_name, id: en_cocktail_name, ...} -> id:int, en_cocktail_name: str
        result = {}
        response: list[tuple] = self._get_all_cocktail_names()
        [result.setdefault(item[-1], item[0]) for item in response]
        return result

    def _get_cash_ingredients(self):
        result = {}
        response: list[tuple] = self._get_all_ingredients()
        [result.setdefault(item[0], item[-1]) for item in response]

        return result


class SearchController(DataInterfaces):

    def __init__(self, db_path):
        super().__init__(db_path)

        # {en_cocktail_name: id, ru_cocktail_name: id, additional_name: id, ...}
        self.cash_cocktail_names = self._get_cash_cocktail_names_id()

        # {id: en_cocktail_name, id: en_cocktail_name, ...}
        self.cash_display_cocktail_names = self._get_cash_id_en_cocktail_names()

        # {ingredient: id, ingredient: id, ...}
        self.cash_ingredients = self._get_cash_ingredients()

    def search_in_cocktail_names(self, user_query):
        result = list()
        pattern = r"[\s\'\.\-’()№]"
        user_alias = re.sub(pattern, "", user_query)
        user_alias = user_alias.lower()
        for key in self.cash_cocktail_names.keys():
            key_alias = re.sub(pattern, "", key)
            key_alias = key_alias.lower()
            if user_alias in key_alias:
                result.append(key)
        return result

    def search_ingredients(self, user_query):
        result = list()
        pattern = r"[\s\'\.\-’()№]"
        user_alias = re.sub(pattern, "", user_query)
        user_alias = user_alias.lower()
        for key in self.cash_ingredients.keys():
            key_alias = re.sub(pattern, "", key)
            key_alias = key_alias.lower()
            if user_alias in key_alias:
                result.append(key)
        return result

    async def get_cocktail_names_by_user_query(self, user_query):
        result = []
        cocktail_names = self.search_in_cocktail_names(user_query)
        if cocktail_names:
            for cocktail_name in cocktail_names:
                cocktail_id = self.cash_cocktail_names[cocktail_name]
                en_cocktail_name = self.cash_display_cocktail_names[cocktail_id]
                item = {'name': en_cocktail_name, 'id': self.cash_cocktail_names[en_cocktail_name]}
                if item not in result:
                    result.append(item)

        await asyncio.sleep(0)

        ingredients = self.search_ingredients(user_query)
        if ingredients:
            for ingredient in ingredients:
                ingredient_id = self.cash_ingredients[ingredient]
                # Get related cocktails
                rec_list = await self._get_related_cocktail_names_by_ingredient_id(ingredient_id)
                if rec_list:
                    for en_cocktail_name in rec_list:
                        item = {'name': en_cocktail_name, 'id': self.cash_cocktail_names[en_cocktail_name]}
                        if item not in result:
                            result.append(item)
        return result


search_controller = SearchController('cocktails_book.db')
data_controller = DataInterfaces('cocktails_book.db')
# import asyncio
# asyncio.run(search_controller.get_cocktail_names_by_user_query("секс"))

