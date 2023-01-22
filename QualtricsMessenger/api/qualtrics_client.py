import logging
import requests
from pprint import pprint 

class Client:
    def __init__(self, api_token=None, url = "https://duke.yul1.qualtrics.com/API/v3"):
        if api_token is None:
            raise Exception("API Token must be set")
        
        self.url = url
        self.api_token = api_token

    def get_participants(self, mailinglist_id, directory_id = 'POOL_3G9cvWCMcS1Xq68'):
        if mailinglist_id is None:
            raise Exception("Mailing List ID must be provided")

        baseUrl = "{0}/directories/{1}/mailinglists/{2}/contacts".format(self.url, directory_id, mailinglist_id)

        headers = {
            "x-api-token": self.api_token,
            }


        response = requests.get(baseUrl, headers=headers)

        return response.json()

    def create_survey_links(self, survey_id, mailinglist_id, expiration_date, description):
        baseUrl = f"{self.url}/distributions"

        headers = {
            "x-api-token": self.api_token,
            "content-type": "application/json",
            }

        post_data = {
            "expirationDate": expiration_date,
            "surveyId": survey_id,
            "linkType": "Individual",
            "description": description,
            "action": "CreateDistribution",
            "mailingListId": mailinglist_id
        }

        response = requests.post(baseUrl, headers=headers, json=post_data)

        print(response.json())

        return response.json()
    
    def get_contact_survey_links(self, distribution_id, survey_id):
        baseUrl = f"{self.url}/distributions/{distribution_id}/links?surveyId={survey_id}"

        headers = {
            "x-api-token": self.api_token,
            }

        response = requests.get(baseUrl, headers=headers)

        pprint(response.json())

        return response.json()