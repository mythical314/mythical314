from flask import Flask, request, jsonify, render_template, Blueprint, redirect, url_for, session
from flask_login import *  # type: ignore
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_admin import Admin  # type: ignore
from flask_bcrypt import Bcrypt
from flask_admin.contrib.sqla import ModelView  # type: ignore
from flask_login import current_user, login_user, login_required, logout_user  # added this
from sqlalchemy import desc
from sqlalchemy.orm import backref
from wtforms.validators import ValidationError
from flask_bcrypt import Bcrypt  # type: ignore
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'

db = SQLAlchemy(app)

login_manager = LoginManager()  # type: ignore
login_manager.init_app(app)  # added this
login_manager.login_view = 'login_page'  # added this
app.secret_key = 'super secret key'
admin = Admin(app, name='microblog')

bcrypt = Bcrypt()

# generates each time the app runs, but that should be ok
hashed = bcrypt.generate_password_hash("your_password").decode('utf-8')
bcrypt.check_password_hash(hashed, "your_password")


# friendship = db.Table('friendship',
#                       db.Column('first_friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
#                       db.Column('second_friend_id', db.Integer, db.ForeignKey('user.id'), primary_key=True))

class Friendship(db.Model):
    __tablename__ = 'friendship'

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20))

    requester = db.relationship('User', foreign_keys=[requester_id], back_populates='sent_friend_requests')
    recipient = db.relationship('User', foreign_keys=[recipient_id], back_populates='received_friend_requests')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)

    # friend_request_sent = db.relationship('User', secondary=friendship, primaryjoin=id == friendship.c.first_friend_id,
    #     secondaryjoin=id == friendship.c.second_friend_id, backref=db.backref('friend_request_received', lazy='subquery'))

    sent_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.requester_id',
                                           back_populates='requester')
    received_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.recipient_id',
                                               back_populates='recipient')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return self.fullname

    @property
    def is_authenticated(self):
        return True

    def is_active(self):
        return True  # need this bc get error that User doesn't have is_active attribute

    def get_id(self):
        return str(self.id)

    def is_anonymous(self):
        return False


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_name = db.Column(db.String(100), nullable=False)
    quiz_topic = db.Column(db.String(100), nullable=False)
    quiz_private = db.Column(db.Boolean, nullable=False)
    quiz_length = db.Column(db.Integer, nullable=False)
    quiz_type = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_quizzes', lazy=True, cascade='all, delete-orphan'))

    # a user can have many quizzes

    def __repr__(self):
        return self.quiz_name


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.String(100), nullable=False)
    answer1 = db.Column(db.String(100), nullable=False)
    answer2 = db.Column(db.String(100), nullable=False)
    answer3 = db.Column(db.String(100), nullable=False)
    answer4 = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.Integer, nullable=False)

    question_quiz = db.relationship('Quiz',
                                    backref=db.backref('quiz_questions', lazy=True, cascade='all, delete-orphan'))
    # a quiz can have many questions


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    challenger_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    challenge_quiz = db.relationship('Quiz',
                                     backref=db.backref("quiz_challenges", lazy=True, cascade='all, delete-orphan'))
    challenger = db.relationship('User', foreign_keys=[challenger_id], backref='challenges_sent')
    invitee = db.relationship('User', foreign_keys=[invitee_id], backref='challenges_received')

    challenger_score = db.Column(db.Integer, nullable=False, default=0)
    invitee_score = db.Column(db.Integer, nullable=False, default=0)

    challenger_done = db.Column(db.Boolean, nullable=False, default=False)
    invitee_done = db.Column(db.Boolean, nullable=False, default=False)
    # a challenge can have only one quiz
    # a quiz can be used in multiple challenges
    # a challenge can have one challenger and one invitee


class UserView(ModelView):  # this works if you use pip uninstall WTForms, pip install WTForms==3.1.2
    def is_accessible(self):
        return current_user.role == 'Admin'  # //bc login

    can_delete = True
    can_create = True
    can_edit = True
    column_exclude_list = ['password']

    column_list = ['fullname', 'username', 'role']


class QuizView(ModelView):  # this works if you use pip uninstall WTForms, pip install WTForms==3.1.2
    def is_accessible(self):
        return current_user.role == 'Admin'  # //bc login

    can_delete = True
    can_create = True
    can_edit = True


