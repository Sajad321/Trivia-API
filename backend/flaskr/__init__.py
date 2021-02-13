import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import json

from models import setup_db, Question, Category


QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization")
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET, POST, PUT, PATCH, OPTIONS")
        return response
    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type
        results = {
            'success': True,
            'categories': formatted_categories
        }
        return jsonify(results)

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
    def get_questions():

        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {}
        for category in categories:
            formatted_categories[category.id] = category.type

        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)
        if len(current_questions) > 0:
            result = {
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': formatted_categories,
                'current_category': None
            }
            return jsonify(result)

        abort(404)

    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        question_query = Question.query.get(question_id)
        if question_query:
            Question.delete(question_query)
            result = {
                "success": True,
                "deleted_id": question_id,
                "total_questions": len(Question.query.all())
            }
            return jsonify(result)
        abort(404)
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
        question_data = request.get_json()
        if question_data:

            if ('question' in question_data
                and 'answer' in question_data
                and 'difficulty' in question_data
                    and 'category' in question_data):

                question = question_data.get('question')
                answer = question_data.get('answer')
                difficulty = question_data.get('difficulty')
                category = question_data.get('category')
                new_question = Question(
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    category=category
                )

                Question.insert(new_question)
                result = {
                    "success": True,
                    "question": question,
                    "answer": answer,
                    "difficulty": difficulty,
                    "category": category,
                    "total_questions": len(Question.query.all())
                }
                return jsonify(result), 201

            abort(400)

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
    @app.route("/questions/search", methods=['POST'])
    def search_questions():
        question_data = request.get_json()
        if question_data:
            if 'searchTerm' in question_data:
                search = question_data.get('searchTerm')
                filtered = Question.question.ilike('%{}%'.format(search))
                questions = Question.query.order_by(
                    Question.id).filter(filtered).all()
                current_questions = paginate_questions(request, questions)
                if len(current_questions) > 0:
                    results = {
                        "success": True,
                        "questions": current_questions,
                        "total_results": len(current_questions),
                        "current_category": None
                    }
                    return jsonify(results), 200

            abort(404)

        abort(422)

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        category_data = Category.query.get(category_id)
        category_query = Category.query.all()
        categories = [category.format() for category in category_query]
        questions = Question.query.filter_by(category=category_id).all()
        formatted_questions = paginate_questions(request, questions)
        if len(formatted_questions) > 0:
            result = {
                "success": True,
                "questions": formatted_questions,
                "total_questions": len(questions),
                "categories": categories,
                "current_category": Category.format(category_data),
            }
            return jsonify(result)
        abort(404)

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
    @app.route("/quizzes", methods=['POST'])
    def play():
        search_data = request.get_json()
        if search_data:
            if ('quiz_category' in search_data
                and 'id' in search_data['quiz_category']
                    and 'previous_questions' in search_data):
                category = search_data['quiz_category']['id']
                previous_questions = search_data["previous_questions"]
                if category == 0:
                    questions_query = Question.query.filter(
                        Question.id.notin_(previous_questions)).all()
                else:
                    questions_query = Question.query.filter_by(
                        category=category
                    ).filter(
                        Question.id.notin_(previous_questions)
                    ).all()
                length_of_available_question = len(questions_query)
                if length_of_available_question > 0:
                    result = {
                        "success": True,
                        "question": Question.format(
                            questions_query[random.randrange(
                                0,
                                length_of_available_question
                            )]
                        )
                    }
                else:
                    result = {
                        "success": True,
                        "question": None
                    }
                return jsonify(result)
            abort(404)
        abort(422)
    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(400)
    def bad_request(error):
        error_data = {
            "success": False,
            "error": 400,
            "message": "Bad request"
        }
        return jsonify(error_data), 400

    @app.errorhandler(404)
    def not_found(error):
        error_data = {
            "success": False,
            "error": 404,
            "message": "Source not found"
        }
        return jsonify(error_data), 404

    @app.errorhandler(422)
    def unprocessable(error):
        error_data = {
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }
        return jsonify(error_data), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        error_data = {
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }
        return jsonify(error_data), 500

    return app