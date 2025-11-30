from twilio.rest import Client

# Replace with your actual SID and token


client = Client(account_sid, auth_token)

call = client.calls.create(
    twiml='<Response><Say>Hello is this Aanirudh nice to see you  ?</Say></Response>',
    to='+91 9080904517',       # Your verified number (e.g., your mobile number)
    from_='+16205511790'      # Your Twilio number
)

print("Call initiated. SID:", call.sid)


# to run this code --->  python call.py