import sqlalchemy
import os
import dotenv
from faker import Faker
import random
import numpy as np
import uvicorn
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()
    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)
with engine.begin() as connection:
    connection.execute(sqlalchemy.text(
            """
            TRUNCATE game_log, inventory, quest_ledger, stock, quests, shops, items, characters
            """))
    #Base Quantities
    num_items = 1000
    num_quests = 1000
    num_shops = 1000
    num_characters = 70000

    #Depends On Above
    num_stock = num_shops * 10
    num_quest_ledger = num_characters * 5
    num_inventory = num_characters * 10

    last_item_id = 0
    last_quest_id = 0
    last_shop_id = 0
    last_character_id = 0
    #Fill out items, quests, and shops
    for i in range(num_items):
        item_str = "item" + str(i)
        last_item_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO items (name, description, level, sell_price)
            VALUES (:item, 'sampleitem', :randomlevel, :randomgold)
            returning Id
            """), {'item': item_str, 'randomgold': random.randint(50, 200), 'randomlevel': random.randint(0, 100)}).scalar_one()
        quest_str = "quest" + str(i)
        last_quest_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO quests (name, description, level, gold)
            VALUES (:quest, 'samplequest', :randomlevel, :randomgold)
            returning Id
            """), {'quest': quest_str, 'randomgold': random.randint(50, 500), 'randomlevel': random.randint(0, 100)}).scalar_one()
        shop_str = "shop" + str(i)
        last_shop_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO shops (name, level, gold)
            VALUES (:shop, :randomlevel, :randomgold)
            returning Id
            """), {'shop': shop_str, 'randomgold': random.randint(500, 5000), 'randomlevel': random.randint(0, 100)}).scalar_one()
    
    #Populate Characters
    for i in range(num_characters):
        char_str = "character" + str(i)
        last_character_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO characters (name, level, gold, health, inventory_size)
            VALUES (:character, :randomlevel, :randomgold, 100, 20)
            returning Id
            """), {'character': char_str, 'randomgold': random.randint(0, 1000), 'randomlevel': random.randint(0, 100)}).scalar_one()
    
    #Get Foreign Key Indexes
    print(last_item_id)
    print(last_quest_id)
    print(last_shop_id)
    print(last_character_id)
    first_item_id = last_item_id - num_items + 1
    first_quest_id = last_quest_id - num_quests + 1
    first_shop_id = last_shop_id - num_shops + 1
    first_character_id = last_character_id - num_characters + 1
    print(first_item_id)
    print(first_quest_id)
    print(first_shop_id)
    print(first_character_id)

    #Populate Stock
    for i in range(num_stock):
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO stock (shop_id, item_id, price, quantity)
            VALUES (:shop, :item, :randomquant, :randomgold)
            """), {'shop': random.randint(first_shop_id, last_shop_id),
                   'item': random.randint(first_item_id, last_item_id), 
                   'randomgold': random.randint(0, 100), 
                   'randomquant': random.randint(0, 10)})
        
    #Populate Quest_Ledger
    for i in range(num_quest_ledger):
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO quest_ledger (char_id, quest_id, complete)
            VALUES (:char, :quest, true)
            """), {'char': random.randint(first_character_id, last_character_id),
                   'quest': random.randint(first_quest_id, last_quest_id)})
    
    #Populate Inventory
    for i in range(num_inventory):
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO inventory (equipped, equip_slot, quantity, char_id, item_id)
            VALUES (false, :slot, 1, :char, :item)
            """), {'char': random.randint(first_character_id, last_character_id),
                   'item': random.randint(first_item_id, last_item_id),
                   'slot': random.randint(0, 2)})
