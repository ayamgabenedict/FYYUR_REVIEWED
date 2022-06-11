#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import error
import json
from sre_parse import State
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, session, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
Base = declarative_base()
db = SQLAlchemy(app)

migrate=  Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:roottoor@localhost:5432/projtodoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='Venue', lazy=True)

#def __repr__(self):
 #  return f'<Venue ID:{self.id}, name: {self.name}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, genres: {self.genres}, website_link: {self.website_link}, seeking_talent: {self.seeking_talent}, seeking_description: {self.seeking_description}, shows: {self.shows}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='Artist', lazy=True)
    
  
   
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable= False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable= False)
    start_time = db.Column(db.DateTime, nullable= False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue. 
  
  venue_query= Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  venue_state_city=''
  data=[]
  for v in venue_query:
    upcoming_shows= v.query.filter(Show.start_time > current_time).all()
    if venue_state_city==v.city + v.state:
      data[len(data) - 1]["v"].append({ 
      "id": v.id,
      "name":v.name,
      "num_upcoming_shows": len(upcoming_shows) 
      })
    else:
      venue_state_city == v.city + v.state
      data.append({
        "city":v.city,
        "state":v.state,
        "venues": [{
          "id": v.id,
          "name":v.name,
          "num_upcoming_shows": len(upcoming_shows)
        }]
      })

 
      
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #venue_query_partial = db.session.query(Venue).filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
  #v_list = list(map(Venue.short, venue_query_partial)) 
  try:
    data = []
    venues = []
    search_term = request.form.get("search_term").lower()
    for venue in db.session.query(Venue):
      if search_term in venue.name:
         venues.append(venue)
    for venue in venues:
      next_shows = Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > datetime.utcnow().strftime('%d-%m-%y %H:%M:%S')).all()
      data.append({
         "id": venue.id,
         "name": venue.name,
         "num_upcoming_shows": len(next_shows)
      })
      response = {
        'count':len(venues),
        'data': venues
     }
  except:
     # on unsuccessful db insert, flash an error instead.
       flash('An error occurred. Show  could not be listed!')
       db.session.rollback()
       print(sys.exc_info())
  finally:
        db.session.close()
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue_info=''
  venue_query_on_id = db.session.query(Venue).get(venue_id)
  if venue_query_on_id:
   # venue_info =  venue_info(venue_query_on_id)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    shows_query = db.session.query(Show).options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id)
    
    new_shows_query = shows_query.filter(Show.start_time > current_time).all()
    new_show_list = list(map(Show.artist_id, new_shows_query))
    venue_info["upcoming_shows"] = new_show_list
    venue_info["upcoming_shows_count"] = len(new_show_list)
    past_shows_query = shows_query.filter(Show.start_time <= current_time).all()
    past_shows = list(map(Show.artist_id, past_shows_query))
    show_venue["past_shows"] = past_shows
    venue_info["past_shows_count"] = len(past_shows)

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=show_venue)
  #return render_template('pages/show_venue.html', venue=venue_info)
  return render_template('errors/404.html')

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  #error= False
  seeking_talent = False
  seeking_description = ''
  if 'seeking_talent' in request.form:
    seeking_talent = request.form['seeking_talent'] == 'y'
  if 'seeking_description' in request.form:
    seeking_description = request.form['seeking_description']
  new_venue = Venue(
    name=request.form['name'],
    city=request.form['city'],
    state=request.form['state'],
    address=request.form['address'],
    phone=request.form['phone'],
    image_link=request.form['image_link'],
    facebook_link=request.form['facebook_link'],
    genres=request.form.getlist('genres'),
    website_link=request.form['website_link'],
    seeking_talent=seeking_talent,
    seeking_description=seeking_description
    )
  #insert new_venue records into the database
  db.session.add(new_venue)
  db.session.commit()
  # on successful db insert, flash success
  flash('Your Venue ' + request.form['name'] + ' was successfully listed!')
    
  db.session.rollback()
  print(sys.exc_info())
 
  db.session.close() 
 
  return render_template('pages/home.html')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    #flash('An error occurred with your data insertion.' + 'Venue ' + request.form['name'] + ' could not be listed. Plese check and try again')  


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    db.session.query(Venue).filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback() 
    print(sys.exc_info())
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  #Search for all artists
  artist_query = Artist.query.all()
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  return render_template('pages/artists.html', artists=artist_query)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  data = []
  artists = []
  search_term = request.form.get("search_term").lower()
  for artist in db.session.query(Artist):
    if search_term in artist.name:
      artists.append(artist)
  for artist in artists:
    next_shows = Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > datetime.utcnow().strftime('%d-%m-%y %H:%M:%S')).all()
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(next_shows)
    })
    response = {
      'count':len(artists),
      'data': artists
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artist_query_on_id = db.session.query(Artist).get(artist_id)
  if artist_query_on_id:
    artist_info = Artist[artist_query_on_id]
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    shows_query= db.session.query(Show).options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id)
    
    new_shows_query = shows_query.filter(Show.start_time > current_time).all()
    new_show_list = list(map(Show.venue_info, new_shows_query))
    artist_info["upcoming_shows"] = new_show_list
    artist_info["upcoming_shows_count"] = len(new_show_list) 
    past_shows_query = shows_query.filter(Show.start_time <= current_time).all()
    past_shows = list(map(Show.venue_info, past_shows_query))
    artist_info["past_shows"] = past_shows
    artist_info["past_shows_count"] = len(past_shows)
    return render_template('pages/show_artist.html', artist=artist_info)
  return render_template('errors/404.html')


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    artist_info = db.session.query(Artist).get(artist_id)
    if artist_info:
        if form.validate():
            seeking_venue = False
            seeking_description = ''
            if 'seeking_venue' in request.form:
                seeking_venue = request.form['seeking_venue'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(artist_info, 'name', request.form['name'])
            setattr(artist_info, 'city', request.form['city'])
            setattr(artist_info, 'state', request.form['state'])
            setattr(artist_info, 'phone', request.form['phone'])
            setattr(artist_info, 'genres', request.form.getlist('genres'))
            setattr(artist_info, 'image_link', request.form['image_link'])
            setattr(artist_info, 'facebook_link', request.form['facebook_link'])
            setattr(artist_info, 'website_link', request.form['website_link'])
            setattr(artist_info, 'seeking_venue', seeking_venue)
            setattr(artist_info, 'seeking_description', seeking_description)
            Artist.update(artist_info)
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            print(form.errors)
    return render_template('errors/404.html'), 404

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_query = db.session.query(Venue).get(venue_id)
  if venue_query:
    venue_info = Venue.detail(venue_query)
    form.name.data = venue_info["name"]
    form.city.data = venue_info["city"]
    form.state.data = venue_info["state"]
    form.address.data = venue_info["address"]
    form.phone.data = venue_info["phone"]
    form.image_link.data = venue_info["image_link"]
    form.facebook_link.data = venue_info["facebook_link"]
    form.genres.data = venue_info["genres"]
    form.website.data = venue_info["website_link"]
    form.seeking_talent.data = venue_info["seeking_talent"]
    form.seeking_description.data = venue_info["seeking_description"]
    return render_template('form/edit_venue.html', form=form, Venue=venue_info)
  return render_template('errors/404.html')
  
  # TODO: populate form with values from venue with ID <venue_id>
  #return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue_info = db.session.query(Venue).get(venue_id)
  if venue_info:
      if form.validate():
          seeking_venue = False
          seeking_description = ''
          if 'seeking_venue' in request.form:
              seeking_venue = request.form['seeking_venue'] == 'y'
          if 'seeking_description' in request.form:
              seeking_description = request.form['seeking_description']
          setattr(venue_info, 'name', request.form['name'])
          setattr(venue_info, 'city', request.form['city'])
          setattr(venue_info, 'state', request.form['state'])
          setattr(venue_info, 'phone', request.form['phone'])
          setattr(venue_info, 'genres', request.form.getlist('genres'))
          setattr(venue_info, 'image_link', request.form['image_link'])
          setattr(venue_info, 'facebook_link', request.form['facebook_link'])
          setattr(venue_info, 'website_link', request.form['website_link'])
          setattr(venue_info, 'seeking_venue', seeking_venue)
          setattr(venue_info, 'seeking_description', seeking_description)
          Venue.update(venue_info)
          return redirect(url_for('show_artist', venue_id=venue_id))
      else:
            print(form.errors)
  return render_template('errors/404.html'), 404


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion 
  seeking_venue = False
  seeking_description = ''
  if 'seeking_venue' in request.form:
    seeking_venue = request.form['seeking_venue'] == 'y'
  if 'seeking_description' in request.form:
    seeking_description = request.form['seeking_description']    
  new_artist = Artist(
    name=request.form['name'],
    city=request.form['city'],
    state=request.form['state'],
    phone=request.form['phone'],
    genres=request.form.getlist('genres'),
    image_link=request.form['image_link'],
    facebook_link=request.form['facebook_link'],
    website_link=request.form['website_link'],
    seeking_venue=seeking_venue,
    seeking_description=seeking_description
    )
  #insert new_artist records into the database
  db.session.add(new_artist)
  db.session.commit()
  # on successful db insert, flash success.
  flash('Artist ' + request.form['name'] + ' was successfully listed!')

  db.session.rollback()
  print(sys.exc_info())
  
  db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #Search for all shows
  data= db.session.query(Show, Artist, Venue).join(Artist).join(Venue).all()
  return render_template('pages/shows.html', show=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    
  try: 
    new_show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time']
    )
  #insert new_show records into the database
    db.session.add(new_show)
    db.session.commit()
  # on successful db insert, flash success   
    flash('Show  was successfully listed!')
  except:
  # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show  could not be listed!')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')
     

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
