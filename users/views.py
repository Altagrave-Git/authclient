from .serializers import UserSerializer
from django.contrib.auth import login
from rest_framework.response import Response
from rest_framework import status, permissions
from users.models import User
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from client import settings
import requests, random, string, base64, hashlib, jwt, hmac


CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
REDIRECT_URI = 'http://127.0.0.1:3000/login/'

# Generate random alphanumeric string of random length up to 128 characters
CODE_VERIFIER = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randint(43, 128)))
# Encode in base64 with characters usable in urls
CODE_VERIFIER = base64.urlsafe_b64encode(CODE_VERIFIER.encode('utf-8'))

# Generate 256-bit hash of code verifier
CODE_CHALLENGE = hashlib.sha256(CODE_VERIFIER).digest()
# Encode in url-safe base64, changing bytes to string and remove '=' which has specific meaning in urls
CODE_CHALLENGE = base64.urlsafe_b64encode(CODE_CHALLENGE).decode('utf-8').replace('=', '')

AUTH_URL = "http://127.0.0.1:8000/o/authorize/?response_type=code&code_challenge={}&code_challenge_method=S256&client_id={}&redirect_uri={}".format(CODE_CHALLENGE, CLIENT_ID, REDIRECT_URI)


@api_view(["GET"])
def authorize(request):
    code = request.GET.get("code")

    if not code:
        return Response(data={"url": AUTH_URL})
    
    else:
        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "code_verifier": CODE_VERIFIER,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        auth_request = requests.post(
            "http://127.0.0.1:8000/o/token/",
            headers=headers,
            data=data
        )

        auth_request = auth_request.json()

        user_data = {
            "access_token": auth_request.get("access_token"),
            "expires_in": auth_request.get("expires_in"),
            "token_type": auth_request.get("token_type"),
            "scope": auth_request.get("scope"),
            "refresh_token": auth_request.get("refresh_token"),
        }

        id_token = auth_request.get("id_token")

        decrypted_id_token = jwt.decode(
            id_token,
            key=CLIENT_SECRET,
            algorithms=["HS256"],
            options={"verify_signature": False}
        )

        user_data["sub"] = decrypted_id_token.get("sub")
        user_data["username"] = decrypted_id_token.get("username")
        user_data["email"] = decrypted_id_token.get("email")
        user_data["first_name"] = decrypted_id_token.get("first_name")
        user_data["last_name"] = decrypted_id_token.get("last_name")

        user = User.objects.filter(sub=user_data.get("sub"))
        localuser = User.objects.filter(username=user_data.get("username"), sub=None)

        # If user with matching foreign ID exists, update fields
        if user.exists():
            serializer = UserSerializer(user[0], data=user_data)
        # If user exists locally and has not been assigned foreign ID
        elif localuser.exists():
            serializer = UserSerializer(localuser[0], data=user_data)
        # Else create new user
        else:
            serializer = UserSerializer(data=user_data)

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)
    