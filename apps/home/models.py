# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from datetime import datetime
from apps import db, login_manager

class Dancers(db.Model):
    __tablename__ = 'Dancers'
    id              = db.Column(db.Integer, primary_key=True)
    id_user         = db.Column(db.Integer)
    name            = db.Column(db.String)
    lastname        = db.Column(db.String)
    birth_date      = db.Column(db.String)
    picture         = db.Column(db.String)
    sex             = db.Column(db.String)

class User_data(db.Model):
    __tablename__ = 'User_data'
    id          = db.Column(db.Integer, primary_key=True)
    id_user     = db.Column(db.Integer)
    name        = db.Column(db.String)
    lastname    = db.Column(db.String)
    address     = db.Column(db.String)
    city        = db.Column(db.String)
    post_code   = db.Column(db.String)
    country     = db.Column(db.String)
    studio      = db.Column(db.String)
    phone       = db.Column(db.String)

class Events(db.Model):
    __tablename__ = 'Events'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String)
    event_from      = db.Column(db.String)
    event_to        = db.Column(db.String)
    picture         = db.Column(db.String)
    description     = db.Column(db.Text)
    reference_date  = db.Column(db.String)
    active          = db.Column(db.Integer)

    def __init__(self, name, event_from, event_to, picture, description, reference_date, active):
        self.name           = name
        self.event_from     = event_from
        self.event_to       = event_to
        self.picture        = picture
        self.description    = description
        self.reference_date = reference_date
        self.active         = active

class Application(db.Model):
    __tablename__ = 'Application'
    id              = db.Column(db.Integer, primary_key=True)
    id_event        = db.Column(db.Integer)
    user_id         = db.Column(db.Integer)
    choreography    = db.Column(db.String)
    choreograph     = db.Column(db.String)
    age_group       = db.Column(db.Integer)
    discipline      = db.Column(db.Integer)
    category        = db.Column(db.Integer)
    federation      = db.Column(db.Integer)
    level           = db.Column(db.Integer)
    audio           = db.Column(db.String)
    song_author     = db.Column(db.String)
    song_name       = db.Column(db.String)
    entered_date    = db.Column(db.String)
    
    def __init__(self, id_event, user_id, choreography, choreograph, age_group, discipline, category, federation, level, audio, song_author, song_name, entered_date):
        self.id_event        = id_event
        self.user_id         = user_id
        self.choreography    = choreography
        self.choreograph     = choreograph
        self.age_group       = age_group
        self.discipline      = discipline
        self.category        = category
        self.federation      = federation
        self.level           = level
        self.audio           = audio
        self.song_author     = song_author
        self.song_name       = song_name
        self.entered_date    = entered_date

class Application_dancer(db.Model):
    __tablename__ = 'Application_dancer'
    id              = db.Column(db.Integer, primary_key=True)
    id_application  = db.Column(db.Integer)
    id_dancer       = db.Column(db.Integer)

    def __init__(self, id_application, id_dancer):
        self.id_application = id_application
        self.id_dancer      = id_dancer

class Age_group(db.Model):
    __tablename__ = 'Age_group'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String)
    min_years       = db.Column(db.Integer)
    max_years       = db.Column(db.Integer)
    use_average     = db.Column(db.Integer)
    active          = db.Column(db.Integer)

class Category(db.Model):
    __tablename__ = 'Category'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String)
    min_dancers     = db.Column(db.Integer)
    max_dancers     = db.Column(db.Integer)
    price           = db.Column(db.Integer)
    active          = db.Column(db.Integer)

class Discipline(db.Model):
    __tablename__ = 'Discipline'
    id              = db.Column(db.Integer, primary_key=True)
    discipline      = db.Column(db.String)
    use_ref_date    = db.Column(db.Integer)
    active          = db.Column(db.Integer)

class Level(db.Model):
    __tablename__ = 'Level'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String)
    active  = db.Column(db.Integer)

class Federation(db.Model):
    __tablename__ = 'Federation'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String)
    active  = db.Column(db.Integer)

class Event_age_group(db.Model):
    __tablename__ = 'Event_age_group'
    id              = db.Column(db.Integer, primary_key=True)
    id_event        = db.Column(db.Integer)
    id_age_group    = db.Column(db.Integer)
    def __init__(self, id_event, id_age_group):
        self.id_event       = id_event
        self.id_age_group   = id_age_group

class Event_category(db.Model):
    __tablename__ = 'Event_category'
    id              = db.Column(db.Integer, primary_key=True)
    id_event        = db.Column(db.Integer)
    id_category     = db.Column(db.Integer)
    def __init__(self, id_event, id_category):
        self.id_event       = id_event
        self.id_category    = id_category

class Event_discipline(db.Model):
    __tablename__ = 'Event_discipline'
    id              = db.Column(db.Integer, primary_key=True)
    id_event        = db.Column(db.Integer)
    id_discipline   = db.Column(db.Integer)
    def __init__(self, id_event, id_discipline):
        self.id_event       = id_event
        self.id_discipline    = id_discipline

class Event_federation(db.Model):
    __tablename__ = 'Event_federation'
    id              = db.Column(db.Integer, primary_key=True)
    id_event        = db.Column(db.Integer)
    id_federation   = db.Column(db.Integer)
    def __init__(self, id_event, id_federation):
        self.id_event       = id_event
        self.id_federation  = id_federation

class Event_level(db.Model):
    __tablename__ = 'Event_level'
    id          = db.Column(db.Integer, primary_key=True)
    id_event    = db.Column(db.Integer)
    id_level    = db.Column(db.Integer)
    def __init__(self, id_event, id_level):
        self.id_event   = id_event
        self.id_level   = id_level

class Event_category_ordering(db.Model):
    __tablename__ = 'Event_category_ordering'
    id              = db.Column(db.Integer, primary_key=True)
    id_head        = db.Column(db.Integer)
    id_age_group    = db.Column(db.Integer)
    id_discipline   = db.Column(db.Integer)
    id_category     = db.Column(db.Integer)
    eo              = db.Column(db.Integer)
    live            = db.Column(db.Integer)

    def __init__(self, id_head, id_age_group, id_discipline, id_category, eo, live):
        self.id_head       = id_head
        self.id_age_group   = id_age_group
        self.id_discipline  = id_discipline
        self.id_category    = id_category
        self.eo             = eo
        self.live           = live

class Event_category_ordering_head(db.Model):
    __tablename__ = 'Event_category_ordering_head'
    id          = db.Column(db.Integer, primary_key=True)
    id_event    = db.Column(db.Integer)
    date        = db.Column(db.Integer)
    time        = db.Column(db.Integer)


    def __init__(self, id_event, date, time):
        self.id_event   = id_event
        self.date       = date
        self.time       = time
