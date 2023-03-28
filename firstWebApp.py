import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth

CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
SCOPES = ['https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile']
REDIRECT_URI = 'https://localhost:8501f/' # Make sure this URI is authorized in your Google Cloud Console

# @st.cache(allow_output_mutation=True)
def get_credentials():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentialsStreamlit.json', SCOPES)
    authorization_url, state = flow.authorization_url(
        access_type='offline', include_granted_scopes='true'
    )

    # flow.fetch_token(authorization_response=authorization_url)

    st.markdown(f"Please authorize the app [here]({authorization_url})")
    response_url = st.text_input("Enter the URL you were redirected to:")

    flow.fetch_token(authorization_response=response_url)

    credentials = flow.credentials
    return credentials

# st.markdown(f"Please authorize the app [here]({authorization_url})")
# response_url = st.text_input("Enter the URL you were redirected to:")

creds = get_credentials()

if not creds.valid:
    creds.refresh(google.auth.transport.requests.Request())

st.write(f"Access token: {creds.token}")
st.write(f"Refresh token: {creds.refresh_token}")
st.write(f"Expires at: {creds.expiry}")
st.write(f"Scopes: {creds.scopes}")
st.write(f"ID token: {creds.id_token}")