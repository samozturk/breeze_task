import chromadb
import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import os

class LocalVenueSearch:
    def __init__(self, db_path="./venue_search_db"):
        # Initialize Chroma with persistent storage
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="venues",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        # Initialize CLIP model
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Set device (MPS for M4 Mac)
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.model = self.model.to(self.device)
        
        print(f"Using device: {self.device}")
        print(f"Database initialized at: {os.path.abspath(db_path)}")
        print(f"Current collection size: {self.collection.count()}")
    
    def get_text_embeddings(self, texts):
        """Get embeddings for text (reviews)"""
        inputs = self.processor(text=texts, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            text_embeddings = self.model.get_text_features(**inputs)
        
        return text_embeddings.cpu().numpy()

    def get_image_embeddings(self, images):
        """Get embeddings for images. 'images' is expected to be a list of image file paths."""
        try:
            pil_images = [Image.open(path) for path in images]
        except FileNotFoundError as e:
            print(f"Error: Could not find an image file. {e}")
            return np.array([])
        except Exception as e:
            print(f"An error occurred while opening images: {e}")
            return np.array([])

        inputs = self.processor(images=pil_images, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            image_embeddings = self.model.get_image_features(**inputs)
        
        return image_embeddings.cpu().numpy()

    def get_long_text_embeddings(self, texts, max_tokens=77):
        """Handle long texts by chunking and averaging embeddings"""
        all_embeddings = []
        
        for text in texts:
            # Tokenize the text
            inputs = self.processor.tokenizer(text, return_tensors="pt", padding=True)
            input_ids = inputs['input_ids'][0]  # Remove batch dimension
            
            # If text fits in token limit, process normally
            if len(input_ids) <= max_tokens:
                chunk_embeddings = self.get_text_embeddings([text])
                all_embeddings.append(chunk_embeddings[0])
            else:
                # Split into chunks
                chunks = []
                for i in range(0, len(input_ids), max_tokens - 2):  # -2 for special tokens
                    chunk = input_ids[i:i + max_tokens - 2]
                    # Decode back to text
                    chunk_text = self.processor.tokenizer.decode(chunk, skip_special_tokens=True)
                    if chunk_text.strip():  # Only add non-empty chunks
                        chunks.append(chunk_text)
                
                if chunks:
                    # Get embeddings for all chunks
                    chunk_embeddings = self.get_text_embeddings(chunks)
                    # Average the chunk embeddings
                    avg_embedding = np.mean(chunk_embeddings, axis=0)
                    all_embeddings.append(avg_embedding)
                else:
                    # Fallback to truncated text
                    truncated_text = self.processor.tokenizer.decode(
                        input_ids[:max_tokens-2], skip_special_tokens=True
                    )
                    chunk_embeddings = self.get_text_embeddings([truncated_text])
                    all_embeddings.append(chunk_embeddings[0])
        
        return np.array(all_embeddings)

    def create_venue_embedding(self, venue_reviews, venue_images, alpha=0.5):
        """
        Combine text and image embeddings for a venue
        alpha: weight for text vs images (0.5 = equal weight)
        """
        # Handle reviews (might be long)
        if venue_reviews:
            review_embeddings = self.get_long_text_embeddings(venue_reviews)
            avg_review_embedding = np.mean(review_embeddings, axis=0)
        else:
            # If no reviews, create zero embedding
            avg_review_embedding = np.zeros(512)  # CLIP embedding dimension
        
        # Handle images
        if venue_images:
            image_embeddings = self.get_image_embeddings(venue_images)
            avg_image_embedding = np.mean(image_embeddings, axis=0)
        else:
            # If no images, create zero embedding
            avg_image_embedding = np.zeros(512)
        
        # Combine text and image embeddings
        if venue_reviews and venue_images:
            combined_embedding = (alpha * avg_review_embedding + 
                                 (1 - alpha) * avg_image_embedding)
        elif venue_reviews:
            combined_embedding = avg_review_embedding
        elif venue_images:
            combined_embedding = avg_image_embedding
        else:
            raise ValueError("Venue must have either reviews or images")
        
        # Normalize the combined embedding
        combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)
        
        return combined_embedding
    
    def add_venue(self, venue_id, reviews=None, images=None, metadata=None):
        """Add a venue to the local database"""
        if not reviews and not images:
            raise ValueError("Must provide either reviews or images")
        
        # Create embedding
        embedding = self.create_venue_embedding(
            venue_reviews=reviews or [],
            venue_images=images or []
        )
        
        # Store in Chroma
        self.collection.add(
            embeddings=[embedding.tolist()],
            ids=[venue_id],
            metadatas=[metadata or {}]
        )
        print(f"Added venue: {venue_id}")
    
    def search_venues(self, query, top_k=10, filters=None):
        """Search venues locally"""
        # Get query embedding
        query_embedding = self.get_text_embeddings([query])[0]
        
        # Search in local database
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filters
        )
        
        return results
    
    def update_venue(self, venue_id, reviews=None, images=None, metadata=None):
        """Update an existing venue"""
        # Delete existing
        self.collection.delete(ids=[venue_id])
        
        # Add updated version
        self.add_venue(venue_id, reviews, images, metadata)
        print(f"Updated venue: {venue_id}")
    
    def delete_venue(self, venue_id):
        """Delete a venue"""
        self.collection.delete(ids=[venue_id])
        print(f"Deleted venue: {venue_id}")
    
    def get_venue_by_id(self, venue_id):
        """Get a specific venue by ID"""
        results = self.collection.get(ids=[venue_id])
        return results
    
    def get_stats(self):
        """Get database statistics"""
        count = self.collection.count()
        return f"Local database contains {count} venues"
    
    def list_all_venues(self):
        """List all venues in the database"""
        results = self.collection.get()
        return results

# Usage example
if __name__ == "__main__":
    # Initialize local search system
    search_system = LocalVenueSearch()
    
    # Example: Add a venue with just reviews (no images)
    search_system.add_venue(
        venue_id="Affinity Bar",
        reviews=[
            "Amazing bar with authentic flavors. The beer was perfectly fine and the fries was incredible. Staff was very friendly and attentive.",
            "Great atmosphere for a romantic date. Dim lighting and cozy seating.",
            "Excellent service and the wine selection is outstanding"
        ],
        metadata={
            "name": "Affinity Bar",
            "type": "Bar",
            "rating": 4.5,
            "price_range": "1"
        }
    )
    
    # Example: Add a venue with just text description (simulating no images available)
    search_system.add_venue(
        venue_id="cafe_1",
        reviews=[
            "Cozy coffee shop with great WiFi. Perfect for working. Amazing pastries and strong coffee.",
            "Modern decor with lots of natural light. Friendly baristas."
        ],
        metadata={
            "name": "The Daily Grind",
            "type": "cafe",
            "rating": 4.2,
            "price_range": "$"
        }
    )
    
    # Search locally
    print("\n--- Searching for 'romantic Italian restaurant' ---")
    results = search_system.search_venues(
        "romantic Italian restaurant",
        top_k=5
    )
    
    # Display results
    for i, (venue_id, distance, metadata) in enumerate(zip(
        results['ids'][0], 
        results['distances'][0], 
        results['metadatas'][0]
    )):
        print(f"{i+1}. {metadata.get('name', venue_id)} (similarity: {1-distance:.3f})")
        print(f"   Type: {metadata.get('type')}, Rating: {metadata.get('rating')}")
    
    print(f"\n{search_system.get_stats()}")