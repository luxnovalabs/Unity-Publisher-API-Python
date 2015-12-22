from mongoengine import *

class PurchasedItem(Document):
	product_name = StringField()
	invoice_number = IntField()
	creation_date = DateTimeField()
	last_edit = DateTimeField()
	purchase_date = DateTimeField()
	email = StringField()
	last_email = StringField()
	meta = {
		'indexes':[
			'product_name',
			'invoice_number',
			'creation_date',
			'last_edit',
			'purchase_date',
			'email',
		]
	}