class QuestionView(ModelView):  # this works if you use pip uninstall WTForms, pip install WTForms==3.1.2
    def is_accessible(self):
        return current_user.role == 'Admin'  # //bc login

    can_delete = True
    can_create = True
    can_edit = True


class FriendshipView(ModelView):  # this works if you use pip uninstall WTForms, pip install WTForms==3.1.2
    def is_accessible(self):
        return current_user.role == 'Admin'  # //bc login

    column_list = ['requester', 'recipient', 'status']
    can_delete = True
    can_create = True
    can_edit = True


class ChallengeView(ModelView):  # this works if you use pip uninstall WTForms, pip install WTForms==3.1.2
    def is_accessible(self):
        return current_user.role == 'Admin'  # //bc login

    can_delete = True
    can_create = True
    can_edit = True


admin.add_view(UserView(User, db.session))
admin.add_view(FriendshipView(Friendship, db.session))
admin.add_view(QuizView(Quiz, db.session))
admin.add_view(QuestionView(Question, db.session))
admin.add_view(ChallengeView(Challenge, db.session))


@app.route('/')
def emptyRoute():
    return redirect(url_for('login_page'))


@app.route('/login_page')
def login_page():
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_process():
    # print(request.json['username'])
    # print(request.json['password'])

    Username = request.json['username']
    Password = request.json['password']

    the_user = User.query.filter_by(username=Username).first()
    if the_user is None or not the_user.check_password(Password):  # if the login was unsuccessful
        return jsonify({'success': False, 'redirect': url_for('login_page')})  # url for means the function name

    # if it gets here, it was successsful

    login_user(the_user)  # NOTE: this is what is causing the currrent issue

    # print(url_for('main_page') + "/" + Username)

    if the_user.role == "Admin":
        return jsonify({'success': True, 'redirect': '/admin/'})
    else:
        return jsonify(
            {'success': True, 'redirect': 'main_menu/' + Username})  # url_for('main_menu') + "/" + Username})


@app.route('/main_menu/<username>')
@login_required
def main_menu(username):
    return render_template("main_menu.html", USERNAME=username)


@app.route('/quiz_list/<username>')
@login_required
def quiz_list(username):
    return render_template("quiz_list.html", USERNAME=username)


@app.route('/quiz_list/quizzes/<username>', methods=['GET'])
def fetch_quizzes(username):
    user = User.query.filter_by(username=username.replace("%20", " ")).first()
    user_quizzes = Quiz.query.filter_by(user_id=user.id).all()
    body = {}
    for row in user_quizzes:
        array = [row.quiz_name, row.quiz_topic, row.quiz_private, row.quiz_length]
        body[row.id] = array
    return jsonify(body)


@app.route('/quiz_list/quizzes/<username>/<quiz_id>', methods=['POST', 'PUT'])
@login_required
def update_quiz(username, quiz_id):
    data = request.get_json()  # {meta : [name, topic, private, length, type], 1: [Question, Answer, Answer...], 2: [Question, Answer, Answer...]
    user = User.query.filter_by(username=username.replace("%20", " ")).first()

    if request.method == 'PUT':
        old_quiz = Quiz.query.filter_by(id=quiz_id).first() # (id=data['meta'][0]).first()
        if old_quiz is not None:
            db.session.delete(old_quiz)
            db.session.commit()

    quiz_private_value = data['meta'][2].lower() == 'true'

    new_quiz = Quiz(user=user, quiz_name=data['meta'][0], quiz_topic=data['meta'][1], quiz_private=quiz_private_value,
                    quiz_length=data['meta'][3], quiz_type=data['meta'][4])
    db.session.add(new_quiz)
    db.session.commit()
    data.pop('meta')

    for key, value in data.items():
        new_question = Question(quiz_id=new_quiz.id, question_number=int(key), question_text=value[0], answer1=value[1],
                                answer2=value[2], answer3=value[3], answer4=value[4], correct_answer=value[5]) #let array = [question, answer1, answer2, answer3, answer4, correct_answer]; temp_data[number] = array;
        db.session.add(new_question)
        db.session.commit()

    user_quizzes = Quiz.query.filter_by(user_id=user.id).all()
    body = {}
    for row in user_quizzes:
        array = [row.quiz_name, row.quiz_topic, row.quiz_private, row.quiz_length]
        body[row.id] = array
    return jsonify(body)


