import json
import weaviate
import os
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core.schema import TextNode
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv
load_dotenv()


# client = weaviate.Client(
#     url=os.getenv('WCS_URL'),
#     auth_client_secret=weaviate.auth.AuthApiKey(os.getenv('WCS_KEY')),
# )

client = weaviate.connect_to_wcs(
    cluster_url=os.getenv('WCS_URL'),  
    auth_credentials=weaviate.auth.AuthApiKey(os.getenv('WCS_KEY'))
    # headers={'X-OpenAI-Api-key': os.getenv("OPENAI_APIKEY")}  # Replace with your OpenAI API key
    )



vector_store = WeaviateVectorStore(
    weaviate_client=client, index_name="AirbnbGPTnew"
)

#shoot me a dm @hi_jamari on twitter if you'd like to access the dataset!
with open('/Users/jamarimorrison/Downloads/dataset_airbnb-scraper_2024-05-27_22-10-57-092.json') as f:
    imported_json = json.load(f)#[0]['result']

nodes = []
for listing in imported_json:
    #empty try-catch, skip malformed listings
    try: 
        if 'studio' in listing['bedroomLabel'].lower():
            bedroom_count = 1
        else:
            bedroom_count = float(''.join(filter(str.isdigit, listing['bedroomLabel'])))
        
        if 'half-bath' in listing['bathroomLabel'].lower():
            bathroom_count = 0.5
        else:
            bathroom_count = float(''.join(filter(str.isdigit, listing['bathroomLabel'])))


        
        listing_metadata = {
            'stars': listing['stars'],
            'address': listing['address'],
            'name': listing['name'],
            'url': listing['url'],
            'number_of_guests': listing['numberOfGuests'],
            'amenity_ids': [],
            'allows_pets': listing['guestControls']['allowsPets'],
            'allows_smoking': listing['guestControls']['allowsSmoking'],
            'thumbnail': listing['photos'][0]['pictureUrl'],
            'bedroom_count': bedroom_count,
            'bed_count': float(''.join(filter(str.isdigit, listing['bedLabel']))),
            'bathroom_label': bathroom_count,
        }
        if 'no longer available' in listing_metadata['name'].lower() or 'unavailable' in listing_metadata['name'].lower() or 'not available' in listing_metadata['name'].lower() :
            continue
        for amenity in listing['listingAmenities']:
            if amenity['isPresent']:
                listing_metadata['amenity_ids'].append(str(amenity['id']))


        desc_node_text = f"Listing name: {listing['name']}\nDescription: {listing['sectionedDescription']['description']}"
        desc_node = TextNode(text=desc_node_text, metadata=listing_metadata)
        nodes.append(desc_node)


        
        review_count = 0
        for review in listing['reviews']:
            if review_count >= 10:
                break
            review_node_text = f"Listing name: {listing['name']}\nReview: {review['comments']}"
            review_node = TextNode(text=review_node_text, metadata=listing_metadata)
            nodes.append(review_node)
            review_count+=1
    except:
        pass


    
embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=os.getenv("OPENAI_APIKEY"), dimensions=1536)

# nodes = nodes[:1000]
nodes = nodes[1000:]
# quit(0)

for node in nodes:
    node_embedding = embed_model.get_text_embedding(
        node.get_content(metadata_mode="all")
    )
    node.embedding = node_embedding

vector_store.add(nodes)

