# Get DB
1. Create ORM objects for each table
    - participant
    - distributions
    - distribution_list (holds generated links, distribution to participant, and survey status)

# Create distributions
1. Get following parameters from user:
    - Survey ID
    - Mailing list ID
    - Expiration Date
    - Description
    - Text message
2. Use mailing list ID to populate participant table if it doesn't already exist
3. Post request to https://duke.yul1.qualtrics.com/API/v3/distributions to create distribution ID (EMD_xxx)
4. Record distribution ID in distribution with:
    - id
    - expirationDate
    - mailingListId
    - description
5. Get list of generated links from https://duke.yul1.qualtrics.com/API/v3/distributions/<distributionId>/links?surveyId=<surveyId>
6. for each item in res['result']['elements'], record into `distribution_list` table:
    - distributions_id
    - participant_contactId as contactId
    - `link` as surveyLink
    - `status` as surveyStatus
    - surveyDelivered set to `FALSE`
7. For each entry in `distribution_list`, call PinPoint to schedule text message with Text Message parameter:
    - Use expiration date @ 5AM EST, 10 UTC to send `messages/surveyStart` with templated survey link

# Check status

1. create schedule for Mondays and Fridays @2PM EST run check status script
2. Query database to get `id` from `distributions` where `expirationDate` = today 
3. call distribution history with https://duke.yul1.qualtrics.com/API/v3/distributions/<distributionId>/history
4. For each response in response['result']['elements'] (as dh):
    - if dh['status'] != 'SurveyFinished' 
        - Get dh['contactId']
        - select phone_number from participant where contactId = contactId
        - call pinpoint to schedule text with `surveyReminder` using survey link as template
    - else update `surveyStatus` = `FINISHES` where contactId = contactId and distributions_id = distributionId from distribution_list

# Last check

1. create schedule for Mondays and Fridays @ 5PM to update survey completion status
 