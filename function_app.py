import azure.functions as func
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="ReadGameInstance")
def ReadGameInstance(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
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


async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await func.AsgiMiddleware(app).handle_async(req)