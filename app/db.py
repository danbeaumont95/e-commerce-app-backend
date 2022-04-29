import os
import motor.motor_asyncio

from dotenv import load_dotenv
load_dotenv()
db_username = os.getenv("db_username")
db_password = os.getenv("db_password")
jwt_secret = os.getenv('secret')
jwt_algorithm = os.getenv('algorithm')


client = motor.motor_asyncio.AsyncIOMotorClient(
    f"mongodb+srv://{db_username}:{db_password}@e-commerce-app.z4k96.mongodb.net/myFirstDatabase?retryWrites=true&w=majority", tls=True, tlsAllowInvalidCertificates=True)
db = client['e-commerce-app']
