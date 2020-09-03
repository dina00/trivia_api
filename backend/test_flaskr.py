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
        self.database_path = "postgresql://{}/{}".format('postgres:123@localhost:5432', self.database_name)
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
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_retrieve_questions(self):
        # parse response
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # check if the correct responses are sent
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10) # pagination 

    def test_delete_question(self):
        question = Question(question='test question', answer='test answer',
                            difficulty=1, category=1)
        question.insert()
        question_id = question.id

        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        question = Question.query.filter(
            Question.id == question.id).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    # try deleting a non existant question
    def test_delete_non_existant_question(self):
        response = self.client().delete('/questions/x')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable entity')

    def test_search_question(self):
        new_search = {'searchTerm': 'title'}
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_seach_term_non_existant(self):
        new_search = {
            'searchTerm': '',
        }
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_error_retrieve_questions_per_category(self):
        response = self.client().get('/categories/sdfuisafh/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        test_quiz_round = {'previous_questions': [],
                          'quiz_category': {'type': 'Entertainment', 'id': 1}}

        response = self.client().post('/quizzes', json=test_quiz_round)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

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