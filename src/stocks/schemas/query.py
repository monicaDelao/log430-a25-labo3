import graphene
from graphene import ObjectType, String, Int
from stocks.schemas.product import Product
from db import get_redis_conn, get_sqlalchemy_session
from stocks.models.product import Product as ProductModel
from stocks.models.stock import Stock

class Query(ObjectType):       
    product = graphene.Field(Product, id=String(required=True))
    stock_level = Int(product_id=String(required=True))
    
    def resolve_product(self, info, id):
        """ Create an instance of Product based on product and stock info from Redis or database """
        redis_client = get_redis_conn()
        
        # D'abord essayer de récupérer depuis Redis
        product_data = redis_client.hgetall(f"stock:{id}")
        
        if product_data and 'name' in product_data:
            # Si Redis contient toutes les informations, les utiliser
            return Product(
                id=int(id),
                name=product_data['name'],
                sku=product_data['sku'],
                price=float(product_data['price']),
                quantity=int(product_data['quantity'])
            )
        else:
            # Sinon, récupérer depuis la base de données
            session = get_sqlalchemy_session()
            
            # JOIN pour obtenir les informations du produit et du stock
            result = session.query(
                ProductModel.id,
                ProductModel.name,
                ProductModel.sku,
                ProductModel.price,
                Stock.quantity
            ).join(Stock, ProductModel.id == Stock.product_id).filter(ProductModel.id == id).first()
            
            if result:
                return Product(
                    id=result.id,
                    name=result.name,
                    sku=result.sku,
                    price=float(result.price),
                    quantity=int(result.quantity)
                )
        return None
    
    def resolve_stock_level(self, info, product_id):
        """ Retrieve stock quantity from Redis """
        redis_client = get_redis_conn()
        quantity = redis_client.hget(f"stock:{product_id}", "quantity")
        return int(quantity) if quantity else 0