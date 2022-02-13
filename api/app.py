from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import create_db

import sqlite3

app = Flask(__name__)
CORS(app)

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Python Tech Test API"
    }
)
app.register_blueprint(swaggerui_blueprint)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# TODO - you will need to implement the other endpoints
# GET /api/person/{id} - get person with given id
# POST /api/people - create 1 person
# PUT /api/person/{id} - Update a person with the given id
# DELETE /api/person/{id} - Delete a person with a given id
@app.route("/api/people")
def getall_people():
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_people = cur.execute('SELECT * FROM Person;').fetchall()

    return jsonify(all_people)


@app.route("/api/people/<int:id>", methods = ['GET','PUT','DELETE'])
def get_person(id):
    """
    I assumed that the data validation tends to be performed on the client-side
    and send as a JSON object.

    Data send for PUT request:

        firstName   --> dtype: str
        lastName    --> dtype: str
        authorised  --> dtype: boolean as 1 = True , 0 = Flase
        enabled     --> dtype: boolean as 1 = True , 0 = Flase
    """
    api_method = request.method
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    try:
        if api_method == 'GET':
            query_retrive = (f"SELECT * FROM Person WHERE id = {id}")
            one_person = cur.execute(query_retrive).fetchall()
            
            return jsonify(one_person)

        if api_method == 'PUT':
            data = request.get_json()
            # Checks if the record exists.
            check_if_exists = cur.execute(f"SELECT * FROM Person WHERE id = {id}").fetchall()
            
            if check_if_exists == []:

                return jsonify(message = 'Record not exists.')

            else:
                query_update = (f"""UPDATE Person SET 
                                    firstName = :firstName, lastName = :lastName,
                                    authorised = :authorised, enabled = :enabled 
                                    WHERE id = {id};""")
                cur.execute(query_update,data)
                conn.commit()

                return jsonify(message = f'Record {id} successfully updated.')

        if api_method == 'DELETE':
            query_delete = (f"""DELETE FROM Person WHERE id = {id};""")
            cur.execute(query_delete)
            conn.commit()

            return jsonify(message = f'Record {id} successfully deleted.')

    # If not all the values are given show an error.
    except sqlite3.ProgrammingError as error:
        return jsonify(message =  f'{error}')

    finally:
        conn.close()


@app.route("/api/people", methods = ['POST'])
def create_person():
    """
    I assumed that the data validation tends to be performed on the client-side
    and send as a JSON object.

    Data send for POST request:

        firstName   --> dtype: str
        lastName    --> dtype: str
        authorised  --> dtype: boolean as 1 = True , 0 = Flase
        enabled     --> dtype: boolean as 1 = True , 0 = Flase
    """
    data = request.get_json()
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()

    try:
        query_insert = (f"""INSERT INTO Person (firstName, lastName, enabled, authorised)
                            VALUES (:firstName, :lastName, :enabled,:authorised);""")
        cur.execute(query_insert,data)
        conn.commit()


        return jsonify(message = 'New record successfully created.')

    # If not all the values are given show an error.
    except sqlite3.ProgrammingError as error:
        return jsonify(message =  f'{error}')

    finally:
        conn.close() 

if __name__ == '__main__':
    app.run()
