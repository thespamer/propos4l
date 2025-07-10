from typing import Dict, List, Optional, Counter as CounterType
from collections import Counter
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from app.models.database import Document, SemanticBlock, BlockType
from app.database import get_session
from app.core.logging import get_logger
from app.core.monitoring import monitor_performance
from app.services.nlp_service import NLPServiceStore

class PatternAnalyzer:
    def __init__(self, vector_store=None):
        """Initialize the pattern analyzer"""
        self.logger = get_logger(__name__)
        self.vector_store = vector_store
        self.nlp_service = NLPServiceStore()
        
    async def analyze_block_patterns(self, block_type: BlockType, min_samples: int = 3) -> Dict:
        """
        Analyze patterns in blocks of a specific type
        """
        # Get all blocks of this type from vector store
        blocks = await self.vector_store.search(
            query="",  # Empty query to get all blocks
            k=100,  # Get a good sample size
            index_type=block_type
        )
        
        if not blocks:
            return {}
            
        # Analyze language patterns
        language_patterns = self._analyze_language_patterns([
            b['metadata']['language_patterns'] for b in blocks
        ])
        
        # Analyze formatting patterns
        formatting_patterns = self._analyze_formatting_patterns([
            b['metadata']['formatting_metadata'] for b in blocks
        ])
        
        # Analyze content structure
        content_patterns = await self._analyze_content_patterns(blocks, min_samples)
        
        # Enhanced NLP analysis
        nlp_analysis = {
            'entities': self.nlp_service.extract_entities([b['content'] for b in blocks]),
            'key_phrases': self.nlp_service.extract_key_phrases([b['content'] for b in blocks], method='hybrid'),
            'technical_terms': self.nlp_service.extract_technical_terms([b['content'] for b in blocks]),
            'text_structure': self.nlp_service.analyze_text_structure([b['content'] for b in blocks])
        }
        
        # Combine patterns with NLP insights
        patterns = {
            'language_patterns': language_patterns,
            'formatting_patterns': formatting_patterns,
            'content_patterns': content_patterns,
            'nlp_patterns': {
                'entity_patterns': self._analyze_entity_patterns(nlp_analysis['entities']),
                'key_phrase_patterns': self._analyze_phrase_patterns(nlp_analysis['key_phrases']),
                'technical_patterns': self._analyze_technical_patterns(nlp_analysis['technical_terms']),
                'complexity_patterns': self._analyze_complexity_patterns(nlp_analysis['text_structure'])
            }
        }
        
        return patterns
    
    def _analyze_language_patterns(self, patterns_list: List[Dict]) -> Dict:
        """
        Analyze common language patterns across blocks
        """
        aggregated = {
            'bullet_points': [],
            'numbered_lists': [],
            'technical_terms': [],
            'monetary_values': [],
            'dates': [],
            'percentages': [],
            'sentence_count': [],
            'average_sentence_length': []
        }
        
        # Collect all values
        for patterns in patterns_list:
            for key in aggregated:
                if key in patterns:
                    aggregated[key].append(patterns[key])
        
        # Calculate statistics
        stats = {}
        for key, values in aggregated.items():
            if values:
                stats[key] = {
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values) if len(values) > 1 else 0,
                    'min': min(values),
                    'max': max(values)
                }
        
        return stats
    
    def _analyze_formatting_patterns(self, formatting_list: List[Dict]) -> Dict:
        """
        Analyze common formatting patterns across blocks
        """
        # Aggregate formatting attributes
        fonts = Counter()
        font_sizes = Counter()
        layout_styles = Counter()
        features = {
            'has_tables': 0,
            'has_images': 0,
            'has_bold': 0,
            'has_italic': 0
        }
        
        total = len(formatting_list)
        if total == 0:
            return {}
        
        for fmt in formatting_list:
            # Count fonts and sizes
            for font, count in fmt.get('fonts', {}).items():
                fonts[font] += count
            for size, count in fmt.get('font_sizes', {}).items():
                font_sizes[float(size)] += count
            
            # Count layout styles
            layout_styles[fmt.get('layout_style', 'text')] += 1
            
            # Count features
            for feature in features:
                if fmt.get(feature, False):
                    features[feature] += 1
        
        # Convert to percentages
        feature_stats = {
            key: (count / total) * 100 
            for key, count in features.items()
        }
        
        return {
            'common_fonts': dict(fonts.most_common(3)),
            'common_font_sizes': dict(font_sizes.most_common(3)),
            'layout_distribution': dict(layout_styles),
            'feature_usage': feature_stats
        }
    
    async def _analyze_content_patterns(self, blocks: List[Dict], min_samples: int) -> Dict:
        """
        Analyze content patterns using clustering
        """
        if len(blocks) < min_samples:
            return {}
        
        # Extract features for clustering
        features = []
        for block in blocks:
            patterns = block['metadata']['language_patterns']
            features.append([
                patterns.get('bullet_points', 0),
                patterns.get('numbered_lists', 0),
                patterns.get('technical_terms', 0),
                patterns.get('sentence_count', 0),
                patterns.get('average_sentence_length', 0)
            ])
        
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Cluster similar blocks
        clustering = DBSCAN(eps=0.5, min_samples=min_samples).fit(features_scaled)
        
        # Analyze clusters
        clusters = {}
        for i, label in enumerate(clustering.labels_):
            if label == -1:  # Noise points
                continue
            
            if label not in clusters:
                clusters[label] = []
            clusters[label].append({
                'content': blocks[i]['content'][:200],  # First 200 chars
                'similarity_score': blocks[i]['similarity_score'],
                'language_patterns': blocks[i]['metadata']['language_patterns']
            })
        
        # Calculate cluster statistics
        cluster_stats = {}
        for label, cluster_blocks in clusters.items():
            cluster_stats[f'cluster_{label}'] = {
                'size': len(cluster_blocks),
                'avg_similarity': np.mean([b['similarity_score'] for b in cluster_blocks]),
                'common_patterns': self._analyze_language_patterns([
                    b['language_patterns'] for b in cluster_blocks
                ]),
                'examples': cluster_blocks[:2]  # Show 2 examples per cluster
            }
        
        return {
            'total_clusters': len(clusters),
            'noise_points': sum(1 for l in clustering.labels_ if l == -1),
            'clusters': cluster_stats
        }
    
    def _analyze_entity_patterns(self, entities: List[List[str]]) -> Dict:
        """
        Analyze entity patterns
        """
        # Aggregate entities
        entity_counts = Counter()
        for entity_list in entities:
            for entity in entity_list:
                entity_counts[entity] += 1
        
        # Calculate statistics
        stats = {}
        for entity, count in entity_counts.items():
            stats[entity] = {
                'count': count,
                'frequency': count / len(entities)
            }
        
        return stats
    
    def _analyze_phrase_patterns(self, phrases: List[List[str]]) -> Dict:
        """
        Analyze phrase patterns
        """
        # Aggregate phrases
        phrase_counts = Counter()
        for phrase_list in phrases:
            for phrase in phrase_list:
                phrase_counts[phrase] += 1
        
        # Calculate statistics
        stats = {}
        for phrase, count in phrase_counts.items():
            stats[phrase] = {
                'count': count,
                'frequency': count / len(phrases)
            }
        
        return stats
    
    def _analyze_technical_patterns(self, technical_terms: List[List[str]]) -> Dict:
        """
        Analyze technical term patterns
        """
        # Aggregate technical terms
        technical_term_counts = Counter()
        for term_list in technical_terms:
            for term in term_list:
                technical_term_counts[term] += 1
        
        # Calculate statistics
        stats = {}
        for term, count in technical_term_counts.items():
            stats[term] = {
                'count': count,
                'frequency': count / len(technical_terms)
            }
        
        return stats
    
    def _analyze_complexity_patterns(self, complexity_analysis: List[Dict]) -> Dict:
        """
        Analyze complexity patterns
        """
        # Aggregate complexity metrics
        complexity_metrics = {
            'complexity_score': [],
            'sentence_count': [],
            'avg_sentence_length': [],
            'noun_phrases': [],
            'verb_phrases': []
        }
        
        for analysis in complexity_analysis:
            for metric, value in analysis.items():
                complexity_metrics[metric].append(value)
        
        # Calculate statistics
        stats = {}
        for metric, values in complexity_metrics.items():
            if values:
                stats[metric] = {
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values) if len(values) > 1 else 0,
                    'min': min(values),
                    'max': max(values)
                }
        
        return stats
    
    async def get_block_recommendations(self, block_type: BlockType, content: str) -> Dict:
        """
        Get recommendations for improving a block based on patterns
        """
        # Get similar blocks
        similar_blocks = await self.vector_store.search_similar_blocks(
            content=content,
            block_type=block_type,
            k=5,
            confidence_threshold=0.7
        )
        
        if not similar_blocks:
            return {}
        
        # Analyze patterns in similar blocks
        patterns = await self.analyze_block_patterns(block_type)
        
        # Generate recommendations
        recommendations = {
            'formatting': self._get_formatting_recommendations(
                content, patterns.get('formatting_patterns', {})
            ),
            'language': self._get_language_recommendations(
                content, patterns.get('language_patterns', {})
            ),
            'similar_examples': [
                {
                    'content': block['content'][:200],
                    'similarity': block['similarity_score']
                }
                for block in similar_blocks[:2]
            ]
        }
        
        return recommendations
    
    def _get_formatting_recommendations(self, content: str, patterns: Dict) -> List[str]:
        """
        Generate formatting recommendations based on patterns
        """
        recommendations = []
        
        if not patterns:
            return recommendations
            
        # Check layout recommendations
        layout_dist = patterns.get('layout_distribution', {})
        if layout_dist:
            most_common = max(layout_dist.items(), key=lambda x: x[1])[0]
            if most_common != 'text':
                recommendations.append(
                    f"Consider using {most_common} layout style for better presentation"
                )
        
        # Check feature recommendations
        features = patterns.get('feature_usage', {})
        if features:
            if features.get('has_tables', 0) > 50 and 'table' not in content.lower():
                recommendations.append(
                    "Consider adding a table to organize information"
                )
            if features.get('has_bold', 0) > 70:
                recommendations.append(
                    "Use bold text to emphasize key points"
                )
        
        return recommendations
    
    def _get_language_recommendations(self, content: str, patterns: Dict) -> List[str]:
        """
        Generate language recommendations based on patterns
        """
        recommendations = []
        
        if not patterns:
            return recommendations
            
        # Check bullet points usage
        bullet_stats = patterns.get('bullet_points', {})
        if bullet_stats and bullet_stats.get('mean', 0) > 3 and '•' not in content:
            recommendations.append(
                "Consider using bullet points to list key items"
            )
        
        # Check sentence length
        sent_length = patterns.get('average_sentence_length', {})
        if sent_length:
            mean_length = sent_length.get('mean', 0)
            if mean_length > 0:
                current_length = len(content.split()) / max(1, len(content.split('.')))
                if current_length > mean_length * 1.5:
                    recommendations.append(
                        "Consider breaking down into shorter sentences for better readability"
                    )
        
        return recommendations
