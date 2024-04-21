import boto3
import pymysql as pms

from datetime import datetime, timedelta
from os import environ, getenv

def get_connection():
    password = __get_db_password()
    print("Connecting to database ", environ["DB_SCHEMA"])
    # Connect to the database
    connection = pms.connect(host=environ["DB_HOST"],
                                user=environ["DB_USER"],
                                password=environ["DB_PASS"],
                                database=environ["DB_SCHEMA"],
                                charset='utf8mb4',
                                cursorclass=pms.cursors.DictCursor,
                                ssl={"fake_flag_to_enable_tls":True})

    print("Connected.")

    return connection

def __get_db_password():
    sm_client = boto3.client("secretsmanager")
    secret_path = environ["DB_SECRET_NAME"]

    password = sm_client.get_secret_value(SecretId=secret_path)

    return password

def insert_distribution(conn, distribution_id, expiration_date, mailing_list, description, survey_id):
    
    query = """
        INSERT INTO distribution (id, expirationDate, mailingListId, description, surveyId)
        VALUES(%s, %s, %s, %s, %s) 
        ON DUPLICATE KEY UPDATE expirationDate=%s, description=%s
    """

    inputs = (distribution_id, expiration_date, mailing_list, description, survey_id, expiration_date, description)
    with conn.cursor() as cur:
        cur.execute(query, inputs)
        conn.commit()

def insert_distribution_list_many(conn, distribution_id, expiration_date, distribution_list):
    query = """
        INSERT INTO distribution_list
        (distributionId, participantId, surveyLink, surveyStatus, surveyDelivered, linkExpiration, externalDataReference)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE linkExpiration=%s, participantId=%s, surveyLink=%s
    """

    print(query)
    inputs = [
        (
            distribution_id, 
            distribution["contact_id"], 
            distribution['survey_link'],
            distribution['survey_status'],
            distribution['survey_delivered'],
            expiration_date,
            str(distribution['external_data_reference']),
            expiration_date,
            distribution["contact_id"], 
            distribution['survey_link']
        ) 
        for distribution in distribution_list
    ]
    
    print(inputs)

    with conn.cursor() as cur:
        cur.executemany(query, inputs)
        conn.commit()

def insert_distribution_list_many_alt(conn, distribution_id, distribution_list):
    query = """
        INSERT INTO distribution_list
        (distributionId, participantId, surveyLink, surveyStatus, surveyDelivered, linkExpiration, externalDataReference)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE linkExpiration=%s, participantId=%s, surveyLink=%s
    """

    with conn.cursor() as cur:
        for distribution in distribution_list:
            input = (
                        distribution_id, 
                        distribution["contact_id"], 
                        distribution['survey_link'],
                        distribution['survey_status'],
                        distribution['survey_delivered'],
                        distribution['link_expiration'],
                        distribution['external_data_reference'],
                        distribution['link_expiration'],
                        distribution["contact_id"], 
                        distribution['survey_link']
                    ) 
            cur.execute(query, input)
        conn.commit()
        
def update_text_message_id(conn, message_id, distribution_id, contact_id):
    query = """
        UPDATE distribution_list
        SET textMessageId = %s
        WHERE distributionId = %s AND participantId = %s
    """

    inputs = (message_id, distribution_id, contact_id)
    with conn.cursor() as cur:
        cur.execute(query, inputs)

def update_survey_delivered(conn, delivered, distribution_id, contact_id):
    
    query = """
        UPDATE distribution_list
        SET surveyDelivered = %s
        WHERE distributionId = %s AND participantId = %s
    """

    inputs = (delivered, distribution_id, contact_id)
    with conn.cursor() as cur:
        cur.execute(query, inputs)

def update_survey_status(conn, survey_status, distribution_id, contact_id):

    query = """
        UPDATE distribution_list
        SET surveyStatus = %s
        WHERE distributionId = %s AND participantId = %s
    """

    inputs = (survey_status, distribution_id, contact_id)
    with conn.cursor() as cur:
        cur.execute(query, inputs)
        conn.commit()

def update_survey_status_many(conn, survey_dict):
    """ Update many contact's survey status with dict:

    Exptected input:
    {
        "contact_id": "contactId",
        "distribution_id": "distributionId",
        "survey_status": 'SurveyFinished'
    }

    """

    query = """
        UPDATE distribution_list
        SET surveyStatus = %s
        WHERE distributionId = %s AND participantId = %s
    """

    inputs = [
        (
            survey["survey_status"],
            survey["distribution_id"],
            survey["contact_id"]
        )
        for survey in survey_dict
    ]
    with conn.cursor() as cur:
        cur.executemany(query, inputs)
        conn.commit()

def get_distribution_by_date(conn, start_date, end_date):
    print(start_date, end_date)
    query = "select * from distribution where expirationDate >= %s and expirationDate < %s;" 
    
    inputs = (start_date, end_date)

    results = []
    with conn.cursor() as cur:
        cur.execute(query, inputs)

        results = cur.fetchall()

    return results

def get_distribution_by_id(conn, distribution_id):
    query = "select * from distribution where id = %s;" 
    
    inputs = (distribution_id)

    results = []
    with conn.cursor() as cur:
        cur.execute(query, inputs)

        results = cur.fetchall()

    return results

def get_distribution_list_by_distribution_id(conn, distribution_id):
    query = "select * from distribution_list where distributionId = %s;" 
    
    inputs = (distribution_id)

    results = []
    with conn.cursor() as cur:
        cur.execute(query, inputs)

        results = cur.fetchall()

    return results


def get_distribution_list_by_expiration_date(conn, expiration_date):
    print (expiration_date)
    query = """SELECT *
    FROM distribution_list
    WHERE linkExpiration >= %s AND linkExpiration <= %s;""" 
    
    inputs = (expiration_date, expiration_date + timedelta(days=1))

    with conn.cursor() as cur:
        cur.execute(query, inputs)

        results = cur.fetchall()

    return results
    
def get_status(conn, tomorrow):
    query = """SELECT d.description, dl.* 
    FROM distribution_list as dl, distribution as d
    WHERE dl.distributionId = d.id AND dl.linkExpiration < %s
    ORDER BY dl.participantId, dl.linkExpiration;""" 
    
    input = (tomorrow)
    with conn.cursor() as cur: 
        cur.execute(query, input)

        results = cur.fetchall()

    return results