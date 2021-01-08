from flask import Flask, render_template, send_file
import os
import psycopg2
import pandas
from pandas import DataFrame 
from IPython.display import HTML
import plotly.graph_objects as go


# FalconSQL Login https://api.plot.ly/

"""Create and configure an instance of the Flask application"""
app = Flask(__name__)
### local development ###
# app.config['TESTING'] = True
# app.config['TEMPLATES_AUTO_RELOAD'] = True
# app.config['STATIC_AUTO_RELOAD'] = True
# app.run(debug=True)

@app.route('/')
def root():
    return render_template('home.html')

@app.route('/twitterbot')
def twitterbot():
    AWSdatabase_TWIT = os.getenv("AWSDATABASE_TWIT")
    AWSuser_TWIT = os.getenv("AWSUSER_TWIT")
    AWSpassword_TWIT = os.getenv("AWSPASSWORD_TWIT")
    AWShost_TWIT = os.getenv("AWSHOST_TWIT")
    AWSport_TWIT = os.getenv("AWSPORT_TWIT")
    ## connect to AWS database ###
    connection = psycopg2.connect(database=AWSdatabase_TWIT,
                                user=AWSuser_TWIT,
                                password=AWSpassword_TWIT,
                                host=AWShost_TWIT,
                                port=AWSport_TWIT)
    print("connected to database")
    cur = connection.cursor()

    sql_select_Query = "select * from tweets_storage" # query all of database 
    cur.execute(sql_select_Query)
    data = cur.fetchall()
    df = DataFrame(data)  # set as dataframe 
    df.columns = ['id', 'date', 'name', 'text', 'tags'] # label the columns 
    df = df.sort_values('date', ascending=False)
    table = HTML(df.to_html(classes='table table-striped'))
    cur.close()

    return render_template('twitterbot.html',tables=[table])

@app.route('/covid19usagraph')
def covid19usagraph():
    ### AWS credentials ###
    AWSdatabase_COVI = os.getenv("AWSDATABASE_COVI")
    AWSuser_COVI = os.getenv("AWSUSER_COVI")
    AWSpassword_COVI = os.getenv("AWSPASSWORD_COVI")
    AWShost_COVI = os.getenv("AWSHOST_COVI")
    AWSport_COVI = os.getenv("AWSPORT_COVI")
    ### connect to AWS database ###
    connection = psycopg2.connect(database=AWSdatabase_COVI,
                                user=AWSuser_COVI,
                                password=AWSpassword_COVI,
                                host=AWShost_COVI,
                                port=AWSport_COVI)
    cur = connection.cursor()                           
    print("connected to database")
    ### SQL query table ###
    sql_select_Query = "select * from covid19us" # query all of database 
    cur.execute(sql_select_Query)
    data = cur.fetchall()
    df = DataFrame(data)  # set as dataframe 
    print("pulled data")
    ### clean and organize data ###
    df.columns = ['Date', 'States', 'TestsToday', 'TestsDailyChange', 'TotalTests', 'PositivesToday', 'PostiviesDailyChange', 'TotalPositives', 
            'NegativesToday', 'NegativesDailyChange', 'TotalNegatives',
            'HospitalizedToday', 'HospitalizedDailyChange', 'HospitalizedCurrently', 'TotalHospitalized', 
            'IcuToday', 'IcuDailyChange', 'IcuCurrently', 'TotalIcu', 
            'VentilatorsToday', 'VentilatorsDailyChange', 'VentilatorsCurrently', 'TotalVentilators', 
            'DeathsToday', 'DeathsDailyChange', 'TotalDeaths', 'RecoveredToday', 'RecoveredDailyChange', 'TotalRecovered'] 
    df = df.sort_values('Date', ascending=False)     
    df.reset_index(drop=True)       
    pos = lambda x: "+"+str(x) if x>0 else x
    df['TestsDailyChange'] = df['TestsDailyChange'].apply(pos)
    df['PostiviesDailyChange'] = df['PostiviesDailyChange'].apply(pos)
    df['NegativesDailyChange'] = df['NegativesDailyChange'].apply(pos)
    df['HospitalizedDailyChange'] = df['HospitalizedDailyChange'].apply(pos)
    df['IcuDailyChange'] = df['IcuDailyChange'].apply(pos)
    df['VentilatorsDailyChange'] = df['VentilatorsDailyChange'].apply(pos)
    df['DeathsDailyChange'] = df['DeathsDailyChange'].apply(pos)
    df['RecoveredDailyChange'] = df['RecoveredDailyChange'].apply(pos)
    print("cleaned data")
    ### set today's numbers ###
    today_date = df.Date[0]
    today_hospitalized = int(df.HospitalizedToday[0])
    today_icu = int(df.IcuToday[0])
    today_ventilators = int(df.VentilatorsToday[0])
    today_deaths =int(df.DeathsToday[0])
    today = [today_date, "{:,}".format(today_hospitalized), "{:,}".format(today_icu),
                "{:,}".format(today_ventilators), "{:,}".format(today_deaths)]       
    today_change = [df.HospitalizedDailyChange[0], df.IcuDailyChange[0],
                    df.VentilatorsDailyChange[0], df.DeathsDailyChange[0]]            
    cur.close()
    print("push to html")

    return render_template('covid19usagraph.html', today = today, change = today_change)#, yesterday = yesterday)

