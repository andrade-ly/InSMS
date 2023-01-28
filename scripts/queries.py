import pymysql

def insert_participant(conn, participant_list):
    """
    Insert a list of participants where the elements are dict of:
        {
            contact_id: "",
            email: "",
            phone_number: ""
        }
    """

    query = """
        INSERT INTO participant (contactId, email, phone_number) values(%s, %s, %s)
    """

    with conn.cursor() as cur:
        for participant in participant_list:
            inputs = (participant['contact_id'], participant['email'], participant['phone_number'])
            cur.execute(query, inputs)
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

def insert_distribution_list(conn, distribution_id, expiration_date, distribution_list):

    query = """
        INSERT INTO distribution_list
        (distributionId, participantId, surveyLink, surveyStatus, surveyDelivered, linkExpiration)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    with conn.cursor() as cur:
        for gen_link in distribution_list:
            inputs = (
                distribution_id, 
                gen_link["contactId"], 
                gen_link['surveyLink'],
                'NotStarted',
                False,
                expiration_date
            )

            cur.execute(query, inputs)
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

def get_distribution_by_date(conn, date):
    pass

def get_distribution_by_id(conn, date):
    pass

def get_distribution_list_by_contact_id(conn, contact_id):
    pass