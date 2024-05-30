from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from supabase import create_client, Client

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Supabase configuration
SUPABASE_URL = "https://ldkbzfcoewzynxawicxg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxka2J6ZmNvZXd6eW54YXdpY3hnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU4NjQwMDQsImV4cCI6MjAzMTQ0MDAwNH0.sE_JK5ZbobAOzWKR6osasEVfZPWhVt08NhRf0XgrsmA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/add_client', methods=['POST'])
def add_client():
    if 'user_id' in session:
        # Fetch admin details to verify role
        response = supabase.table('users').select('*').eq('id', session['user_id']).execute()
        admin = response.data[0] if response.data else None
        if admin and admin['role'] == 'admin':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']
            review_link = request.form['review_link']
            extraction_url = request.form['extraction_url']
            logo_url = request.form['logo_url']
            # Insert new client into the database
            insert_response = supabase.table('users').insert({
                'username': username,
                'password': password,
                'role': role
            }).execute()
            # Check for errors in the response
            if insert_response.data:
                # Get the ID of the newly inserted user
                user_id = insert_response.data[0]['id']
                # Insert corresponding client record
                client_insert_response = supabase.table('clients').insert({
                    'user_id': user_id,
                    'review_link': review_link,
                    'extraction_url': extraction_url,
                    'logo_url': logo_url
                }).execute()
                if client_insert_response.data:
                    message = 'Client added successfully'
                else:
                    message = f"Failed to add client: {client_insert_response.error}"
            else:
                message = f"Failed to add client: {insert_response.error}"
                
            return render_template('dashboard.html', user=admin, message=message)
        else:
            message = 'Unauthorized'
            return render_template('dashboard.html', user=admin, message=message)
    else:
        return redirect(url_for('login'))

# Other routes remain the same...
@app.route('/')
def home():
    if 'user_id' in session:
        user_response = supabase.table('users').select('*').eq('id', session['user_id']).execute()
        user = user_response.data[0] if user_response.data else None
        return render_template('dashboard.html', user=user)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_response = supabase.table('users').select('*').eq('username', username).execute()
        user = user_response.data[0] if user_response.data else None
        if user and user['password'] == password:
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        else:
            return 'Login failed', 401
    return render_template('login.html')

@app.route('/add_salesman', methods=['POST'])
def add_salesman():
    if 'user_id' in session:
        user_response = supabase.table('users').select('*').eq('id', session['user_id']).execute()
        user = user_response.data[0] if user_response.data else None
        if user and user['role'] == 'client':
            name = request.form['name']
            salesman_id = request.form['salesman_id']  # Assuming you have an input field for salesman_id
            client_id = user['id']  # Assuming client ID is stored in the session

            # Generate the review link
            # Assuming the current page URL is stored in the session as 'current_url'
            current_url = session.get('current_url')
            if current_url:
                review_link = f"{current_url}/app/{client_id}/{salesman_id}"
            else:
                # Handle the case when current_url is not available
                review_link = "Review link not available"

            # Insert new salesman into the database
            insert_response = supabase.table('salesmen').insert({
                'client_id': client_id,
                'name': name,
                'salesman_id': salesman_id,
                'points': 0  # Assuming you want to set points to 0 initially
            }).execute()

            if insert_response.data:
                message = 'Salesman added successfully'
            else:
                message = f"Failed to add salesman: {insert_response.error}"
            return render_template('dashboard.html', user=user, message=message)
        else:
            return 'Unauthorized', 403
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)