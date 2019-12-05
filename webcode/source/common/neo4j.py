from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo, FloatProperty, BooleanProperty, DateProperty)

class Stock_Node(StructuredNode):
	symbol = StringProperty(unique_index=True, required=True)
	curr_price = FloatProperty(required=True)

class Transaction_Node(StructuredNode):
	tid = UniqueIdProperty()
	price = FloatProperty(required=True)
	buy = BooleanProperty(required=True)
	quantity = IntegerProperty(required=True)
	date = DateProperty(required=True)
	stock = RelationshipTo(Stock_Node, "TRANSACTIONTOSTOCK")

class Portfolio_Node(StructuredNode):
	uid = StringProperty(unique_index=True, required=True)
	symbol = StringProperty(required=True)
	profit = FloatProperty(required=True)
	quantity = IntegerProperty(required=True)
	stock = RelationshipTo(Stock_Node, "CONTAINS")

class User_Node(StructuredNode):
    uid = StringProperty(unique_index=True, required=True)
    stock = RelationshipTo(Stock_Node, "OWNS")
    transaction = RelationshipTo(Transaction_Node, "PERFORMS")
    portfolio = RelationshipTo(Portfolio_Node, "HASPORTFOLIO")