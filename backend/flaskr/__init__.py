import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request):
    page_no = request.args.get('page', 1, type=int)  # grab page no. from url
    start = (page_no - 1) * QUESTIONS_PER_PAGE
    limit = start + QUESTIONS_PER_PAGE

    all_questions = Question.query.all()
    questions = [i.format() for i in all_questions]
    available_questions = questions[start:limit]

    return available_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app, resources={'/': {'origins': '*'}})
    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    # for get operations we select all items in DB and return them
    # for delete we filter to get item to be deleted then perform operation
    # for adding make sure that the insertion was successful
    # for search we match the search term with a question then return all matches (case insensitive)
    # for quiz play we randomly return a question out of all questions and
    # make sure it isn't included in previous questions

    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()

        return jsonify({
            'categories': {i.id: i.type for i in categories},
            'success': True,
        })
    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    def retrieve_questions():

        current_questions = paginate_questions(request)

        categories = Category.query.all()

        questions = Question.query.all()

        if not current_questions:
            abort(404)

        return jsonify({
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': {category.id: category.type for category in categories},
            'current category': None,
            'success': True,
        })
    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).first()
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except BaseException:
            abort(422)
    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route("/questions", methods=['POST'])
    def add_question():
        body = request.get_json()
        if 'question' not in body or 'answer' not in body or 'difficulty' not in body or 'category' not in body:
            abort(422)

        get_question = body.get('question')
        get_answer = body.get('answer')
        get_difficulty = body.get('difficulty')
        get_category = body.get('category')

        try:
            question = Question(
                question=get_question,
                answer=get_answer,
                difficulty=get_difficulty,
                category=get_category)
            question.insert()
            # print('insert successful')
            questions = Question.query.all()

            return jsonify({
                'success': True,
                'created': question.id,
                'total_questions': len(questions)
            })
        except BaseException:
            abort(422)
    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term != '':
            search_results = Question.query.filter(
                Question.question.ilike(
                    '%' + search_term + '%')).all()

            # print('---------------------',search_term,'--------',search_results)

            if search_results is not None and len(search_results) != 0:
                return jsonify({
                    'success': True,
                    # check format function in models.py
                    'questions': [question.format() for question in search_results],
                    'total_questions': len(search_results),
                    'current_category': None
                })
            else:
                abort(404)
        else:
            abort(404)
    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):
        try:
            questions = Question.query.filter(
                Question.category == str(category_id)).all()

            if not questions:
                return jsonify({
                    'success': True,
                    'questions': 'no questions available at this time',
                    'total_questions': len(questions),
                    'current_category': category_id
                })

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except BaseException:
            abort(404)  # not found

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz_question():
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        quiz_category = data.get('quiz_category')

        # if a category is not provided
        if not quiz_category:
            abort(422)

        questions = Question.query.filter_by(
            category=quiz_category['id']).all()

        # get a random question
        random_question = questions[random.randint(0, len(questions) - 1)]

        while True:
            if random_question in previous_questions:
                random_question = questions[random.randint(
                    0, len(questions) - 1)]
            else:
                break

        return jsonify({
            'question': random_question.format(),
            'success': True,
        })

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable entity"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
