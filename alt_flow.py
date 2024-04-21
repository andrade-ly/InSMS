from qualtrics_client import Client

import boto3

from datetime import datetime, timedelta
import queries
from os import environ
from dateutil import tz

from botocore.exceptions import ClientError

def update_distribution_email(connection, distribution_id, survey_id):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')

    c = Client()

    # Create personal links
    distribution_data = c.get_distribution_by_email(distribution_id, survey_id)
    utc = datetime.strptime(distribution_data["surveyLink"]["expirationDate"], "%Y-%m-%dT%H:%M:%SZ")
    
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    expiration_date = utc.astimezone(to_zone)
    
    survey_description = distribution_data["headers"]["subject"]
    mailing_list_id = distribution_data["recipients"]["mailingListId"]
    queries.insert_distribution(connection, distribution_id, expiration_date, mailing_list_id, survey_description, survey_id)
    
    return expiration_date
    
def update_distribution_list(connection, distribution_id, expiration_date, survey_id):
    directory_id = environ["DIRECTORY_ID"]

    # Create client for qualtrics API
    c = Client()
    
    print("getting surveys")
    response = c.get_contact_survey_links(distribution_id, survey_id)

    print(f"Got this many survey: {len(response)}")
    survey_list = []
    
    for element in response:
        vals = {
            'contact_id': element["contactId"],
            'distribution_id': distribution_id,
            "survey_link": element["link"],
            'survey_status': element["status"],
            'survey_delivered': True,
            'link_expiration': expiration_date,
            'external_data_reference': element["externalDataReference"]
        }

        survey_list.append(vals)
    print("inserting into distribution list")

    queries.insert_distribution_list_many_alt(connection, distribution_id, survey_list)
    print("finished inserting into distribution list")


def survey_check(connection):
    directory_id = environ["DIRECTORY_ID"]

    # Create client for qualtrics API
    c = Client()

    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    distributions = queries.get_distribution_by_date(connection, datetime(2023, 3, 2), tomorrow)

    status_list = []

    for distribution in distributions:
        surveys = c.get_distribution_history(distribution_id=distribution["id"])
        print(surveys)
        for survey in surveys:
            
            status_list.append({
                "contact_id": survey['contactId'],
                "distribution_id": distribution["id"],
                "survey_status": survey['status']
            })
                
    queries.update_survey_status_many(connection, status_list)

