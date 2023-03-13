# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import base64
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash, jsonify, session, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from sqlalchemy.orm import relationship
from flask_login import login_required, LoginManager, current_user
from jinja2 import TemplateNotFound, Template
from apps.home.models import *
from apps.home.functions import *
from apps import db
from werkzeug.utils import secure_filename
from base64 import b64encode
from datetime import datetime
import os
import json

UPLOAD_FOLDER_DANCERS = 'apps/static/assets/images/dancers/'
IMAGE_FOLDER_DANCERS = '/static/assets/images/dancers/'

UPLOAD_FOLDER_EVENTS = 'apps/static/assets/images/events/'
IMAGE_FOLDER_EVENTS = '/static/assets/images/events/'

UPLOAD_FOLDER_AUDIO = 'apps/static/assets/audio/'
AUDIO_FOLDER = '/static/assets/audio/'

@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')


    

@blueprint.route('/<template>')
@login_required
def route_template(template):

    
    try:
        
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        if template == 'chat.html':
            print(template)
            name = 'test1'
            room = 'test2'
            return render_template("home/chat.html", name=name, room=room)

        if template == 'settings.html':
            user_data = User_data.query.filter_by(id_user=current_user.id).first()

            return render_template("home/" + template, segment=segment, data=user_data)
        
        if template == 'dancers.html':
            dancers = getDancers()

            return render_template("home/" + template, segment=segment, data=dancers)
        
        if template == 'events.html':
            events = getEvents()
            age_group   = Age_group.query.filter_by(active=1).all()
            category    = Category.query.filter_by(active=1).all()
            discipline  = Discipline.query.filter_by(active=1).all()
            level       = Level.query.filter_by(active=1).all()
            federation  = Federation.query.filter_by(active=1).all()
            
            return render_template("home/" + template, segment=segment, data=events, age_group = age_group, category = category, discipline = discipline, level = level, federation = federation)
        
        if template == 'event.html':
            id = request.args.get('id', default = 1, type = int)
            if id > 0:
                event           = Events.query.filter_by(id=id).first()
                message_bytes   = base64.b64decode(event.picture)
                picture         = message_bytes.decode('ascii')
                event.image     = IMAGE_FOLDER_EVENTS + picture
                
                age_group       = getEventAgeGroup(id)
                category        = getEventCategory(id)
                discipline      = getEventDiscipline(id)
                level           = getEventLevel(id)
                federation      = getEventFederation(id)
                dancers         = Dancers.query.filter_by(id_user=current_user.id).all()
                applications    = getEventApplications(id)

                return render_template("home/" + template, segment=segment, data=event, age_group=age_group, category = category, discipline = discipline, dancers = dancers, level = level, federation = federation, applications=applications)
            else:
                return render_template('home/events.html', segment=segment)
        
        return render_template("home/" + template, segment=segment)
        
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

@blueprint.route('userData', methods=['POST'])
def userData():

    id_user = int(request.form.get('id_user'))
    if id_user > 0:
        user_data = User_data.query.filter_by(id_user=request.form.get('id_user')).first()
        if user_data:
            user_data.name      = request.form.get('name')
            user_data.lastname  = request.form.get('lastname')
            user_data.address   = request.form.get('address')
            user_data.city      = request.form.get('city')
            user_data.post_code = request.form.get('post_code')
            user_data.country   = request.form.get('country')
            user_data.studio    = request.form.get('studio')
            user_data.phone     = request.form.get('phone')
            db.session.commit()
        else:
            print(request.form)
            user_data = User_data(**request.form)
            db.session.add(user_data)
            db.session.commit()

    return redirect('settings.html')

@blueprint.route('addDancer', methods=['POST'])
def addDancer():
    dancer = Dancers(**request.form)

    file            = request.files['picture']
    filename        = secure_filename(file.filename)
    picture_name_e  = filename.encode('ascii')
    picture_name    = base64.b64encode(picture_name_e)
    dancer.id_user  = current_user.id
    dancer.picture  = picture_name

    file.save(os.path.join(UPLOAD_FOLDER_DANCERS, filename))

    db.session.add(dancer)
    db.session.commit()

    return redirect('dancers.html')

@blueprint.route('editDancer', methods=['POST'])
def editDancer():

    dancer = Dancers.query.filter_by(id=request.form.get('id')).first()

    dancer.name         = request.form.get('name')
    dancer.lastname     = request.form.get('lastname')
    dancer.birth_date   = request.form.get('birth_date')
    dancer.sex          = request.form.get('sex')

    file = request.files['picture']
    filename = secure_filename(file.filename)
    if filename != '':
        if dancer.picture != filename:
            picture_name_e  = filename.encode('ascii')
            picture_name    = base64.b64encode(picture_name_e)
            dancer.picture  = picture_name
            file.save(os.path.join(UPLOAD_FOLDER_DANCERS, filename))

    db.session.commit()

    return redirect('dancers.html')


@blueprint.route('deleteDancer',methods=['POST'])
def deleteDancer():
    id = request.form.get('id')
    dancer = Dancers.query.filter(Dancers.id == id).first()
    db.session.delete(dancer)
    db.session.commit()

    return redirect('dancers.html')

