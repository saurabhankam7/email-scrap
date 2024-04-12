import imaplib
import email
from datetime import datetime
import mysql.connector

def fetch_emails(mode, date_str=None):
    # IMAP settings
    username = 'saurabhankam111@gmail.com'
    password = 'rraz tzmw itvq htqj'
    imap_server = 'imap.gmail.com'
    mailbox = 'INBOX'
    print("Email Connected")

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(username, password)
    mail.select(mailbox)

    if mode == 'specified_date':
        # Convert date_str to datetime object
        from_date = datetime.strptime(date_str, '%Y-%m-%d')

        # Search for emails from the specified date to the current date
        date_query = '(SINCE {from_date})'.format(from_date=from_date.strftime('%d-%b-%Y'))
    elif mode == 'today':
        # Get today's date
        today_date = datetime.today().strftime('%d-%b-%Y')
        date_query = '(SINCE {today_date})'.format(today_date=today_date)
    else:
        print("Invalid mode specified.")
        return []
    
    # search_query = f'X-GM-RAW "label:inbox -label:social -label:promotions -label:updates -label:forums" {date_query}'
    # Search for emails based on the date query
    result, data = mail.search(None, date_query)

    # Fetch email ids
    email_ids = data[0].split()

    emails = []
    for email_id in email_ids:
        # Fetch email data
        result, data = mail.fetch(email_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract relevant information from the email
        sender = msg['from']
        receivers = msg['to']
        subject = msg['subject']
        date = msg['date']

        emails.append({'Sender': sender, 'Receiver': receivers, 'Subject': subject, 'Date': date})

    # Close the connection
    mail.close()
    mail.logout()

    return emails

def insert_emails_to_database(emails):
    db_connection = mysql.connector.connect(user='root', password='rational',host='localhost',database='demo1')
    cur = db_connection.cursor()
    for email_data in emails:
        sender = email_data['Sender']
        receiver = email_data['Receiver']
        subject = email_data['Subject']
        date1 = email_data['Date']
        sql = "INSERT INTO email2 (sender, receiver, subject, date1) VALUES (%s, %s, %s, %s)"
        values = (sender, receiver, subject, date1)
        try:
            cur.execute(sql, values)
            db_connection.commit()  # Commit changes to the database
        except mysql.connector.Error as err:
            print("Error inserting data:", err)
    cur.close()
    db_connection.close()

# Example usage
mode = 'today'  # 'specified_date' for a specified date or 'today' for today's date
date_str = '2024-04-05'  # Specify the date if mode is 'specified_date'
emails = fetch_emails(mode, date_str)
for email_data in emails:
    print("Sender:", email_data['Sender'])
    print("Receiver:", email_data['Receiver'])
    print("Subject:", email_data['Subject'])
    print("Date:", email_data['Date'])

# Insert emails into the database
insert_emails_to_database(emails)
