from typing import List, Dict, Optional, Set
import spacy
from spacy.tokens import Doc
from collections import Counter
import yake
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util
from app.core.logging import get_logger
from app.core.monitoring import monitor_performance

logger = get_logger(__name__)

class NLPServiceStore:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._service = NLPService()
        return cls._instance
    
    def __getattr__(self, name):
        # Delegate all method calls to the underlying NLPService instance
        return getattr(self._service, name)

class NLPService:
    def __init__(self):
        """Initialize NLP models and components"""
        self.logger = get_logger(__name__)
        
        # Load spaCy model for NER and dependency parsing
        self.logger.info("Loading spaCy model...")
        self.nlp = spacy.load("en_core_web_lg")
        
        # Initialize keyword extraction
        self.logger.info("Initializing keyword extractors...")
        self.yake_extractor = yake.KeywordExtractor(
            lan="en",
            n=3,  # ngrams up to 3
            dedupLim=0.3,  # similarity threshold for duplicate removal
            top=20,
            features=None
        )
        self.keybert_model = KeyBERT()
        
        # Initialize sentence transformer for semantic analysis
        self.logger.info("Loading sentence transformer...")
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
    
    @monitor_performance()
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text using spaCy
        
        Returns:
            Dict mapping entity types to lists of entities
        """
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            # Avoid duplicates
            if ent.text not in entities[ent.label_]:
                entities[ent.label_].append(ent.text)
        
        return entities
    
    @monitor_performance()
    def extract_key_phrases(self, text: str, method: str = 'hybrid') -> List[str]:
        """
        Extract key phrases using multiple methods
        
        Args:
            text: Input text
            method: One of 'yake', 'keybert', or 'hybrid'
            
        Returns:
            List of key phrases
        """
        if method not in ['yake', 'keybert', 'hybrid']:
            raise ValueError("Method must be one of: yake, keybert, hybrid")
        
        phrases = set()
        
        if method in ['yake', 'hybrid']:
            # Extract using YAKE
            yake_keywords = self.yake_extractor.extract_keywords(text)
            phrases.update([kw[0] for kw in yake_keywords])
        
        if method in ['keybert', 'hybrid']:
            # Extract using KeyBERT
            keybert_keywords = self.keybert_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 3),
                stop_words='english',
                use_maxsum=True,
                nr_candidates=20,
                top_n=10
            )
            phrases.update([kw[0] for kw in keybert_keywords])
        
        return list(phrases)
    
    @monitor_performance()
    def analyze_semantic_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts
        
        Returns:
            Similarity score between 0 and 1
        """
        # Encode texts
        embedding1 = self.sentence_transformer.encode(text1, convert_to_tensor=True)
        embedding2 = self.sentence_transformer.encode(text2, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = util.pytorch_cos_sim(embedding1, embedding2)
        return float(similarity[0][0])
    
    @monitor_performance()
    def extract_technical_terms(self, text: str) -> List[Dict[str, str]]:
        """
        Extract technical terms and their contexts
        
        Returns:
            List of dicts containing term and its context
        """
        doc = self.nlp(text)
        technical_terms = []
        
        # Custom technical term patterns
        technical_patterns = [
            'API', 'SDK', 'cloud', 'infrastructure', 'integration',
            'implementation', 'deployment', 'database', 'server',
            'security', 'network', 'framework', 'platform', 'service',
            'architecture', 'interface', 'protocol', 'algorithm',
            'authentication', 'authorization', 'encryption', 'scaling'
        ]
        
        for token in doc:
            if (token.text.lower() in technical_patterns or 
                token.like_num or  # Version numbers
                (token.pos_ == 'PROPN' and token.text.isupper())):  # Acronyms
                
                # Get context (surrounding words)
                start = max(token.i - 5, 0)
                end = min(token.i + 6, len(doc))
                context = doc[start:end].text
                
                technical_terms.append({
                    'term': token.text,
                    'context': context
                })
        
        return technical_terms
    
    @monitor_performance()
    def analyze_text_structure(self, text: str) -> Dict:
        """
        Analyze the structure and complexity of text
        
        Returns:
            Dict containing various text metrics
        """
        doc = self.nlp(text)
        
        # Calculate various metrics
        sentence_lengths = [len(sent) for sent in doc.sents]
        word_lengths = [len(token.text) for token in doc if not token.is_punct]
        
        metrics = {
            'sentence_count': len(list(doc.sents)),
            'avg_sentence_length': sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            'avg_word_length': sum(word_lengths) / len(word_lengths) if word_lengths else 0,
            'unique_words': len(set(token.text.lower() for token in doc if token.is_alpha)),
            'noun_phrases': len(list(doc.noun_chunks)),
            'verb_phrases': len([token for token in doc if token.pos_ == 'VERB']),
            'complexity_score': self._calculate_complexity_score(doc)
        }
        
        return metrics
    
    def _calculate_complexity_score(self, doc: Doc) -> float:
        """Calculate text complexity score based on various factors"""
        # Count complex sentence structures
        complex_structures = sum(1 for token in doc if token.dep_ in ['ccomp', 'xcomp', 'advcl'])
        
        # Count technical or domain-specific terms
        technical_terms = len(self.extract_technical_terms(doc.text))
        
        # Calculate average dependency tree depth
        depths = []
        for token in doc:
            depth = 1
            current = token
            while current.head != current:
                depth += 1
                current = current.head
            depths.append(depth)
        
        avg_depth = sum(depths) / len(depths) if depths else 0
        
        # Combine factors into a score (0-1)
        score = (
            0.4 * min(complex_structures / max(len(list(doc.sents)), 1), 1) +
            0.3 * min(technical_terms / max(len(doc), 1), 1) +
            0.3 * min(avg_depth / 5, 1)  # Normalize by typical max depth
        )
        
        return score
