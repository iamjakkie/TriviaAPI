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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is the most common programming language?',
            'answer': 'Javascript',
            'category': 5,
            'difficulty': 2
        }
        self.new_question_empty = {
            'question': '',
            'answer': '',
            'category': 1,
            'difficulty': 1
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_all_categories(self):
        '''
        Test to get all categories
        return 'success': True, 'categories': categories
        :pass
        '''
        res = self.client().get('/categories')
        data = json.loads(res.data)
        # check if the status code = 200
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)
    
    def test_get_paginate_questions(self):
        '''
        Test to get 10 questions
        return 'success': True, get maximum 10 questions
        :pass
        '''
        res = self.client().get('/questions')
        data = json.loads(res.data)
        # check if the status code = 200
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_error_paginate_questions(self):
        '''
        Test the unreasonable number set in pages
        return 'success': False, 404, and resource not found
        :pass
        '''
        res = self.client().get('/questions?page=10000000')
        data = json.loads(res.data)
        # confirm the status response code is 404
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        # confirm response has element equal "message": "resource not found"
        self.assertEqual(data['message'], 'resource not found')

    def test_sucsse_delete_question(self):
        '''
        Test the delete the question exit in db
        :pass
        '''
        res = self.client().delete('/questions/14')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question successfully deleted")
        self.assertTrue(data['delete_id'])

    def test_delete_question_not_exit(self):
        '''
        Test the delete the question not exit in db
        becesed cannot delete record not exit in db
        :pass
        '''
        res = self.client().delete('/questions/62334')
        data = json.loads(res.data)
        # confirm the status response code is 422
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")

    def test_create_new_question(self):
        '''
        Test insert question with data in db
        :pass
        '''
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        # check if the status code = 200
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['question'])

    def test_404_if_questions_creation_no_data(self):
        '''
        Test insert question without data in db
        :pass
        '''
        res = self.client().post('/questions', json=self.new_question_empty)
        data = json.loads(res.data)
        # confirm the status response code is 422
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_search_in_questions(self):
        '''
        Test search question with data in db
        :pass
        '''
        data_json = {
            'searchTerm': 'What boxer\'s original name is Cassius Clay'
        }
        res = self.client().post('/questions/search', json=data_json)
        data = json.loads(res.data)
        # check if the status code = 200
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['questions'])

    def test_search_in_questions_no_data(self):
        '''
        Test insert question without data in db
        :pass
        '''
        res = self.client().post('/questions/search', json={'searchTerm': ''})
        data = json.loads(res.data)
        # confirm the status response code is 422
        self.assertEqual(res.status_code, 422)

    def test_search_in_questions_no_data_in_db(self):
        '''
        Test insert question with data not in db
        :pass
        '''
        res = self.client().post('/questions/search',json={'searchTerm': 'xxxyz'})
        data = json.loads(res.data)
        # confirm the status response code is 404
        self.assertEqual(res.status_code, 404)

    def test_get_questions_on_category(self):
        '''
        Test get question on category with data in db
        :pass
        '''
        res = self.client().get('/categories/{}/questions'.format(4))
        data = json.loads(res.data)
        # check if the status code = 200
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['categories'], 'Art')
        self.assertTrue(data['categories'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['questions'])

    def test_get_error_questions_on_category(self):
        '''
        Test get question on category with data not exit in db
        :pass
        '''
        res = self.client().get('/categories/{}/questions'.format(19))
        data = json.loads(res.data)
        # confirm the status response code is 404
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_all_quizzes(self):
        '''
        Test play quizzes on all categores with data in db
        :pass
        '''
        data_json = {
            "previous_questions": [3, 5, 10, 11, 12, 4],
            "quiz_category": {"type": "click", "id": 0}
        }
        res = self.client().post('/quizzes', json=data_json)
        data = json.loads(res.data)
        # check if the status code = 200
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['question'])
        self.assertNotEqual(data['question']['id'], 3)
        self.assertNotEqual(data['question']['id'], 12)

    def test_get_quizzes_in_category(self):
        '''
        Test play quizzes on category with data in db
        :pass
        '''
        data_json = {
            "previous_questions": [3, 4, 10, 12, 11, 5],
            "quiz_category": {"type": "Art", "id": 2}
        }
        res = self.client().post('/quizzes', json=data_json)
        data = json.loads(res.data)
        # check if the status code = 200
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['question'])
        self.assertNotEqual(data['question']['id'], 3)
        self.assertNotEqual(data['question']['id'], 12)

    def test_error_quiz_category_not_found_quizzes(self):
        '''
        Test play quizzes on none (no data) category with data in db
        :pass
        '''
        data_json = {
            "previous_questions": [3, 4, 10, 12, 11, 5],
            "quiz_category": None
        }
        res = self.client().post('/quizzes', json=data_json)
        data = json.loads(res.data)
        # confirm the status response code is 400
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()