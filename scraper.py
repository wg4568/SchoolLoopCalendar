import configparser
import requests
import bs4

config = configparser.ConfigParser()
config.read_file(open('settings.cfg'))

LOGIN = '/portal/guest_home?etarget=login_form'
ASSIGNMENT = '/calendar/assignment_detail?d=x&id='
CALENDAR = '/calendar/month?template=print'

URL = 'https://' + config.get('SCHOOLLOOP', 'domain') + '.schoolloop.com'
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

def get_assignment_list():
	resp = session.get(URL + CALENDAR)
	soup = bs4.BeautifulSoup(resp.text, features='html.parser')

	get_id = lambda a: int(a['href'].split('=')[-1])

	classes = soup.find_all('div', {'class': 'cal_text_course'})
	assignments = soup.find_all('a', href=lambda s: 'assignment' in s)
	assignments = { get_id(a) : {'class': classes[i].text, 'name': a.text} for i,a in enumerate(assignments) }

	full_assignments = {}

	for identifier in assignments:
		info1 = assignments[identifier];
		info2 = get_assignment_info(identifier)

		full_assignments[identifier] = {
			'class': info1['class'],
			'title': info1['name'],
			'due': info2['due'],
			'info': info2['info']
		}

	return full_assignments

def get_assignment_info(identifier):
	resp = session.get(URL + ASSIGNMENT + str(identifier))
	soup = bs4.BeautifulSoup(resp.text, features='html.parser')

	info = soup.find('div', {'class': 'sllms-content-body'})
	info = info.text.strip('\n')

	due = soup.find_all('span', {'class': 'black'})
	due = due[1].text

	return {'due': due, 'info': info}

form_data_id = get_form_data_id()

login(USERNAME, PASSWORD, form_data_id)

assignments = get_assignment_list()

for a in assignments:
	print(assignments[a]['class'], '-', assignments[a]['title'], 'DUE:', assignments[a]['due'])
	print(assignments[a]['info'])
	print('====================')