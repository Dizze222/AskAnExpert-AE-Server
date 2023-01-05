from collections import defaultdict
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from datetime import datetime
import random
from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'my-super-secret-key'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
db = SQLAlchemy(app)
jwt = JWTManager(app)


class PhotographerModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String, nullable=False)
    idPhotographer = db.Column(db.Integer, nullable=False)
    author = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    like = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.Column(db.JSON, nullable=False)
    authorOfComments = db.Column(db.JSON, nullable=False)


class AuthModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    secondName = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class ProfileModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    secondName = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.String, nullable=False)
    bio = db.Column(db.String, nullable=False)
    idOfUser = db.Column(db.Integer, nullable=False)


testTwo = defaultdict(list)
testAuthorOfComments = defaultdict(list)


@app.route('/register', methods=['POST'])
def register_user():
    try:
        phoneNumber = int(request.form['phoneNumber'])
        name = str(request.form['name'])
        secondName = str(request.form['secondName'])
        password = str(request.form['password'])
        print(phoneNumber, name, secondName, password, "   /register")
        model = AuthModel.query.order_by(AuthModel.date).all()
        # userOfProfileModel = ProfileModel.quer.oreder_by(ProfileModel.date).all()
        for i in model:
            print(i.phoneNumber)
            if phoneNumber == int(i.phoneNumber):
                return jsonify([{'accessToken': None, 'refreshToken': None, 'successRegister': False}])
        accessToken = create_access_token(identity=phoneNumber, expires_delta=timedelta(minutes=30), fresh=True)
        refreshToken = create_refresh_token(identity=phoneNumber, expires_delta=timedelta(days=30))
        modelOfRegister = AuthModel(phoneNumber=phoneNumber, name=name, secondName=secondName, password=password)
        modelOfUserProfile = ProfileModel(name=name, secondName=secondName, image="empty",idOfUser=phoneNumber,bio="no bio")
        db.session.add(modelOfRegister)
        db.session.add(modelOfUserProfile)
        db.session.commit()
        return jsonify([{'accessToken': accessToken, 'refreshToken': refreshToken, 'successRegister': True}])
    except Exception as error:
        print(error)
        return error


# Login
@app.route('/authentication', methods=['POST'])
def login_user():
    try:
        phoneNumber = int(request.form['phoneNumber'])
        password = str(request.form['password'])
        model = AuthModel.query.order_by(AuthModel.date).all()
        print(phoneNumber, password, "   /authentication")
        for i in model:
            if password == str(i.password) and phoneNumber == int(i.phoneNumber):
                print("point 1")
                accessToken = create_access_token(identity=phoneNumber, expires_delta=timedelta(minutes=5), fresh=True)
                refreshToken = create_refresh_token(identity=phoneNumber, expires_delta=timedelta(days=30))
                print("return true")
                return jsonify([{'accessToken': accessToken, 'refreshToken': refreshToken, 'success': True}])
        else:
            print("return false")
            return jsonify([{'accessToken': None, 'refreshToken': None, 'success': False}])
    except Exception as error:
        print(error)
        return "some exeption"


# check if the token is valid
@app.route('/action-with-token', methods=['GET'])
@jwt_required()
def protected():
    currentUser = get_jwt_identity()
    if currentUser > 1:
        return jsonify([{'success': True, 'loggedInAs': currentUser}])
    return jsonify([{'success': None, 'loggedInAs': currentUser}])


@app.route('/token/refresh')
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    accessToken = create_access_token(identity=identity)
    refreshToken = create_refresh_token(identity=identity)
    print(accessToken, refreshToken)
    return jsonify({'accessToken': accessToken, 'refreshToken': refreshToken, 'success': True})


@app.route('/person_data/<int:id>')
@jwt_required()
def get_person_data(id):
    identity = get_jwt_identity()
    if identity > 1:
        try:
            model = AuthModel.query.order_by(AuthModel.date).all()
            arrayOfUserData = []
            for i in model:
                if id == i.phoneNumber:
                    arrayOfUserData.append({
                        'id': str(i.id),
                        'phoneNumber': int(i.phoneNumber),
                        'name': str(i.name),
                        'secondName': str(i.secondName)
                    })
            return jsonify(arrayOfUserData)
        except:
            return "Some exception"
    else:
        return jsonify([{'id': None, 'phoneNumber': None, 'name': None, 'secondName': None}])


@app.route('/splash')
@jwt_required()
def splash():
    currentUser = get_jwt_identity()
    if currentUser > 10:
        return jsonify()


if __name__ == "__main__":
    app.run()