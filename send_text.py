from qualtrics_client import Client

import logging
import boto3
from jinja2 import Environment, FileSystemLoader

from datetime import date, datetime, timedelta
from time import sleep
import queries
from os import environ
import re

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def send_sms_message(
        pinpoint_client, app_id, origination_number, destination_number, message,
        message_type):
    """
    Sends an SMS message with Amazon Pinpoint.

    :param pinpoint_client: A Boto3 Pinpoint client.
    :param app_id: The Amazon Pinpoint project/application ID to use when you send
                   this message. The SMS channel must be enabled for the project or
                   application.
    :param destination_number: The recipient's phone number in E.164 format.
    :param origination_number: The phone number to send the message from. This phone
                               number must be associated with your Amazon Pinpoint
                               account and be in E.164 format.
    :param message: The content of the SMS message.
    :param message_type: The type of SMS message that you want to send. If you send
                         time-sensitive content, specify TRANSACTIONAL. If you send
                         marketing-related content, specify PROMOTIONAL.
    :return: The ID of the message.
    """
    try:
        response = pinpoint_client.send_messages(
            ApplicationId=app_id,
            MessageRequest={
                'Addresses': {destination_number: {'ChannelType': 'SMS'}},
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': message,
                        'MessageType': message_type,
                        'OriginationNumber': origination_number}}})
    except ClientError:
        logger.exception("Couldn't send message.")
        raise
    else:
        return response['MessageResponse']['Result'][destination_number]['DeliveryStatus']

def reminder_check(connection):
    directory_id = environ["DIRECTORY_ID"]

    # Create client for qualtrics API
    c = Client()

    today = date.today()
    tomorrow = today + timedelta(days=1)
    distributions = queries.get_distribution_by_date(connection, today, tomorrow)

    reminder_list = []
    survey_finished_participants = []

    print(distributions)
    for distribution in distributions:
        surveys = c.get_distribution_history(distribution_id=distribution["id"])
        
        for survey in surveys:
            if survey['status'] != 'SurveyFinished':
                participant = c.get_participant(survey['contactId'], directory_id)

                reminder_list.append({
                    'survey_link': survey['surveyLink'],
                    'phone_number': participant["phone"],
                    "contact_id": survey['contactId'],
                    "distribution_id": distribution["id"],
                    "survey_status": survey['status']
                })
            else:
                survey_finished_participants.append({
                    "contact_id": survey['contactId'],
                    "distribution_id": distribution["id"],
                    "survey_status": survey['status']
                })
    
    if reminder_list:
        rem_list = reminder_text(reminder_list)
        queries.update_survey_status_many(connection, reminder_list)
    
    if survey_finished_participants:
        queries.update_survey_status_many(connection, survey_finished_participants)

def reminder_text(reminder_list):
    environment = Environment(loader=FileSystemLoader("./"))
    template = environment.get_template("surveyReminder.txt")

    directory_id = environ["DIRECTORY_ID"]
    app_id = environ["PROJECT_ID"]
    origination_number = environ["ORIGINATION_NUMBER"]
    message_type = "PROMOTIONAL"

    for participant in reminder_list:
        message = template.render(survey_link=participant["survey_link"])

        
        if participant["phone_number"] == "" or participant["phone_number"] is None:
            continue
        destination_number = normalize_number(participant["phone_number"])

        if not verify_number(destination_number):
            print(f"Unable to send - bad number for {survey['participantId']}")
            participant["survey_status"] = "TextFailedToSend"
            # queries.update_survey_delivered(conn, False, survey['distributionId'], survey['participantId'])
            continue
        print(f"Sending reminder message to {participant['contact_id']}")
        message_id = send_sms_message(
            boto3.client('pinpoint'), app_id, origination_number, destination_number,
            message, message_type)
        print(f"Message sent! Message ID: {message_id}.")
        sleep(2)
        #TODO Update DB survey_sent = TR
    return reminder_list

