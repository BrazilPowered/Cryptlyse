from flask import Flask, make_response, request, render_template, Markup
import string, random, pprint, requests, json


app = Flask(__name__.split('.')[0],template_folder='./')

phraseAPI_url = "http://quotesondesign.com/wp-json/posts?filter[orderby]=rand&filter[posts_per_page]=1"

@app.route('/')
def home():
    return '''
        <form action="/landing" method="post">
            <p>Hey Cutie ;)</p>
            <p>Feel Better!!</p>
            <!--<p><input type=text name=username></p>-->
            <p><input type=submit value=Login></p>
        </form>
    '''
@app.route('/landing', methods=['POST'])
def landing_page():

    return '''
        <form action="/puzzler" method="get">
            <p>For your first time, Start Here:
            <p><button name="newBtn" type="submit">Make a new puzzle!</button></p>
            <p><small>Note: This will overwrite any previous puzzle you saw on this machine.</small></p>
        </form>
        <br/>
        <form action="/puzzle" method="get">
            <p><button name="resumeBtn" type="submit">View/resume last puzzle</button></p>
            <p><small>Note that an "Error" Page may appear if you haven't yet done a puzzle on this computer, or it has been a while since you have.</small></p>
            <p><small>In that case, go 'back' to this page and make a new puzzle</small></p>
        </form>
        <br/>
        <form action="/answer" method="get">
            <p><b>Or: Click here to view the answer of your latest puzzle:</b></p>
            <p><input type=submit value=Answer></p>
        </form>
    '''

@app.route('/puzzler', methods=['GET'])
def change_puzzle_page():
    resp = make_response(render_template('change_puzzle_text.html', change_message=''))
    return resp

@app.route('/change_puzzle', methods=['POST'])
def change_puzzle_text():
    puzzle_phrase = getNewQuote()
    #TODO:make me a template
    change_message=Markup('''
            <form action="/puzzle" method="get">
                <button name="changeBtn" type="submit">Click here to go staright to the new Puzzle</button>
            </form>
        ''')

    resp = make_response(render_template('change_puzzle_text.html', change_message=change_message))
    resp.set_cookie('puzzle_phrase', puzzle_phrase['content'])
    resp.set_cookie('puzzle_author', puzzle_phrase['title'])
    return resp

@app.route('/puzzle', methods=['GET'])
def print_page():
    phrase = request.cookies.get('puzzle_phrase')
    # use cookies.get(key) instead of cookies[key] to not get a
    # KeyError if the cookie is missing.
    puzzle_key=gen_cryptex()
    puzzle_plain_text = (phrase).upper()
    puzzle = "".join(str(x) for x in encode_via_cypher(puzzle_plain_text,puzzle_key))

    #pprint.pprint(puzzle_key)
    return puzzle

@app.route('/answer', methods=['GET'])
def print_ans_page():
    phrase = request.cookies.get('puzzle_phrase') + " --Quoting: " + request.cookies.get('puzzle_author')
    #pprint.pprint(puzzle_key)
    return phrase

#fetches quote json and splits it into a dictionary object: content is phrase, title is author
def getNewQuote():
    quote_api_response = requests.get(phraseAPI_url) #This should be a simple <Response [200]> with additional metadata
    quote_content = quote_api_response.content #This should be the content as a BYTE array
    if(quote_api_response.status_code == 200):
        if (type(quote_content) != str):
            if (type(quote_content) == bytes):
                #convert from byte array to json-string to dict (via loads)
                #loads returns a list containing a single element: a dict. Grab the dict with [0]:
                quote_content_dict = json.loads(quote_content.decode('utf-8').replace("'",'"'))[0]
            else:
                print("No handling for puzzle_phrase_response content type of " + type(quote_content) + ". \n Handling as String; Unexpected results may occur.")
    #quote_content_dict
    print (quote_content_dict['content'])
    return quote_content_dict

def encode_via_cypher(plain_text_string,cypher_key_dict):
    encoding =[]
    for char in list(plain_text_string):
        if(char in cypher_key_dict):
            encoding.append(cypher_key_dict.get(char))
        else:
            encoding.append(char)
    return encoding

#Generate cryptex using alphabet only
def gen_cryptex():
    return gen_cypher(string.ascii_uppercase)

#Generate a 2-d array, where 1st col is original char, 2nd is new char
def gen_cypher(charset):
    cypherset = crypt_lshift(charset,5)
    cypherset = crypt_sub(cypherset,5)
    cypher=dict(zip(list(charset),cypherset))
    return cypher

#shift a flat list Left #num times
#returns shifted list
def crypt_lshift(charset,num=13):
    char_list = list(charset)
    while num > 0:
        next_letter  = char_list.pop(0)
        char_list.append(next_letter)
        num-=1
    return char_list

#substitute 2 chars for eachother at random in a list #num times
#returns subbed list
def crypt_sub(charset,num=2):
    while num > 0:
        first_letter=random.choice(charset)
        first_index=charset.index(first_letter)
        second_letter=random.choice(charset)
        second_index=charset.index(second_letter)
        charset.insert(first_index,second_letter)
        charset.pop(first_index+1)
        charset.insert(second_index,first_letter)
        charset.pop(second_index+1)
        num-=1
    return charset

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')
#print_page()#for debugging