
import logging
import boto3
from jinja2 import Environment, FileSystemLoader

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
        return response['MessageResponse']['Result'][destination_number]['MessageId']


def main():
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("surveyStart.txt")

    app_id = ""
    origination_number = ""
    destination_number = "" #participant.phoneNumber

    message_type = "TRANSACTIONAL"

    for participant in distribution_list:
        message = template.render(survey_link=participant["survey_link"])

        print("Sending SMS message.")
        message_id = send_sms_message(
            boto3.client('pinpoint'), app_id, origination_number, destination_number,
            message, message_type)
        print(f"Message sent! Message ID: {message_id}.")

        #TODO Update DB survey_sent = TRUE

if __name__ == '__main__':
    main()
