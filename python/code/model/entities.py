# Model management class

from peewee import *
from playhouse.fields import ManyToManyField

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
    base_value = DecimalField(decimal_places=2, auto_round=True, null=True)
    active = BooleanField()

    class Meta:
        indexes = (
            (('chat_id', 'name'), True),  # cant have user with same name and chat_id
        )


class Charge(BaseModel):
    charge_day = IntegerField()
    reference_month = CharField()
    users = ManyToManyField(User)

    class Meta:
        indexes = (
            (('chat_id', 'reference_month'), True),  # cant have two charges for same month and chat
        )


class Expense(BaseModel):
    name = CharField()
    value = DecimalField(decimal_places=2, auto_round=True, null=True)
    charge_day = IntegerField(null=True)
    paid = BooleanField(null=True)
    recurrent = BooleanField(null=True)
    charge = ForeignKeyField(Charge, related_name='expenses', null=True)

    class Meta:
        indexes = (
            (('chat_id', 'name', 'charge'), True),  # cant have expense with same name and chat_id and charge
        )


UserCharge = Charge.users.get_through_model()

# Drop tables
# database.drop_tables([User, Expense, Charge, Chat], cascade=True)
database.create_tables([User, Expense, Charge, Chat, UserCharge], safe=True)
