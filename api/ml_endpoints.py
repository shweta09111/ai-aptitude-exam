from flask import Blueprint, request, jsonify
import logging
import sys
import os
import sqlite3

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ml_api = Blueprint('ml_api', __name__, url_prefix='/api/ml')

@ml_api.route('/health', methods=['GET'])
def health_check():
    """Check if ML API is working"""
    try:
        from ml_models.difficulty_classifier import DifficultyClassifier
        classifier = DifficultyClassifier()
        
        return jsonify({
            'status': 'healthy',
            'message': 'ML API is running and classifier is available',
            'model_loaded': True
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'ML API error: {str(e)}',
            'model_loaded': False
        }), 500

@ml_api.route('/classify_difficulty', methods=['POST'])
def classify_difficulty():
    """API endpoint to classify question difficulty"""
    try:
        data = request.get_json()
        question_text = data.get('question_text', '')
        
        if not question_text:
            return jsonify({'error': 'question_text is required'}), 400
        
        from ml_models.difficulty_classifier import DifficultyClassifier
        classifier = DifficultyClassifier()
        
        # Get prediction
        result = classifier.predict(question_text)
        
        return jsonify({
            'success': True,
            'difficulty': result['difficulty'],
            'confidence': result['confidence'],
            'probabilities': result['probabilities'],
            'method': result['method']
        })
        
    except Exception as e:
        logging.error(f"Error in classify_difficulty: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@ml_api.route('/classify_all', methods=['POST'])
def classify_all_questions():
    """Classify all questions in the database"""
    try:
        from ml_models.difficulty_classifier import DifficultyClassifier
        
        classifier = DifficultyClassifier()
        
        # Get all questions from database
        conn = sqlite3.connect("aptitude_exam.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, question_text, difficulty FROM question WHERE question_text IS NOT NULL")
        questions = cursor.fetchall()
        
        if not questions:
            return jsonify({
                'success': False,
                'error': 'No questions found in database'
            }), 404
        
        classified_count = 0
        updated_count = 0
        
        for question_id, question_text, current_difficulty in questions:
            try:
                # Get AI prediction
                result = classifier.predict(question_text)
                predicted_difficulty = result['difficulty']
                
                # Update only if different from current or if current is None/empty
                if not current_difficulty or current_difficulty != predicted_difficulty:
                    cursor.execute(
                        "UPDATE question SET difficulty = ? WHERE id = ?",
                        (predicted_difficulty, question_id)
                    )
                    updated_count += 1
                
                classified_count += 1
                
            except Exception as e:
                logging.error(f"Error classifying question {question_id}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'classified_count': classified_count,
            'updated_count': updated_count,
            'total_questions': len(questions),
            'message': f'Successfully classified {classified_count} questions, updated {updated_count}'
        })
        
    except Exception as e:
        logging.error(f"Error in classify_all_questions: {e}")
        return jsonify({
            'success': False,
            'error': f'Classification failed: {str(e)}'
        }), 500

# Add these new endpoints to your existing ml_endpoints.py

@ml_api.route('/next_question', methods=['POST'])
def get_next_adaptive_question():
    """Get next question using adaptive algorithm"""
    try:
        from ml_models.adaptive_engine import AdaptiveTestEngine
        
        data = request.get_json()
        student_id = data.get('student_id', 1)
        session_id = data.get('session_id', 'default')
        
        engine = AdaptiveTestEngine()
        question = engine.select_next_question(student_id, session_id)
        
        if question:
            return jsonify({
                'success': True,
                'question': question,
                'max_questions': engine.max_questions
            })
        else:
            # No more questions, generate final report
            report = engine.generate_session_report(student_id, session_id)
            return jsonify({
                'success': True,
                'completed': True,
                'report': report
            })
            
    except Exception as e:
        logging.error(f"Error in get_next_adaptive_question: {e}")
        return jsonify({'error': f'Failed to get next question: {str(e)}'}), 500

@ml_api.route('/submit_response', methods=['POST'])
def submit_adaptive_response():
    """Submit student response and get feedback"""
    try:
        from ml_models.adaptive_engine import AdaptiveTestEngine
        
        data = request.get_json()
        student_id = data.get('student_id', 1)
        session_id = data.get('session_id', 'default')
        question_id = data.get('question_id')
        selected_option = data.get('selected_option')
        time_taken = data.get('time_taken', 0)
        
        if not all([question_id, selected_option]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        engine = AdaptiveTestEngine()
        result = engine.record_response(
            student_id, session_id, question_id, selected_option, time_taken
        )
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error in submit_adaptive_response: {e}")
        return jsonify({'error': f'Failed to submit response: {str(e)}'}), 500

@ml_api.route('/session_report/<session_id>', methods=['GET'])
def get_session_report(session_id):
    """Get comprehensive session report"""
    try:
        from ml_models.adaptive_engine import AdaptiveTestEngine
        
        student_id = request.args.get('student_id', 1)
        
        engine = AdaptiveTestEngine()
        report = engine.generate_session_report(student_id, session_id)
        
        return jsonify({
            'success': True,
            'report': report,
            'session_id': session_id
        })
        
    except Exception as e:
        logging.error(f"Error in get_session_report: {e}")
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500
