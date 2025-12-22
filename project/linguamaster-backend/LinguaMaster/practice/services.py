import whisper
from django.conf import settings
from difflib import SequenceMatcher

class SpeechRecognitionService:
    def __init__(self):
        self.model = whisper.load_model("base")  # You can change model size: tiny, base, small, medium, large
    
    def analyze_pronunciation(self, audio_file_path, reference_text, language="fr"):
        try:
            # Use local Whisper model for transcription
            result = self.model.transcribe(audio_file_path, language=language)
            transcription = result['text'].strip()
            
            accuracy_metrics = self._calculate_accuracy(transcription, reference_text, language)
            feedback = self._generate_feedback(transcription, reference_text, accuracy_metrics, language)
            score = self._calculate_score(accuracy_metrics)
            
            return {
                'success': True,
                'transcription': transcription,
                'confidence': 0.8,  # Local whisper doesn't provide confidence, using default
                'accuracy': accuracy_metrics['overall_accuracy'],
                'metrics': accuracy_metrics,
                'feedback': feedback,
                'score': score
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_accuracy(self, user_text, reference_text, language):
        similarity = SequenceMatcher(None, user_text.lower(), reference_text.lower()).ratio()
        user_words = user_text.lower().split()
        reference_words = reference_text.lower().split()
        
        correct_words = sum(1 for uw, rw in zip(user_words, reference_words) if uw == rw)
        word_error_rate = (len(reference_words) - correct_words) / max(len(reference_words), 1) * 100
        
        return {
            'overall_accuracy': similarity * 100,
            'word_error_rate': word_error_rate,
            'word_accuracy': max(0, 100 - word_error_rate),
            'words_correct': correct_words,
            'total_words': len(reference_words)
        }
    
    def _generate_feedback(self, user_text, reference_text, metrics, language):
        feedback = []
        accuracy = metrics['overall_accuracy']
        
        if accuracy >= 90:
            feedback.append("Excellent pronunciation! Very close to native.")
        elif accuracy >= 70:
            feedback.append("Good job! Your pronunciation is clear.")
        elif accuracy >= 50:
            feedback.append("Fair pronunciation. Keep practicing!")
        else:
            feedback.append("Let's work on pronunciation basics.")
        
        if language == 'fr':
            if 'on' in reference_text.lower() and 'on' not in user_text.lower():
                feedback.append("Try pronouncing 'on' more nasally.")
            if 'r' in reference_text.lower():
                feedback.append("Practice the French 'r' sound - it's softer than in English.")
        
        return feedback
    
    def _calculate_score(self, metrics):
        weights = {
            'overall_accuracy': 0.5,
            'word_accuracy': 0.3,
        }
        
        score = 0
        for metric, weight in weights.items():
            if metric in metrics:
                score += metrics[metric] * weight
        
        return min(100, score)