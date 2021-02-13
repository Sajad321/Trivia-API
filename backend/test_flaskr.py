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
        self.database_path = "postgres://postgres:1@{}/{}".format(
            'localhost:5432', self.database_name)
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
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    def test_404_get_questions_beyond_valid_page(self):
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Source not found")

    def test_delete_question(self):
        response = self.client().delete('/questions/25')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted_id"])
        self.assertTrue(data["total_questions"])

    def test_404_delete_question(self):
        response = self.client().delete('/questions/90')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Source not found")

    def test_post_new_question(self):
        post_data = {
            'question': 'a',
            'answer': 'a',
            'difficulty': 1,
            'category': 1
        }
        response = self.client().post('/questions', json=post_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertTrue(data["answer"])
        self.assertTrue(data["difficulty"])
        self.assertTrue(data["category"])
        self.assertTrue(data["total_questions"])

    def test_400_post_new_question(self):
        post_data = {
            'question': 'a',
            'answer': 'a',
            'category': 1
        }
        response = self.client().post('/questions', json=post_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad request")

    def test_422_post_new_question(self):
        response = self.client().post('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_search_questions(self):
        post_data = {
            'search': 'S',
        }
        response = self.client().post('/questions/search', json=post_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_results"])
        self.assertTrue(data["current_questions"])

    def test_404_search_questions_beyond_valid_page(self):
        post_data = {
            'search': 'b',
        }
        response = self.client().post('/questions/search?page=100', json=post_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Source not found")

    def test_422_post_paginated_search_questions(self):
        response = self.client().post('/questions/search')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_get_question_by_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["current_category"]))

    def test_404_get_question_by_category_beyond_valid_page(self):
        response = self.client().get('/categories/1/questions?page=100')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Source not found")

    def test_play_quiz(self):
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }
        response = self.client().post('/quizzes', json=post_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_404_play_quiz(self):
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
            }
        }
        response = self.client().post('/quizzes', json=post_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Source not found")

    def test_422_play_quiz(self):
        response = self.client().post('/quizzes')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()