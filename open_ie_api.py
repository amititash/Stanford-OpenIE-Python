'''
Re-using the code for exposing the API for getting triplets

'''

from __future__ import print_function

# we need flask for exposing the API

from flask import Flask
from flask import jsonify
from flask import request

import json
import os

import urllib

from main import stanford_ie



app = Flask(__name__)

tmp_folder = '/tmp/openie/'
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)


def texts_to_files(texts):
    full_tmp_file_names = []
    count = 0
    for text in texts:
        tmp_filename = str(count) + '.txt'
        full_tmp_filename = '{}/{}'.format(tmp_folder, tmp_filename).replace('//', '/')
        with open(full_tmp_filename, 'w') as f:
            f.write(text)
        full_tmp_file_names.append(full_tmp_filename)
        count += 1
    return full_tmp_file_names


def call_api_many(texts, pagination_param=10000, verbose=False):
    reduced_results = []
    paginated_texts_list = [texts[i:i + pagination_param] for i in range(0, len(texts), pagination_param)]
    for paginated_texts in paginated_texts_list:
        tmp_file_names = texts_to_files(paginated_texts)
        joint_filename = ','.join(tmp_file_names)
        results = stanford_ie(joint_filename, verbose=verbose)
        reduced_results.extend(results)
    return reduced_results


def call_api_single(text):
    if os.path.isfile(text):
        full_tmp_filename = text
    else:
        full_tmp_filename = texts_to_files([text])[0]
    results = stanford_ie(full_tmp_filename, verbose=False)
    return results

@app.route("/gettriplets/")
def get_triplets():
    result_triplet = call_api_single(u'' + request.args.get('sentence'))

    if result_triplet:
        # get the root term for each triplet element
        # we know that each triplet is always going to have either a noun chunk
        # or a verb chunk

        posUrl = 'http://localhost:5000/getpos/?sentence='
        print("*******")
        final_list = [x.strip() for x in result_triplet[0]]
        print (final_list)
        cleaned_list = [json.loads(urllib.request.urlopen(posUrl+urllib.parse.quote_plus(x)).read()) for x in final_list ]
        # print(cleaned_list[0][0][0], cleaned_list[1][0][0], cleaned_list[2][0][0])

        
        # the cleaned list 0 or 2 are empty it means that there is no usefule value in 
        # this triplet and we shouldnt send it back. 
        # if relationship is empty, we might still have a useful value. 

        if cleaned_list[1][0] and cleaned_list[0][0] :
            

            # unpacking the nested json
            simplified = [x[0][0] for x in cleaned_list ]
            print(simplified)
            return json.dumps(simplified)
        else :
            print("err due to empty array elements")
            return json.dumps("err")
    else :
        print("error due to entire array empty")
        return json.dumps("err")

'''

if __name__ == '__main__':
    print(len(call_api_many(['Barack Obama was born in Hawaii.'] * 30, pagination_param=100, verbose=True)))
'''