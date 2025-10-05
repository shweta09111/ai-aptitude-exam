#!/usr/bin/env python3
"""
Analytics API Blueprint for exam performance analysis
"""

from flask import Blueprint, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import random

# Create blueprint
analytics_api = Blueprint('analytics_api', __name__)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('aptitude_exam.db')
    conn.row_factory = sqlite3.Row
    return conn

@analytics_api.route('/dashboard_data')
def dashboard_data():
    """Get analytics dashboard data"""
    try:
        conn = get_db_connection()
        
        # Basic statistics
        total_questions = conn.execute("SELECT COUNT(*) FROM question").fetchone()[0]
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_exams = conn.execute("SELECT COUNT(*) FROM results").fetchone()[0]
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_exams = conn.execute(
            "SELECT COUNT(*) FROM results WHERE created_at >= ?", 
            (week_ago.isoformat(),)
        ).fetchone()[0]
        
        # Difficulty distribution
        difficulty_dist = dict(conn.execute('''
            SELECT difficulty, COUNT(*) as count 
            FROM question 
            GROUP BY difficulty
        ''').fetchall())
        
        # Performance statistics
        if total_exams > 0:
            avg_score = conn.execute("SELECT AVG(percentage) FROM results").fetchone()[0]
            avg_score = round(avg_score, 2) if avg_score else 0
        else:
            avg_score = 0
        
        # Topic performance
        topic_stats = conn.execute('''
            SELECT 
                SUBSTR(topic, 1, INSTR(topic, '-') - 1) as category,
                COUNT(*) as question_count
            FROM question 
            WHERE topic LIKE '%-%'
            GROUP BY category
            ORDER BY question_count DESC
            LIMIT 10
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'summary': {
                'total_questions': total_questions,
                'total_users': total_users,
                'total_exams': total_exams,
                'recent_exams': recent_exams,
                'avg_score': avg_score
            },
            'difficulty_distribution': difficulty_dist,
            'topic_stats': [
                {'category': row[0], 'count': row[1]} 
                for row in topic_stats
            ],
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@analytics_api.route('/performance_trends')
def performance_trends():
    """Get performance trends over time"""
    try:
        conn = get_db_connection()
        
        # Daily performance for last 30 days
        trends = conn.execute('''
            SELECT 
                DATE(created_at) as date,
                AVG(percentage) as avg_score,
                COUNT(*) as exam_count
            FROM results 
            WHERE created_at >= datetime('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'trends': [
                {
                    'date': row[0],
                    'avg_score': round(row[1], 2) if row[1] else 0,
                    'exam_count': row[2]
                }
                for row in trends
            ],
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@analytics_api.route('/user_analytics/<int:user_id>')
def user_analytics(user_id):
    """Get analytics for specific user"""
    try:
        conn = get_db_connection()
        
        # User statistics
        user_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_attempts,
                AVG(percentage) as avg_score,
                MAX(percentage) as best_score,
                MIN(percentage) as lowest_score,
                AVG(time_taken) as avg_time
            FROM results 
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        # Recent results
        recent_results = conn.execute('''
            SELECT percentage, time_taken, created_at
            FROM results 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'user_stats': {
                'total_attempts': user_stats[0] or 0,
                'avg_score': round(user_stats[1], 2) if user_stats[1] else 0,
                'best_score': round(user_stats[2], 2) if user_stats[2] else 0,
                'lowest_score': round(user_stats[3], 2) if user_stats[3] else 0,
                'avg_time': round(user_stats[4], 2) if user_stats[4] else 0
            },
            'recent_results': [
                {
                    'score': round(row[0], 2),
                    'time_taken': row[1],
                    'date': row[2]
                }
                for row in recent_results
            ],
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@analytics_api.route('/adaptive_sessions')
def adaptive_sessions():
    """Get adaptive exam sessions data"""
    try:
        conn = get_db_connection()
        
        # Check if adaptive_responses table exists
        try:
            sessions = conn.execute('''
                SELECT 
                    session_id,
                    COUNT(*) as question_count,
                    AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) as accuracy,
                    AVG(time_taken) as avg_time
                FROM adaptive_responses
                GROUP BY session_id
                ORDER BY MIN(created_at) DESC
                LIMIT 20
            ''').fetchall()
            
            return jsonify({
                'sessions': [
                    {
                        'session_id': row[0],
                        'question_count': row[1],
                        'accuracy': round(row[2] * 100, 2) if row[2] else 0,
                        'avg_time': round(row[3], 2) if row[3] else 0
                    }
                    for row in sessions
                ],
                'status': 'success'
            })
            
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            return jsonify({
                'sessions': [],
                'message': 'No adaptive sessions found yet',
                'status': 'success'
            })
        
        finally:
            conn.close()
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@analytics_api.route('/question_stats')
def question_stats():
    """Get question-level statistics"""
    try:
        conn = get_db_connection()
        
        # Question difficulty distribution
        difficulty_stats = dict(conn.execute('''
            SELECT difficulty, COUNT(*) as count 
            FROM question 
            GROUP BY difficulty
        ''').fetchall())
        
        # Topic distribution
        topic_stats = conn.execute('''
            SELECT topic, COUNT(*) as count 
            FROM question 
            WHERE topic IS NOT NULL
            GROUP BY topic
            ORDER BY count DESC
            LIMIT 15
        ''').fetchall()
        
        # Source distribution
        source_stats = dict(conn.execute('''
            SELECT source, COUNT(*) as count 
            FROM question 
            WHERE source IS NOT NULL
            GROUP BY source
        ''').fetchall())
        
        conn.close()
        
        return jsonify({
            'difficulty_distribution': difficulty_stats,
            'topic_distribution': [
                {'topic': row[0], 'count': row[1]} 
                for row in topic_stats
            ],
            'source_distribution': source_stats,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

# Health check
@analytics_api.route('/health')
def health_check():
    """Analytics API health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'analytics_api',
        'version': '1.0'
    })
