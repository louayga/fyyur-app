#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections
collections.Callable = collections.abc.Callable
from flask_migrate import Migrate
import sys
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:louay25689@localhost:5432/project1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
    
    num_upcoming_shows = db.Column(db.Integer)
    
    shows = db.relationship('Show', backref='venue', lazy=True)
    
    def __repr__(self):
      return f"<Venue {self.id} name: {self.name}>"
    
    
class Artist(db.Model):
    __tablename__ = 'artist'

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
    seeking_venue = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
    
    num_upcoming_shows = db.Column(db.Integer)
    
    shows = db.relationship('Show', backref='artist', lazy=True)
    
    def __repr__(self):
      return f"<Artis {self.id} name: {self.name}>"
    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    
    def __repr__(self):
      return f"<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>"
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
  data=[]
  areas = Venue.query.all()
  
  for area in areas:
        
        venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
        for venue in venues:
          data.append({
            "id": venue.id,
            "name": venue.name, 
            "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
          })
        data.append({
          "city": area.city,
          "state": area.state, 
          "venues": data
        })
  
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
  data = []
  
  for venue in search:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": venue.upcoming_shows
    })
    
  response={
    "count": len(search),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  venueid = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now()

  for show in shows:
    show_data = {
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
           "artist_image_link": show.artist.image_link,
           "start_time": format_datetime(str(show.start_time))
        }
    if show.start_time >= current_time:
      upcoming_shows.append(show_data)
    else:
      past_shows.append(show_data)

  
  data={
    "id": venueid.id,
    "name": venueid.name,
    "image_link": venueid.image_link,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
 
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  try:
    form = VenueForm(request.form)
    venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data
        
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue: {0} created successfully'.format(venue.name))
  except Exception as err:
    flash('An error occurred creating the Venue: {0}. Error: {1}'.format(venue.name, err))
    db.session.rollback()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    venue_created = Venue()
    venue_created.name = request.form['name']
    venue_created.city = request.form['city']
    venue_created.state = request.form['state']
    venue_created.address = request.form['address']
    venue_created.phone = request.form['phone']
    venue_created.genres = request.form ['genres']
    venue_created.image_link = request.form['image_link']
    venue_created.facebook_link = request.form['facebook_link']
    venue_created.website_link= request.form['website_link']
    venue_created.seeking_talent  = request.form['seeking_talent']
    venue_created.seeking_description = request.form['seeking_description']
    
    try:
      db.session.add(venue_created)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except: 
      db.session.rollback()
      print(sys.exc_info())
       # TODO: on unsuccessful db insert, flash an error instead.
       # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
       # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
    finally: 
      db.session.close()    
    
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash(f'An error occurred. Venue {venue_id} could not be deleted.')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Venue {venue_id} was successfully deleted.')
  finally:
    db.session.close()
 
  
  return redirect(url_for('home.html'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  artists = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })

  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  search = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  data = []
  
  for result in search:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })
    
  response={
    "count": len(search),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  artistid = Artist.query.get(artist_id)
  shows = Show.query.filter_by(venue_id=artist_id).all()
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now()

  for show in shows:
    data = {
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
           "venue_image_link": show.artist.image_link,
           "start_time": format_datetime(str(show.start_time))
        }
    if show.start_time >= current_time:
      upcoming_shows.append(data)
    else:
      past_shows.append(data)

  
  data={
    "id": artistid.id,
    "name": artistid.name,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist_data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue ": artist.seeking_venue ,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  artist = Artist.query.get(artist_id)
  
  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = request.form.get('genres')
  artist.image_link = request.form['image_link']
  artist.facebook_link = request.form['facebook_link']
  artist.website_link = request.form['website_link']
  artist.seeking_venue  =request.form['seeking_venue ']
  artist.seeking_description = request.form['seeking_description']
  try:
    db.session.commit()
  except: 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Artist could not be changed.')
  if not error: 
    flash('Artist was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  venue = Venue.query.get(venue_id)

  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.get('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent =  request.form['seeking_talent']
    venue.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash(f'Venue was successfully updated!')
   
  except: 
    
    db.session.rollback()
    print(sys.exc_info())
    flash(f'An error occurred. Venue could not be changed.')
    
  finally: 
    
    db.session.close()
 
    
  return redirect(url_for('show_venue', venue_id=venue_id))

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
 
  try: 
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.get('genres'),
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website_link = request.form['website_link']
    seeking_venue = request.form['seeking_venue']
    seeking_description = request.form['seeking_description']
    
    artist = Artist(name=name, 
                    city=city, 
                    state=state,
                    phone=phone,
                    genres=genres,
                    facebook_link=facebook_link, 
                    image_link=image_link, 
                    website_link=website_link, 
                    seeking_talent=seeking_venue, 
                    seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except: 
    
    db.session.rollback()
    print(sys.exc_info())  
    
    flash('An error occurred. Artist ' + request.form['name']+ ' could not be listed.')
  finally: 
    db.session.close()  
    
 
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = db.session.query(Show).join(Artist).join(Venue).all()
  
  shows_data = []
  for show in shows: 
    shows_data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time":  format_datetime(str(show.start_time))
    })
  return render_template('pages/shows.html', shows=shows_data)

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
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed')
  except: 
    
    db.session.rollback()
    print(sys.exc_info())
    
    flash('An error occurred. Show could not be listed.')
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