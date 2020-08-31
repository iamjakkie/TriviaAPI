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
    try:
      questionData = request.get_json()
      question = questionData.get('question')
      answer = questionData.get('answer')
      difficulty = questionData.get('difficulty')
      category = questionData.get('category')
    except:
      abort(422)
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

  @app.route('/questions/search', methods=['POST'])
  def searchQuestion():
    try:
      searchData = request.get_json().get('searchTerm', '')
      searchTerm = "%{}%".format(searchData)
      
      question = Question.query.filter(Question.question.ilike(searchTerm)).all()
      if question == 0 or not question:
        abort(404)
      else:
        current_questions = paginate_questions(request, question, QUESTIONS_PER_PAGE)
        categories = [category['category'] for category in current_questions]
        return jsonify({
          'success': True,
          'questions': current_questions,
          'totalQuestions': len(current_questions),
          'current_category': categories
        })
    except Exception:
      abort(404)
  
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def getQuestionsOnCategory(category_id):
    try:
      category_query = Category.query.filter_by(id=category_id).one_or_none()
      questions = Question.query.filter_by(category=category_id).all()
      total_questions = len(questions)
      current_questions = paginate_questions(request, questions, QUESTIONS_PER_PAGE)
      return jsonify({
          'success': True,
          'questions': current_questions,
          'totalQuestions': total_questions,
          'category': category_query.type
      })
    except Exception:
      abort(404)

  @app.route('/quizzes', methods=['POST'])
  def quizPlay():
    try:
      category_id = request.get_json()['quiz_category']['id']
      previous_questions = request.get_json()['previous_questions']

      if(category_id == 0):
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
      else:
        questions = Question.query.filter(Question.category == category_id).filter(Question.id.notin_(previous_questions)).all()

      if not questions:
        next_question = None
      else:
        new_question = random.choices(questions, k=1)
        next_question = (Question.query.filter_by(id = new_question[0].id).one_or_none()).format()
      
      return jsonify({
        "success": True,
        "question": next_question
      })

    except:
      abort(422)

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

    