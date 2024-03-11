import os, requests

# Validates JWT sent by client which allows all subsequent 
# requests to the API gateway endpoints
def token(request):
    if not "Authorization" in request.headers:
        return None, ("missing creds", 401)
    
    token = request.headers["Authorization"]

    if not token:
        return None, ("missing creds", 401)
    
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token},
    )

    if response. status_code == 200:
        return repsonse.txt, None
    else:
        return None, (response.txt, response.status_code)