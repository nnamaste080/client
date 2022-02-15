import uuid

def my_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4()) # Convert UUID format to a Python string.
    random = random.upper() # Make all characters uppercase.
    random = random.replace("-","") # Remove the UUID '-'.
    return random[0:string_length] # Return the random string.

worker_id = 'worker_'+my_random_string(4)


data = f"""{{
    "id":"{worker_id}",
    "host":"http://localhost:1000",
    "username":"sai",
    "benchmark_re": "(?<=.........:   ).*?(?=\/s)",
    "status_re":"(?<=Status...........: ).*"
}}"""

with open('config.json','w+') as f:
	f.write(data)
    
print('worker_id generation success')