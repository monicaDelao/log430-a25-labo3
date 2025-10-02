from graphene import Float
from graphene import Int
from graphene import ObjectType
from graphene import String


class Product(ObjectType):
    id = Int()
    name = String()
    sku = String()
    price = Float()
    quantity = Int()
