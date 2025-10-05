#!/usr/bin/env python3
"""Advanced analytics engine for adaptive testing research"""

import sqlite3
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

class PerformanceAnalyzer:
    def __init__(self):
        self.db_path = "aptitude_exam.db"
        
    def get_adaptive_sessions(self):
        """Get all adaptive testing sessions"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT 
            session_id,
            student_id,
            COUNT(*) as total_questions,
            AVG(CAST(correct AS FLOAT)) as accuracy,
            AVG(time_taken) as avg_time,
            MIN(response_time) as start_time,
            MAX(response_time) as end_time,
            GROUP_CONCAT(difficulty) as difficulty_sequence
        FROM adaptive_responses 
        WHERE session_id IS NOT NULL
        GROUP BY session_id, student_id
        ORDER BY start_time DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_session_details(self, session_id):
        """Get detailed data for a specific session"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT 
            ar.*,
            q.question_text,
            q.topic
        FROM adaptive_responses ar
        LEFT JOIN question q ON ar.question_id = q.id
        WHERE ar.session_id = ?
        ORDER BY ar.response_time
        """
        
        df = pd.read_sql_query(query, conn, params=[session_id])
        conn.close()
        
        return df
    
    def calculate_ability_progression(self, session_id):
        """Calculate ability progression over time using IRT"""
        session_data = self.get_session_details(session_id)
        
        if len(session_data) == 0:
            return []
        
        # Simulate ability estimation progression
        ability_estimates = []
        running_correct = 0
        difficulty_weights = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        
        for i, row in session_data.iterrows():
            if row['correct']:
                running_correct += difficulty_weights.get(row['difficulty'], 2)
            
            total_weight = sum(difficulty_weights.get(r['difficulty'], 2) 
                             for _, r in session_data.iloc[:i+1].iterrows())
            
            if total_weight > 0:
                weighted_accuracy = running_correct / total_weight
                # Convert to ability scale (-3 to +3)
                if weighted_accuracy >= 0.99:
                    ability = 2.5
                elif weighted_accuracy <= 0.01:
                    ability = -2.5
                else:
                    ability = np.log(weighted_accuracy / (1 - weighted_accuracy))
                    ability = max(-3.0, min(3.0, ability))
            else:
                ability = 0.0
            
            ability_estimates.append({
                'question_number': i + 1,
                'ability': ability,
                'accuracy': weighted_accuracy if total_weight > 0 else 0.5,
                'difficulty': row['difficulty'],
                'correct': row['correct'],
                'time_taken': row['time_taken']
            })
        
        return ability_estimates
    
    def analyze_question_selection_patterns(self):
        """Analyze how the adaptive algorithm selects questions"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT 
            session_id,
            question_id,
            difficulty,
            difficulty_level,
            correct,
            time_taken,
            ROW_NUMBER() OVER (PARTITION BY session_id ORDER BY response_time) as question_order
        FROM adaptive_responses
        ORDER BY session_id, response_time
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Analyze difficulty progression patterns
        patterns = {}
        for session in df['session_id'].unique():
            session_data = df[df['session_id'] == session]
            
            difficulty_sequence = session_data['difficulty'].tolist()
            accuracy_sequence = session_data['correct'].tolist()
            
            patterns[session] = {
                'difficulty_progression': difficulty_sequence,
                'accuracy_progression': accuracy_sequence,
                'adaptation_effectiveness': self.calculate_adaptation_effectiveness(
                    difficulty_sequence, accuracy_sequence
                )
            }
        
        return patterns
    
    def calculate_adaptation_effectiveness(self, difficulties, accuracies):
        """Calculate how effectively the system adapted difficulty"""
        if len(accuracies) < 3:
            return 0.5
        
        # Target accuracy around 70-80% for optimal learning
        target_accuracy = 0.75
        recent_accuracy = np.mean(accuracies[-5:])  # Last 5 questions
        
        effectiveness = 1.0 - abs(recent_accuracy - target_accuracy)
        return max(0.0, min(1.0, effectiveness))
    
    def generate_learning_curve_data(self, session_id):
        """Generate data for learning curve visualization"""
        ability_progression = self.calculate_ability_progression(session_id)
        
        if not ability_progression:
            return None
        
        return {
            'question_numbers': [p['question_number'] for p in ability_progression],
            'abilities': [p['ability'] for p in ability_progression],
            'accuracies': [p['accuracy'] for p in ability_progression],
            'difficulties': [p['difficulty'] for p in ability_progression],
            'times': [p['time_taken'] for p in ability_progression]
        }
    
    def compare_sessions(self, session_ids):
        """Compare multiple sessions for research analysis"""
        comparison_data = {}
        
        for session_id in session_ids:
            curve_data = self.generate_learning_curve_data(session_id)
            if curve_data:
                comparison_data[session_id] = curve_data
        
        return comparison_data
    
    def generate_research_statistics(self):
        """Generate comprehensive statistics for research paper"""
        sessions_df = self.get_adaptive_sessions()
        
        if len(sessions_df) == 0:
            return None
        
        stats = {
            'total_sessions': len(sessions_df),
            'total_questions_administered': sessions_df['total_questions'].sum(),
            'average_session_length': sessions_df['total_questions'].mean(),
            'overall_accuracy': sessions_df['accuracy'].mean(),
            'accuracy_std': sessions_df['accuracy'].std(),
            'average_time_per_question': sessions_df['avg_time'].mean(),
            'session_duration_stats': {
                'min': sessions_df['total_questions'].min(),
                'max': sessions_df['total_questions'].max(),
                'median': sessions_df['total_questions'].median()
            },
            'accuracy_distribution': {
                'high_performers': len(sessions_df[sessions_df['accuracy'] > 0.8]),
                'medium_performers': len(sessions_df[(sessions_df['accuracy'] >= 0.6) & 
                                                   (sessions_df['accuracy'] <= 0.8)]),
                'low_performers': len(sessions_df[sessions_df['accuracy'] < 0.6])
            }
        }
        
        return stats
    
    def export_research_data(self, output_dir="research_exports"):
        """Export data in formats suitable for academic analysis"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Export session summaries
        sessions_df = self.get_adaptive_sessions()
        sessions_df.to_csv(output_path / "session_summaries.csv", index=False)
        
        # Export detailed responses
        conn = sqlite3.connect(self.db_path)
        detailed_query = """
        SELECT 
            ar.*,
            q.question_text,
            q.topic,
            q.option_a,
            q.option_b,
            q.option_c,
            q.option_d,
            q.correct_option
        FROM adaptive_responses ar
        LEFT JOIN question q ON ar.question_id = q.id
        ORDER BY ar.session_id, ar.response_time
        """
        
        detailed_df = pd.read_sql_query(detailed_query, conn)
        detailed_df.to_csv(output_path / "detailed_responses.csv", index=False)
        conn.close()
        
        # Export research statistics
        stats = self.generate_research_statistics()
        if stats:
            with open(output_path / "research_statistics.json", 'w') as f:
                json.dump(stats, f, indent=2, default=str)
        
        print(f"✅ Research data exported to {output_path}")
        return output_path


# Test the analyzer
if __name__ == "__main__":
    print("🔬 Testing Performance Analyzer")
    print("=" * 50)
    
    analyzer = PerformanceAnalyzer()
    
    # Get sessions
    sessions = analyzer.get_adaptive_sessions()
    print(f"📊 Found {len(sessions)} adaptive testing sessions")
    
    if len(sessions) > 0:
        # Analyze first session
        session_id = sessions.iloc[0]['session_id']
        print(f"🔍 Analyzing session: {session_id}")
        
        # Get ability progression
        progression = analyzer.calculate_ability_progression(session_id)
        print(f"📈 Ability progression: {len(progression)} data points")
        
        if progression:
            final_ability = progression[-1]['ability']
            final_accuracy = progression[-1]['accuracy']
            print(f"🎯 Final ability estimate: {final_ability:.2f}")
            print(f"📊 Final accuracy: {final_accuracy:.2%}")
        
        # Generate research statistics
        stats = analyzer.generate_research_statistics()
        if stats:
            print(f"\n📋 Research Statistics:")
            print(f"   Total sessions: {stats['total_sessions']}")
            print(f"   Average accuracy: {stats['overall_accuracy']:.2%}")
            print(f"   Average session length: {stats['average_session_length']:.1f} questions")
        
        # Export data
        export_path = analyzer.export_research_data()
        print(f"\n💾 Data exported for research analysis")
    
    else:
        print("❌ No adaptive testing sessions found")
        print("💡 Take some adaptive exams first to generate data for analysis")
