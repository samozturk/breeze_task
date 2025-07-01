import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image


# Check if MPS (Metal Performance Shaders) is available
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

# Load model with device
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
model = model.to(device)

processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

image = Image.open("../data/output/photos/Affinity_Bar/2.jpeg")

text_sample = "Three people are behind a brightly lit bar, with a drag performer in a sparkly outfit standing between two smiling bartenders in patterned shirts. The bar is decorated with colorful LED lights, bottles, and beer taps, including a prominent Heineken tap. The mood is festive and lively, suggesting a fun night out or themed event."
text_op = "dead snake"
inputs = processor(text=[text_sample], images=image, return_tensors="pt", padding=True).to(device)

# Get image embeddings

image_embeds = model.get_image_features(inputs['pixel_values'])
text_embeds = model.get_text_features(inputs['input_ids'])

# Calculate cosine similarity
cosine_similarity = torch.nn.functional.cosine_similarity(image_embeds, text_embeds)

print(f"Cosine similarity: {cosine_similarity.item()}")