@blueprint.route('addEvent', methods=['POST'])
def addEvent():

    name            = request.form['name']
    event_from      = request.form['event_from']
    event_to        = request.form['event_to']
    picture         = ''
    description     = request.form['description']
    reference_date  = request.form['reference_date']
    active          = 1


    event = Events(name, event_from, event_to, picture, description, reference_date, active)
    file = request.files['picture']

    filename        = secure_filename(file.filename)
    picture_name_e  = filename.encode('ascii')
    picture_name    = base64.b64encode(picture_name_e)
    event.picture   = picture_name

    file.save(os.path.join(UPLOAD_FOLDER_EVENTS, filename))

    db.session.add(event)
    db.session.flush() 
    db.session.commit()

    id_event = event.id

    for d in request.form.getlist('discipline'):
        event_d = Event_discipline(id_event,d)
        db.session.add(event_d)
        db.session.commit()

    for ag in request.form.getlist('age_group'):
        event_ag = Event_age_group(id_event,ag)
        db.session.add(event_ag)
        db.session.commit()

    for c in request.form.getlist('category'):
        event_c = Event_category(id_event,c)
        db.session.add(event_c)
        db.session.commit()

    for l in request.form.getlist('level'):
        event_l = Event_level(id_event,l)
        db.session.add(event_l)
        db.session.commit()

    for f in request.form.getlist('federation'):
        event_f = Event_federation(id_event,f)
        db.session.add(event_f)
        db.session.commit()
    
    return redirect('events.html')

@blueprint.route('deleteEvent',methods=['POST'])
def deleteEvent():
    id = request.form.get('id')
    event = Events.query.filter(Events.id == id).first()
    event.active = 0
    db.session.commit()
    """
    db.session.delete(event)
    db.session.commit()

    event_d = Event_discipline.query.filter(Event_discipline.id_event == id).all()
    if event_d:
        db.session.delete(event_d)
        db.session.commit()

    event_ag = Event_age_group.query.filter(Event_age_group.id_event == id).all()
    if event_ag:
        db.session.delete(event_ag)
        db.session.commit()

    event_c = Event_category.query.filter(Event_category.id_event == id).all()
    if event_c:
        db.session.delete(event_c)
        db.session.commit()

    event_l = Event_level.query.filter(Event_level.id_event == id).all()
    if event_l:
        db.session.delete(event_l)
        db.session.commit()
    
    event_f = Event_federation.query.filter(Event_federation.id_event == id).all()
    if event_f:
        db.session.delete(event_f)
        db.session.commit()
    """

    return redirect('events.html')

@blueprint.route('addChoreography', methods=['POST'])
def addChoreography():

    now = datetime.now()
    id_event        = request.form.get('id_event')
    user_id         = current_user.id
    choreography    = request.form.get('choreography')
    choreograph     = request.form.get('choreograph')
    age_group       = request.form.get('age_group')
    discipline      = request.form.get('discipline')
    category        = request.form.get('category')
    federation      = request.form.get('federation')
    level           = request.form.get('level')
    audio           = ''
    song_author     = request.form.get('song_author')
    song_name       = request.form.get('song_name')
    entered_date    = now.strftime("%Y-%m-%d %H:%M:%S")


    application = Application(id_event, user_id, choreography, choreograph, age_group, discipline, category, federation, level, audio, song_author, song_name, entered_date)

    file                = request.files['audio']
    filename            = secure_filename(file.filename)
    audio_name_a        = filename.encode('ascii')
    audio_name          = base64.b64encode(audio_name_a)
    application.audio   = audio_name

    file.save(os.path.join(UPLOAD_FOLDER_AUDIO, filename))

    db.session.add(application)
    db.session.commit()

    id_application = application.id

    for d in request.form.getlist('dancers'):
        application_dancer = Application_dancer(id_application,d)
        db.session.add(application_dancer)
        db.session.commit()

    return redirect('event.html?id='+id_event)
    
@blueprint.route('editChoreography', methods=['POST'])
def editChoreography():

    id_event = request.form.get('id_event')
    application = Application.query.filter_by(id=request.form.get('id')).first()

    now = datetime.now()
    application.id_event        = id_event
    application.user_id         = current_user.id
    application.choreography    = request.form.get('choreography')
    application.choreograph     = request.form.get('choreograph')
    application.age_group       = request.form.get('age_group')
    application.discipline      = request.form.get('discipline')
    application.category        = request.form.get('category')
    application.federation      = request.form.get('federation')
    application.level           = request.form.get('level')
    application.song_author     = request.form.get('song_author')
    application.song_name       = request.form.get('song_name')

    file = request.files['audio']
    filename = secure_filename(file.filename)
    if filename != '':
        if application.audio != filename:
            audio_name_a        = filename.encode('ascii')
            audio_name          = base64.b64encode(audio_name_a)
            application.audio   = audio_name
            file.save(os.path.join(UPLOAD_FOLDER_AUDIO, filename))

    db.session.commit()

    return redirect('event.html?id='+id_event)

def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'

        return segment

    except:
        return None