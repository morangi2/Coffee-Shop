import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
#from jose import jwt

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

""" @app.route('/testconnection')
def test_connection():
    return 'hello mercy!'
 """


# ROUTES
'''
@TODO == DONE ... implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    short_drink = [drink.short() for drink in drinks]

    return jsonify(
        {
            'success': True,
            'drinks': short_drink
        }
    )


'''
@TODO == DONE ... implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    if 'get:drinks-detail' in payload['permissions']:
        drinks = Drink.query.all()

        long_drinks = [drink.long() for drink in drinks]

        return jsonify(
            {
                'success': True,
                'drinks': long_drinks
            }
        )




'''
@TODO == DONE... implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    title_input = request.get_json().get("title")
    recipe_input = json.dumps(request.get_json().get("recipe"))

    if 'post:drinks' in payload['permissions']:
        drink = Drink(title=title_input, recipe=str(recipe_input))
        drink.insert()

        return jsonify(
            {
                'drink': drink.long(),
                'success': True
            }
        )
    else:
        abort(AuthError)
    


    



'''
@TODO == DONE... implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, drink_id):
    if 'patch:drinks' in payload['permissions']:
        try:
            drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

            if drink is None:
                abort(422)
            else:
                body_input = request.get_json()
                title_input = body_input.get('title')
                #recipe_input = body_input.get('recipe')

                drink.title = title_input
                #drink.recipe = recipe_input
                drink.update()

                return jsonify(
                    {
                        'success': True,
                        'drinks': [drink.long()]
                    }
                )
        except:
            abort(422)





'''
@TODO == DONE ... implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    if 'delete:drinks' in payload['permissions']:
        try:
            drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

            if drink is None:
                abort(404)
            else:
                drink.delete()

                return jsonify(
                    {
                        'success': True,
                        'delete': drink_id
                    }
                )
        except:
            abort(404)
    else:
        print('*************DELETE DRINKS ERROR*************')




# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
@TODO == DONE ... implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify(
        {
            "success": False,
            "error": 404,
            "message": "resource not found"
        }
    ), 404



'''
@TODO == DONE ... implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    print('**********')
    print(error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error.get('description')
    }), error.status_code