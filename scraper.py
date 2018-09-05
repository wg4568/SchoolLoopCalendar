import configparser
import re
import requests
import bs4

config = configparser.ConfigParser()
config.read_file(open('settings.cfg'))

LOGIN = '/portal/guest_home?etarget=login_form'
CALENDAR = '/calendar/month?template=print'

URL = config.get('SCHOOLLOOP', 'url').rstrip('/')
USERNAME = config.get('SCHOOLLOOP', 'username')
PASSWORD = config.get('SCHOOLLOOP', 'password')

session = requests.Session()

def get_form_data_id():
	resp = session.get(URL)
	soup = bs4.BeautifulSoup(resp.text, features='html.parser')

	form_data_id = soup.find('input', id='form_data_id').get('value')
	return form_data_id

def login(username, password, form_data_id):
	payload = {
		'login_name': username,
		'password': password,
		'form_data_id': form_data_id,
		'event_override': 'login'
	}

	resp = session.post(URL + LOGIN, data=payload)

def get_assignments():
	resp = session.get(URL + CALENDAR)
	soup = bs4.BeautifulSoup(resp.text, features='html.parser')

	assignments = soup.find_all('a', href=lambda s: 'assignment' in s)
	assignments = [ a['href'] for a in assignments ]

	return assignments

form_data_id = get_form_data_id()

login(USERNAME, PASSWORD, form_data_id)

assignments = get_assignments()
print(assignments)