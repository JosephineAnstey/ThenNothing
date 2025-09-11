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
        """Extract descriptive passages from text"""
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Filter for descriptive sentences (longer sentences with descriptive words)
        descriptive_sentences = []
        for sentence in sentences:
            if len(sentence.split()) > 8:  # Longer sentences tend to be more descriptive
                # Check for descriptive indicators
                descriptive_indicators = [
                    r'\b(was|were|is|are|been|being)\b',  # Being verbs
                    r'\b(with|in|on|at|by|through|across)\b',  # Prepositions
                    r'\b(which|that|who|whose|whom)\b',  # Relative pronouns
                ]
                
                indicator_count = 0
                for indicator in descriptive_indicators:
                    if re.search(indicator, sentence, re.IGNORECASE):
                        indicator_count += 1
                
                if indicator_count >= 2:
                    descriptive_sentences.append(sentence)
        
        # Create passages by grouping sentences
        passages = []
        if len(descriptive_sentences) >= passage_length:
            for _ in range(num_passages):
                if len(descriptive_sentences) < passage_length:
                    break
                    
                start_index = random.randint(0, len(descriptive_sentences) - passage_length)
                passage = " ".join(descriptive_sentences[start_index:start_index + passage_length])
                passages.append(passage)
                
                # Remove these sentences to avoid repetition
                descriptive_sentences = descriptive_sentences[:start_index] + descriptive_sentences[start_index + passage_length:]
        
        return passages
    
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
                        'text': passage,
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
    passages = extractor.get_dickens_descriptions(num_passages=4)
    
    print("\n" + "="*60)
    print("DESCRIPTIVE PASSAGES FROM CHARLES DICKENS' WORKS")
    print("="*60)
    
    for i, passage in enumerate(passages, 1):
        print(f"\n{i}. From {passage['source']} (Book ID: {passage['book_id']}):")
        print('-' * 40)
        print(passage['text'])
        print()
