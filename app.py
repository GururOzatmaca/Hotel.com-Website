import sqlite3 as sql
from flask import Flask, render_template, redirect, url_for, session, request
from datetime import datetime, timedelta
from flask_oauthlib.client import OAuth
from datetime import datetime
import requests
import re

app = Flask(__name__)








def initDB():
    conn = sql.connect('database.db')
    print( "Opened database successfully")   
    
    conn.execute("""CREATE TABLE IF NOT EXISTS HOTELS(
        imageUrl text,
        rating text,
        ratingName text,
        commentCount text,
        availableDateFrom text,
        availableDateTo text,
        hotelName text,
        hotelLocation text,
        discountedPrice text,
        oldPrice  text,
        loginDiscount  text,
        defaultDiscount  text,
        availableGuestCount text,
        amenities text
    )    """)
    
    conn.execute("""CREATE TABLE IF NOT EXISTS USERS(
        firstName text,
        lastName text,
        eMail text,
        password  text,
        country text,
        city text
    )    """)

    
    print ("Table created successfully")
    conn.close()


def get_next_weekend():
    today = datetime.now()
    next_saturday = today + timedelta(days=(5 - today.weekday() + 7) % 7)
    next_sunday = next_saturday + timedelta(days=1)
    return next_saturday, next_sunday


def get_hotels():
    conn = sql.connect('database.db')
    cursor = conn.cursor()

    next_saturday, next_sunday = get_next_weekend()
    

    cursor.execute("""
    SELECT * FROM HOTELS
    WHERE date(availableDateFrom) <= date(?) AND date(availableDateTo) >= date(?)
    ORDER BY rating DESC
    LIMIT 3
    """, (next_saturday.strftime('%Y-%m-%d'), next_sunday.strftime('%Y-%m-%d')))


    hotels = cursor.fetchall()
    


    conn.close()
    return hotels


def get_next_weekend_formatted():
    today = datetime.now()
    days_until_saturday = (5 - today.weekday() + 7) % 7
    days_until_sunday = (6 - today.weekday() + 7) % 7
    saturday = today + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=2)
    formatted_saturday = saturday.strftime('%d %B')
    formatted_sunday = sunday.strftime('%d %B')

    return f"{formatted_saturday} - {formatted_sunday}"





def get_discounted_price():
    
    
    conn = sql.connect('database.db')
    cursor = conn.cursor()

    next_saturday, next_sunday = get_next_weekend()
    

    cursor.execute("""
    SELECT discountedPrice FROM HOTELS
    WHERE date(availableDateFrom) <= date(?) AND date(availableDateTo) >= date(?)
    ORDER BY rating DESC
    LIMIT 3
    """, (next_saturday.strftime('%Y-%m-%d'), next_sunday.strftime('%Y-%m-%d')))


    

    results = cursor.fetchall()
    discounted_prices = [int(float(result[0]) * 0.90) for result in results]

    conn.close()
    return  discounted_prices

    





def get_openstreetmap_iframe(latitude, longitude, zoom=150, width=600, height=400):
    try:
        url = f"https://www.openstreetmap.org/export/embed.html?bbox={longitude-0.01},{latitude-0.01},{longitude+0.01},{latitude+0.01}&layer=mapnik&marker={latitude},{longitude}&zoom={zoom}"

        return f'<iframe width="{width}" height="{height}" frameborder="0" style="border:0" src="{url}" allowfullscreen></iframe>'
    except Exception as e:
        return f"An error occurred: {str(e)}"


def get_coordinates_by_hotel_name(hotel_name):
    try:
        connection = sql.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("SELECT latitude, longitude FROM HOTELS WHERE hotelName = ?", (hotel_name,))
        
        result = cursor.fetchone()

        if result:
            latitude, longitude = map(float, result)
            return latitude, longitude
        else:
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

    finally:
        connection.close()
        
        







@app.route('/')
def home():
    
    
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("""SELECT * from HOTELS """)

    
    guest_count_options = list(range(1, 11))
    
    with sql.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT hotelLocation FROM HOTELS")
        cities = [row[0] for row in cursor.fetchall()]
    
    next_weekend = get_next_weekend_formatted()
    
    hotels = get_hotels()
    
    if(username !=""):
        return redirect(url_for('manuallogin'))

    
    return render_template('home.html', guest_count_options=guest_count_options,cities=cities, next_weekend=next_weekend, hotels = hotels, username=username)







    
@app.route('/loginned')
def manuallogin():

    
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM HOTELS")

    guest_count_options = list(range(1, 11))

    with sql.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT hotelLocation FROM HOTELS")
        cities = [row[0] for row in cursor.fetchall()]

    next_weekend = get_next_weekend_formatted()
    hotels = get_hotels()
    discountedPrice = get_discounted_price()
    
    

    
    

    return render_template('loginned.html', guest_count_options=guest_count_options, cities=cities,
        next_weekend=next_weekend, hotels=hotels, discountedPrice=discountedPrice,username= username)



app.secret_key = 'your_secret_key'

oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='140953316451-9gn0k0ahso1ei0sftuke7jovdscrlas8.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'email profile',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)



