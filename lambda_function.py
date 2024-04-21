import json
import generate_links
import alt_flow
import send_text
import requests
from io import StringIO
import csv
import queries
from datetime import datetime, timedelta
import boto3
from time import sleep
from os import environ

def lambda_handler(event, context):
    c = queries.get_connection()
    if event["action"] is None:
        print("Action not specified")
        return
    
    if event["action"] == "generate":
        for survey in event["surveys"]:
            print("Generating survey")
            
            generate_links.generate_survey_links(
                survey["survey_id"], 
                survey["survey_description"], 
                survey["mailing_list_id"], 
                survey["expiration_date"])
    elif event["action"] == "start_text":
        send_text.start_text(c)
    elif event["action"] == "remind_text":
        send_text.reminder_check(c)
    elif event["action"] == "start_text_baseline":
        send_text.start_text_baseline(c, event["expiration_date"])
    elif event["action"] == "remind_text_baseline":
        send_text.reminder_check_baseline(c, event["expiration_date"])    
    elif event["action"] == "final_check":
        alt_flow.survey_check(c)
    elif event["action"] == "update_distribution":

        for distribution in event["distributions"]:
            print("Update distribution " + distribution["distribution_id"])
            expiration_date = alt_flow.update_distribution_email(c, distribution["distribution_id"], distribution["survey_id"])
            
            print("Update distribution list " + distribution["distribution_id"])
            alt_flow.update_distribution_list(c, distribution["distribution_id"], expiration_date, distribution["survey_id"])
    elif event["action"] == "export":
        export_to_s3(c)
    elif event["action"] == "generate_schema":
        queries.generate_schema_from_file(c, "./db/createInSMS.sql")
    else:
        print (f'Unknown command: {event["action"]}')
    
    return

def export_to_s3(c):
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    vals = queries.get_status(c, tomorrow)
    
    if len(vals) < 1:
        raise Exception("Not work")

    field_name = vals[0].keys()

    csv_buffer = StringIO()
    csv_writer = csv.DictWriter(csv_buffer, fieldnames=field_name) 
    
    csv_writer.writeheader()

    for val in vals:
        csv_writer.writerow(val)

    bucket = environ['S3_BUCKET_NAME']
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, f'export_{today.strftime("%Y_%m_%d")}.csv').put(Body=csv_buffer.getvalue())
