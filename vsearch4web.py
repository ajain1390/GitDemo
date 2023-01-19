from flask import Flask, render_template, request, redirect, escape
from vsearch import search4letters
from DBcm import UseDatabase


app = Flask(__name__)

app.config['dbconfig'] = {'host': '127.0.0.1',
                'user': 'vsearch',
                'password': 'vsearchpasswd',
                'database': 'vsearchlogDB'
                }

'''
@app.route('/')
def hello() -> '302':  #flask sends back 302 back to your browser when "redirect" is invoked
    return redirect('/entry')
'''
def log_request(req: 'flask_request', res: str) -> None:

    #Using Context manager class "UseDatabase"
    '''
    Following code is replaced with flask own built-in configuration mechanism -
    a dictionary

    dbconfig = {'host': '127.0.0.1',
                'user': 'vsearch',
                'password': 'vsearchpasswd',
                'database': 'vsearchlogDB'
                }
    '''
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into log
                  (phrase, letters, ip, browser_string, resulta)
                  value
                  (%s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (req.form['phrase'],
                              req.form['letters'],
                              req.remote_addr,
                              req.user_agent.browser,
                              res, ))


    '''
    #Without using context manager
    #logging to a mysql DB
    dbconfig = { 'host': '127.0.0.1',
                  'user': 'vsearch',
                  'password': 'vsearchpasswd',
                   'database': 'vsearchlogDB', }

    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    _SQL = """insert into log
              (phrase, letters, ip, browser_string, resulta)
              values
              (%s, %s, %s, %s, %s)"""
    cursor.execute(_SQL, (req.form['phrase'],
                          req.form['letters'],
                          req.remote_addr,
                          req.user_agent.browser,
                          res,
                          )
                   )
    conn.commit()
    cursor.close()
    conn.close()
    '''
    ''' when loging to a file
    with open('vsearch.log', 'a') as log:
        print(req.form, req.remote_addr, req.user_agent, res, file=log, sep='|')
    '''

@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    title = "Here are your results:"
    results = str(search4letters(phrase, letters))
    log_request(request, results)
    return render_template('results.html',
                           the_phrase=phrase,
                           the_letters=letters,
                           the_title=title,
                           the_results=results,)

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html', the_title='Welcome to search4letters on the web')


@app.route('/viewlog')
def view_the_log() -> str:
    '''
    ***This is when data is saved in log file instead of DB
    contents = []
    with open('vsearch.log') as log:
        for line in log:
            contents.append([])
            for item in line.split('|'):
                contents[-1].append(escape(item))
    '''
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """ Select phrase, letters, ip, browser_string, resulta
                    from log"""
        cursor.execute(_SQL)
        contents =  cursor.fetchall()
    titles = ['Phrase', 'Letters', 'Remote_Addr', 'User_agent', 'Results']

    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=contents,)



if __name__ =='__main__':
    app.run(debug=True)
