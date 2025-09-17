from gutenberg_extractor import GutenbergTextExtractor

def main():
    # Create an instance of the extractor with config file
    extractor = GutenbergTextExtractor("config.txt")
    
    # Get descriptive passages from Dickens' works
    passages = extractor.get_dickens_descriptions(num_passages=3)
    
    # Display the results
    print("\n" + "="*70)
    print("LANDSCAPE, SEASCAPE, AND CITYSCAPE DESCRIPTIONS FROM CHARLES DICKENS")
    print("="*70)
    
    for i, passage in enumerate(passages, 1):
        print(f"\n{i}. {passage['type'].upper()} from {passage['source']} (Book ID: {passage['book_id']}):")
        print('-' * 60)
        print(passage['text'])
        print()
        

if __name__ == "__main__":
    main()