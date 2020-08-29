import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, paginate_questions

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app, resources={r"/*": {"origins": "*"}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                              'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                              'GET,PUT,POST,DELETE,OPTIONS,PATCH')
    return response

  @app.route('/categories', methods=['GET'])
  def get_all_categories():
    categories = Category.query.all()
    category_response = {category.id : category.type.format() for category in categories}
    return jsonify({
      'success': True,
      'categories': category_response
    })

  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions = Question.query.order_by(Question.id).all()
    total_questions = len(questions)
    category_query = Category.query.order_by(Category.id).all()
    current_questions = paginate_questions(
        request, questions,
        QUESTIONS_PER_PAGE)
    if (len(current_questions) == 0):
        abort(404)
    categories = {category.id : category.type.format() for category in category_query}
    return jsonify({
        'success': True,
        'questions': current_questions,
        'totalQuestions': total_questions,
        'categories': categories
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

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def deleteQuestion(question_id):
      try:
          question = Question.query.get(question_id)
          question.delete()
          return jsonify({
            'success': True,
            'message': "Question successfully deleted",
            'delete_id': question_id
          })
      except Exception:
          abort(422)

  @app.route('/questions', methods=['POST'])
  def createQuestion():
    questionData = request.get_json()
    question = questionData.get('question')
    answer = questionData.get('answer')
    difficulty = questionData.get('difficulty')
    category = questionData.get('category')
    if ((question == '') or (answer == '') or
            (difficulty == '') or (category == '')):
        abort(422)
    try:
      new_question = Question(question=question, answer=answer,
                                difficulty=difficulty,
                                category=category)
      new_question.insert()
      return jsonify({
        'success': True,
        'question': question,
        'answer': answer,
        'difficulty': difficulty,
        'category': category
      })
    except Exception:
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

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


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

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "Resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad Request"
      }), 400

  @app.errorhandler(500)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal Server Error"
      }), 500
  
  return app

    