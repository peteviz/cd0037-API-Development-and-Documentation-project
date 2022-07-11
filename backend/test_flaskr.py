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
        self.database_name = 'trivia'
        self.database_path = 'postgres://{}:{}@{}/{}'.format(
            'postgres', 'Dam1l0laak1nd3', 'localhost:5432', 'trivia')
        # self.database_name = "trivia"
        # self.database_path = "postgres://{}/{}".format(
        #     'localhost:5000', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # sample question
        self.question = {
            'question': "What human organ is used to breathe?",
            'category': "1",
            'answer': "Lungs",
            'difficulty': "1"

        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        """cheeck if all categories are succesfully retrieved"""
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_paginate_questions(self):
        """Check if questions are paginated"""

        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data["categories"])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data["questions"]), 10)
        # self.assertTrue(data["total_questions"])

    def test_invalid_page(self):
        """Test if page requested is invalid and returns a 404 error"""
        response = self.client().get('/questions?page=2500')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Requested page not found')

    def test_question_deletion(self):
        """Test for deletion of question"""

        question_del = Question(
            question=self.question['question'],
            category=self.question['category'],
            answer=self.question['answer'],
            difficulty=self.question['difficulty']
        )

        question_del.insert()
        response = self.client().delete('/questions/{}'.format(question_del.id))
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)

    def test_failed_question_deletion(self):
        """Failed deletion of question not in database"""
        response = self.client().delete('/questions/2600')
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(response.status_code, 404)

    def test_submit_questiom(self):
        """Test submission of question to database successfully"""
        response = self.client().post('/questions', json=self.question)
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)

    def test_failed_submit_question(self):
        """Test to check submission with missing data"""
        self.question['difficulty'] = None
        response = self.client().post('/questions', json=self.question)
        data = json.loads(response.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(response.status_code, 422)

    def test_questions_by_category(self):
        """Test to retrieve all questions in a category"""
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])

    def test_failed_question_by_category(self):
        """Test to get a non-esistent category"""
        response = self.client().get('/categories/2700/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)


        # Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
