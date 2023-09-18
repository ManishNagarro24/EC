from flask import Flask, request, jsonify
import gpt
import database
from data_access import process_website
from flask_cors import CORS
import seq_chain

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


@app.route('/',methods=['GET'])
def main():
    return jsonify({"Welcome":"Hi"})

@app.route('/generate', methods=['POST'])
def generate_content():
    try:
        user_input=request.json['user_input']
        chat_history=request.json['chat_history']
        

        # Create the prompt using the current inputs
        #prompt = f"This is user current input {user_input} and this is its history of prompt and response {chat_history}"
        prompt =f"{user_input}" 
        # Generate content using OpenAI
        response=seq_chain.seq_chain(prompt)
        # Store the conversation history in the database
        return jsonify({"generated_content": response})

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)})

@app.route('/save', methods=['POST'])
def save_response():
    try:
        
        chat_history=request.json['chat_history']
        database.save_conversation(chat_history)

        return jsonify({"message": "Final response saved successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})
    
@app.route('/saveorganizationinfo',methods=['POST'])
def save_organization_info():
    try:
    #     organization_name=request.json['organization_name']
    #     organization_website=request.json['organization_website']
        userInput = request.get_json() 
        website = userInput['organization_website']
        index_name = userInput['organisation_name']
        response = process_website(website,index_name)
        if response["statusCode"] == 200:
            return jsonify({'success': True, 'message': response["statusMessage"]})
        else:
         
            return jsonify({'success': False, 'message': response["statusMessage"]})

    except Exception as e:
       
        return jsonify({'success': False, 'message': str(e)})
        # Call methods to generate organization informations by web scraping
        # Information will be stored as vector embeddings
    #     return jsonify({"message":"Organization Info saved successfully"})
    # except Exception as e:
    #     return jsonify({'error':str(e)})

if __name__ == '__main__':
    app.run(debug=True)
