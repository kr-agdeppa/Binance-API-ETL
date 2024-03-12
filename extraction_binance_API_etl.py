import boto3
from botocore.exceptions import ClientError
from dotenv import dotenv_values
from binance.spot import Spot
import json
import joblib

def get_secret(boto3_session):
    secret_name = "binance-apis"
    region_name = "ap-southeast-2"

    secrets_client = boto3_session.client(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = secrets_client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']

    return secret

def extract_data(boto3_session):
    SECRETS = json.loads(get_secret(boto3_session))

    BINANCE_API_KEY = SECRETS["BINANCE-API-KEY"]
    BINANCE_SECRET_KEY = SECRETS["BINANCE-SECRET-KEY"]

    binance_api_client = Spot(api_key=BINANCE_API_KEY, api_secret=BINANCE_SECRET_KEY)

    # Get klines of BTCUSDT at 1m interval
    api_response = binance_api_client.klines("BTCUSDT", "1d", limit=1000)

    joblib.dump(api_response, "BTCUSDT-PRICES.joblib")


def load_stagingarea():
    region_name = "ap-southeast-2"
    bucket_name = 'btc-prices-bucket'

    s3_client = session.client(
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        service_name='s3',
        region_name=region_name
        )   

    with open('BTCUSDT-PRICES.joblib', 'rb') as data:
        s3_client.upload_fileobj(data, bucket_name, 'objkeyprices')


if __name__ == "__main__":
    AWS_ACCESS_KEY = dotenv_values(".env.local")["AWS_ACCESS_KEY"]
    AWS_SECRET_KEY = dotenv_values(".env.local")["AWS_SECRET_KEY"]

    session = boto3.session.Session()

    extract_data(session)
    load_stagingarea()

    






