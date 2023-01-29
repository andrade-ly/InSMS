""" Script to generate personal survey links for a mailing list.
"""

from QualtricsMessenger.api.qualtrics_client import Client
from pprint import pprint
from time import sleep
import pymysql
import queries
from dotenv import load_dotenv, dotenv_values
from os import environ, getenv

def generate_survey_links (client, survey_id, mailing_list_id, expiration_date, description):
    response = c.create_survey_links(survey_id, mailing_list_id, expiration_date, description)

    return response

def update_distribution_list(c, token, distribution_id):
    response = c.get_contact_survey_links(distribution_id, "SV_77ozMThNJWlmyay")

    survey_list = []
    for element in response:
        vals = {
            'contact_id': element["contactId"],
            'distribution_id': distribution_id,
            "survey_link": element["link"],
            'survey_status': 'NotSent',
            'survey_delivered': False,
        }

        survey_list.append(vals)
        
    return survey_list

if __name__ == '__main__':
    config = dotenv_values(".env")
    token = config["Q_TOKEN"]
    mailing_list_id = config["MAILING_LIST_ID"]

    # Connect to the database
    connection = queries.get_connection()

    # Create client for qualtrics API
    c = Client(api_token=token)

    # Get participants for the mailing ID and update database
    participants = c.get_participants(mailing_list_id)
    queries.insert_participants(connection, participants)

    # Create
    survey_id = config["SURVEY_ID"]
    expiration_date = "2023-02-20 20:00:00"
    description = "lifestyles week 1 monday"
    distribution_id = c.create_survey_links(survey_id, mailing_list_id, expiration_date, description)

    queries.insert_distribution(connection, distribution_id, expiration_date, mailing_list_id, description, survey_id)
    sleep(2)

    distribution_list = update_distribution_list(c, token, distribution_id)

    queries.insert_distribution_list_many(connection, distribution_id, expiration_date, distribution_list)



    