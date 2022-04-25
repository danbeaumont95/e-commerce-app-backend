from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import load_dotenv, dotenv_values
import pymongo
import certifi
app = FastAPI()


class Item(BaseModel):
    name: str
    description: str = None
    price: int
    seller: str = None

# uvicorn main:app --reload


config = dotenv_values(".env")
db_name = config['db_name']
db_username = config['db_username']
db_password = config['db_password']


load_dotenv()
conn = pymongo.MongoClient(
    f'mongodb+srv://{db_username}:{db_password}@e-commerce-app.z4k96.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = conn[f'{db_name}']
app = FastAPI()
papersCol = db['e-commerce']
items = db['items']


@app.get("/items")
def root():

    alItems = list(items.find())
    print(alItems, 'all')
    print('hi')
    return {"Items": f"{alItems}"}


@app.post('/item')
def create_course(item: Item):

    new_item = {"name": f"{item.name}", "description": f"{item.description}",
                "price": f"{item.price}", "seller": f"{item.seller}"}
    print(new_item, 'new_item')

    x = items.insert_one(new_item)

    return item
