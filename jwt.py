import datetime

import jwt


def generateJWT(userId):

    # Generate token
    timeLimit = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=30
    )  # set limit for user
    payload = {"user_id": userId, "exp": timeLimit}
    return jwt.encode(payload, "super-secret-6FDFBB8F--3F685784355E")  # noboost


def generateJWT2(userId):

    # Generate token
    timeLimit = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=30
    )  # set limit for user
    payload = {"user_id": userId, "exp": timeLimit}
    return jwt.encode(payload, "super-secret-6FDFBB8F--3F685784355E")

def generateJWT3(userId):

    # Generate token
    timeLimit = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=30
    )  # set limit for user
    payload = {"user_id": userId, "exp": timeLimit}
    return jwt.encode(payload, "super-secret-6FDFBB8F--3F685784355E")
