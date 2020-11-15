from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Required
from app.models import Currency

class login_form(FlaskForm):
	username = StringField('Имя пользователя', validators=[DataRequired()])
	password = PasswordField('Пароль', validators=[DataRequired()])
	remember_me = BooleanField('Запомнить меня')
	submit = SubmitField('Войти')

class payment_form(FlaskForm):
	amount = DecimalField('Сумма платежа', validators=[DataRequired()])
	currency = SelectField('Валюта', choices=[(c.code, c.name) for c in Currency.query.all()], validators=[Required()])
	description = TextAreaField('Описание товара')
	submit = SubmitField('Подтвердить платёж')

class pay_form(payment_form):
	sign = StringField('signature', validators=[DataRequired()])
	shop_id = IntegerField('Идентификатор магазина', validators=[DataRequired()])
	shop_order_id = StringField('Номер заказа', validators=[DataRequired()])
	currency = IntegerField('Код Валюты', validators=[DataRequired()])

class bill_form(payment_form):
	shop_id = IntegerField('Идентификатор магазина', validators=[DataRequired()])
	shop_order_id = StringField('Номер заказа', validators=[DataRequired()])
	shop_currency = IntegerField('Код валюты зачисления', validators=[DataRequired()])
	shop_amount = DecimalField('Сумма к зачислению', validators=[DataRequired()])
	payer_currency = SelectField('Валюта списания', choices=[(c.code, c.name) for c in Currency.query.all()], validators=[Required()])