@app.route('/quiz_list/quizzes/<username>/<quiz_id>', methods=['DELETE'])
@login_required
def delete_quiz(username, quiz_id):
    old_quiz = Quiz.query.filter_by(id=quiz_id).first()
    db.session.delete(old_quiz)
    db.session.commit()
    user = User.query.filter_by(username=username.replace("%20", " ")).first()

    user_quizzes = Quiz.query.filter_by(user_id=user.id).all()
    body = {}
    for row in user_quizzes:
        array = [row.quiz_name, row.quiz_topic, row.quiz_private, row.quiz_length]
        body[row.id] = array
    return jsonify(body)


@app.route('/quiz_editor/<username>/<quiz_id>')
@login_required
def quiz_editor(username, quiz_id):
    if (quiz_id == 'new_quiz'):
        print("dsdfsfidfwvnwiunhhib")
        new_quiz = Quiz(quiz_name='New Quiz', quiz_topic='New Topic', quiz_private=True, quiz_type="", quiz_length=0,
                        user=User.query.filter_by(username=username.replace("%20", " ")).first())
        db.session.add(new_quiz)
        db.session.commit()
        return render_template('quiz_editor.html', USERNAME=username, QUIZ_ID=new_quiz.id)
    else:
        return render_template("quiz_editor.html", USERNAME=username, QUIZ_ID=quiz_id)

@app.route('/quiz_editor/questions/<quiz_id>', methods=['GET'])
@login_required
def fetch_questions(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    quiz_questions = Question.query.filter_by(quiz_id=quiz.id).order_by(desc(Question.question_number)).all()
    body = {}
    for row in quiz_questions:
        array = [row.question_text, row.answer1, row.answer2, row.answer3, row.answer4, row.correct_answer]
        body[row.question_number] = array
    array = [quiz.quiz_name, quiz.quiz_topic, quiz.quiz_private, quiz.quiz_length, quiz.quiz_type]
    body["meta"] = array

    body = json.dumps(body)    

    return jsonify(body)


@app.route('/quiz_editor/questions/<quiz_id>/<question_number>', methods=['DELETE'])
@login_required
def delete_question(username, quiz_id, question_number):
    old_quiz = Quiz.query.filter_by(id=quiz_id).first()
    old_question = Question.query.filter_by(question_quiz=old_quiz).first()
    db.session.delete(old_question)
    db.session.commit()

    quiz_questions = Quiz.query.filter_by(quiz_id=old_quiz.id).all()
    body = {}
    for row in quiz_questions:
        array = [row.id]
        body[row.id] = array
    return jsonify(body)


@app.route('/challenge_creator/<username>')
@login_required
def challenge_creator(username):
    return render_template("challenge_creator.html", USERNAME=username)

@app.route('/challenge_creator/<username>/<quiz_id>')
@login_required
def challenge_creator_specific_ID(username, quiz_id):
    return render_template("challenge_creator2.html", USERNAME=username, QUIZ_ID=quiz_id)

@app.route('/challenge_creator', methods=['POST'])
@login_required
def create_challenge():
    data = request.get_json()
    challenge = Challenge(quiz_id=data['data'][1], challenger=User.query.filter_by(username=data['data'][0]).first(), invitee=User.query.filter_by(username=data['data'][2]).first())
    db.session.add(challenge)
    db.session.commit()
    return_data = {'data': challenge.id}
    return jsonify(return_data)

@app.route('/challenge_quiz/<username>/<challenge_id>')
@login_required
def challenge_started(username, challenge_id):
    return render_template("start_challenge.html", USERNAME=username, CHALLENGE_ID=challenge_id)

@app.route('/challenge_quiz/<username>/<challenge_id>/<question_number>')
@login_required
def challenge_quiz(username, challenge_id, question_number):

    user = User.query.filter_by(username=username.replace("%20", " ")).first()
    challenge = Challenge.query.filter_by(id=int(challenge_id)).first()

    if int(question_number) > challenge.challenge_quiz.quiz_length:
        if username == challenge.challenger.username:
            challenge.challenger_done = True
            db.session.commit()
            return render_template("end_challenge.html", USERNAME=username, CHALLENGE_ID=challenge_id, CORRECT_ANSWERS=challenge.challenger_score)
        elif username == challenge.invitee.username:
            challenge.invitee_done = True
            db.session.commit()
            return render_template("end_challenge.html", USERNAME=username, CHALLENGE_ID=challenge_id, CORRECT_ANSWERS=challenge.invitee_score)

    elif user.id == challenge.challenger.id or user.id == challenge.invitee.id:
        question = Question.query.filter_by(question_number=question_number, quiz_id=challenge.quiz_id).first()
        return render_template("challenge_quiz.html", USERNAME=username, QUESTION=question.question_text, ANSWER1=question.answer1, ANSWER2=question.answer2, ANSWER3=question.answer3, ANSWER4=question.answer4, CURRENT_QUESTION=question_number, CHALLENGE_ID=challenge_id)
    else:
        return

@app.route('/challenge_quiz/answer', methods=['POST'])
@login_required
def check_answer():
    data = request.get_json()
    challenge = Challenge.query.filter_by(id=data['challenge_id']).first()
    quiz = Quiz.query.filter_by(id=challenge.quiz_id).first()
    question = Question.query.filter_by(question_number=int(data['current_question']), quiz_id=quiz.id).first()
    correct = False

    if int(data['answer']) == question.correct_answer:
        correct = True
        if data['username'] == challenge.challenger.username:
            challenge.challenger_score+=1
            db.session.commit()
        elif data['username'] == challenge.invitee.username:
            challenge.invitee_score+=1
            db.session.commit()

    return jsonify({'correct': correct})



# TODO: code this to GET results from a challenge
@app.route('/challenge_stats/<challenge_id>')
@login_required
def challenge_stats(challenge_id):
    return


@app.route('/test_for_challenge_quiz_html_page')
def challenge_quiz_page_test():  # put application's code here
    return render_template('challenge_quiz.html', QUESTION="What is 2 + 2?", ANSWER1="1", ANSWER2="2", ANSWER3="3",
                           ANSWER4="4")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/check_if_user_is_logged_in/', methods=['GET'])
def check_if_logged_in():
    returnValue = {}
    logged_in = False

    logged_in = current_user.is_authenticated  # get whether the user is logged in

    returnValue = {'logged in': logged_in}  # save that boolean value to the returnValue variable

    return jsonify(returnValue)  # return the jsonified variable


def populate_db():
    if (User.query.count() == 0):  # if there are no users in the database
        print('no data in the database')

        user0 = User(fullname="Admin_Don't_Delete", username="admin", password="the_key",
                     role="Admin")  # Do not delete because this is to be able to acess the admin page
        # these are test users. Changes made in the admin page do get saved
        user1 = User(fullname="TEST USER", username="tester", password="secret", role="Regular User")
        user2 = User(fullname="Susan Walker", username="swalker", password="secret", role="Regular User")
        user3 = User(fullname="John Smith", username="jsmith", password="third", role="Regular User")
        user4 = User(fullname="Bob Wheeler ", username="bwheeler", password="fourth", role="Regular User")
        user5 = User(fullname="Cleo Mccarty ", username="mccarty", password="fifth", role="Regular User")

        # salt their passwords
        user0.password = bcrypt.generate_password_hash(user0.password).decode('utf-8')
        user1.password = bcrypt.generate_password_hash(user1.password).decode('utf-8')
        user2.password = bcrypt.generate_password_hash(user2.password).decode('utf-8')
        user3.password = bcrypt.generate_password_hash(user3.password).decode('utf-8')
        user4.password = bcrypt.generate_password_hash(user4.password).decode('utf-8')
        user5.password = bcrypt.generate_password_hash(user5.password).decode('utf-8')

        db.session.add(user0)
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.add(user4)
        db.session.add(user5)

        db.session.commit()

        f1 = Friendship(requester=user5, recipient=user2, status='pending')
        f2 = Friendship(requester=user1, recipient=user2, status='pending')
        f3 = Friendship(requester=user2, recipient=user3, status='pending')

        db.session.add(f1)
        db.session.add(f2)
        db.session.add(f3)

        db.session.commit()

        # friendship_request = db.session.query(Friendship).filter_by(requester_id=user1.id, recipient_id=user2.id, status='pending').first()
        # if friendship_request:
        #     friendship_request.status = 'accepted'

        second_friendship_request = db.session.query(Friendship).filter_by(requester_id=user5.id, recipient_id=user2.id,
                                                                           status='pending').first()
        if second_friendship_request:
            second_friendship_request.status = 'denied'

        quiz1 = Quiz(quiz_name="Math Basics", quiz_topic="Mathematics", quiz_private=False, quiz_length=3, quiz_type="", user=user1)

        quiz2 = Quiz(quiz_name="Science Quiz", quiz_topic="Science", quiz_private=True, quiz_length=2, quiz_type="", user=user2)

        db.session.add(quiz1)
        db.session.add(quiz2)

        db.session.commit()

        q1 = Question(question_quiz=quiz1, question_number=1, question_text="What is 2 + 2?", answer1="3", answer2="4",
                      answer3="5", answer4="6", correct_answer=2)
        q2 = Question(question_quiz=quiz1, question_number=2, question_text="What is 10 / 2?", answer1="2", answer2="4",
                      answer3="5", answer4="10", correct_answer=3)
        q3 = Question(question_quiz=quiz1, question_number=3, question_text="What is 12 * 6?", answer1="25",
                      answer2="48", answer3="72", answer4="50", correct_answer=4)

        db.session.add(q1)
        db.session.add(q2)
        db.session.add(q3)

        q4 = Question(question_quiz=quiz2, question_number=1, question_text="What is the chemical symbol for water?",
                      answer1="H2O", answer2="O2", answer3="CO2", answer4="H2", correct_answer=1)
        q5 = Question(question_quiz=quiz2, question_number=2, question_text="What is the powerhouse of the cell?",
                      answer1="Nucleus", answer2="Mitochondria", answer3="Electron", answer4="Proton", correct_answer=2)

        db.session.add(q4)
        db.session.add(q5)

        challenge1 = Challenge(challenge_quiz=quiz1, challenger=user1, invitee=user2)

        challenge2 = Challenge(challenge_quiz=quiz2, challenger=user2, invitee=user3)

        db.session.add(challenge1)
        db.session.add(challenge2)

        db.session.commit()  # so ID is saved


@app.route('/challenge_creator/quizzes/<username>')
def fetch_quizzes_challenge(username):
    user = User.query.filter_by(username=username.replace("%20", " ")).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    user_quizzes = Quiz.query.filter_by(user_id=user.id).all()
    public_quizzes = Quiz.query.filter_by(quiz_private=False).all()
    body = {}
    for row in user_quizzes:
        array = [row.quiz_name, row.quiz_topic, row.quiz_private, row.quiz_length]
        body[row.id] = array
    for row in public_quizzes:
        array = [row.quiz_name, row.quiz_topic, row.quiz_private, row.quiz_length]
        body[row.id] = array

    return jsonify(body)

@app.route('/challenge_creator/friends/<username>')
def fetch_friends_challenge(username):
    user = User.query.filter_by(username=username.replace("%20", " ")).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    user_friendships = Friendship.query.filter(Friendship.status=="accepted", or_(Friendship.requester_id==user.id, Friendship.recipient_id==user.id)).all()
    body = {}
    for row in user_friendships:
        friend_id = 0
        if row.requester_id == user.id:
            friend_id = row.recipient_id
        else:
            friend_id = row.requester_id
        friend = User.query.filter_by(id=friend_id).first()
        #TODO: calculate winrate
        array = [friend.username, 0]
        body[row.id] = array

    return jsonify(body)

# --------------------------------------------------------------------------------------------------------- #
# -----------------------------           Friends Stuff         ------------------------------------------- #
# --------------------------------------------------------------------------------------------------------- #
# =============================================================== #
# ======================    Friends List   ====================== #
# =============================================================== #
@app.route('/main_menu/friends_list/<username>', methods=['GET'])
@login_required
def friends_list(username):
    return render_template('friends_list.html', USERNAME=username)


# @app.route('/friends_list/<username>', methods=['GET'])
# @login_required
# def get_friends_list(username):
#     current_user = User.query.filter_by(username=username).first()

#     if not current_user:
#         return jsonify({"error": "User not found"}), 404

#     users = User.query.filter(User.username != username, User.role == 'Regular User').all()  # Filter by role
#     friends_list = {}
#     for user in users:
#     # Check if a friendship exists between the current user and another user
#         friendship = Friendship.query.filter_by(requester_id=current_user.id, recipient_id=user.id).first()
#         if not friendship:
#             friendship = Friendship.query.filter_by(requester_id=user.id, recipient_id=current_user.id).first()
#         is_request_sent = False
#         if friendship:
#             if friendship.status == 'pending' and friendship.requester_id == current_user.id:
#                 is_request_sent = True
#             elif friendship.status == 'accepted':
#                 continue  # No need to show friends that are already accepted

#         friends_list[user.username] = {
#             'fullname': user.fullname,
#             'isRequestSent': is_request_sent
#         }
#     return jsonify(friends_list)

@app.route('/friends_list/<username>', methods=['GET'])
@login_required
def get_friends_list(username):
    current_user = User.query.filter_by(username=username).first()

    if not current_user:
        return jsonify({"error": "User not found"}), 404

    # Get IDs of users who have sent a pending request to the current user
    pending_requesters = db.session.query(Friendship.requester_id).filter_by(recipient_id=current_user.id,
                                                                             status='pending').subquery()

    # Get IDs of users who are already friends with the current user
    accepted_friends_requester = db.session.query(Friendship.recipient_id).filter_by(requester_id=current_user.id,
                                                                                     status='accepted').subquery()
    accepted_friends_recipient = db.session.query(Friendship.requester_id).filter_by(recipient_id=current_user.id,
                                                                                     status='accepted').subquery()

    users = User.query.filter(
        User.username != username,
        User.role == 'Regular User',
        User.id.notin_(pending_requesters),  # Exclude users who sent a pending request
        User.id.notin_(accepted_friends_requester),  # Exclude already accepted friends (as recipient)
        User.id.notin_(accepted_friends_recipient)  # Exclude already accepted friends (as requester)
    ).all()

    friends_list = {}
    for user in users:
        # Check if the current user has already sent a request to this user
        sent_request = Friendship.query.filter_by(requester_id=current_user.id, recipient_id=user.id,
                                                  status='pending').first()
        is_request_sent = sent_request is not None

        friends_list[user.username] = {
            'fullname': user.fullname,
            'isRequestSent': is_request_sent
        }
    return jsonify(friends_list)


@app.route('/send_friend_request', methods=['POST'])
@login_required
def send_friend_request():
    data = request.get_json()
    sender_username = data['sender_username']
    receiver_username = data['receiver_username']
    sender = User.query.filter_by(username=sender_username).first()
    receiver = User.query.filter_by(username=receiver_username).first()

    if not sender or not receiver:
        return jsonify({'error': 'User not found'}), 400
    existing_request = Friendship.query.filter_by(requester_id=sender.id, recipient_id=receiver.id).first()
    if existing_request:
        return jsonify({'error': 'Friend request already sent'}), 400

    new_request = Friendship(requester_id=sender.id, recipient_id=receiver.id, status='pending')
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'message': 'Friend request sent successfully'})


