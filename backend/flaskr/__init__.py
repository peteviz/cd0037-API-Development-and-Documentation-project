import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, all_questions, QUESTIONS_PER_PAGE):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted_questions = [question.format() for question in all_questions]
    current_questions = formatted_questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    cors = CORS(app, resources={'/': {"origins": "*"}})
    # CORS(app)
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization,true')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def all_categories():
        categories = Category.query.order_by(Category.id).all()
        cat_Dict = {}

        for category in categories:
            cat_Dict[category.id] = category.type

        if len(cat_Dict) == 0:
            abort(404)

        return jsonify({
            'categories': cat_Dict,
            'success': True
        })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_all_questions():
        all_questions = Question.query.order_by(Question.id).all()
        current_questions_page = paginate_questions(
            request, all_questions, QUESTIONS_PER_PAGE)

        if (len(current_questions_page) == 0):
            abort(404)

        categories = Category.query.order_by(Category.id).all()
        cat_dict = {}
        for category in categories:
            cat_dict[category.id] = category.type

        return jsonify({
            'success': True,
            'num_all_questions': len(all_questions),
            'questions': current_questions_page,
            'categories': cat_dict
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            question_del = Question.query.filter_by(id=id).one_or_none()

            if question_del is None:
                abort(404)
            question_del.delete()
            total_questions = len(Question.query.all())
            return jsonify({
                'success': True,
                'message': "Question has been deleted successfully",
                'total_questions': total_questions
            })
        except Exception:
            abort(404)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def submit_question():
        data = request.get_json(force=True)

        new_question = data.get('question', None)
        new_answer = data.get('answer', None)
        new_category = data.get('category', None)
        difficulty = data.get('difficulty', None)
        if ((new_question is None) or (new_answer is None) or (new_category is None) or (difficulty is None)):
            abort(422)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=difficulty
            )
            # insert question
            question.insert()

            return jsonify({
                'success': True,
                'message': "Your Question has been added successfully"
            })
        except Exception:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions')
    def questions_by_category(id):
        requested_category = Category.query.filter_by(id=id).one_or_none()

        if (requested_category is None):
            abort(422)

        categorized_questions = Question.query.filter_by(
            category=id).all()

        current_questions_page = paginate_questions(
            request, categorized_questions, QUESTIONS_PER_PAGE)

        return jsonify({
            'success': True,
            'questions': current_questions_page,
            'current_category': requested_category.type,
            'total_questions': len(categorized_questions)
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        data = request.get_json()
        quiz_category = data.get('quiz_category', None)
        previous_questions = data.get('previous_questions', None)

        try:
            if (quiz_category is None):
                quiz_questions = Question.query.all()
            else:
                quiz_questions = Question.query.filter_by(
                    category=quiz_category['id']).all()
            random_question = quiz_questions[random.randrange(
                0, len(quiz_questions))].format() if len(quiz_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': random_question

            })
        except Exception as eror:
            print(e)
            abort(400)

    """
    @TODO:
    # Create error handlers for all expected errors
    # including 404 and 422.
    # """
    @app.errorhandler(400)
    def bad_request_handler(error):
        return jsonify({
            'success': False,
            'error': error,
            'message': "Bad Request"
        }), 400

    @app.errorhandler(404)
    def item_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Requested page not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_request(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "Request was unprocessable"
        }), 422

    return app
