from flask import Flask
from flask import request, redirect, url_for, make_response, session, render_template
from models import PurchasedItem
from datetime import datetime
import AssetStoreAPI
from mongoengine import *
connect('invoice_db')
app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
	if 'token' in session:
		'index had token'
		redirect(url_for('admin'))
	error = None
	if request.method == 'POST':
		try:
			store = AssetStoreAPI.AssetStoreClient()
			store.Login(request.form['username'], request.form['password'])
			if store.IsLoggedIn():
				session['token'] = store.loginToken
				return redirect(url_for('admin'))
			else:
				error = 'Invalid username/password'
		except AssetStoreAPI.AssetStoreException:
			error = 'Invalid username/password'
			
	return render_template('login.html', error=error)

@app.route("/admin", methods=['GET', 'POST'])
def admin():
	if 'token' not in session:
		return redirect(url_for('index'))
	else:
		token = session['token']
		store = AssetStoreAPI.AssetStoreClient()
		store.LoginWithToken(token)
		invoiceNumbersInfo = []

		if request.method == 'POST':
			invoice_numbers = request.form['invoice_numbers'].split(',')
			invoiceNumbersInfo = store.VerifyInvoice(invoice_numbers)

		response = make_response(render_template('admin.html', products=invoiceNumbersInfo))
		response.headers['X-Unity-Session'] = store.GetXUnitySessionCookie()
		return response

@app.route("/add_email", methods=['POST'])
def add_email():
	if 'token' not in session:
		return redirect(url_for('index'))
	else:
		token = session['token']
		store = AssetStoreAPI.AssetStoreClient()
		store.LoginWithToken(token)
		invoiceNumbersInfo = []

		if request.method == 'POST':
			invoice_number = request.form['invoice_numbers']
			product_name = request.form['product_name']
			email = request.form['email']
			purchased_item = PurchasedItem.objects(invoice_number=invoice_number,product_name=product_name).first()
			if purchased_item is not None:
				purchased_item.last_edit = datetime.now()
				purchased_item.last_email = purchased_item.email
				purchased_item.email = email
				purchased_item.save()
			else:
				purchased_item = PurchasedItem(email=email, invoice_number=invoice_number,product_name=product_name, creation_date=datetime.now())
				purchased_item.save()
			
		return redirect(url_for('admin'), code=307)

@app.template_filter('date_format')
def date_format(value):
	value = datetime.utcfromtimestamp(value)
	return value.strftime('%B %d, %Y')

@app.template_filter('find_purchased_item')
def find_purchased_item(invoice_item):
	item = PurchasedItem.objects(invoice_number=invoice_item.GetInvoiceNumber(),product_name=invoice_item.GetPackageName()).first()
	if item is not None:
		return item.email
	else:
		return ""

if __name__ == "__main__":
	app.secret_key = 'A0ZKkjfiaZS6w3ibFLISFr98j/3yX R~XHH!jmN]LWX/,?RTfg97adfNF(#ihbwg'# you should change this
	# app.debug = True
	app.run(host='0.0.0.0',port=7000)

