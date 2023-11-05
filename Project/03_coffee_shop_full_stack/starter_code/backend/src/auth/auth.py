import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'mofsnd.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffeeshopclass'

#login_link = https://mofsnd.us.auth0.com/authorize?audience=coffeeshopclass&response_type=token&client_id=YhJfyttu4kR7urI5t49a2uBUQwAgdS4Y&redirect_uri=https://127.0.0.1:5000/login-results
#morangi2 login_result = https://127.0.0.1:5000/login-results#access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImRRdHZ2Z1VkNHA2NHRsLUd6UkhyMyJ9.eyJpc3MiOiJodHRwczovL21vZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjU0M2UwZjgzYzFiODQwOWJhZTMyYzg1IiwiYXVkIjoiY29mZmVlc2hvcGNsYXNzIiwiaWF0IjoxNjk5MTM4MjQ4LCJleHAiOjE2OTkxNDU0NDgsImF6cCI6IlloSmZ5dHR1NGtSN3VySTV0NDlhMnVCVVF3QWdkUzRZIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcyIsImdldDpkcmlua3NfZGV0YWlsIiwicGF0Y2g6ZHJpbmtzIiwicG9zdDpkcmlua3MiXX0.LKKw8bGyQ4jMhqPKRnklARY5PNv0f5_BgB-kJSIKDSdueOU-7K9goDgk_BgJs4fB3G31lW9lAA6NaO4ZsFVOlHn56b0P95OYiChMIwonqy_uuyGrlvo-8B0gpQUMXJtJOOEyj6y607cIGJrFKbOBmN1IMLAlQI6tismoN7f4JykabXbyLyX3FXnHQX8XcMzx5xNGcJm9XQyhEm9-eyViBFIN3LRC4nQGvXCB5Or924FtV5bHPkdLKpxp85KCH67rObeCaZG2aTcvFYPUolUIGnAACSoJd09DP-CgmjR1ZjsE3RsUdmLMcOc3wIxWdJYawF1SRZIriXRf0VbEqU7H_g&expires_in=7200&token_type=Bearer
#morangi2 JWT = eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImRRdHZ2Z1VkNHA2NHRsLUd6UkhyMyJ9.eyJpc3MiOiJodHRwczovL21vZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjU0M2UwZjgzYzFiODQwOWJhZTMyYzg1IiwiYXVkIjoiY29mZmVlc2hvcGNsYXNzIiwiaWF0IjoxNjk5MTM4MjQ4LCJleHAiOjE2OTkxNDU0NDgsImF6cCI6IlloSmZ5dHR1NGtSN3VySTV0NDlhMnVCVVF3QWdkUzRZIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6ZHJpbmtzIiwiZ2V0OmRyaW5rcyIsImdldDpkcmlua3NfZGV0YWlsIiwicGF0Y2g6ZHJpbmtzIiwicG9zdDpkcmlua3MiXX0.LKKw8bGyQ4jMhqPKRnklARY5PNv0f5_BgB-kJSIKDSdueOU-7K9goDgk_BgJs4fB3G31lW9lAA6NaO4ZsFVOlHn56b0P95OYiChMIwonqy_uuyGrlvo-8B0gpQUMXJtJOOEyj6y607cIGJrFKbOBmN1IMLAlQI6tismoN7f4JykabXbyLyX3FXnHQX8XcMzx5xNGcJm9XQyhEm9-eyViBFIN3LRC4nQGvXCB5Or924FtV5bHPkdLKpxp85KCH67rObeCaZG2aTcvFYPUolUIGnAACSoJd09DP-CgmjR1ZjsE3RsUdmLMcOc3wIxWdJYawF1SRZIriXRf0VbEqU7H_g

#morangi1 login_result = https://127.0.0.1:5000/login-results#access_token=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImRRdHZ2Z1VkNHA2NHRsLUd6UkhyMyJ9.eyJpc3MiOiJodHRwczovL21vZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjU0M2U4ZDE0MjdmYjlmMjc2MjM0ZGM3IiwiYXVkIjoiY29mZmVlc2hvcGNsYXNzIiwiaWF0IjoxNjk5MTM4MzY3LCJleHAiOjE2OTkxNDU1NjcsImF6cCI6IlloSmZ5dHR1NGtSN3VySTV0NDlhMnVCVVF3QWdkUzRZIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzIiwiZ2V0OmRyaW5rc19kZXRhaWwiXX0.cympTd3qypveH2Nlf8lAUQo5-AIhtL8Yv9Kale2Bu2pLXDrGGp0ci1t7XrydfmlMuitiLWAmXz5mRplqUHlq56xW_oVQ7SZ3qer_TNqFVPAad9eDs6DEbebIOFREfqOkjYkl2QdhPNjlnVjPOn20Ix6Fa9gXyUUE36ZK2PR3h4YZKpBQDuKrNmWkIzjvP_Xt94KKEyKF8fDsHbY8qubfkQsSzZlMHlmqdDoUkscxQ5MZA5Ph4LJ6DG3-2DzEp3wN9AQI7FVbinz3y963Ey8KDjEC4qdBO9QkS5_D9mP5jLPUd51SyphtN9m-9L-k-k3kU9Icy-D4Vl1vvZJ_k8DVFQ&expires_in=7200&token_type=Bearer
#morangi1 JWT = eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImRRdHZ2Z1VkNHA2NHRsLUd6UkhyMyJ9.eyJpc3MiOiJodHRwczovL21vZnNuZC51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjU0M2U4ZDE0MjdmYjlmMjc2MjM0ZGM3IiwiYXVkIjoiY29mZmVlc2hvcGNsYXNzIiwiaWF0IjoxNjk5MTM4MzY3LCJleHAiOjE2OTkxNDU1NjcsImF6cCI6IlloSmZ5dHR1NGtSN3VySTV0NDlhMnVCVVF3QWdkUzRZIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJnZXQ6ZHJpbmtzIiwiZ2V0OmRyaW5rc19kZXRhaWwiXX0.cympTd3qypveH2Nlf8lAUQo5-AIhtL8Yv9Kale2Bu2pLXDrGGp0ci1t7XrydfmlMuitiLWAmXz5mRplqUHlq56xW_oVQ7SZ3qer_TNqFVPAad9eDs6DEbebIOFREfqOkjYkl2QdhPNjlnVjPOn20Ix6Fa9gXyUUE36ZK2PR3h4YZKpBQDuKrNmWkIzjvP_Xt94KKEyKF8fDsHbY8qubfkQsSzZlMHlmqdDoUkscxQ5MZA5Ph4LJ6DG3-2DzEp3wN9AQI7FVbinz3y963Ey8KDjEC4qdBO9QkS5_D9mP5jLPUd51SyphtN9m-9L-k-k3kU9Icy-D4Vl1vvZJ_k8DVFQ
 
## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO == DONE implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None) # headers is a dictionary containing various types of headers eg Content-Type, Authorization
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split() # to seperate the name bearer and the token itself
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    print(token)
    return token
    #raise Exception('Not Implemented')




'''
@TODO == DONE implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError(
            {
                'code': 'missing_permissions_string',
                'description': 'Requested permission string is not in the payload permissions array'
            }, 400
        )
    
    if permission not in payload['permissions']:
        raise AuthError(
            {
                'code': 'permissions_not_included',
                'description': 'permissions are not included in the payload'
            }, 403
        )
    
    return True
    #raise Exception('Not Implemented')




'''
@TODO == DONE implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)
    # raise Exception('Not Implemented')






'''
@TODO == DONE implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator