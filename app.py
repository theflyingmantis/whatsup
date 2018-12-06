from flask import Flask,render_template,request, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from bs4 import BeautifulSoup
import random

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://abhinav:abhinav@localhost/whatsup'
db = SQLAlchemy(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

background_color_scheme = ["#388BF2", "#E52A34", "#FBAF18", "#FC8338"]


class Slide(db.Model):
	__tablename__='slides'
	id = db.Column(db.Integer, primary_key=True, unique=True)
	type = db.Column(db.String(80))
	text = db.Column(db.String(500))
	image_url = db.Column(db.String(500))
	background_color = db.Column(db.String(20))
	background_image_url = db.Column(db.String(500))
	is_active = db.Column(db.Boolean, default=False)
	is_deleted = db.Column(db.Boolean, default=False)
	time = db.Column(db.Integer)
	title = db.Column(db.String(100))

	# def __repr__(self):
	# 	return '<slide %r %r %r>' % self.id, self.text, self.is_activ

def slideToJson(id, type, text, image_url, background_color, background_image_url, is_active, is_deleted, time, title):
	return {
		"id": id,
		"type": type,
		"text": text,
		"image_url": image_url,
		"background_image_url": background_image_url,
		"background_color": background_color,
		"is_active": is_active,
		"is_deleted": is_deleted,
		"time" : time,
		"title": title
	}

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

@app.route('/dashboard',methods=['GET', 'POST'])
def dashboard():
	return render_template('dashboard.html')

@app.route('/checkforchange',methods=['GET', 'POST'])
def checkforchange():
	key = getActiveSlideIdConcatenated()
	clientKey = request.args['key']
	slides = [slideToJson(slide.id, slide.type, slide.text, slide.image_url, slide.background_color, slide.background_image_url, slide.is_active, slide.is_deleted, slide.time, slide.title) for slide in Slide.query.filter_by(is_deleted=False, is_active=True).all()]

	obj = {
		"isChanged": clientKey != key,
		"key": key,
		"data": slides
	}
	return jsonify(obj)

def getActiveSlideIdConcatenated():
	slides = Slide.query.filter_by(is_deleted=False, is_active=True).all()
	key = ""
	for slide in slides:
		key+=str(slide.id)
	return key

@app.route('/delete',methods=['GET', 'POST'])
def delete():
	id = request.args['id']
	slide = Slide.query.get(id)
	slide.is_deleted = True
	db.session.commit()
	return redirect(url_for('manage_slides'))

@app.route('/active',methods=['GET', 'POST'])
def active():
	id = request.args['id']
	slide = Slide.query.get(id)
	slide.is_active = True
	db.session.commit()
	return redirect(url_for('manage_slides'))

@app.route('/inactive',methods=['GET', 'POST'])
def inactive():
	id = request.args['id']
	slide = Slide.query.get(id)
	slide.is_active = False
	db.session.commit()
	return redirect(url_for('manage_slides'))


@app.route('/manage_slides',methods=['GET', 'POST'])
def manage_slides():
	slides = Slide.query.filter_by(is_deleted=False).all()
	return render_template('manage_slides.html', slides = slides)


@app.route('/create_slide',methods=['GET', 'POST'])
def create_slide():
	return render_template('create_slide.html')

@app.route('/create_slide_only_text',methods=['GET', 'POST'])
def create_slide_only_text():
	if request.method == "POST":
		background_color = request.values.get('background_color')
		text = request.values.get('text')
		time = request.values.get('time')
		title = request.values.get('title')
		slideObj = Slide(text=text, background_color=background_color, time=time, type="just-text", title=title)
		try:
			db.session.add(slideObj)
			db.session.commit()
			flash("Slide Created")
		except Exception as e:
			exc = str(e)
			flash(exc)
		return redirect(url_for('dashboard'))
	return render_template('create_slide_only_text.html')

@app.route('/create_slide_only_image',methods=['GET', 'POST'])
def create_slide_only_image():
	if request.method == "POST":
		background_image_url = request.values.get('url')
		time = request.values.get('time')
		title = request.values.get('title')
		slideObj = Slide(background_image_url=background_image_url, time=time, type="just-text", title=title)
		try:
			db.session.add(slideObj)
			db.session.commit()
			flash("Slide Created")
		except Exception as e:
			exc = str(e)
			flash(exc)
		return redirect(url_for('dashboard'))
	return render_template('create_slide_only_image.html')

@app.route('/remove_all', methods=['GET', 'POST'])
def remove_all():
	moveAllActiveToInactive()
	return redirect(url_for('dashboard'))

@app.route('/ci_build_fail', methods = ['POST'])
def cifail():
	if request.method == "POST":
		moveAllActiveToInactive()
		service = request.values.get('service')
		logs = request.values.get('logs')
		time = 20000
		title = "cifail-"+str(service)
		image_url = "https://media0.giphy.com/media/5yfle3Ii3jrrO/giphy.gif"
		text = str(service)+" - "+str(logs)
		slideObj = Slide(background_color = background_color_scheme[1], time=time, type="text-and-image", title=title, text=text, image_url=image_url, is_active=True)
		try:
			db.session.add(slideObj)
			db.session.commit()
		except Exception as e:
			exc = str(e)
			flash(exc)
	return redirect(url_for('dashboard'))


def moveAllActiveToInactive():
	slides = Slide.query.filter_by(is_deleted=False, is_active=True).all()
	for slide in slides:
		slide.is_active = False
		db.session.commit()


@app.route('/display_news/<category>', methods=['GET', 'POST'])
def display_news(category):
	news = getNews(category)
	moveAllActiveToInactive()
	for nws in news["data"]:
		text = nws["title"]
		title = nws["title"]
		image_url = nws["imageUrl"]
		time = 4000
		background_color = background_color_scheme[random.randint(0,3)]
		slideObj = Slide(background_color = background_color, time=time, type="text-and-image", title=title, text=text, image_url=image_url, is_active=True)
		try:
			db.session.add(slideObj)
			db.session.commit()
		except Exception as e:
			exc = str(e)
			flash(exc)
	flash("Slide Created")
	return redirect(url_for('dashboard'))


@app.route('/create_slide_text_over_image',methods=['GET', 'POST'])
def create_slide_text_over_image():
	if request.method == "POST":
		background_image_url = request.values.get('url')
		time = request.values.get('time')
		title = request.values.get('title')
		text = request.values.get('text')
		slideObj = Slide(background_image_url=background_image_url, time=time, type="just-text", title=title, text=text)
		try:
			db.session.add(slideObj)
			db.session.commit()
			flash("Slide Created")
		except Exception as e:
			exc = str(e)
			flash(exc)
		return redirect(url_for('dashboard'))
	return render_template('create_slide_text_over_image.html')

@app.route('/create_slide_text_and_image',methods=['GET', 'POST'])
def create_slide_text_and_image():
	if request.method == "POST":
		background_image_url = request.values.get('url')
		time = request.values.get('time')
		title = request.values.get('title')
		text = request.values.get('text')
		image_url = request.values.get('url')
		background_color = request.values.get("background_color")
		slideObj = Slide(background_color = background_color, time=time, type="text-and-image", title=title, text=text, image_url = image_url)
		try:
			db.session.add(slideObj)
			db.session.commit()
			flash("Slide Created")
		except Exception as e:
			exc = str(e)
			flash(exc)
		return redirect(url_for('dashboard'))
	return render_template('create_slide_text_and_image.html')

def getNews(category):
    newsDictionary = {
        'success': True,
        'category': category,
        'data': []
    }

    try:
        htmlBody = requests.get('https://www.inshorts.com/en/read/' + category)
    except requests.exceptions.RequestException as e:
        newsDictionary['success'] = False
        newsDictionary['errorMessage'] = str(e.message)
        return newsDictionary

    soup = BeautifulSoup(htmlBody.text, 'lxml')
    newsCards = soup.find_all(class_='news-card')
    if not newsCards:
        newsDictionary['success'] = False
        newsDictionary['errorMessage'] = 'Invalid Category'
        return newsDictionary

    for card in newsCards:
        try:
            title = card.find(class_='news-card-title').find('a').text
        except AttributeError:
            title = None

        try:
            imageUrl = card.find(
                class_='news-card-image')['style'].split("'")[1]
        except AttributeError:
            imageUrl = None

        try:
            url = ('https://www.inshorts.com' + card.find(class_='news-card-title')
                   .find('a').get('href'))
        except AttributeError:
            url = None

        try:
            content = card.find(class_='news-card-content').find('div').text
        except AttributeError:
            content = None

        try:
            author = card.find(class_='author').text
        except AttributeError:
            author = None

        try:
            date = card.find(clas='date').text
        except AttributeError:
            date = None

        try:
            time = card.find(class_='time').text
        except AttributeError:
            time = None

        try:
            readMoreUrl = card.find(class_='read-more').find('a').get('href')
        except AttributeError:
            readMoreUrl = None

        newsObject = {
            'title': title,
            'imageUrl': imageUrl,
            'url': url,
            'content': content,
            'author': author,
            'date': date,
            'time': time,
            'readMoreUrl': readMoreUrl
        }

        newsDictionary['data'].append(newsObject)

    return newsDictionary


if __name__ == '__main__':
    app.run(debug=True)