@app.route('/revoke_friend_request', methods=['POST'])
@login_required
def revoke_friend_request():
    data = request.get_json()
    sender_username = data['sender_username']
    receiver_username = data['receiver_username']
    sender = User.query.filter_by(username=sender_username).first()
    receiver = User.query.filter_by(username=receiver_username).first()

    if not sender or not receiver:
        return jsonify({'error': 'User not found'}), 400
    existing_request = Friendship.query.filter_by(requester_id=sender.id, recipient_id=receiver.id,
                                                  status='pending').first()
    if not existing_request:
        return jsonify({'error': 'No pending request to revoke'}), 400

    db.session.delete(existing_request)
    db.session.commit()
    return jsonify({'message': 'Friend request revoked successfully'})


# =============================================================== #
# ============     Pending Friends List     ===================== #
# =============================================================== #
@app.route('/main_menu/pending_friends/<username>', methods=['GET'])
@login_required
def pending_friends(username):
    return render_template('pending_friends.html', USERNAME=username)


@app.route('/pending_friends/<username>')
@login_required
def get_pending_requests(username):
    current_user = User.query.filter_by(username=username).first()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    pending_requests = Friendship.query.filter_by(recipient_id=current_user.id, status='pending').all()
    pending_friends_list = {}
    for request in pending_requests:
        sender = User.query.get(request.requester_id)
        if sender:
            pending_friends_list[sender.username] = {'fullname': sender.fullname}
    return jsonify(pending_friends_list)


