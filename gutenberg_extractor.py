import requests
import re
import random
from pathlib import Path

class GutenbergTextExtractor:
    def __init__(self, config_file="config.txt"):
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
        
        # Load configuration from file
        self.load_config(config_file)
    
    def load_config(self, config_file):
        """Load keywords and descriptive checks from config file"""
        self.landscape_keywords = []
        self.seascape_keywords = []
        self.cityscape_keywords = []
        self.adjectives = []
        self.prepositions = []
        
        current_section = None
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Check for section headers
                    if line.lower().startswith('# landscape keywords'):
                        current_section = 'landscape'
                        continue
                    elif line.lower().startswith('# seascape keywords'):
                        current_section = 'seascape'
                        continue
                    elif line.lower().startswith('# cityscape keywords'):
                        current_section = 'cityscape'
                        continue
                    elif line.lower().startswith('# adjectives for descriptive checks'):
                        current_section = 'adjectives'
                        continue
                    elif line.lower().startswith('# prepositions for descriptive checks'):
                        current_section = 'prepositions'
                        continue
                    
                    # Add items to appropriate section
                    if current_section == 'landscape':
                        self.landscape_keywords.append(line.lower())
                    elif current_section == 'seascape':
                        self.seascape_keywords.append(line.lower())
                    elif current_section == 'cityscape':
                        self.cityscape_keywords.append(line.lower())
                    elif current_section == 'adjectives':
                        self.adjectives.append(line.lower())
                    elif current_section == 'prepositions':
                        self.prepositions.append(line.lower())
        
        except FileNotFoundError:
            print(f"Config file {config_file} not found. Using default values.")
            self.set_default_keywords()
    
    def set_default_keywords(self):
        """Set default keywords if config file is not found"""
        # Default landscape keywords
        self.landscape_keywords = [
            'mountain', 'hill', 'valley', 'forest', 'wood', 'field', 'meadow', 'river', 'stream', 
            'brook', 'lake', 'tree', 'flower', 'grass', 'path', 'road', 'countryside', 'landscape',
            'cliff', 'peak', 'slope', 'glade', 'orchard', 'garden', 'park', 'vineyard', 'prairie'
        ]
        
        # Default seascape keywords
        self.seascape_keywords = [
            'sea', 'ocean', 'wave', 'beach', 'shore', 'coast', 'harbor', 'bay', 'tide', 'current',
            'sail', 'ship', 'boat', 'water', 'foam', 'spray', 'cliff', 'rock', 'island', 'cape',
            'strand', 'nautical', 'maritime', 'naval', 'seafaring', 'wharf', 'pier', 'dock'
        ]
        
        # Default cityscape keywords
        self.cityscape_keywords = [
            'city', 'town', 'street', 'avenue', 'boulevard', 'alley', 'square', 'plaza', 'building',
            'house', 'mansion', 'cottage', 'palace', 'tower', 'spire', 'roof', 'window', 'door',
            'bridge', 'canal', 'market', 'shop', 'tavern', 'inn', 'church', 'cathedral', 'monument',
            'urban', 'metropolitan', 'municipal', 'civic', 'downtown', 'suburb', 'quarter', 'district'
        ]
        
        # Default adjectives
        self.adjectives = [
            'beautiful', 'majestic', 'vast', 'towering', 'serene', 'peaceful',
            'grand', 'magnificent', 'picturesque', 'ancient', 'modern', 'busy',
            'bustling', 'crowded', 'quiet', 'tranquil', 'calm', 'stormy', 'windy',
            'sunny', 'shadowy', 'gloomy', 'bright', 'dark', 'colorful', 'grey',
            'misty', 'foggy', 'rainy', 'snowy', 'icy', 'rocky', 'sandy', 'grassy',
            'wooded', 'forested', 'leafy', 'blooming', 'flowering'
        ]
        
        # Default prepositions
        self.prepositions = [
            'in', 'on', 'at', 'over', 'under', 'above', 'below', 'beneath',
            'beside', 'along', 'through', 'across', 'around', 'between',
            'among', 'beyond', 'past', 'near', 'far from'
        ]
    
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
        
        # Combine all keywords
        all_keywords = self.landscape_keywords + self.seascape_keywords + self.cityscape_keywords
        
        # Find sentences containing these keywords
        descriptive_sentences = []
        for sentence in sentences:
            # Check if sentence contains any of our keywords
            if any(keyword in sentence.lower() for keyword in all_keywords):
                # Additional checks to ensure it's descriptive
                adjectives_pattern = r'\b(' + '|'.join(self.adjectives) + r')\b'
                has_adjectives = re.search(adjectives_pattern, sentence, re.IGNORECASE)
                
                prepositions_pattern = r'\b(' + '|'.join(self.prepositions) + r')\b'
                has_prepositions = re.search(prepositions_pattern, sentence, re.IGNORECASE)
                
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
                passage_type = self.classify_passage(passage)
                
                passages.append({
                    'text': passage,
                    'type': passage_type
                })
                
                # Remove these sentences to avoid repetition
                descriptive_sentences = descriptive_sentences[:start_index] + descriptive_sentences[start_index + passage_length:]
        
        return passages
    
    def classify_passage(self, passage):
        """Classify passage as landscape, seascape, or cityscape"""
        passage_lower = passage.lower()
        
        landscape_count = sum(1 for keyword in self.landscape_keywords if keyword in passage_lower)
        seascape_count = sum(1 for keyword in self.seascape_keywords if keyword in passage_lower)
        cityscape_count = sum(1 for keyword in self.cityscape_keywords if keyword in passage_lower)
        
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
                cleaned_text = self.get_clean_text(text)
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
    
    def get_clean_text(self, text):
        """Public method to clean Gutenberg text"""
        return self.clean_gutenberg_text(text)