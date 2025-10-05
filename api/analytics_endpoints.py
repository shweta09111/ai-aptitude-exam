#!/usr/bin/env python3
"""Analytics API endpoints for research dashboard"""

from flask import Blueprint, request, jsonify, send_file, Response
import logging
import json
import csv
import io
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.performance_analyzer import PerformanceAnalyzer

analytics_api = Blueprint('analytics_api', __name__, url_prefix='/api/analytics')

@analytics_api.route('/dashboard_data', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive data for analytics dashboard"""
    try:
        analyzer = PerformanceAnalyzer()
        
        # Get sessions data
        sessions_df = analyzer.get_adaptive_sessions()
        
        if len(sessions_df) == 0:
            return jsonify({
                'success': False,
                'error': 'No adaptive testing sessions found'
            })
        
        # Generate learning curves for top sessions
        session_ids = sessions_df['session_id'].head(5).tolist()
        learning_curves = analyzer.compare_sessions(session_ids)
        
        # Get question selection patterns
        patterns = analyzer.analyze_question_selection_patterns()
        
        # Generate statistics
        stats = analyzer.generate_research_statistics()
        
        # Prepare response time data
        response_times = {'Easy': [], 'Medium': [], 'Hard': []}
        for session_id in session_ids:
            session_details = analyzer.get_session_details(session_id)
            for _, row in session_details.iterrows():
                if row['time_taken'] and row['difficulty']:
                    response_times[row['difficulty']].append(row['time_taken'])
        
        # Prepare sessions data for table
        sessions_data = []
        for _, session in sessions_df.iterrows():
            sessions_data.append({
                'session_id': session['session_id'],
                'total_questions': int(session['total_questions']),
                'accuracy': float(session['accuracy']),
                'avg_time': float(session['avg_time']) if session['avg_time'] else 0,
                'start_time': session['start_time']
            })
        
        return jsonify({
            'success': True,
            'summary': {
                'total_sessions': len(sessions_df),
                'avg_accuracy': float(sessions_df['accuracy'].mean()),
                'total_questions': int(sessions_df['total_questions'].sum()),
                'avg_time': float(sessions_df['avg_time'].mean()) if sessions_df['avg_time'].mean() else 0
            },
            'learning_curves': learning_curves,
            'accuracy_distribution': stats['accuracy_distribution'] if stats else {'high_performers': 0, 'medium_performers': 0, 'low_performers': 0},
            'difficulty_patterns': patterns,
            'response_times': response_times,
            'sessions': sessions_data
        })
        
    except Exception as e:
        logging.error(f"Error in get_dashboard_data: {e}")
        return jsonify({
            'success': False,
            'error': f'Analytics error: {str(e)}'
        }), 500

@analytics_api.route('/export_csv', methods=['GET'])
def export_csv():
    """Export analytics data as CSV"""
    try:
        analyzer = PerformanceAnalyzer()
        
        # Create CSV data
        output = io.StringIO()
        sessions_df = analyzer.get_adaptive_sessions()
        
        if len(sessions_df) > 0:
            sessions_df.to_csv(output, index=False)
            output.seek(0)
            
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=adaptive_testing_sessions.csv'}
            )
        else:
            return jsonify({'error': 'No data to export'}), 404
            
    except Exception as e:
        logging.error(f"Error in export_csv: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@analytics_api.route('/export_statistics', methods=['GET'])
def export_statistics():
    """Export research statistics as JSON"""
    try:
        analyzer = PerformanceAnalyzer()
        stats = analyzer.generate_research_statistics()
        
        if stats:
            return Response(
                json.dumps(stats, indent=2, default=str),
                mimetype='application/json',
                headers={'Content-Disposition': 'attachment; filename=research_statistics.json'}
            )
        else:
            return jsonify({'error': 'No statistics to export'}), 404
            
    except Exception as e:
        logging.error(f"Error in export_statistics: {e}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@analytics_api.route('/session/<session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get detailed analysis for a specific session"""
    try:
        analyzer = PerformanceAnalyzer()
        
        # Get session details
        session_data = analyzer.get_session_details(session_id)
        ability_progression = analyzer.calculate_ability_progression(session_id)
        
        if len(session_data) == 0:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'details': session_data.to_dict('records'),
            'ability_progression': ability_progression,
            'summary': {
                'total_questions': len(session_data),
                'accuracy': float(session_data['correct'].mean()),
                'final_ability': ability_progression[-1]['ability'] if ability_progression else 0,
                'topics_covered': session_data['topic'].unique().tolist()
            }
        })
        
    except Exception as e:
        logging.error(f"Error in get_session_details: {e}")
        return jsonify({'error': f'Failed to get session details: {str(e)}'}), 500

@analytics_api.route('/research_insights', methods=['GET'])  
def get_research_insights():
    """Get insights for academic research"""
    try:
        analyzer = PerformanceAnalyzer()
        
        # Generate comprehensive research insights
        sessions_df = analyzer.get_adaptive_sessions()
        patterns = analyzer.analyze_question_selection_patterns()
        stats = analyzer.generate_research_statistics()
        
        insights = {
            'adaptation_effectiveness': [],
            'learning_patterns': [],
            'system_performance': stats
        }
        
        # Calculate adaptation effectiveness for each session
        for session_id in sessions_df['session_id']:
            if session_id in patterns:
                effectiveness = patterns[session_id]['adaptation_effectiveness']
                insights['adaptation_effectiveness'].append({
                    'session_id': session_id,
                    'effectiveness_score': effectiveness
                })
        
        # Analyze learning patterns
        for session_id in sessions_df['session_id'].head(10):
            progression = analyzer.calculate_ability_progression(session_id)
            if progression and len(progression) > 5:
                initial_ability = progression[0]['ability']
                final_ability = progression[-1]['ability']
                learning_gain = final_ability - initial_ability
                
                insights['learning_patterns'].append({
                    'session_id': session_id,
                    'initial_ability': initial_ability,
                    'final_ability': final_ability,
                    'learning_gain': learning_gain,
                    'questions_completed': len(progression)
                })
        
        return jsonify({
            'success': True,
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error in get_research_insights: {e}")
        return jsonify({'error': f'Failed to generate insights: {str(e)}'}), 500
