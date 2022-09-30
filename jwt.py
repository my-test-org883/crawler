import datetime

import jwt


def generateJWT(userId):

    # Generate token
    timeLimit = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=30
    )  # set limit for user
    payload = {"user_id": userId, "exp": timeLimit}
    return jwt.encode(payload, "super-secret-6FDFBB8F-2909-4565-85EA-3F685784355E")
