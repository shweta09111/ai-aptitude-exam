#!/usr/bin/env python3
"""
AI Proctoring Module with OpenCV Integration
Advanced monitoring for exam integrity
"""

import cv2
import numpy as np
import sqlite3
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import os
from pathlib import Path

class AIProctoring:
    """AI-powered proctoring system for exam monitoring"""
    
    def __init__(self, db_path='aptitude_exam.db'):
        self.db_path = db_path
        self.is_monitoring = False
        self.video_capture = None
        self.face_cascade = None
        self.eye_cascade = None
        
        # Monitoring parameters
        self.face_detection_threshold = 0.6
        self.eye_detection_threshold = 0.3
        self.multiple_face_threshold = 2
        self.no_face_duration_limit = 5  # seconds
        
        # Tracking variables
        self.last_face_detection = time.time()
        self.face_count_history = []
        self.suspicious_activities = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenCV cascades
        self._initialize_cascades()
        
        # Initialize database
        self._initialize_proctoring_db()
    
    def _initialize_cascades(self):
        """Initialize OpenCV Haar cascades for face and eye detection"""
        try:
            # Use built-in OpenCV cascades or download if needed
            cascade_path = cv2.data.haarcascades
            face_cascade_path = os.path.join(cascade_path, 'haarcascade_frontalface_default.xml')
            eye_cascade_path = os.path.join(cascade_path, 'haarcascade_eye.xml')
            
            if os.path.exists(face_cascade_path):
                self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
                self.logger.info("✅ Face cascade loaded successfully")
            else:
                self.logger.error("❌ Face cascade not found")
                
            if os.path.exists(eye_cascade_path):
                self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
                self.logger.info("✅ Eye cascade loaded successfully")
            else:
                self.logger.error("❌ Eye cascade not found")
                
        except Exception as e:
            self.logger.error(f"Error initializing cascades: {e}")
    
    def _initialize_proctoring_db(self):
        """Initialize database tables for proctoring data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Proctoring sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proctoring_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    total_violations INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Violations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS proctoring_violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    violation_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    image_path TEXT,
                    metadata TEXT
                )
            ''')
            
            # Face detection logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS face_detection_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    faces_detected INTEGER DEFAULT 0,
                    eyes_detected INTEGER DEFAULT 0,
                    confidence_score REAL DEFAULT 0.0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    frame_data TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            self.logger.info("✅ Proctoring database initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing proctoring database: {e}")
    
    def start_monitoring(self, user_id: int, session_id: str) -> bool:
        """Start proctoring monitoring for a session"""
        try:
            if self.is_monitoring:
                self.logger.warning("Monitoring already active")
                return False
                
            # Initialize video capture
            self.video_capture = cv2.VideoCapture(0)
            if not self.video_capture.isOpened():
                self.logger.error("❌ Failed to open camera")
                return False
            
            # Start monitoring session in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO proctoring_sessions (user_id, session_id)
                VALUES (?, ?)
            ''', (user_id, session_id))
            conn.commit()
            conn.close()
            
            self.is_monitoring = True
            self.current_session_id = session_id
            self.current_user_id = user_id
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info(f"✅ Proctoring started for session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> Dict:
        """Stop proctoring monitoring and return session summary"""
        try:
            if not self.is_monitoring:
                self.logger.warning("No active monitoring session")
                return {'status': 'error', 'message': 'No active session'}
            
            self.is_monitoring = False
            
            # Release video capture
            if self.video_capture:
                self.video_capture.release()
                cv2.destroyAllWindows()
            
            # Update session end time
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE proctoring_sessions 
                SET end_time = CURRENT_TIMESTAMP, status = 'completed'
                WHERE session_id = ?
            ''', (self.current_session_id,))
            
            # Get session summary
            cursor.execute('''
                SELECT COUNT(*) as total_violations,
                       COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_violations,
                       COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_violations,
                       COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_violations
                FROM proctoring_violations 
                WHERE session_id = ?
            ''', (self.current_session_id,))
            
            summary = cursor.fetchone()
            conn.commit()
            conn.close()
            
            session_summary = {
                'status': 'completed',
                'session_id': self.current_session_id,
                'total_violations': summary[0] if summary else 0,
                'high_severity': summary[1] if summary else 0,
                'medium_severity': summary[2] if summary else 0,
                'low_severity': summary[3] if summary else 0,
                'integrity_score': self._calculate_integrity_score(summary[0] if summary else 0)
            }
            
            self.logger.info(f"✅ Proctoring session completed: {session_summary}")
            return session_summary
            
        except Exception as e:
            self.logger.error(f"Error stopping monitoring: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _monitoring_loop(self):
        """Main monitoring loop running in separate thread"""
        while self.is_monitoring:
            try:
                ret, frame = self.video_capture.read()
                if not ret:
                    self.logger.warning("Failed to read frame from camera")
                    continue
                
                # Analyze frame
                analysis_result = self._analyze_frame(frame)
                
                # Log detection data
                self._log_detection_data(analysis_result)
                
                # Check for violations
                violations = self._check_violations(analysis_result)
                for violation in violations:
                    self._record_violation(violation)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                continue
    
    def _analyze_frame(self, frame) -> Dict:
        """Analyze video frame for face and eye detection"""
        try:
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = []
            if self.face_cascade is not None:
                detected_faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                faces = detected_faces.tolist()
            
            # Detect eyes within faces
            eyes = []
            if self.eye_cascade is not None and len(faces) > 0:
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y+h, x:x+w]
                    detected_eyes = self.eye_cascade.detectMultiScale(roi_gray)
                    eyes.extend(detected_eyes.tolist())
            
            # Calculate confidence scores
            face_confidence = len(faces) / 1.0 if len(faces) <= 1 else 0.5  # Prefer single face
            eye_confidence = min(len(eyes) / 2.0, 1.0)  # Prefer two eyes
            
            return {
                'faces_detected': len(faces),
                'eyes_detected': len(eyes),
                'face_confidence': face_confidence,
                'eye_confidence': eye_confidence,
                'face_coordinates': faces,
                'eye_coordinates': eyes,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing frame: {e}")
            return {
                'faces_detected': 0,
                'eyes_detected': 0,
                'face_confidence': 0.0,
                'eye_confidence': 0.0,
                'face_coordinates': [],
                'eye_coordinates': [],
                'timestamp': time.time()
            }
    
    def _check_violations(self, analysis_result: Dict) -> List[Dict]:
        """Check for proctoring violations based on analysis"""
        violations = []
        current_time = time.time()
        
        # Check for multiple faces
        if analysis_result['faces_detected'] > 1:
            violations.append({
                'type': 'multiple_faces',
                'severity': 'high',
                'description': f"Multiple faces detected ({analysis_result['faces_detected']})",
                'metadata': json.dumps(analysis_result)
            })
        
        # Check for no face detected
        if analysis_result['faces_detected'] == 0:
            if current_time - self.last_face_detection > self.no_face_duration_limit:
                violations.append({
                    'type': 'no_face',
                    'severity': 'medium',
                    'description': f"No face detected for {int(current_time - self.last_face_detection)} seconds",
                    'metadata': json.dumps(analysis_result)
                })
        else:
            self.last_face_detection = current_time
        
        # Check for suspicious eye movement (no eyes detected with face present)
        if analysis_result['faces_detected'] > 0 and analysis_result['eyes_detected'] == 0:
            violations.append({
                'type': 'eyes_not_visible',
                'severity': 'low',
                'description': "Eyes not clearly visible or person looking away",
                'metadata': json.dumps(analysis_result)
            })
        
        # Check for low confidence detection (blurry, dark, etc.)
        if analysis_result['face_confidence'] < self.face_detection_threshold:
            violations.append({
                'type': 'poor_visibility',
                'severity': 'low',
                'description': f"Poor face visibility (confidence: {analysis_result['face_confidence']:.2f})",
                'metadata': json.dumps(analysis_result)
            })
        
        return violations
    
    def _record_violation(self, violation: Dict):
        """Record a violation in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO proctoring_violations 
                (session_id, violation_type, severity, description, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                self.current_session_id,
                violation['type'],
                violation['severity'],
                violation['description'],
                violation['metadata']
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.warning(f"🚨 Violation recorded: {violation['type']} - {violation['description']}")
            
        except Exception as e:
            self.logger.error(f"Error recording violation: {e}")
    
    def _log_detection_data(self, analysis_result: Dict):
        """Log detection data for analysis"""
        try:
            # Only log every 10th frame to reduce database size
            if int(time.time() * 10) % 10 == 0:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO face_detection_logs 
                    (session_id, faces_detected, eyes_detected, confidence_score, frame_data)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    self.current_session_id,
                    analysis_result['faces_detected'],
                    analysis_result['eyes_detected'],
                    analysis_result['face_confidence'],
                    json.dumps(analysis_result)
                ))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            self.logger.error(f"Error logging detection data: {e}")
    
    def _calculate_integrity_score(self, total_violations: int) -> float:
        """Calculate integrity score based on violations"""
        # Simple scoring algorithm - can be enhanced
        if total_violations == 0:
            return 100.0
        elif total_violations <= 3:
            return max(85.0 - (total_violations * 5), 70.0)
        elif total_violations <= 10:
            return max(70.0 - ((total_violations - 3) * 3), 50.0)
        else:
            return max(50.0 - ((total_violations - 10) * 2), 0.0)
    
    def get_session_report(self, session_id: str) -> Dict:
        """Get comprehensive proctoring report for a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get session info
            cursor.execute('''
                SELECT * FROM proctoring_sessions WHERE session_id = ?
            ''', (session_id,))
            session_info = cursor.fetchone()
            
            if not session_info:
                return {'error': 'Session not found'}
            
            # Get violations summary
            cursor.execute('''
                SELECT violation_type, severity, COUNT(*) as count
                FROM proctoring_violations 
                WHERE session_id = ?
                GROUP BY violation_type, severity
            ''', (session_id,))
            violations_summary = cursor.fetchall()
            
            # Get detection statistics
            cursor.execute('''
                SELECT 
                    AVG(faces_detected) as avg_faces,
                    AVG(eyes_detected) as avg_eyes,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(*) as total_frames
                FROM face_detection_logs 
                WHERE session_id = ?
            ''', (session_id,))
            detection_stats = cursor.fetchone()
            
            conn.close()
            
            # Format report
            report = {
                'session_id': session_id,
                'user_id': session_info[1],
                'start_time': session_info[3],
                'end_time': session_info[4],
                'status': session_info[6],
                'violations_summary': [
                    {
                        'type': v[0],
                        'severity': v[1],
                        'count': v[2]
                    } for v in violations_summary
                ],
                'detection_statistics': {
                    'avg_faces_detected': round(detection_stats[0], 2) if detection_stats[0] else 0,
                    'avg_eyes_detected': round(detection_stats[1], 2) if detection_stats[1] else 0,
                    'avg_confidence': round(detection_stats[2], 2) if detection_stats[2] else 0,
                    'total_frames_analyzed': detection_stats[3] if detection_stats[3] else 0
                },
                'integrity_score': self._calculate_integrity_score(len(violations_summary))
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating session report: {e}")
            return {'error': str(e)}
    
    def is_camera_available(self) -> bool:
        """Check if camera is available for proctoring"""
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                return ret
            return False
        except:
            return False
    
    def get_system_status(self) -> Dict:
        """Get proctoring system status"""
        return {
            'camera_available': self.is_camera_available(),
            'face_cascade_loaded': self.face_cascade is not None,
            'eye_cascade_loaded': self.eye_cascade is not None,
            'monitoring_active': self.is_monitoring,
            'opencv_version': cv2.__version__
        }


# Global proctoring instance
proctoring_system = None

def get_proctoring_system() -> AIProctoring:
    """Get singleton proctoring system instance"""
    global proctoring_system
    if proctoring_system is None:
        proctoring_system = AIProctoring()
    return proctoring_system

def initialize_proctoring() -> bool:
    """Initialize proctoring system"""
    try:
        system = get_proctoring_system()
        status = system.get_system_status()
        
        if not status['camera_available']:
            print("⚠️ Camera not available for proctoring")
            return False
        
        if not (status['face_cascade_loaded'] and status['eye_cascade_loaded']):
            print("⚠️ OpenCV cascades not loaded properly")
            return False
        
        print("✅ AI Proctoring system initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize proctoring system: {e}")
        return False


# Test the proctoring system
if __name__ == "__main__":
    print("🔐 Testing AI Proctoring System")
    print("=" * 50)
    
    # Initialize system
    system = AIProctoring()
    status = system.get_system_status()
    
    print("System Status:")
    print(f"  Camera Available: {'✅' if status['camera_available'] else '❌'}")
    print(f"  Face Detection: {'✅' if status['face_cascade_loaded'] else '❌'}")
    print(f"  Eye Detection: {'✅' if status['eye_cascade_loaded'] else '❌'}")
    print(f"  OpenCV Version: {status['opencv_version']}")
    
    if status['camera_available'] and status['face_cascade_loaded']:
        print("\n🧪 Running 10-second test monitoring...")
        
        # Start test monitoring
        system.start_monitoring(user_id=1, session_id="test_session")
        time.sleep(10)  # Monitor for 10 seconds
        
        # Stop and get summary
        summary = system.stop_monitoring()
        print(f"\n📊 Test Summary: {summary}")
        
        # Get detailed report
        report = system.get_session_report("test_session")
        print(f"\n📋 Detailed Report: {json.dumps(report, indent=2)}")
    
    else:
        print("\n⚠️ Cannot run test - missing camera or OpenCV cascades")
        print("To install OpenCV: pip install opencv-python")