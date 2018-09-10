import requests
import bs4

def require_logged_in(func):
	def new(self, *args, **kwargs):
		if not self.logged_in: raise NotLoggedIn()
		else: return func(self, *args, **kwargs)
	return new

class InvalidLogin(Exception): pass
class NotLoggedIn(Exception): pass
class InvalidDomain(Exception): pass

class Scraper:
	PROTOCOL = 'https://'
	URL = '.schoolloop.com'

	HOME = '/portal/student_home'
	LOGIN = '/portal/guest_home?etarget=login_form'
	ASSIGNMENT = '/calendar/assignment_detail?d=x&id='
	CALENDAR = '/calendar/month?template=print'
	PROGRESS_REPORT = '/progress_report/report?&period_id='
	DOMAIN_CHECK = 'https://live.schoolloop.com/portal/school_list'
	LOGIN_CHECK = '/portal/login'

	def __init__(self, domain, logger=lambda x: x):
		self.logger = logger
		self.username = None
		self.domain = domain
		self.logged_in = False

		self.session = requests.Session()

	def log(self, *args):
		if self.logged_in: ps = '%s@' % self.username
		else: ps = ''

		pref = '[%s%s.schoolloop.com]' % (ps, self.domain)
		self.logger(pref, *args)

	def build_url(self, suffix):
		return Scraper.PROTOCOL + self.domain + Scraper.URL + suffix

	def login(self, username, password):
		self.username = username
		page = self.build_url(Scraper.HOME)
		resp = self.session.get(page)
		if resp.url == Scraper.DOMAIN_CHECK:
			raise InvalidDomain()
			return

		self.log('Connected to %s.schoolloop.com' % self.domain)

		soup = bs4.BeautifulSoup(resp.text, features='html.parser')
		form_data_id = soup.find('input', id='form_data_id').get('value')

		payload = {
			'login_name': self.username,
			'password': password,
			'form_data_id': form_data_id,
			'event_override': 'login'
		}

		self.log('Logging in as %s' % self.username)
		page = self.build_url(Scraper.LOGIN)
		resp = self.session.post(page, data=payload)

		if resp.url == self.build_url(Scraper.LOGIN_CHECK):
			self.logged_in = False
			raise InvalidLogin()
		else:
			self.logged_in = True
			self.log('Login successful')

	@require_logged_in
	def logout(self):
		self.session = requests.Session()
		self.username = None
		self.logged_in = False
		self.log('Session logged out')

	@require_logged_in
	def fetch_calendar(self):
		page = self.build_url(Scraper.CALENDAR)
		self.log('Fetching calendar from %s' % page)

		resp = self.session.get(page)
		soup = bs4.BeautifulSoup(resp.text, features='html.parser')

		get_id = lambda a: int(a['href'].split('=')[-1])

		classes = soup.find_all('div', {'class': 'cal_text_course'})
		assignments = soup.find_all('a', href=lambda s: 'assignment' in s)
		assignments = { get_id(a) : {'class': classes[i].text, 'name': a.text} for i,a in enumerate(assignments) }

		full_assignments = {}

		for idx, identifier in enumerate(assignments):
			info = assignments[identifier];


			page = self.build_url(Scraper.ASSIGNMENT + str(identifier))
			self.log('%s/%s\t scraping: %s' % (idx + 1, len(assignments), page))

			resp = self.session.get(page)
			soup = bs4.BeautifulSoup(resp.text, features='html.parser')

			description = soup.find('div', {'class': 'sllms-content-body'})
			description = description.text.strip('\n')

			due = soup.find_all('span', {'class': 'black'})
			due = due[1].text

			full_assignments[identifier] = {
				'class': info['class'],
				'title': info['name'],
				'info': description,
				'due': due
			}

		return full_assignments

	@require_logged_in
	def fetch_class_ids(self):
		page = self.build_url(Scraper.HOME)
		resp = self.session.get(page)
		soup = bs4.BeautifulSoup(resp.text, features='html.parser')

		classes = soup.find_all('a', text='Progress Report')
		classes = [ a.get('href').split('period_id=')[1] for a in classes ]
		classes = [ int(a.split('&')[0]) for a in classes ]

		return classes

	@require_logged_in
	def fetch_progress_report(self, period):
		page = self.build_url(Scraper.PROGRESS_REPORT + str(period))
		resp = self.session.get(page)
		soup = bs4.BeautifulSoup(resp.text, features='html.parser')

		general_body = soup.find('tbody', {'class': 'general_body'})
		assignment_trs = general_body.find_all('tr')

		print(len(assignment_trs 	))

		assignments = {}
		for assignment in assignment_trs:
			print(assignment)
			print('==============================')

# import main