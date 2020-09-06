import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'postgres:123@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # the point of this is test to test all of the api calls by initializing a mock database
    # and performing operations on it and see if they pass the tests or not.
    # all of the available assert methods:
    # https://http-api-base.readthedocs.io/en/latest/test/#writing-tests

    # test load all categories
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        categories = Category.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertEqual(len(categories), len(data['categories']))

    # check that all the questions are retrieved
    def test_retrieve_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        questions = Question.query.all()

        # check if the correct responses are sent
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['total_questions'], len(questions))
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)  # pagination

    def test_delete_question(self):
        question = Question(question='test question', answer='test answer',
                            difficulty=1, category=1)
        question.insert()
        questions = Question.query.all()

        # get the no. of questions before delete.
        len_questions_before = len(questions)
        question_id = question.id

        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        # get the no. of questions after delete, check if they are equal to
        # before (add one to after).
        questions = Question.query.all()
        len_questions_after = len(questions)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(len_questions_before, len_questions_after + 1)
        self.assertEqual(question, None)

    # try deleting a non existant question
    # we want the delete to fail
    def test_delete_non_existant_question(self):
        response = self.client().delete('/questions/x')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable entity')

    # test search by using a valid search term
    def test_search_question(self):
        new_search = {'searchTerm': 'title'}
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    # no search term is provided
    def test_seach_term_non_existant(self):
        new_search = {
            'searchTerm': '',
        }
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # no search results from the search term by using an invalid search term

    def test_no_search_results(self):
        new_search = {
            'searchTerm': '@#$%^&',
        }
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # make sure the new question is adding by checking the no of questions
    # before and after insertion (valid insertion)
    def test_add_question(self):
        total_questions_before = len(Question.query.all())
        test_question = {
            'question': 'test question',
            'answer': 'test answer',
            'difficulty': 1,
            'category': 1,
        }

        response = self.client().post('/questions', json=test_question)
        data = json.loads(response.data)
        total_questions_after = len(Question.query.all())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions_after, total_questions_before + 1)
        self.assertEqual(data['total_questions'], total_questions_after)

    # omit a field to invoke an error (invalid insertion)
    def test_error_add_question(self):
        test_question = {
            'answer': 'test answer',
            'difficulty': 1,
            'category': 1
        }

        response = self.client().post('/questions', json=test_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable entity")

    def test_retrieve_questions_per_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        questions = Question.query.filter(
            Question.category == str(1)).all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertEqual(len(data['questions']), len(questions))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    # invalid category
    def test_error_retrieve_questions_per_category(self):
        response = self.client().get('/categories/sdfuisafh/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    # valid quiz round, we get a random question
    def test_play_quiz(self):
        test_quiz_round = {'previous_questions': [],
                           'quiz_category': {'type': 'Entertainment', 'id': 1}}

        response = self.client().post('/quizzes', json=test_quiz_round)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # invoke an error by not providing a category
    def test_error_play_quiz(self):
        test_quiz_round = {'previous_questions': []}
        response = self.client().post('/quizzes', json=test_quiz_round)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable entity")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
