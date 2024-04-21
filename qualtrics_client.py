import boto3
import logging
import requests
from pprint import pprint 
from os import environ
import json

class Client:
    def __init__(self, api_token=None, customer_name = None):
        
        if api_token is None:
            raise Exception("API Token must be set")
        
        url = "https://{}.yul1.qualtrics.com/API/v3"
        if customer_name is not None:
            url = url.format(customer_name)
        elif environ["QUALTRICS_CUSTOMER_NAME"] is not None:
            url = url.format(environ["QUALTRICS_CUSTOMER_NAME"])
        else:
            raise Exception("Must supply your customer name in either the customer_name parameter or setting the environment variable QUALTRICS_CUSTOMER_NAME")

        self.url = url
        self.api_token = self.__get_api_token()

    def __get_api_token(self):
        client = boto3.client("secretsmanager")
        secret_path = environ["API_SECRET_NAME"]

        get_secret_value_response = sm_client.get_secret_value(SecretId=secret_path)

        print(f"Getting secret from {secret_path}")
        get_secret_value_response = sm_client.get_secret_value(SecretId=secret_path)
        
        json_response = json.loads(get_secret_value_response["SecretString"])
        
        return json_response["password"]

    def get_participant(self, contact_id, directory_id):
        if contact_id is None:
            raise Exception("Contact ID must be provided")
        if directory_id is None:
            raise Exception("Directory ID must be provided")
        
        baseUrl = "{0}/directories/{1}/contacts/{2}".format(self.url, directory_id, contact_id)

        headers = {
            "x-api-token": self.api_token,
            }

        res = requests.get(baseUrl, headers=headers)

        if not res.ok:
            raise Exception(res.raise_for_status())
        
        response = res.json()
        result = response['result']

        return result

    def get_participants(self, mailinglist_id, directory_id = 'POOL_3G9cvWCMcS1Xq68'):
        if mailinglist_id is None:
            raise Exception("Mailing List ID must be provided")

        baseUrl = "{0}/directories/{1}/mailinglists/{2}/contacts".format(self.url, directory_id, mailinglist_id)

        headers = {
            "x-api-token": self.api_token,
            }

        res = requests.get(baseUrl, headers=headers)

        if not res.ok:
            raise Exception(res.raise_for_status())
        
        response = res.json()
        results = response['result']['elements']
        while response['result']['nextPage']:           
            response = requests.get(response['result']['nextPage'], headers=headers).json()
            results.extend(response['result']['elements'])

        return results

    def create_survey_links(self, survey_id, mailinglist_id, expiration_date, description):
        if survey_id is None:
            raise Exception("Must have survey_id")
    
        if mailinglist_id is None:
            raise Exception("Must have mailinglist_id")
        
        if expiration_date is None:
            raise Exception("Must have expiration_date")
        
        if description is None:
            raise Exception("Must have description")
        
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

        print("Sending request to ", baseUrl)
        response = requests.post(baseUrl, headers=headers, json=post_data).json()

        print("Received response ", response)
        return response['result']['id']
    
    def get_contact_survey_links(self, distribution_id, survey_id):
        baseUrl = f"{self.url}/distributions/{distribution_id}/links?surveyId={survey_id}"

        headers = {
            "x-api-token": self.api_token,
            }

        response = requests.get(baseUrl, headers=headers).json()
        print(response)
        results = response['result']['elements']
        while response['result']['nextPage']:           
            response = requests.get(response['result']['nextPage'], headers=headers).json()
            results.extend(response['result']['elements'])

        return results
        
    def get_distribution_by_email(self, distribution_id, survey_id):
        baseUrl = f"{self.url}/distributions/{distribution_id}?surveyId={survey_id}"

        headers = {
            "x-api-token": self.api_token,
            }

        response = requests.get(baseUrl, headers=headers).json()
        
        result = response['result']
        
        return result
        

    def get_distribution_history(self, distribution_id):
        """
        Returns 
        {
            "result": {
                "elements": [
                    {
                        "contactId": "CID_3yJ86kfnM89U1Vk",
                        "contactLookupId": "CGC_jsMDpDZo38Q6HOx",
                        "distributionId": "EMD_q49DwTeL57FFPCj",
                        "status": "Pending",
                        "surveyLink": "https://duke.qualtrics.com/jfe/form/SV_77ozMThNJWlmyay?Q_CHL=gl&Q_DL=EMD_q49DwTeL57FFPCj_77ozMThNJWlmyay_CGC_jsMDpDZo38Q6HOx&_g_=g",
                        "contactFrequencyRuleId": null,
                        "responseId": null,
                        "responseCompletedAt": null,
                        "sentAt": "2023-01-12T03:18:49.180Z",
                        "openedAt": null,
                        "responseStartedAt": null,
                        "surveySessionId": null
                    }
                ],
                "nextPage": null
            },
            "meta": {
                "requestId": "a396740d-59ba-4d69-ab4c-0bdd47110b2a",
                "httpStatus": "200 - OK"
            }
        }
        """
        if distribution_id is None:
            raise Exception("distribution_id is expected")
        baseUrl = f"{self.url}/distributions/{distribution_id}/history"

        headers = {
            "x-api-token": self.api_token,
            }

        response = requests.get(baseUrl, headers=headers).json()

        results = response['result']['elements']
        while response['result']['nextPage']:           
            response = requests.get(response['result']['nextPage'], headers=headers).json()
            results.extend(response['result']['elements'])

        return results