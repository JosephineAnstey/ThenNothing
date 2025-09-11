import requests
import re
import random
from pathlib import Path

class GutenbergTextExtractor:
    def __init__(self):
        self.base_url = "https://www.gutenberg.org/files"
        # Dickens' works with descriptive potential
        self.dickens_books = {
            46: "A Christmas Carol",
            98: "A Tale of Two Cities",
            766: "David Copperfield",
            1023: "Bleak House",
            1400: "Great Expectations",
            730: "Oliver Twist"
        }
    
    def get_book_text(self, book_id):
        """Fetch book text from Project Gutenberg"""
        try:
            # Try the standard format first
            url = f"{self.base_url}/{book_id}/{book_id}-0.txt"
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except:
            # Fallback to alternative format
            try:
                url = f"{self.base_url}/{book_id}/{book_id}.txt"
                response = requests.get(url)
                response.raise_for_status()
                return response.text
            except:
                print(f"Failed to retrieve book ID {book_id}")
                return None
    
    def clean_gutenberg_text(self, text):
        """Remove Project Gutenberg headers and footers"""
        # Pattern to find start of actual content
        start_patterns = [
            r"\*\*\* START OF (THIS|THE) PROJECT GUTENBERG EBOOK.*\*\*\*",
            r"\*\*\* START OF (THIS|THE) PROJECT GUTENBERG.*\*\*\*"
        ]
        
        # Pattern to find end of content
        end_patterns = [
            r"\*\*\* END OF (THIS|THE) PROJECT GUTENBERG EBOOK.*\*\*\*",
            r"\*\*\* END OF (THIS|THE) PROJECT GUTENBERG.*\*\*\*"
        ]
        
        start_index = 0
        for pattern in start_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_index = match.end()
                break
        
        end_index = len(text)
        for pattern in end_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                end_index = match.start()
                break
        
        return text[start_index:end_index].strip()
    
    def extract_descriptive_passages(self, text, num_passages=3, passage_length=3):
        """Extract landscape, seascape, or cityscape passages from text"""
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Keywords for landscape, seascape, and cityscape descriptions
        landscape_keywords = [
            'mountain', 'hill', 'valley', 'forest', 'wood', 'field', 'meadow', 'river', 'stream', 
            'brook', 'lake', 'tree', 'flower', 'grass', 'path', 'road', 'countryside', 'landscape',
            'cliff', 'peak', 'slope', 'glade', 'orchard', 'garden', 'park', 'vineyard', 'prairie'
        ]
        
        seascape_keywords = [
            'sea', 'ocean', 'wave', 'beach', 'shore', 'coast', 'harbor', 'bay', 'tide', 'current',
            'sail', 'ship', 'boat', 'water', 'foam', 'spray', 'cliff', 'rock', 'island', 'cape',
            'strand', 'nautical', 'maritime', 'naval', 'seafaring', 'wharf', 'pier', 'dock'
        ]
        
        cityscape_keywords = [
            'city', 'town', 'street', 'avenue', 'boulevard', 'alley', 'square', 'plaza', 'building',
            'house', 'mansion', 'cottage', 'palace', 'tower', 'spire', 'roof', 'window', 'door',
            'bridge', 'canal', 'market', 'shop', 'tavern', 'inn', 'church', 'cathedral', 'monument',
            'urban', 'metropolitan', 'municipal', 'civic', 'downtown', 'suburb', 'quarter', 'district'
        ]
        
        # Combine all keywords
        all_keywords = landscape_keywords + seascape_keywords + cityscape_keywords
        
        # Find sentences containing these keywords
        descriptive_sentences = []
        for sentence in sentences:
            # Check if sentence contains any of our keywords
            if any(keyword in sentence.lower() for keyword in all_keywords):
                # Additional checks to ensure it's descriptive
                has_adjectives = re.search(r'\b(beautiful|majestic|vast|towering|serene|peaceful|'
                                         r'grand|magnificent|picturesque|ancient|modern|busy|'
                                         r'bustling|crowded|quiet|tranquil|calm|stormy|windy|'
                                         r'sunny|shadowy|gloomy|bright|dark|colorful|grey|'
                                         r'misty|foggy|rainy|snowy|icy|rocky|sandy|grassy|'
                                         r'wooded|forested|leafy|blooming|flowering)\b', 
                                         sentence, re.IGNORECASE)
                
                has_prepositions = re.search(r'\b(in|on|at|over|under|above|below|beneath|'
                                           r'beside|along|through|across|around|between|'
                                           r'among|beyond|past|near|far from)\b', 
                                           sentence, re.IGNORECASE)
                
                # Longer sentences tend to be more descriptive
                if len(sentence.split()) > 6 and (has_adjectives or has_prepositions):
                    descriptive_sentences.append(sentence)
        
        # Create passages by grouping sentences
        passages = []
        if len(descriptive_sentences) >= passage_length:
            for _ in range(num_passages):
                if len(descriptive_sentences) < passage_length:
                    break
                    
                start_index = random.randint(0, len(descriptive_sentences) - passage_length)
                passage = " ".join(descriptive_sentences[start_index:start_index + passage_length])
                
                # Classify the passage type
                passage_type = self.classify_passage(passage, landscape_keywords, 
                                                    seascape_keywords, cityscape_keywords)
                
                passages.append({
                    'text': passage,
                    'type': passage_type
                })
                
                # Remove these sentences to avoid repetition
                descriptive_sentences = descriptive_sentences[:start_index] + descriptive_sentences[start_index + passage_length:]
        
        return passages
    
    def classify_passage(self, passage, landscape_keywords, seascape_keywords, cityscape_keywords):
        """Classify passage as landscape, seascape, or cityscape"""
        passage_lower = passage.lower()
        
        landscape_count = sum(1 for keyword in landscape_keywords if keyword in passage_lower)
        seascape_count = sum(1 for keyword in seascape_keywords if keyword in passage_lower)
        cityscape_count = sum(1 for keyword in cityscape_keywords if keyword in passage_lower)
        
        if seascape_count > landscape_count and seascape_count > cityscape_count:
            return "seascape"
        elif cityscape_count > landscape_count and cityscape_count > seascape_count:
            return "cityscape"
        else:
            return "landscape"
    
    def get_dickens_descriptions(self, num_passages=3):
        """Get descriptive passages from Dickens' works"""
        all_passages = []
        
        for book_id, title in self.dickens_books.items():
            print(f"Processing {title}...")
            
            text = self.get_book_text(book_id)
            if text:
                cleaned_text = self.clean_gutenberg_text(text)
                passages = self.extract_descriptive_passages(cleaned_text, num_passages=1)
                
                for passage in passages:
                    all_passages.append({
                        'text': passage['text'],
                        'type': passage['type'],
                        'source': title,
                        'book_id': book_id
                    })
        
        # Randomly select the requested number of passages
        if len(all_passages) > num_passages:
            return random.sample(all_passages, num_passages)
        else:
            return all_passages

# Example usage
if __name__ == "__main__":
    extractor = GutenbergTextExtractor()
    passages = extractor.get_dickens_descriptions(num_passages=3)
    
    print("\n" + "="*70)
    print("LANDSCAPE, SEASCAPE, AND CITYSCAPE DESCRIPTIONS FROM CHARLES DICKENS")
    print("="*70)
    
    for i, passage in enumerate(passages, 1):
        print(f"\n{i}. {passage['type'].upper()} from {passage['source']} (Book ID: {passage['book_id']}):")
        print('-' * 60)
        print(passage['text'])
        print()