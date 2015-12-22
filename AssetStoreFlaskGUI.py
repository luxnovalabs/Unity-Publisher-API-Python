from flask import Flask
from flask import render_template
from flask import request, redirect, url_for, make_response, session
import datetime
import AssetStoreAPI
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

@app.template_filter('date_format')
def date_format(value):
	value = datetime.datetime.utcfromtimestamp(value)
	return value.strftime('%B %d, %Y')

if __name__ == "__main__":
	app.secret_key = 'A0ZKkjfiaZS6w3ibFLISFr98j/3yX R~XHH!jmN]LWX/,?RTfg97adfNF(#ihbwg'# you should change this
	app.debug = True
	app.run()

