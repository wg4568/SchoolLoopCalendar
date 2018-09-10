import schoolloop
import secrets
import json

client = schoolloop.Scraper('branham', logger=print)
client.login(secrets.USERNAME, secrets.PASSWORD)

calendar = client.fetch_calendar()
with open('calendar.json', 'w+') as f:
	json.dump(calendar, f)

client.logout()

# class_ids = client.fetch_class_ids()
# client.fetch_progress_report(class_ids[4])