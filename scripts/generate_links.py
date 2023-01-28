""" Script to generate personal survey links for a mailing list.

"""

from QualtricsMessenger.api.qualtrics_client import Client
from pprint import pprint
from time import sleep
# def generate_survey_links (client, survey_id, mailing_list_id, expiration_date, description):
#     if survey_id is None:
#         raise Exception("Must have survey_id")
    
#     if mailing_list_id is None:
#         raise Exception("Must have mailing_list_id")
    
#     if expiration_date is None:
#         raise Exception("Must have expiration_date")
    
#     if description is None:
#         raise Exception("Must have description")

    

def create_survey_links(c, token):
    # participants = c.getParticipants(mailinglist_id="CG_UfKFyE4EYCZRvzz")
    response = c.create_survey_links("SV_77ozMThNJWlmyay", "CG_UfKFyE4EYCZRvzz", "2023-01-20 20:00:00", "lifestyles week 1 monda")

    return response["result"]["id"]

def update_distribution_list(c, token, distribution_id):
    response = c.get_contact_survey_links(distribution_id, "SV_77ozMThNJWlmyay")

    survey_list = []
    for element in response['result']['elements']:
        vals = {
            'contact_id': element["contactId"],
            'distribution_id': distribution_id,
            "survey_link": element["link"],
            'survey_status': 'not_sent',
            'survey_delivered': False,
        }

        survey_list.append(vals)
        
    return survey_list

if __name__ == '__main__':
    token = ""

    c = Client(api_token=token)

    distribution_id = create_survey_links(c, token)

    print(distribution_id)
    sleep(5)
    distribution_list = update_distribution_list(c, token, distribution_id)

    #TODO Update DB

    # Create message

    