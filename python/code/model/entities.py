# Model management class
from _decimal import Decimal

from peewee import *
from playhouse.fields import ManyToManyField
from telegram import update

from python.resources import properties

# open database connection
database = PostgresqlDatabase(properties.db['name'], host=properties.db['host'], user=properties.db['user'],
                              password=properties.db['password'])


# Base model for setting database
class BaseModel(Model):
    chat_id = IntegerField()

    class Meta:
        database = database


# Bot related entities
class Chat(BaseModel):
    language = CharField(max_length=5, null=True)


# Housesharing related entities
class User(BaseModel):
    name = CharField(null=True)
    base_value = BigIntegerField(null=True)
    active = BooleanField()

    def set_base_value(self, value):
        self.base_value = round(Decimal(value), ndigits=2)

    class Meta:
        indexes = (
            (('chat_id', 'name'), True),  # cant have user with same name and chat_id
        )


class Charge(BaseModel):
    charge_day = IntegerField()
    reference_month = CharField()
    users = ManyToManyField(User)


class Expense(BaseModel):
    name = CharField()
    charge_day = IntegerField()
    paid = BooleanField()
    charge = ForeignKeyField(Charge, related_name='expenses')


UserCharge = Charge.users.get_through_model()

# Drop tables
# database.drop_tables([User, Expense, Charge, Chat], cascade=True)
database.create_tables([User, Expense, Charge, Chat], safe=True)