@app.route('/google-login')
def loginGoogle():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

username = ""

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    
    
    
    
    con = sql.connect('database.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM HOTELS")

    guest_count_options = list(range(1, 11))

    with sql.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT hotelLocation FROM HOTELS")
        cities = [row[0] for row in cursor.fetchall()]

    next_weekend = get_next_weekend_formatted()
    hotels = get_hotels()
    discountedPrice = get_discounted_price()

    user_info = google.get('userinfo')
    
    name = user_info.data.get('name', 'Unknown')
    
    print("çalıştı")
    global username
    username = name
    return redirect(url_for('manuallogin'))
    

    return render_template('loginned.html', guest_count_options=guest_count_options, cities=cities,
        next_weekend=next_weekend, hotels=hotels, discountedPrice=discountedPrice,username= username)
    
    
    
    

    

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')








@app.route('/details/<hotel_name>')
def hotel_details(hotel_name):
    conn = sql.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM HOTELS WHERE hotelName=?", (hotel_name,))
    hotel_details = cursor.fetchone()


    if hotel_details:
        hotel_name = hotel_details[6]

    coordinates = get_coordinates_by_hotel_name(hotel_name)
    if coordinates:
        latitude, longitude = coordinates
        
        
        
    google_maps_iframe = get_openstreetmap_iframe(latitude, longitude)

    if hotel_details:
        return render_template('details.html', hotel_details=hotel_details,google_maps_iframe = google_maps_iframe, username=username)
    else:
        return render_template('home.html', hotel_name=hotel_name, )







@app.route('/search', methods=['POST'])
def search():
    
    conn = sql.connect('database.db')
    cursor = conn.cursor()
    city = request.form.get('city')
    daterange = request.form.get('daterange')
    guest_count = request.form.get('guest_count')  
    start_date, end_date = map(str.strip, daterange.split('-'))



    
    guest_count_options = list(range(1, 11))
    
    with sql.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT hotelLocation FROM HOTELS")
        cities = [row[0] for row in cursor.fetchall()]
    
    next_weekend = get_next_weekend_formatted()
    
    hotels = get_hotels()
    

    
    search_start_date = datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
    search_end_date = datetime.strptime(end_date, '%m/%d/%Y').strftime('%Y-%m-%d')

    
    cursor.execute("""
        SELECT * FROM HOTELS 
        WHERE hotelLocation=? 
        AND availableDateFrom <= ? 
        AND availableDateTo >= ? 
        AND availableGuestCount >= ?
    """, (city, search_start_date, search_end_date, guest_count))

    search_results = cursor.fetchall()
    


    return render_template('search.html', search_results=search_results, guest_count_options=guest_count_options,cities=cities, next_weekend=next_weekend, hotels = hotels, username=username)





def get_cities():
    json_url = 'https://run.mocky.io/v3/d80d93a8-4e4c-4375-81d7-60df6b7a110c'  
    response = requests.get(json_url)
    if response.status_code == 200:
        cities_data = response.json()
        return cities_data.get('cities', [])
    else:
        return []


@app.route('/register')
def register():
    
    cities = get_cities()
    return render_template('register.html', cities= cities)


@app.route('/login')
def login():
    

    return render_template('login.html')






@app.route('/login', methods=['POST'])
def registerUser():
    
    conn = sql.connect('database.db') 
    cursor = conn.cursor()
    
    first_name = request.form.get('name')
    last_name = request.form.get('surname')
    email = request.form.get('mail')
    password = request.form.get('password')
    againpasword = request.form.get('againpassword')
    country = request.form.get('country')
    city = request.form.get('city')


    if not all([first_name, last_name, email, password, againpasword, country, city]):
        return "All fields must be filled."

    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$', password):
        return "Password must be at least 8 characters, contain at least one number, and one non-alphanumeric character."

    if password != againpasword:
        return "Passwords do not match."
    
    cursor.execute("""
                SELECT eMail FROM USERS
                WHERE eMail = ?
            """, (email,))

    existing_email = cursor.fetchone()
    if existing_email:
                return "Email is already on use!"

    
    cursor.execute("""
    INSERT INTO USERS 
    VALUES (?, ?, ?, ?, ?, ?)
    """,(first_name, last_name, email, password, country, city))

    conn.commit()
    conn.close()
    

    return render_template('login.html')



@app.route('/loginned', methods=['POST'])
def loginUser():
    try:
        if request.method == 'POST':
            email = request.form.get('mail')
            password = request.form.get('password')
            
            conn = sql.connect('database.db')
            cursor = conn.cursor()


            
            cursor.execute("""
                SELECT * FROM USERS
                WHERE eMail = ? AND password = ?
            """, (email, password))
            
            user = cursor.fetchone()
            print(user)
            
            
            
            if(user != None):
                global username
                username = user[0]
                conn.close()
                return redirect(url_for('manuallogin'))
            
            else:
                return "Login failed. Invalid email or password."
    except Exception as e:
        return f"An error occurred: {str(e)}"
    return render_template('login.html')




if __name__ == '__main__':
    initDB()
    app.run()