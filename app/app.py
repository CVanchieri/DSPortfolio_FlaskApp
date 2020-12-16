from decouple import config
from flask import Flask, render_template, request
#from .models import DB, User, Tweet
import os
import psycopg2
from pandas import DataFrame 
def create_app():
    """Create and configure an instance of the Flask application"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #DB.init_app(app)

    AWSdatabase = os.getenv("AWSDATABASE")
    AWSuser = os.getenv("AWSUSER")
    AWSpassword = os.getenv("AWSPASSWORD")
    AWShost = os.getenv("AWSHOST")
    AWSport = os.getenv("AWSPORT")

    ## connect to AWS database ###
    connection = psycopg2.connect(database=AWSdatabase,
                                user=AWSuser,
                                password=AWSpassword,
                                host=AWShost,
                                port=AWSport)

    cur = connection.cursor()

    sql_select_Query = "select * from tweets_storage" # query all of database 
    cur.execute(sql_select_Query)
    records = cur.fetchall()
    df = DataFrame(records)  # set as dataframe 
    df.columns = ['id', 'date', 'name', 'text', 'tags'] # label the columns 
    
    connection.close()
    
    @app.route('/')
    def root():
        pass

    @app.route('/home')
    def home():
        s = "<table style='border:1px solid red'>"
        for row in df:
            s = s+"<tr>"
            for x in row:
                s = s+"<td>"+str( x)+"</td>"    
            s = s+"</tr>"    

        return "<html><body>"+s+"</body></htm>"
        #return render_template('base.html', title='TwitterBot', data=df)

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

    return app