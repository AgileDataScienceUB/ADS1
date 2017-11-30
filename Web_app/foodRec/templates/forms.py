from wtforms import Form 
from wtforms import TextAreaField, TextField, FloatField, BooleanField, SelectField
from wtforms.validators import Length, NumberRange,required
from wtforms import PasswordField

class ProductForm(Form):
  name = TextField('Name', [Length(max=255)])
  description = TextAreaField('Description')
  price = FloatField('price',[NumberRange(0.00),required()] )

class LoginForm(Form):
    """Render HTML input for user login form.

    Authentication (i.e. password verification) happens in the view function.
    """
    username = TextField('Username', [required()])
    password = PasswordField('Password', [required()])

class RegistrationForm(Form):
    username = TextField('Username', [required()])
    password = PasswordField('Password', [required()])
    repeatPassword = PasswordField('Repeat Password', [required()])
	
class FilterForm(Form):
    vegan = BooleanField('Vegan')
    italian = BooleanField('Italian')
    time = SelectField('Time of preparation')
    ingredients = SelectField('Number of ingredients')
    discard = TextField('Discard ingredients')