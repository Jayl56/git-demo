import requests

TOKEN_URL = "http://169.254.169.254/latest/api/token"
METADATA_URL = "http://169.254.169.254/latest/meta-data"


def get_metadata():
    # Obtener token para IMDSv2
    token = requests.put(
        TOKEN_URL,
        headers={
            "X-aws-ec2-metadata-token-ttl-seconds": "21600"
        },
        timeout=2,
    )

    token.raise_for_status()

    headers = {
        "X-aws-ec2-metadata-token": token.text
    }

    # Obtener región
    region = requests.get(
        f"{METADATA_URL}/placement/region",
        headers=headers,
        timeout=2,
    )

    region.raise_for_status()

    # Obtener Availability Zone
    az = requests.get(
        f"{METADATA_URL}/placement/availability-zone",
        headers=headers,
        timeout=2,
    )

    az.raise_for_status()

    return {
        "region": region.text,
        "availability_zone": az.text,
    }