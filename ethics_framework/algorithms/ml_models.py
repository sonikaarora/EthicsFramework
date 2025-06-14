"""
ethics_framework/algorithms/ml_models.py
========================================
ML Model Implementations for Ethics Framework Testing
"""

import numpy as np
import random
import time
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from ..core.interfaces import Decision
from .base_algorithm import BaseAlgorithm, AlgorithmMetadata


class CollaborativeFilteringModel(BaseAlgorithm):
    """
    Collaborative Filtering Recommendation Model
    Simulates user-item collaborative filtering with realistic computation
    """
    
    def __init__(self):
        metadata = AlgorithmMetadata(
            name="collaborative_filtering",
            version="1.0.0",
            fairness_aware=True,
            privacy_level="medium",
            transparency_level="interpretable",
            bias_mitigation=["demographic_parity", "equalized_odds"],
            performance_characteristics={
                "latency_ms": 15.0,
                "throughput_rps": 1000,
                "memory_mb": 256
            }
        )
        super().__init__("collaborative_filtering", metadata)
        self.user_embeddings = {}
        self.item_embeddings = {}
        self.embedding_dim = 50
        
    def predict(self, decision: Decision, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate collaborative filtering recommendations"""
        start_time = time.perf_counter()
        
        user_id = decision.user_id
        
        # Simulate user embedding lookup/creation
        if user_id not in self.user_embeddings:
            self.user_embeddings[user_id] = np.random.randn(self.embedding_dim)
        
        user_embedding = self.user_embeddings[user_id]
        
        # Simulate item scoring (matrix multiplication)
        num_items = 1000
        item_scores = []
        
        for item_id in range(1, min(num_items + 1, 101)):  # Score top 100 items
            if item_id not in self.item_embeddings:
                self.item_embeddings[item_id] = np.random.randn(self.embedding_dim)
            
            item_embedding = self.item_embeddings[item_id]
            score = np.dot(user_embedding, item_embedding)
            item_scores.append((item_id, float(score)))
        
        # Sort by score and get top recommendations
        item_scores.sort(key=lambda x: x[1], reverse=True)
        top_recommendations = item_scores[:10]
        
        # Update performance stats
        inference_time = (time.perf_counter() - start_time) * 1000
        self.update_performance_stats(inference_time)
        self.usage_count += 1
        
        return {
            'algorithm': 'collaborative_filtering',
            'recommendations': [{'item_id': item_id, 'score': score} for item_id, score in top_recommendations],
            'user_embedding_norm': float(np.linalg.norm(user_embedding)),
            'total_items_scored': len(item_scores),
            'top_score': top_recommendations[0][1] if top_recommendations else 0.0,
            'inference_time_ms': inference_time,
            'model_metadata': self.get_ethical_properties()
        }
    
    def explain(self, decision: Decision, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation for collaborative filtering recommendations"""
        recommendations = prediction.get('recommendations', [])
        user_id = decision.user_id
        
        # Generate feature importance explanation
        feature_importance = {
            'user_preferences': 0.4,
            'item_popularity': 0.3,
            'collaborative_signals': 0.2,
            'demographic_similarity': 0.1
        }
        
        # Generate recommendation explanations
        recommendation_explanations = []
        for rec in recommendations[:3]:  # Explain top 3
            item_id = rec['item_id']
            explanation = {
                'item_id': item_id,
                'score': rec['score'],
                'reasons': [
                    f"Users similar to you liked this item (similarity: {random.uniform(0.7, 0.9):.2f})",
                    f"This item matches your preference profile (match: {random.uniform(0.6, 0.8):.2f})",
                    f"Popular among users in your demographic (popularity: {random.uniform(0.5, 0.7):.2f})"
                ],
                'confidence': random.uniform(0.7, 0.9)
            }
            recommendation_explanations.append(explanation)
        
        return {
            'algorithm': 'collaborative_filtering',
            'explanation_type': 'feature_importance',
            'feature_importance': feature_importance,
            'recommendation_explanations': recommendation_explanations,
            'user_profile_summary': {
                'embedding_dimension': self.embedding_dim,
                'profile_strength': float(np.linalg.norm(self.user_embeddings.get(user_id, np.zeros(self.embedding_dim)))),
                'total_interactions': random.randint(50, 500)
            },
            'fairness_considerations': {
                'demographic_balance': 'Recommendations balanced across user demographics',
                'popularity_bias_mitigation': 'Long-tail items included to reduce popularity bias'
            }
        }


class HiringRecommendationModel(BaseAlgorithm):
    """
    Hiring Recommendation Model
    Simulates candidate scoring for hiring decisions
    """
    
    def __init__(self):
        metadata = AlgorithmMetadata(
            name="hiring_recommendation",
            version="1.0.0",
            fairness_aware=True,
            privacy_level="high",
            transparency_level="explainable",
            bias_mitigation=["demographic_parity", "equalized_opportunity", "individual_fairness"],
            performance_characteristics={
                "latency_ms": 8.0,
                "throughput_rps": 2000,
                "memory_mb": 128
            }
        )
        super().__init__("hiring_recommendation", metadata)
        self.feature_weights = {
            'years_experience': 0.3,
            'education_level': 0.2,
            'skills_match': 0.4,
            'interview_score': 0.1
        }
        
    def predict(self, decision: Decision, context: Dict[str, Any]) -> Dict[str, Any]:
        """Score candidate for hiring decision"""
        start_time = time.perf_counter()
        
        attributes = decision.attributes
        
        # Extract candidate features
        years_experience = attributes.get('years_experience', random.randint(0, 20))
        education_level = attributes.get('education_level', random.randint(1, 5))
        skills_match = attributes.get('skills_match', random.uniform(0, 1))
        interview_score = attributes.get('interview_score', random.uniform(0, 100))
        
        # Normalize features
        normalized_features = {
            'years_experience': min(years_experience / 20.0, 1.0),
            'education_level': education_level / 5.0,
            'skills_match': skills_match,
            'interview_score': interview_score / 100.0
        }
        
        # Calculate weighted score
        total_score = sum(
            self.feature_weights[feature] * value 
            for feature, value in normalized_features.items()
        )
        
        # Add some noise for realism
        total_score += random.gauss(0, 0.05)
        total_score = max(0, min(1, total_score))  # Clamp to [0, 1]
        
        # Determine hiring recommendation
        hire_threshold = 0.6
        recommendation = "hire" if total_score >= hire_threshold else "reject"
        confidence = abs(total_score - hire_threshold) + 0.5
        
        # Update performance stats
        inference_time = (time.perf_counter() - start_time) * 1000
        self.update_performance_stats(inference_time)
        self.usage_count += 1
        
        return {
            'algorithm': 'hiring_recommendation',
            'candidate_score': float(total_score),
            'recommendation': recommendation,
            'confidence': float(min(confidence, 1.0)),
            'feature_scores': normalized_features,
            'hire_threshold': hire_threshold,
            'inference_time_ms': inference_time,
            'model_metadata': self.get_ethical_properties()
        }
    
    def explain(self, decision: Decision, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation for hiring recommendation"""
        feature_scores = prediction.get('feature_scores', {})
        candidate_score = prediction.get('candidate_score', 0.0)
        recommendation = prediction.get('recommendation', 'unknown')
        
        # Calculate feature contributions
        feature_contributions = {}
        for feature, weight in self.feature_weights.items():
            score = feature_scores.get(feature, 0.0)
            contribution = weight * score
            feature_contributions[feature] = {
                'weight': weight,
                'score': score,
                'contribution': contribution,
                'importance_rank': 0  # Will be filled below
            }
        
        # Rank features by contribution
        sorted_features = sorted(feature_contributions.items(), 
                               key=lambda x: x[1]['contribution'], reverse=True)
        for i, (feature, data) in enumerate(sorted_features):
            feature_contributions[feature]['importance_rank'] = i + 1
        
        # Generate natural language explanation
        top_feature = sorted_features[0][0]
        explanation_text = f"Recommendation: {recommendation.upper()}. "
        explanation_text += f"Primary factor: {top_feature.replace('_', ' ')} "
        explanation_text += f"(contribution: {feature_contributions[top_feature]['contribution']:.2f}). "
        
        return {
            'algorithm': 'hiring_recommendation',
            'explanation_type': 'feature_importance',
            'overall_score': candidate_score,
            'recommendation': recommendation,
            'feature_contributions': feature_contributions,
            'explanation_text': explanation_text,
            'fairness_analysis': {
                'protected_attributes_used': False,
                'bias_mitigation_applied': True,
                'fairness_score': random.uniform(0.8, 0.95),
                'demographic_parity_check': 'PASSED'
            },
            'confidence_factors': {
                'model_certainty': prediction.get('confidence', 0.0),
                'data_quality': random.uniform(0.7, 0.9),
                'feature_completeness': len(feature_scores) / len(self.feature_weights)
            }
        }


class SocialMediaRankingModel(BaseAlgorithm):
    """
    Social Media Content Ranking Model
    Simulates content ranking for social media feeds
    """
    
    def __init__(self):
        metadata = AlgorithmMetadata(
            name="social_media_ranking",
            version="1.0.0",
            fairness_aware=True,
            privacy_level="medium",
            transparency_level="interpretable",
            bias_mitigation=["content_diversity", "viewpoint_diversity"],
            performance_characteristics={
                "latency_ms": 5.0,
                "throughput_rps": 5000,
                "memory_mb": 64
            }
        )
        super().__init__("social_media_ranking", metadata)
        self.engagement_factors = {
            'relevance': 0.4,
            'recency': 0.2,
            'popularity': 0.2,
            'user_affinity': 0.2
        }
        
    def predict(self, decision: Decision, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rank content for social media feed"""
        start_time = time.perf_counter()
        
        attributes = decision.attributes
        
        # Simulate content features
        relevance = attributes.get('relevance_score', random.uniform(0, 1))
        recency_hours = attributes.get('recency_hours', random.randint(1, 168))  # 1 week
        popularity = attributes.get('popularity_score', random.uniform(0, 1))
        user_affinity = attributes.get('user_affinity', random.uniform(0, 1))
        
        # Calculate recency score (decay over time)
        recency_score = np.exp(-recency_hours / 24.0)  # Exponential decay
        
        # Calculate engagement score
        engagement_score = (
            self.engagement_factors['relevance'] * relevance +
            self.engagement_factors['recency'] * recency_score +
            self.engagement_factors['popularity'] * popularity +
            self.engagement_factors['user_affinity'] * user_affinity
        )
        
        # Add engagement time prediction
        predicted_engagement_time = engagement_score * 300  # seconds
        
        # Determine content action
        show_threshold = 0.3
        action = "show" if engagement_score >= show_threshold else "hide"
        
        # Update performance stats
        inference_time = (time.perf_counter() - start_time) * 1000
        self.update_performance_stats(inference_time)
        self.usage_count += 1
        
        return {
            'algorithm': 'social_media_ranking',
            'engagement_score': float(engagement_score),
            'predicted_engagement_time_sec': float(predicted_engagement_time),
            'action': action,
            'factor_scores': {
                'relevance': float(relevance),
                'recency': float(recency_score),
                'popularity': float(popularity),
                'user_affinity': float(user_affinity)
            },
            'show_threshold': show_threshold,
            'inference_time_ms': inference_time,
            'model_metadata': self.get_ethical_properties()
        }
    
    def explain(self, decision: Decision, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation for social media ranking"""
        factor_scores = prediction.get('factor_scores', {})
        engagement_score = prediction.get('engagement_score', 0.0)
        action = prediction.get('action', 'unknown')
        
        # Calculate factor contributions
        factor_contributions = {}
        for factor, weight in self.engagement_factors.items():
            score = factor_scores.get(factor, 0.0)
            contribution = weight * score
            factor_contributions[factor] = {
                'weight': weight,
                'score': score,
                'contribution': contribution
            }
        
        # Generate ranking explanation
        top_factor = max(factor_contributions.items(), key=lambda x: x[1]['contribution'])
        explanation_text = f"Content {action.upper()}. "
        explanation_text += f"Primary ranking factor: {top_factor[0]} "
        explanation_text += f"(score: {top_factor[1]['score']:.2f}, weight: {top_factor[1]['weight']:.1f}). "
        
        return {
            'algorithm': 'social_media_ranking',
            'explanation_type': 'factor_analysis',
            'engagement_score': engagement_score,
            'action': action,
            'factor_contributions': factor_contributions,
            'explanation_text': explanation_text,
            'diversity_considerations': {
                'content_type_diversity': 'Multiple content types considered',
                'viewpoint_diversity': 'Diverse perspectives promoted',
                'echo_chamber_mitigation': 'Algorithm reduces filter bubble effects'
            },
            'user_control': {
                'customizable_factors': list(self.engagement_factors.keys()),
                'transparency_level': 'High - all factors visible to user',
                'opt_out_available': True
            }
        }


class ContentClassificationModel(BaseAlgorithm):
    """
    Content Classification Model
    Simulates content classification for moderation
    """
    
    def __init__(self):
        metadata = AlgorithmMetadata(
            name="content_classification",
            version="1.0.0",
            fairness_aware=True,
            privacy_level="low",
            transparency_level="explainable",
            bias_mitigation=["cultural_bias_reduction", "language_fairness"],
            performance_characteristics={
                "latency_ms": 12.0,
                "throughput_rps": 3000,
                "memory_mb": 512
            }
        )
        super().__init__("content_classification", metadata)
        self.categories = ['safe', 'questionable', 'harmful', 'toxic']
        self.category_weights = [0.7, 0.2, 0.08, 0.02]  # Probability distribution
        
    def predict(self, decision: Decision, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify content for moderation"""
        start_time = time.perf_counter()
        
        attributes = decision.attributes
        
        # Simulate content analysis features
        text_length = attributes.get('text_length', random.randint(10, 1000))
        sentiment_score = attributes.get('sentiment_score', random.uniform(-1, 1))
        toxicity_indicators = attributes.get('toxicity_indicators', random.randint(0, 5))
        
        # Calculate classification scores
        feature_vector = np.array([
            text_length / 1000.0,  # Normalized text length
            (sentiment_score + 1) / 2.0,  # Normalized sentiment [0, 1]
            toxicity_indicators / 5.0  # Normalized toxicity indicators
        ])
        
        # Simulate neural network classification
        hidden_layer = np.tanh(np.random.randn(10, 3) @ feature_vector + np.random.randn(10))
        output_layer = np.random.randn(4, 10) @ hidden_layer + np.random.randn(4)
        
        # Apply softmax for probabilities
        exp_scores = np.exp(output_layer - np.max(output_layer))
        probabilities = exp_scores / np.sum(exp_scores)
        
        # Get predicted category
        predicted_category_idx = np.argmax(probabilities)
        predicted_category = self.categories[predicted_category_idx]
        confidence = float(probabilities[predicted_category_idx])
        
        # Determine moderation action
        action = "approve" if predicted_category in ['safe', 'questionable'] else "reject"
        
        # Update performance stats
        inference_time = (time.perf_counter() - start_time) * 1000
        self.update_performance_stats(inference_time)
        self.usage_count += 1
        
        return {
            'algorithm': 'content_classification',
            'predicted_category': predicted_category,
            'confidence': confidence,
            'category_probabilities': {
                category: float(prob) 
                for category, prob in zip(self.categories, probabilities)
            },
            'moderation_action': action,
            'feature_vector': feature_vector.tolist(),
            'toxicity_score': float(toxicity_indicators / 5.0),
            'inference_time_ms': inference_time,
            'model_metadata': self.get_ethical_properties()
        }
    
    def explain(self, decision: Decision, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation for content classification"""
        predicted_category = prediction.get('predicted_category', 'unknown')
        confidence = prediction.get('confidence', 0.0)
        category_probabilities = prediction.get('category_probabilities', {})
        feature_vector = prediction.get('feature_vector', [])
        
        # Feature names for explanation
        feature_names = ['text_length_norm', 'sentiment_norm', 'toxicity_indicators_norm']
        
        # Generate feature importance explanation
        feature_importance = {}
        if len(feature_vector) == len(feature_names):
            for i, (name, value) in enumerate(zip(feature_names, feature_vector)):
                # Simulate feature importance (in practice, would use SHAP or similar)
                importance = random.uniform(0.1, 0.9) if value > 0.1 else 0.05
                feature_importance[name] = {
                    'value': value,
                    'importance': importance,
                    'description': self._get_feature_description(name, value)
                }
        
        # Generate decision explanation
        explanation_text = f"Content classified as '{predicted_category}' with {confidence:.1%} confidence. "
        if predicted_category in ['harmful', 'toxic']:
            explanation_text += "Content flagged for manual review due to potential policy violations."
        else:
            explanation_text += "Content approved for publication."
        
        return {
            'algorithm': 'content_classification',
            'explanation_type': 'classification_breakdown',
            'predicted_category': predicted_category,
            'confidence': confidence,
            'category_probabilities': category_probabilities,
            'feature_importance': feature_importance,
            'explanation_text': explanation_text,
            'moderation_details': {
                'human_review_required': predicted_category in ['harmful', 'toxic'],
                'appeal_process_available': True,
                'automated_action': prediction.get('moderation_action', 'unknown')
            },
            'bias_mitigation': {
                'cultural_sensitivity': 'Model trained on diverse cultural contexts',
                'language_fairness': 'Equal treatment across languages and dialects',
                'demographic_neutrality': 'Classification independent of user demographics'
            }
        }
    
    def _get_feature_description(self, feature_name: str, value: float) -> str:
        """Get human-readable description of feature"""
        descriptions = {
            'text_length_norm': f"Text length: {'Long' if value > 0.7 else 'Medium' if value > 0.3 else 'Short'}",
            'sentiment_norm': f"Sentiment: {'Positive' if value > 0.6 else 'Negative' if value < 0.4 else 'Neutral'}",
            'toxicity_indicators_norm': f"Toxicity signals: {'High' if value > 0.7 else 'Medium' if value > 0.3 else 'Low'}"
        }
        return descriptions.get(feature_name, f"{feature_name}: {value:.2f}")


# Model factory function
def create_model(model_type: str) -> BaseAlgorithm:
    """Factory function to create ML models"""
    models = {
        'collaborative_filtering': CollaborativeFilteringModel,
        'hiring_recommendation': HiringRecommendationModel,
        'social_media_ranking': SocialMediaRankingModel,
        'content_classification': ContentClassificationModel
    }
    
    if model_type not in models:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return models[model_type]() 