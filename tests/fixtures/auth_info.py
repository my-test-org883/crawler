import jwt

token_json = {
    "iat": 1234567890,
    "exp": 1234567890,
    "iss": "OneAuth",
    "username": "username",
    "authPoints": {"jira": True, "sso": True, "p4": True, "dem": False},
}

header = {"Authorization": f'Bearer {jwt.encode(token_json, "").decode()}'}

params = {
    "os_version": "Android 10.0 (QQ)",
    "date": "2019/10/15",
    "ap_template": "ap_template",
    "cp_template": "cp_template",
    "model_name": "SM-A505G",
}

auth_json = {
    "jira": {
        "authorization_cookie": None,
        "authorization_token": "di5iYXJyb25jYXM6Vm5iQDIyIzE5OTI=",
        "cookies": None,
        "credentials": {"password": "password", "user_id": "username"},
    },
    "p4": {
        "authorization_cookie": None,
        "authorization_token": None,
        "cookies": None,
        "credentials": {"password": "password", "user_id": "username"},
    },
    "plm": {
        "authorization_cookie": {
            "domain": ".co",
            "name": "WLSESSIONID",
            "path": "/",
            "value": "nY2gGAFcovsvEn5vkrJ0vI98g21Kc9023392",
        },
        "authorization_token": None,
        "cookies": [
            {
                "domain": "frfr.com",
                "name": "WLSESSIONID",
                "path": "/",
                "value": "nY2gGAFcovsvEn5vkrJ0vI98g21Kc9023392",
            },
            {
                "domain": "frfr.com",
                "name": "_xm_webid_1_",
                "path": "/",
                "value": "863128361",
            },
            {
                "domain": "sts.secsso.net",
                "name": "MSISAuth",
                "path": "/adfs",
                "value": "nwox/tn4JstK1eRyRe567B0Cm9EPoS9CA==",
            },
            {
                "domain": "sts.secsso.net",
                "name": "MSISAuthenticated",
                "path": "/adfs",
                "value": "MTEvNy8yMDIwIDEyOjI1OjMzIEFN",
            },
            {
                "domain": "sts.secsso.net",
                "name": "MSISLoopDetectionCookie",
                "path": "/adfs",
                "value": "MjAyMC0xMS0wNzowMDoyNTozM1pcMQ==",
            },
        ],
        "credentials": {"password": "password", "user_id": "username"},
    },
    "sso": {
        "authorization_cookie": {
            "domain": ".co",
            "name": "crowd.token_key",
            "path": "/",
            "value": "lH0qtRVs9EKD5Zy8eeXv9AAAAAAAlgABdi5iYXJyb25jYXM=",
        },
        "authorization_token": None,
        "cookies": [
            {
                "domain": ".com",
                "name": "crowd.token_key",
                "path": "/",
                "value": "lH0qtRVs9EKD5Zy8eeXv9AAAAAAAlgABdi5iYXJyb25jYXM=",
            },
            {
                "domain": "ferfwfwef.com",
                "name": "JSESSIONID",
                "path": "/",
                "value": "E12FC9563A1F1DAE74FCA71F6B50B10A",
            },
            {
                "domain": "ferfwfwef.com",
                "name": "hub_token",
                "path": "/",
                "value": "1",
            },
            {
                "domain": "ferfwfwef.com",
                "name": "__VCAP_ID__",
                "path": "/hub",
                "value": "80ddab21-2c2f-45ff-58eb-e24b",
            },
            {
                "domain": "ferfwfwef.com",
                "name": "JSESSIONID",
                "path": "/hub/main",
                "value": "ED74DC91F4210D2725A7AFCB9602F071",
            },
            {
                "domain": "ferfwfwef.com",
                "name": "__VCAP_ID__",
                "path": "/hub/main",
                "value": "c74cde42-1b83-49e1-760f-7d14",
            },
            {
                "domain": "sts.secsso.net",
                "name": "MSISAuth",
                "path": "/adfs",
                "value": "MZr7slEaIqLAboEAd+kmrdf0MI/bOG041ApNkwkBvu6bXzSOOoEx1PUmjw==",
            },
            {
                "domain": "sts.secsso.net",
                "name": "MSISAuthenticated",
                "path": "/adfs",
                "value": "MTEvNy8yMDIwIDEyOjI4OjE0IEFN",
            },
            {
                "domain": "sts.secsso.net",
                "name": "MSISLoopDetectionCookie",
                "path": "/adfs",
                "value": "MjAyMC0xMS0wNzowMDoyODoxMFpcMg==",
            },
            {
                "domain": "sts.secsso.net",
                "name": "SamlSession",
                "path": "/adfs",
                "value": "NzcwMjM1Jl85MDY2N2YzYi04NGMzLTQzYWQtYmMwMS1hYmJjYTVmZDdiNWI=",
            },
        ],
        "credentials": {"password": "password", "user_id": "username"},
    },
}
