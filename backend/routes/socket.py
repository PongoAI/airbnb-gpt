from fastapi import (
    APIRouter,
    WebSocket,
)

import json
from dotenv import load_dotenv
import os
import json
import pongo
from openai import OpenAI
from exa_py import Exa
import weaviate
socket_router = APIRouter()
load_dotenv()



together_client = OpenAI(api_key=os.environ.get("TOGETHER_API_KEY"), base_url='https://api.together.xyz/v1')
pongo_client = pongo.PongoClient(os.environ.get("PONGO_API_KEY"))

exa_client = Exa( os.environ.get("EXA_API_KEY"))

#In prod, just include names in your data base objs 

weaviate_client = weaviate.Client(
    url=os.getenv('WCS_URL'),
    auth_client_secret=weaviate.auth.AuthApiKey(os.getenv('WCS_KEY')),
)
oai_client = OpenAI(api_key=os.environ.get("OPENAI_APIKEY"))






@socket_router.websocket("/sockets/airbnb")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        query = await websocket.receive_text()



        llm_prompt = f"""You are a system that generates JSON out of user queries of a rental listing database. You ONLY respond with valid JSON.
        Based on the user query at the end of this prompt, construct a JSON that represents their request as a JSON query.
        Each key in the JSON should be an attribute taken from the query, and each value should be an object with properties "operator" and either "valueNumber" or "valueBoolean" or "valueString".
        The options for "operator" are "Equal", "GreaterThan", and "LessThan". The value for this operator can be a boolean, or number. If it's a number, use the key "valueNumber", and if it's a boolean use "valueBoolean", and if it's a string use "valueString"
        Below are the possible keys for your JSON and what aspects of the user's query they represent. Only include a property if the user's query directly or indirectly mentions it.
        You do not support querying on price, so skip it if the user mentions it

        - "number_of_guests" (number): The maximum number of guests allowed at a listing.
        - "allows_pets" (boolean): Whether pets are allowed at a listing.
        - "allows_smoking" (boolean): Whether smoking is allowed at a listing.
        - "bedroom_count" (number): The number of bedrooms in a listing.
        - "bed_count" (number): The number of beds in a listing.
        - "bathroom_label" (number): The number of bathrooms in a listing.
        - "8" (boolean): Whether the listing has a kitchen.
        - "1" (boolean): Whether the listing has a TV.
        - "4" (boolean): Whether the listing has Wifi.
        - "5" (boolean): Whether the listing has Air Conditioning.
        - "9" (boolean): Whether the listing has free parking.
        - "30" (boolean): Whether the listing has heating.
        - "33" (boolean): Whether the listing has a washer.
        - "34" (boolean): Whether the listing has a dryer.
        - "101" (boolean): Whether the listing has a backyard.
 

        

        The returned JSON should also always have a "new_query" field, which should be the user's query that has any properties represented in the JSON removed.

        Example query: Show me cozy houses in that have A/C, more than 2 bedrooms, and are by a lake
        Example output JSON: {"{'5': {'operator': 'Equal', 'valueBoolean': true}, 'bedroom_count': {'operator': 'GreaterThan', 'valueNumber': 2}, 'new_query': 'Show me cozy houses that are by a lake'}"}
        User query: {query}"""

        
        new_query = ''
        llm_failed = False
        # try:
        completion_response = json.loads(together_client.chat.completions.create(
            model="meta-llama/Llama-3-70b-chat-hf",
            messages=[{"role": "user", "content": llm_prompt}],
            stream=False,
            temperature=0.2,
        ).choices[0].message.content)
        print(completion_response)
        # Remove all fields from the completion_response object aside from the specified ones
        allowed_fields = [
            "number_of_guests", "allows_pets", "allows_smoking", "bedroom_count", 
            "bed_count", "bathroom_label", "8", "1", "4", "5", "9", "30", "33", "34", "101", "new_query"
        ]
        completion_response = {key: value for key, value in completion_response.items() if key in allowed_fields}
        # except:
        #     pass
        

        new_query = completion_response['new_query']
        await websocket.send_text('COMPLETION_RESPONSE:'+json.dumps(completion_response))


        

        query_vector = (
            oai_client.embeddings.create(
                input=new_query, model="text-embedding-3-small", dimensions=1536
            )
            .data[0]
            .embedding
        )

        weaviate_query = weaviate_client.query.get("AirbnbGPTnew", ['stars', 'thumbnail', 'text', 'address', 'name', 'thumbnail', 'url']
        )




        for key, value in completion_response.items():
            if key == 'new_query':
                continue
            elif key == 'address':
                location = value['valueString']
                weaviate_query = weaviate_query.with_where({
                    "path": ["text"],
                    "operator": "ContainsAny",
                    "valueText": [location, location.lower(), location.upper()]
                })

            elif key.isdigit():
                weaviate_query = weaviate_query.with_where({'path': 'amenity_ids', 'operator': 'ContainsAll', "valueText": [key] })
            else:

                if 'valueBoolean' in value:
                    weaviate_query = weaviate_query.with_where({'path': key, 'valueBoolean': value['valueBoolean'], 'operator': value['operator']})
                else:
                    weaviate_query = weaviate_query.with_where({'path': key, 'valueNumber': value['valueNumber'], 'operator': value['operator']})


        
        
        search_results = weaviate_query.with_near_vector(
        {'vector': query_vector}
        ).with_limit(300).do()
        
        # print(search_results)

        data_for_pongo = search_results['data']['Get']['AirbnbGPTnew']

        if len(data_for_pongo) == 0:
            await websocket.send_text('NO_DATA_FOUND')
            continue



        i = 0
        for cur_result in data_for_pongo:

            
            cur_result['id'] = i  

            
            i+=1
        
        filtered_results = pongo_client.filter(query=query, docs=data_for_pongo, num_results=30, public_metadata_field="metadata", key_field="id", text_field='text')

        filtered_body = filtered_results.json()
        await websocket.send_text('PONGO_RESPONSE:'+json.dumps(filtered_body))

        

    

        

        

        
        
        



        

