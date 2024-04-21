""" Script to generate personal survey links for a mailing list.
"""

from qualtrics_client import Client
from pprint import pprint
from time import sleep
import pymysql
import queries
from os import environ

def generate_survey_links (survey_id, survey_description, mailing_list_id, expiration_date):
    # Connect to the database
    connection = queries.get_connection()

    print("connected to database")
    # Create client for qualtrics API
    c = Client()

    print("Qualtrics client created")
    
    # Create personal links
    distribution_id = c.create_survey_links(survey_id, mailing_list_id, expiration_date, survey_description)
    
    print("Created distribution ", distribution_id)

    queries.insert_distribution(connection, distribution_id, expiration_date, mailing_list_id, survey_description, survey_id)
    sleep(2)
    
    print("Inserted to db")

    distribution_list = update_distribution_list(c, token, distribution_id, survey_id)

    print("Add distribution list ", distribution_list)

    queries.insert_distribution_list_many(connection, distribution_id, expiration_date, distribution_list)

    print("done generating links")


def update_distribution_list(c, token, distribution_id, survey_id):
    response = c.get_contact_survey_links(distribution_id, survey_id)

    survey_list = []
    for element in response:
        vals = {
            'contact_id': element["contactId"],
            'distribution_id': distribution_id,
            "survey_link": element["link"],
            'survey_status': 'NotSent',
            'survey_delivered': False,
            'external_data_reference': element['externalDataReference']
        }

        survey_list.append(vals)
        
    return survey_list