def start_text(conn):
    environment = Environment(loader=FileSystemLoader("./"))
    template = environment.get_template("surveyStart.txt")

    directory_id = environ["DIRECTORY_ID"]
    app_id = environ["PROJECT_ID"]
    origination_number = environ["ORIGINATION_NUMBER"]

    message_type = "PROMOTIONAL"

    c = Client()

    distribution_list = queries.get_distribution_list_by_expiration_date(conn, date.today())

    print(f"Sending text to {distribution_list}")
    for survey in distribution_list:
        try:
            participant = c.get_participant(survey['participantId'], directory_id)
            message = template.render(survey_link=survey["surveyLink"])
    
            if participant["phone"] == "" or participant["phone"] is None:
                continue
        
            destination_number = normalize_number(participant["phone"])
            
            if not verify_number(destination_number):
                print(f"Unable to send - bad number for {survey['participantId']}")
                queries.update_survey_delivered(conn, False, survey['distributionId'], survey['participantId'])
                continue
    
            print(f"Sending SMS message to {survey['participantId']}")
            message_id = send_sms_message(
                boto3.client('pinpoint'), app_id, origination_number, destination_number,
                message, message_type)
            print(f"Message status: {message_id}.")
    
            #Update DB surveyDelivered = TRUE
            # queries.update_text_message_id(conn, message_id, survey['distributionId'], survey['participantId'])
            queries.update_survey_delivered(conn, True, survey['distributionId'], survey['participantId'])
            
            sleep(2)
        except:
            continue

def start_text_baseline(conn, expiration_date):
    environment = Environment(loader=FileSystemLoader("./"))
    template = environment.get_template("surveyStart.txt")

    directory_id = environ["DIRECTORY_ID"]
    app_id = environ["PROJECT_ID"]
    origination_number = environ["ORIGINATION_NUMBER"]

    message_type = "PROMOTIONAL"

    c = Client()

    exp_datetime = datetime.strptime(expiration_date, '%m/%d/%Y')

    distribution_list = queries.get_distribution_list_by_expiration_date(conn, exp_datetime)

    print(distribution_list)
    for survey in distribution_list:
        try:
            participant = c.get_participant(survey['participantId'], directory_id)
            message = template.render(survey_link=survey["surveyLink"])
    
            if participant["phone"] == "" or participant["phone"] is None:
                continue
        
            destination_number = normalize_number(participant["phone"])
    
            print (message)
            if not verify_number(destination_number):
                print(f"Unable to send - bad number for {survey['participantId']}")
                queries.update_survey_delivered(conn, False, survey['distributionId'], survey['participantId'])
                continue
    
            print("Sending SMS message.")
            message_id = send_sms_message(
                boto3.client('pinpoint'), app_id, origination_number, destination_number,
                message, message_type)
            print(f"Message Status: {message_id}.")
    
            #Update DB surveyDelivered = TRUE
            # queries.update_text_message_id(conn, message_id, survey['distributionId'], survey['participantId'])
            queries.update_survey_delivered(conn, True, survey['distributionId'], survey['participantId'])
        except Exception as e:
            print(e)
            continue

def reminder_check_baseline(connection, expiration_date):
    directory_id = environ["DIRECTORY_ID"]

    # Create client for qualtrics API
    c = Client()

    exp_datetime = datetime.strptime(expiration_date, '%m/%d/%Y')
    tomorrow = exp_datetime + timedelta(days=1)
    distributions = queries.get_distribution_by_date(connection, exp_datetime, tomorrow)

    reminder_list = []
    survey_finished_participants = []

    print(distributions)
    for distribution in distributions:
        surveys = c.get_distribution_history(distribution_id=distribution["id"])
        
        for survey in surveys:
            if survey['status'] != 'SurveyFinished':
                participant = c.get_participant(survey['contactId'], directory_id)

                reminder_list.append({
                    'survey_link': survey['surveyLink'],
                    'phone_number': participant["phone"],
                    "contact_id": survey['contactId'],
                    "distribution_id": distribution["id"],
                    "survey_status": survey['status']
                })
            else:
                survey_finished_participants.append({
                    "contact_id": survey['contactId'],
                    "distribution_id": distribution["id"],
                    "survey_status": survey['status']
                })
    
    if reminder_list:
        rem_list = reminder_text(reminder_list)
        queries.update_survey_status_many(connection, reminder_list)
    
    if survey_finished_participants:
        queries.update_survey_status_many(connection, survey_finished_participants)

def normalize_number(phone_number):
    normalized_number = re.sub('[ -]', '', phone_number)
    
    matched_format = re.match(r"(\+)?(1)?\d{10}$", normalized_number)
    add_plus = "+" if matched_format.groups()[0] is None else ""
    add_one = "1" if matched_format.groups()[1] is None else ""
    return f"{add_plus}{add_one}{normalized_number}"
    
def verify_number(number):
    return re.match(r"^\+1\d{10}$", number) is not None