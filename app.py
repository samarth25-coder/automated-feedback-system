from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from textblob import TextBlob
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
db = SQLAlchemy(app)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text)
    sentiment = db.Column(db.Float)

@app.route('/')
def index():
    feedbacks = Feedback.query.all()
    
    # Basic analytics
    total = len(feedbacks)
    avg_rating = round(sum([f.rating for f in feedbacks])/total, 1) if total else 0
    
    # Generate sentiment chart
    if total > 0:
        plt.figure(figsize=(8,4))
        sentiments = [f.sentiment for f in feedbacks]
        plt.hist(sentiments, bins=20, color='skyblue')
        plt.title('Feedback Sentiment Distribution')
        plt.xlabel('Sentiment Polarity (-1 to 1)')
        plt.ylabel('Count')
        plt.savefig('static/sentiment_chart.png')
    
    return render_template('index.html', 
                          feedbacks=feedbacks,
                          total=total,
                          avg_rating=avg_rating)

@app.route('/submit', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        rating = int(request.form['rating'])
        comments = request.form['comments']
        
        # Sentiment analysis
        analysis = TextBlob(comments)
        sentiment = analysis.sentiment.polarity
        
        # Save to database
        new_feedback = Feedback(
            name=name,
            email=email,
            rating=rating,
            comments=comments,
            sentiment=sentiment
        )
        db.session.add(new_feedback)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('feedback.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)