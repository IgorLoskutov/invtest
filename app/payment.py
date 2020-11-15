from decimal import Decimal
from requests import post
import json 
from datetime import datetime


from app import app, auth, db
from flask import g, request, url_for
from flask_login import current_user

from app.models import Currency, Order
import app.forms as forms


class Payment():
	sign_fields = {
		'pay': ['amount', 'currency', 'shop_id', 'shop_order_id'],
		'bill': ['shop_amount', 'shop_currency', 'shop_id', 'shop_order_id', 'payer_currency'],
		'invoice':['amount', 'currency', 'payway', 'shop_id', 'shop_order_id']
	}
	methods_map = {
		'EUR': 'pay',
		'USD': 'bill',
		'RUR': 'invoice'
	}
	piastrix_url = 'https://core.piastrix.com/{}/create'


	def __init__(self, form_data: dict):
		self.data = form_data
		self.curr = form_data.get('currency') or form_data.get('shop_currency')
		self.method = self.methods_map.get(Currency().query.filter(Currency.code == self.curr).first().name, 'invoice')
		self.fields = self.sign_fields[self.method]
		if not self.data.get('shop_order_id'):
			order = Order(
				amount = self.data['amount'],
	    		currency_id = Currency().query.filter(Currency.code == self.curr).first().id,
	    		stime = datetime.now(),
	    		user_id = current_user.id)
			db.session.add(order)
			db.session.commit()
			self.data['shop_order_id'] = order.id

		self.data.update({
			'shop_id': app.config['SHOP_ID'],
			})


	def prepare(self):
		self.res = {'tpl': f'{self.method}_confirm.html', 'data': {}, 'url': None}
		return getattr(self.__class__, self.method)(self)


	def pay(self):
		self.sign = auth.sign({k:v for k,v in self.data.items() if k in self.fields})
		self.data.update({'sign' : self.sign})
		form = forms.pay_form()
		form.amount.data = Decimal(self.data['amount'])
		form.currency.data = int(self.data['currency'])
		form.sign.data = self.data['sign']
		form.shop_order_id.data  = self.data['shop_order_id']
		form.shop_id.data = int(self.data['shop_id'])
		self.res.update({'data': form})
		return self.res


	def bill(self):
		if self.data.get('payer_currency'):
			self.sign = auth.sign({k:v for k,v in self.data.items() if k in self.fields})
			self.data.update({'sign' : self.sign})
			data = self._request_piastrix()
			if data.get('error_code', 0):
				self.res.update({'tpl': 'error.html', 'data': data})
				return self.res
			self.res.update({'url': data['data']['url']})
			return self.res
		
		self.data.update({
			'shop_amount': self.data.pop('amount'),
			'shop_currency': self.data.pop('currency'),
			})
		form=forms.bill_form()
		form.shop_amount.data = self.data['shop_amount']
		form.shop_currency.data = self.data['shop_currency']
		form.shop_order_id.data  = self.data['shop_order_id']
		form.shop_id.data = int(self.data['shop_id'])
		self.res.update({'data': form})
		return self.res


	def invoice(self):
		curr = Currency().query.filter(Currency.code == self.curr).first()
		self.data.update({
			'payway': curr.payway,
			'currency': curr.code,
			})
		self.sign = auth.sign({k:v for k,v in self.data.items() if k in self.fields})
		self.data.update({'sign' : self.sign, 'amount': str(self.data['amount'])})
		data = self._request_piastrix()
		if data.get('error_code', 0):
				self.res.update({'tpl': 'error.html', 'data': data})
				return self.res
		res.update({'data': data.get('data', {})})
		return res


	def _request_piastrix(self):
		resp = post(
			url = self.piastrix_url.format(self.method), 
			headers={'content-type': 'application/json'}, 
			json=self.data
			) 
		return json.loads(resp.content.decode())


	