@app.route('/accept_friend_request', methods=['POST'])
@login_required
def accept_friend_request():
    data = request.get_json()
    recipient_username = data['recipient_username']
    requester_username = data['requester_username']
    recipient = User.query.filter_by(username=recipient_username).first()
    requester = User.query.filter_by(username=requester_username).first()

    if not recipient or not requester:
        return jsonify({'error': 'User not found'}), 400
    # Ensure the logged-in user is the recipient
    if current_user.id != recipient.id:
        return jsonify({'error': 'Unauthorized action'}), 403
    pending_request = Friendship.query.filter_by(requester_id=requester.id, recipient_id=recipient.id,
                                                 status='pending').first()
    if not pending_request:
        return jsonify({'error': 'No pending request found'}), 404
    pending_request.status = 'accepted'
    db.session.commit()
    return jsonify({'message': 'Friend request accepted successfully'})


@app.route('/decline_friend_request', methods=['POST'])
@login_required
def decline_friend_request():
    data = request.get_json()
    recipient_username = data['recipient_username']
    requester_username = data['requester_username']
    recipient = User.query.filter_by(username=recipient_username).first()
    requester = User.query.filter_by(username=requester_username).first()

    if not recipient or not requester:
        return jsonify({'error': 'User not found'}), 400
    # Ensure the logged-in user is the recipient
    if current_user.id != recipient.id:
        return jsonify({'error': 'Unauthorized action'}), 403
    pending_request = Friendship.query.filter_by(requester_id=requester.id, recipient_id=recipient.id,
                                                 status='pending').first()
    if not pending_request:
        return jsonify({'error': 'No pending request found'}), 404
    db.session.delete(pending_request)
    db.session.commit()
    return jsonify({'message': 'Friend request declined successfully'})


