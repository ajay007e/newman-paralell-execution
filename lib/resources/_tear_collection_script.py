
import os
import sys


# Overall, this code is designed to execute the process of running multiple Newman Tests
#       with different JSON files and environment settings. This code will create multiple
#       collections from a collection according to the input pattern.


class TearCollection:
    
    def tear_collection_into_multiple_collections(self, collection_path, env_path, pattern):
        
        current_directory = os.getcwd()

        try :
            # Extracting the name of the collection from collection_path
            collection_name = collection_path.split("/").pop().split('.')[0]
            
            # Open the Postman collection file in read mode ('r')
            with open(collection_path, 'r') as file:
                file_contents = file.read()
            
            # Open the environment file in read mode ('r')
            with open(env_path, 'r') as file:
                file_contents_of_env = file.read()

            # Define the file path to save the environment file
            file_path_of_save_env = f'{current_directory}/source/.tmp/{collection_name}-env.json'
            
            # Write the contents of the environment file to the new file path
            with open(file_path_of_save_env, 'w') as file:
                file.write(file_contents_of_env)

            # Split the pattern using a comma as the separator
            diff_points = pattern.split(",")

            # Strip any leading/trailing whitespace from each element in the list
            diff_points = [f'"name": "{int(diff_points[i].strip())})'  for i in range (0,len(diff_points))]

            position_of_diff_json = []

            # Find the positions of each diff point in the JSON
            for i in diff_points:
                position_of_diff_json.append(file_contents.find(i))

            # Define the prefix and suffix for the new JSON files
            preffix = '''{
                "info": {
                    "_postman_id": "cf4e2d7a-b53e-442b-ac87-65337d3cd972",
                    "name": "extra",
                    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                    "_exporter_id": "27931370"
                },
                "item": [
                    {'''
            suffix = ']}'

            # Iterating through each of the partition
            for i in range(len(position_of_diff_json) - 1):

                # Fetching content for the particular index
                json_file_of_given_index = file_contents[position_of_diff_json[i]:position_of_diff_json[i + 1] - 9]

                # Appending prefix and suffix to complete the partitioned collection json
                json_string = (preffix + json_file_of_given_index + suffix)

                # Define the file path to save the partioned collection file
                file_path = f"{current_directory}/source/.tmp/{collection_name}-group-{i + 1}.postman_collection.json"

                # Write the contents of the partitioned collectiono to the new collection
                with open(file_path, 'w') as file:
                    file.write(json_string)
        except:
            print("Sorry! Something went wrong")
            
tear_collection_object = TearCollection()

collection, env, pattern = sys.argv[1:4]

tear_collection_object.tear_collection_into_multiple_collections(collection, env, pattern)
