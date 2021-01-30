# from database_layer.database import execute_query
# from config import database_config
# print(database_config.get_config("DB_USERNAME"))
# print("___________________first_______________")
# a = execute_query("SHOW TABLES")
# # print("A",a)
# for i in a:
#     print("i",i)
#
#
# print("\n___________________Second_______________")
# a = execute_query("SHOW TABLES")
# # print("A",a)
# for i in a:
#     print("j",i)

from constants.flask_constants import DEBUG, GET, POST, PUT, DELETE
from flask import jsonify, request
import flask


app = flask.Flask(__name__)
app.config[DEBUG] = True


@app.route('/login', methods=[GET])
def login():
    return jsonify({request.base_url: request.method})


@app.route('/adminDashboard', methods=[GET])
def admin_dashboard():
    return jsonify({
        request.base_url: request.method,
        'user': request.args.get('user')
                    })


@app.route('/getRoles', methods=[GET])
def get_roles():
    return jsonify({request.base_url: request.method})


@app.route('/addRoles', methods=[POST])
def add_roles():
    return jsonify({request.base_url: request.method})


@app.route('/updateRole', methods=[PUT])
def update_roles():
    return jsonify({request.base_url: request.method})


@app.route('/deleteRole', methods=[DELETE])
def delete_roles():
    return jsonify({request.base_url: request.method})


if __name__ == '__main__':
    app.run()
