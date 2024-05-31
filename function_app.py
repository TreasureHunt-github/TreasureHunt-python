import logging
import azure.functions as func


# API
import pytest
import requests
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Header, APIRouter, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Data formatting
from pydantic import BaseModel
from typing import List

# .env
from dotenv import load_dotenv
import os

# Generic
import logging

# Hashing
import bcrypt

# JWT
import jwt
from datetime import datetime, timedelta

# Forgot Password
import os
import base64

# Paypal
import uuid

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins={"*"},
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load env variables

load_dotenv()

api_key = os.environ["API_KEY"]
subscription_key = os.environ["SUBSCRIPTION_KEY"]

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': api_key,
}

responseHeaders = {
    "Access-Control-Allow-Origin": "https://nice-tree-01aa92803.5.azurestaticapps.net/",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
    "Access-control-Allow-Headers": "Content-Type"
}

class GameInstanceModel(BaseModel):
    gameId: str


def ErrorJson(e):
    print(e.with_traceback())
    raise HTTPException(status_code=500, detail=e.__str__())

# Generics


def IsTruthy(*vals):
    temp = True
    for val in vals:
        if (not bool(val)):
            temp = False
    return temp


def IsString(val):
    if type(val) == str:
        return True
    else:
        return False


def UserIdErrorResponse(data):
    data = json.loads(data)
    if "Error" in data and "message" in data["Error"]:
        error_message = data["Error"]["message"]
        # Occurs when id is in incorrect format
        if error_message == "ObjectId in must be a single string of 12 bytes or a string of 24 hex characters":
            raise HTTPException(status_code=400, detail=error_message)
        if error_message == "Cannot access member '_id' of undefined" or error_message == "Cannot access member 'catalog' of undefined":
            raise HTTPException(status_code=404, detail=error_message)


def UpdateErrorResponse(data):
    data = json.loads(data)
    if "modifiedCount" in data:
        if data["modifiedCount"] == 0:
            raise HTTPException(status_code=400, detail="No change was made")


def ErrorResponse(data):
    data = json.loads(data)
    if "Error" in data:
        if "Status code" in data:
            raise HTTPException(
                status_code=data["Status code"], detail=data["Error"])
        else:
            raise HTTPException(status_code=500, detail=data["Error"])


def DBRequest(method, url, payload):
    response = requests.request(method, url, headers=headers, params=payload)

    if (response.status_code == 200):
        UserIdErrorResponse(response.text)
        UpdateErrorResponse(response.text)
        ErrorResponse(response.text)
        logging.info(f"Response - ${response.text}")
        raise HTTPException(status_code=response.status_code,
                            detail=json.loads(response.text))
    else:
        logging.info(f"Response - ${response.reason}")
        raise HTTPException(status_code=response.status_code,
                            detail=response.reason)


# Subscription

def IsSubscriptionCorrect(sub):
    if sub != subscription_key:
        raise HTTPException(
            status_code=401, detail="Incorrect subscription key")


@app.post("/readGameInstance")
async def ReadExamAttempts(gameInstance: GameInstanceModel, Subscription: str = Header(..., convert_underscores=False)):
    IsSubscriptionCorrect(Subscription)

    payload = {
        "gameInstanceId": gameInstance.gameId
    }

    DBRequest("POST", "https://westeurope.azure.data.mongodb-api.com/app/application-0-wdobenl/endpoint/api/readGameInstance", payload)

