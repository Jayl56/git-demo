# EC2 Region API

Simple FastAPI application that returns the AWS Region and Availability Zone where it is running.

## Requirements

- Python 3.12+
- FastAPI
- Uvicorn
- Requests

## Install

```bash
pip install -r requirements.txt
```

## Run locally

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```
http://localhost:8000
```

> **Note:** The metadata endpoint only works when the application is running on an Amazon EC2 instance with Instance Metadata Service (IMDSv2) enabled.

## Endpoint

```
GET /
```

Example response:

```json
{
    "region": "us-east-1",
    "availability_zone": "us-east-1a"
}
```

## Build

Generate the deployable artifact:

```bash
./build.sh
```

The generated artifact will be located in:

```
dist/app.zip
```