@app.route('/covid19usadata')
def covid19usadata():
    ### 
    AWSdatabase_COVI = os.getenv("AWSDATABASE_COVI")
    AWSuser_COVI = os.getenv("AWSUSER_COVI")
    AWSpassword_COVI = os.getenv("AWSPASSWORD_COVI")
    AWShost_COVI = os.getenv("AWSHOST_COVI")
    AWSport_COVI = os.getenv("AWSPORT_COVI")

    ## connect to AWS database ###
    connection = psycopg2.connect(database=AWSdatabase_COVI,
                                user=AWSuser_COVI,
                                password=AWSpassword_COVI,
                                host=AWShost_COVI,
                                port=AWSport_COVI)
    print("connected to database")

    cur = connection.cursor()

    sql_select_Query = "select * from covid19us" # query all of database 
    cur.execute(sql_select_Query)
    data = cur.fetchall()
    df = DataFrame(data)  # set as dataframe 
    print("pullled data")
    df.columns = ['Date', 'States', 'TestsToday', 'TestsDailyChange', 'TotalTests', 'PositivesToday', 'PostiviesDailyChange', 'TotalPositives', 
            'NegativesToday', 'NegativesDailyChange', 'TotalNegatives',
            'HospitalizedToday', 'HospitalizedDailyChange', 'HospitalizedCurrently', 'TotalHospitalized', 
            'IcuToday', 'IcuDailyChange', 'IcuCurrently', 'TotalIcu', 
            'VentilatorsToday', 'VentilatorsDailyChange', 'VentilatorsCurrently', 'TotalVentilators', 
            'DeathsToday', 'DeathsDailyChange', 'TotalDeaths', 'RecoveredToday', 'RecoveredDailyChange', 'TotalRecovered']
    print("table created")
    table = HTML(df.to_html(classes='table table-striped'))
    cur.close()
    print("push to hml")
    return render_template('covid19usadata.html',tables=[table])

@app.route('/australiabushfires')
def australiabushfires():
    # read in the csv file.
    df = pandas.read_csv("https://raw.githubusercontent.com/CVanchieri/DataSets/master/AustraliaBushFires/australiabushfires.csv", index_col=0)
    table = HTML(df.to_html(classes='table table-striped'))
    # set the time series and data for frames data.

    print("push to html")
    return render_template('australiabushfires.html', table = table)

if __name__ == '__main__':
    app.run(debug=True)

    # @app.route('/user', methods=['POST'])
    # @app.route('/user/<name>', methods=['GET'])
    # def user(name=None, message=''):
    #     name = name or request.values['user_name']
    #     try:
    #         if request.method == 'POST':
    #             add_or_update_user(name)
    #             message = "User {} successfully added!".format(name)
    #         tweets = User.query.filter(User.name == name).one().tweets
    #     except Exception as e:
    #         message = "Error adding {}: {}".format(name, e)
    #         tweets = []
    #     return render_template('user.html', title=name, tweets=tweets, message=message)

    # @app.route('/compare', methods=['POST'])
    # def compare(message=''):
    #     user1 = request.values['user1']
    #     user2 = request.values['user2']
    #     tweet_text = request.values['tweet_text']

    #     if user1 == user2:
    #         message = 'Cannot compare a user to themselves!'
    #     else:
    #         prediction = predict_user(user1, user2, tweet_text)
    #         message = '"{}" is more likely to be said by {} than {}'.format(
    #             request.values['tweet_text'], user1 if prediction else user2,
    #             user2 if prediction else user1)
    #     return render_template('prediction.html', title='Prediction', message=message)

    # @app.route('/reset')
    # def reset():
    #     DB.drop_all()
    #     DB.create_all()
    #     return render_template('base.html', title='Reset database!')

    # @app.route('/update')
    # def update():
    #     update_all_users()
    #     return render_template('base.html', users=User.query.all(), title='All Tweets updated!')