@app.route('/your_friends/<username>')
@login_required
def get_your_friends(username):
    current_user = User.query.filter_by(username=username).first()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    accepted_friendships = Friendship.query.filter(
        ((Friendship.requester_id == current_user.id) | (Friendship.recipient_id == current_user.id)) & (
                    Friendship.status == 'accepted')
    ).all()
    friends_list = {}
    for friendship in accepted_friendships:
        if friendship.requester_id == current_user.id:
            friend = User.query.get(friendship.recipient_id)
        else:
            friend = User.query.get(friendship.requester_id)
        if friend:
            friends_list[friend.username] = {'fullname': friend.fullname}

    return jsonify(friends_list)


@app.route('/remove_friend', methods=['POST'])
@login_required
def remove_friend():
    data = request.get_json()
    current_user_username = data.get('recipient_username')
    friend_to_remove_username = data.get('requester_username')
    current_user_obj = User.query.filter_by(username=current_user_username).first()
    friend_to_remove_obj = User.query.filter_by(username=friend_to_remove_username).first()

    if not current_user_obj or not friend_to_remove_obj:
        return jsonify({'error': 'User not found'}), 400
    if current_user.username != current_user_username:
        return jsonify({'error': 'Unauthorized'}), 403

    friendship_to_delete = Friendship.query.filter(
        ((Friendship.requester_id == current_user_obj.id) & (Friendship.recipient_id == friend_to_remove_obj.id) & (
                    Friendship.status == 'accepted')) |
        ((Friendship.requester_id == friend_to_remove_obj.id) & (Friendship.recipient_id == current_user_obj.id) & (
                    Friendship.status == 'accepted'))
    ).first()

    if friendship_to_delete:
        db.session.delete(friendship_to_delete)
        db.session.commit()
        return jsonify({'message': 'Friend removed successfully'})
    else:
        return jsonify({'error': 'Friendship not found'}), 404


# =============================================================== #
# ======================       Inbox       ====================== #
# =============================================================== #
@app.route('/main_menu/inbox/<username>', methods=['GET'])
@login_required
def inbox(username):
    return render_template('inbox.html', USERNAME=username)

@app.route('/pending_challenges/<username>')
@login_required
def get_pending_challenges(username):
    user = User.query.filter_by(username=username).first_or_404()

    # Show challenges where the current user is the invitee AND they haven't finished
    pending_challenges = Challenge.query.filter(
        Challenge.invitee_id == user.id,
        Challenge.invitee_done == False
    ).all()

    pending_data = {}
    for challenge in pending_challenges:
        challenger = User.query.get(challenge.challenger_id)
        if challenger:
            pending_data[challenger.username] = {'fullname': challenger.fullname}
    return jsonify(pending_data)

