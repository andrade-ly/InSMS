import pymysql as pms
from datetime import datetime, timedelta

from dotenv import load_dotenv, dotenv_values
from os import environ, getenv

def get_connection():
    config = dotenv_values(".env")
    token = config["Q_TOKEN"]
    mailing_list_id = config["MAILING_LIST_ID"]

    # Connect to the database
    connection = pms.connect(host=config["DB_HOST"],
                                user=config["DB_USER"],
                                password=config["DB_PASS"],
                                database=config["DB_SCHEMA"],
                                charset='utf8mb4',
                                cursorclass=pms.cursors.DictCursor)

    return connection

def insert_participants(conn, participant_list):
    """
    Insert a list of participants where the elements are dict of:
        {
            contactId: "",
            email: "",
            phone: ""
        }
    """

    query = """
        INSERT INTO participant (contactId, email, phone_number) values(%s, %s, %s) ON DUPLICATE KEY UPDATE contactId=contactId
    """

    inputs = [(participant['contactId'], participant['email'], participant['phone']) for participant in participant_list]
    with conn.cursor() as cur:
        cur.executemany(query, inputs)
        conn.commit()

def insert_distribution(conn, distribution_id, expiration_date, mailing_list, description, survey_id):
    
    query = """
        INSERT INTO distribution (id, expirationDate, mailingListId, description, surveyId)
        VALUES(%s, %s, %s, %s, %s) 
    """

    inputs = (distribution_id, expiration_date, mailing_list, description, survey_id)
    with conn.cursor() as cur:
        cur.execute(query, inputs)
        conn.commit()

def insert_distribution_list_many(conn, distribution_id, expiration_date, distribution_list):
    query = """
        INSERT INTO distribution_list
        (distributionId, participantId, surveyLink, surveyStatus, surveyDelivered, linkExpiration)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    inputs = [
        (
            distribution_id, 
            distribution["contact_id"], 
            distribution['survey_link'],
            distribution['survey_status'],
            distribution['survey_delivered'],
            expiration_date
        ) 
        for distribution in distribution_list
    ]

    with conn.cursor() as cur:
        cur.executemany(query, inputs)
        conn.commit()

def update_survey_delivered(conn, delivered, distribution_id, contact_id):
    
    query = """
        UPDATE distribution_list
        SET surveyDelivered = %s
        WHERE distributionId = %s AND contactId = %s
    """

    inputs = (delivered, distribution_id, contact_id)
    with conn.cursor() as cur:
        cur.execute(query, inputs)

def update_survey_status(conn, survey_status, distribution_id, contact_id):

    query = """
        UPDATE distribution_list
        SET surveyStatus = %s
        WHERE distributionId = %s AND contactId = %s
    """

    inputs = (survey_status, distribution_id, contact_id)
    with conn.cursor() as cur:
        cur.execute(query, inputs)
        conn.commit()

def get_distribution_by_date(conn, start_date, end_date):
    query = "select * from distribution where expirationDate >= %s and expirationDate <= %s;" 
    
    inputs = (start_date, end_date)

    results = []
    with conn.cursor() as cur:
        cur.execute(query, inputs)

        results = cur.fetchAll()

    return results

def get_distribution_by_id(conn, distribution_id):
    query = "select * from distribution where id = %s;" 
    
    inputs = (distribution_id)

    results = []
    with conn.cursor() as cur:
        cur.execute(query, inputs)

        results = cur.fetchAll()

    return results

def get_distribution_list_by_distribution_id(conn, distribution_id):
    query = "select * from distribution_list where distributionId = %s;" 
    
    inputs = (distribution_id)

    results = []
    with conn.cursor() as cur:
        cur.execute(query, inputs)

        results = cur.fetchAll()

    return results

def get_participants_survey_by_date(conn, expiration_date):
    query = """SELECT p.phone_number, d.surveyLink
    FROM distribution_list as d, participant as p 
    WHERE d.participantId = p.contactId  
    AND d.linkExpiration >= %s AND d.linkExpiration <= %s;""" 
    
    inputs = (expiration_date, expiration_date + timedelta(days=1))

    with conn.cursor() as cur:
        cur.execute(query, inputs)

        results = cur.fetchall()

    return results