@app.route('/inbox/accept_challenge', methods=['POST'])
@login_required
def accept_challenge():
    data = request.get_json()
    recipient_username = data.get('recipient_username')
    challenger_username = data.get('requester_username')

    if not recipient_username or not challenger_username:
        return jsonify({'error': 'Missing recipient or challenger username'}), 400

    recipient = User.query.filter_by(username=recipient_username).first_or_404()
    challenger = User.query.filter_by(username=challenger_username).first_or_404()
    challenge = Challenge.query.filter_by(invitee_id=recipient.id, challenger_id=challenger.id).first()

    if not challenge:
        return jsonify({'error': 'Pending challenge not found'}), 404
    # Construct the URL for the quiz-taking page (adjust as needed)
    redirect_url = url_for('challenge_quiz', username=recipient_username, challenge_id=challenge.id, question_number=1)

    return jsonify({'redirect_url': redirect_url})

@app.route('/inbox/decline_challenge', methods=['POST'])
@login_required
def decline_challenge():
    data = request.get_json()
    recipient_username = data.get('recipient_username')
    challenger_username = data.get('requester_username')

    if not recipient_username or not challenger_username:
        return jsonify({'error': 'Missing recipient or challenger username'}), 400

    recipient = User.query.filter_by(username=recipient_username).first_or_404()
    challenger = User.query.filter_by(username=challenger_username).first_or_404()
    challenge = Challenge.query.filter_by(invitee_id=recipient.id, challenger_id=challenger.id).first()

    if not challenge:
        return jsonify({'error': 'Pending challenge not found'}), 404
    db.session.delete(challenge)
    db.session.commit()

    return jsonify({'message': 'Challenge declined successfully'})

@app.route('/completed_challenges/<username>')
@login_required
def get_completed_challenges(username):
    user = User.query.filter_by(username=username).first_or_404()
    completed_challenges_data = []

    # Find challenges where the current user was either the challenger or the invitee
    completed_challenges = Challenge.query.filter(
        ((Challenge.challenger_id == user.id) | (Challenge.invitee_id == user.id)) &
        (Challenge.challenger_score != None) & (Challenge.invitee_score != None)
    ).all()

    for challenge in completed_challenges:
        challenger = User.query.get(challenge.challenger_id)
        invitee = User.query.get(challenge.invitee_id)

        if challenger and invitee:
            completed_challenges_data.append({
                'challenger_name': challenger.username,  # Always the one who sent the challenge
                'challenger_score': challenge.challenger_score,
                'your_score': challenge.invitee_score if user.id == challenge.invitee_id else challenge.challenger_score
            })
            # if challenger.id == user.id:
            #     completed_challenges_data.append({
            #         'challenger_score': challenge.invitee_score,  # Score of the opponent
            #         'your_score': challenge.challenger_score
            #     })
            # elif invitee.id == user.id:
            #     completed_challenges_data.append({
            #         'challenger_score': challenge.challenger_score if challenge.challenger_score is not None else "-",
            #         'your_score': challenge.invitee_score
            #     })

    return jsonify(completed_challenges_data)


# Sign Up Page
@app.route('/sign_up')
def signup_page():
    return render_template("signup.html") 

@app.route('/signup_process', methods=['POST'])
def signup_process():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not fullname or not username or not password or not confirm_password:
            error = "All fields are required."
            return render_template('sign_up.html', error=error)
        if password != confirm_password:
            error = "Passwords do not match."
            return render_template('sign_up.html', error=error)
        if User.query.filter_by(username=username).first():
            error = "Username already exists. Please choose another."
            return render_template('sign_up.html', error=error)

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # CREATE NEW USER 
        new_user = User(fullname=fullname, username=username, password=hashed_password, role="Regular User")
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user) 
        return redirect(url_for('login_page'))

    return redirect(url_for('signup_page'))



print("hello world")

if __name__ == '__main__':
    resetTheTable = False  # for if needed

    with app.app_context():
        if (resetTheTable):
            db.drop_all()

        db.create_all()
        populate_db()
    print("running locally")
    # port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port)

    app.run(port=5001)
