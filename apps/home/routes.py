# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import base64
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash, jsonify, session, Markup, json
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import login_required, LoginManager, current_user
from jinja2 import *
from apps.home.models import *
from apps.home.functions import *
from apps.authentication.models import *
from apps import db
from werkzeug.utils import secure_filename
from base64 import b64encode
from datetime import datetime, timedelta
import os
import json
import operator

from apps.authentication.util import hash_pass

UPLOAD_FOLDER_DANCERS = 'apps/static/assets/images/dancers/'
IMAGE_FOLDER_DANCERS = '/static/assets/images/dancers/'

UPLOAD_FOLDER_EVENTS = 'apps/static/assets/images/events/'
IMAGE_FOLDER_EVENTS = '/static/assets/images/events/'

UPLOAD_FOLDER_AUDIO = 'apps/static/assets/audio/'
AUDIO_FOLDER = '/static/assets/audio/'

@blueprint.route('/index')
@login_required
def index():
    
    user_data = User_data.query.filter_by(id_user=current_user.id).first()
    if user_data is None and current_user.role == 'user':
        user_data = User_data.query.filter_by(id_user=current_user.id).first()
        return render_template("home/settings.html", data=user_data)
    
        
    else:
        events      = getEvents()
        age_group   = Age_group.query.filter_by(active=1).all()
        category    = Category.query.filter_by(active=1).all()
        discipline  = Discipline.query.filter_by(active=1).all()
        level       = Level.query.filter_by(active=1).all()
        federation  = Federation.query.filter_by(active=1).all()
        judges      = Judges.query.all()
        grades      = Grades.query.all()

        return render_template('home/events.html', segment='events', data=events, age_group = age_group, category = category, discipline = discipline, level = level, federation = federation, judges = judges, grades = grades)
        


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:
        
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        if template == 'chat.html':
            name = 'test1'
            room = 'test2'
            return render_template("home/chat.html", name=name, room=room)
 
        if template == 'judging.html':


            return render_template('home/judging.html', segment=segment)
        
        if template == 'judges.html':
            judges = getJudges()

            return render_template('home/judges.html', segment=segment, data = judges)

        if template == 'event_ordering.html':
            id = request.args.get('id', default = 0, type = int)
            id_head = request.args.get('id_head', default = 0, type = int)
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

                activeCategorys = getEventActiveCategorys(id, id_head)
                orderingHead    = getEventOrderingHeads(id)

                print(activeCategorys)

                return render_template("home/" + template, segment=segment, data=event, age_group=age_group, category = category, discipline = discipline, dancers = dancers, level = level, federation = federation, applications=applications, activeCategorys=activeCategorys, orderingHead=orderingHead)
            else:
                return render_template('home/events.html', segment=segment)
        
        if template == 'event_order_list.html':
            id = request.args.get('id', default = 0, type = int)
            id_head = request.args.get('id_head', default = 0, type = int)
            if id > 0 and id_head > 0:
                event           = Events.query.filter_by(id=id).first()
                #message_bytes   = base64.b64decode(event.picture)
                #picture         = message_bytes.decode('ascii')
                #event.image     = IMAGE_FOLDER_EVENTS + picture
                
                age_group       = getEventAgeGroup(id)
                category        = getEventCategory(id)
                discipline      = getEventDiscipline(id)
                level           = getEventLevel(id)
                federation      = getEventFederation(id)
                dancers         = Dancers.query.filter_by(id_user=current_user.id).all()
                applications    = getEventApplications(id)
                activeCategorys = getEventActiveCategorysByHead(id, id_head)
                listHead        = activeListHead(id_head)
                
            
                return render_template("home/" + template, segment=segment, data=event, age_group=age_group, category = category, discipline = discipline, dancers = dancers, level = level, federation = federation, applications=applications, activeCategorys=activeCategorys, listHead=listHead)
            else:
                return render_template('home/events.html', segment=segment)
            
        if template == 'event_list_grades.html':
            id = request.args.get('id', default = 0, type = int)
            id_head = request.args.get('id_head', default = 0, type = int)
            if id > 0 and id_head > 0:
                event           = Events.query.filter_by(id=id).first()
                #message_bytes   = base64.b64decode(event.picture)
                #picture         = message_bytes.decode('ascii')
                #event.image     = IMAGE_FOLDER_EVENTS + picture
                
                age_group       = getEventAgeGroup(id)
                category        = getEventCategory(id)
                discipline      = getEventDiscipline(id)
                level           = getEventLevel(id)
                federation      = getEventFederation(id)
                dancers         = Dancers.query.filter_by(id_user=current_user.id).all()
                applications    = getEventApplications(id)
                activeCategorys = getEventActiveCategorysByHead(id, id_head)
                listHead        = activeListHead(id_head)
            
                return render_template("home/" + template, segment=segment, data=event, age_group=age_group, category = category, discipline = discipline, dancers = dancers, level = level, federation = federation, applications=applications, activeCategorys=activeCategorys, listHead=listHead)
            else:
                return render_template('home/events.html', segment=segment)
            
        if template == 'event_list_live.html':
            id = request.args.get('id', default = 0, type = int)
            id_head = request.args.get('id_head', default = 0, type = int)
            if id > 0 and id_head > 0:
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
                activeCategorys = getEventActiveCategorysByHead(id, id_head)
                listHead        = activeListHead(id_head)
                grades          = getEventGrade(id) 
                judges          = getEventJudges(id) 

                return render_template("home/" + template, segment=segment, data=event, age_group=age_group, category = category, discipline = discipline, dancers = dancers, level = level, federation = federation, applications=applications, activeCategorys=activeCategorys, listHead=listHead, judges = judges, grades = grades)
            else:
                return render_template('home/events.html', segment=segment)
            
        if template == 'event_list_results.html':
            id = request.args.get('id', default = 0, type = int)
            id_head = request.args.get('id_head', default = 0, type = int)
            if id > 0 and id_head > 0:
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
                activeCategorys = getEventActiveCategorysByHead(id, id_head)
                listHead        = activeListHead(id_head)
                grades          = getEventGrade(id) 
                judges          = getEventJudges(id) 

                return render_template("home/" + template, segment=segment, data=event, age_group=age_group, category = category, discipline = discipline, dancers = dancers, level = level, federation = federation, applications=applications, activeCategorys=activeCategorys, listHead=listHead, judges = judges, grades = grades)
            else:
                return render_template('home/events.html', segment=segment)

        if template == 'settings.html':
            user_data = User_data.query.filter_by(id_user=current_user.id).first()

            return render_template("home/" + template, segment=segment, data=user_data)
        
        if template == 'dancers.html':
            dancers = getDancers()

            return render_template("home/" + template, segment=segment, data=dancers)
        
        if template == 'event_dancers.html':
            id = request.args.get('id', default = 1, type = int)
            if id > 0:
                dancers = getEventDancers(id)

            return render_template("home/" + template, segment=segment, data=dancers)
        
        if template == 'events.html':

            user_data = User_data.query.filter_by(id_user=current_user.id).first()
            if user_data is None and current_user.role == 'user':
                user_data = User_data.query.filter_by(id_user=current_user.id).first()
                return render_template("home/settings.html", data=user_data)
            else:
                events      = getEvents()
                age_group   = Age_group.query.filter_by(active=1).all()
                category    = Category.query.filter_by(active=1).all()
                discipline  = Discipline.query.filter_by(active=1).all()
                level       = Level.query.filter_by(active=1).all()
                federation  = Federation.query.filter_by(active=1).all()
                judges      = Judges.query.all()
                grades      = Grades.query.all()
                
                return render_template("home/" + template, segment=segment, data=events, age_group = age_group, category = category, discipline = discipline, level = level, federation = federation, judges = judges, grades = grades)
        
        if template == 'configuration.html':
            age_group   = Age_group.query.filter_by(active=1).all()
            category    = Category.query.filter_by(active=1).all()
            discipline  = Discipline.query.filter_by(active=1).all()
            level       = Level.query.filter_by(active=1).all()
            federation  = Federation.query.filter_by(active=1).all()
            grades      = Grades.query.all()
            #print(grades)
            return render_template("home/" + template, segment=segment, age_group = age_group, category = category, discipline = discipline, level = level, federation = federation, grades = grades)
        
        if template == 'invoice.html':
            id = request.args.get('id_event', default = 1, type = int)
            if id > 0:
                user_data       = User_data.query.filter_by(id_user=current_user.id).first()
                invoice_data    = getInvoiceData(id)
                print(invoice_data)
                check_invoice = Event_invoice.query.filter_by(id_user=current_user.id, id_event = id).first()
                if check_invoice:
                    invoice_number = check_invoice.invoice_number
                    invoice_year   = check_invoice.year
                else:
                    
                    now = datetime.now()
                    invoice_number_last = Event_invoice.query.filter_by(year = now.year).order_by(desc(Event_invoice.invoice_number)).first()
                    print(invoice_number_last)
                    if invoice_number_last:
                        event_invoice = Event_invoice(id, current_user.id, (invoice_number_last.invoice_number + 1), now.year)
                    else:
                        event_invoice = Event_invoice(id, current_user.id, 1, now.year)

                    db.session.add(event_invoice)
                    db.session.flush() 
                    db.session.commit()

                    invoice_number = event_invoice.invoice_number
                    invoice_year   = event_invoice.year
                    #invoice_number = 0
                    #invoice_year   = 0
                    
                return render_template('home/invoice.html', segment=segment, user_data = user_data, invoice_data = invoice_data, invoice_number = invoice_number, invoice_year = invoice_year)
            return render_template('home/events.html', segment=segment)

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
            user_data = User_data(**request.form)
            db.session.add(user_data)
            db.session.commit()

    return redirect('settings.html')

@blueprint.route('addDancer', methods=['POST'])
def addDancer():
    dancer = Dancers(**request.form)
    dancer.id_user  = current_user.id
    file            = request.files['picture']
    if file:
        filename        = secure_filename(file.filename)
        picture_name_e  = filename.encode('ascii')
        picture_name    = base64.b64encode(picture_name_e)
        
        dancer.picture  = picture_name

        file.save(os.path.join(UPLOAD_FOLDER_DANCERS, filename))

    db.session.add(dancer)
    db.session.commit()

    return redirect('dancers.html')

@blueprint.route('newOrderingList', methods=['POST'])
def newOrderingList():
    orderingList = Event_category_ordering_head(**request.form)

    db.session.add(orderingList)
    db.session.commit()

    id_event = request.form.get('id_event')

    return redirect('event_ordering.html?id='+id_event)




@blueprint.route('eventHeadLive', methods=['POST'])
def eventHeadLive():

    
    id_event        = request.form.get('id_event')
    id_head         = request.form.get('id_head')
    id_discipline   = request.form.get('id_discipline')
    id_age_group    = request.form.get('id_age_group')
    id_category     = request.form.get('id_category')
    id_level        = request.form.get('id_level')

    event_category_ordering = Event_category_ordering.query.all()

    application = Application.query.filter_by(id_event=id_event).all()

    if application:
        for a in application:
            a.live = 0
            db.session.commit()

    active_eco = 0

    if event_category_ordering:
        for eco in event_category_ordering:
            if int(eco.id_head) == int(id_head) and int(eco.id_discipline) == int(id_discipline) and int(eco.id_age_group) == int(id_age_group) and int(eco.id_category) == int(id_category) and int(eco.id_level) == int(id_level):
                active_eco = int(eco.id)
                eco.live = 1
                db.session.commit()
            else:
                eco.live = 0
                db.session.commit()

    return redirect('event_list_live.html?id='+id_event+'&id_head='+id_head+'#orderList'+str(id_discipline)+'_'+str(id_age_group)+'_'+str(id_category)+'_'+str(id_level))


@blueprint.route('removeLive', methods=['POST'])
def removeLive():

    id_head         = request.form.get('id_head')
    id_event        = request.form.get('id_event')

    print(id_head)
    print(id_event)
    application = Application.query.all()

    if application:
        for a in application:
            a.live = 0
            db.session.commit()

    event_category_ordering = Event_category_ordering.query.all()
    if event_category_ordering:
        for eco in event_category_ordering:
            eco.live = 0
            db.session.commit()

    return redirect('event_list_live.html?id='+id_event+'&id_head='+id_head)

@blueprint.route('eventHeadLiveChoreography', methods=['POST'])
def eventHeadLiveChoreography():

    
    id_event        = request.form.get('id_event')
    id_head         = request.form.get('id_head')
    id              = request.form.get('id')

    application = Application.query.filter_by(id_event=id_event).all()

    if application:
        for a in application:
            if int(a.id) == int(id):
                a.live = 1
                db.session.commit()
            else:
                a.live = 0
                db.session.commit()

    return redirect('event_list_live.html?id='+id_event+'&id_head='+id_head+'#app_'+id)


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

@blueprint.route('deleteChoreography',methods=['POST'])
def deleteChoreography():
    id = request.form.get('id')
    application = Application.query.filter(Application.id == id).first()
    id_event = application.id_event
    db.session.delete(application)
    db.session.commit()

    application_dancers = Application_dancer.query.filter(Application_dancer.id_application == id).all()
    for ad in application_dancers:
        db.session.delete(ad)
        db.session.commit()


    return redirect('event.html?id='+str(id_event))


@blueprint.route('addJudge', methods=['POST'])
def addJudge():
    name        = request.form['name']
    lastname    = request.form['lastname']
    username    = request.form['username']
    password    = request.form['password']
    email       = request.form['email']

    user = Users(**request.form)
    user.role = 'judge'
    db.session.add(user)
    db.session.flush() 
    db.session.commit()

    id_user = user.id

    judge = Judges(id_user, name, lastname, username, email)
    db.session.add(judge)
    db.session.commit()

    return redirect('judges.html')

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
    if file:
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
    live            = 0

    application = Application(id_event, user_id, choreography, choreograph, age_group, discipline, category, federation, level, audio, song_author, song_name, entered_date, live)

    file                = request.files['audio']
    if file:
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

@blueprint.route('editOrdering',methods=['POST'])
def editOrdering():

    id_head = request.form.get('id_head')
    id_event = request.form.get('id_event')
    
    event_category_ordering = Event_category_ordering.query.filter(Event_category_ordering.id_head == id_head).all()
    for eco in event_category_ordering:
        db.session.delete(eco)
        db.session.commit()

    #data_s = request.form.getlist('row_s')
    data_ag = request.form.getlist('row_ag')
    data_c = request.form.getlist('row_c')
    data_d = request.form.getlist('row_d')
    data_l = request.form.getlist('row_l')
    #data_o = request.form.getlist('row_o')
    lenght = len(data_l)

    counter = 1
    for x in range(0, lenght):
        event_category_ordering = Event_category_ordering(id_head,data_ag[int(x)], data_d[int(x)], data_c[int(x)], data_l[int(x)], counter, 0)
        db.session.add(event_category_ordering)
        db.session.commit()
        counter += 1

    return redirect('event_ordering.html?id='+id_event)

@blueprint.route('addAgeGroup', methods=['POST'])
def addAgeGroup():
    age_group = Age_group()

    age_group.name          = request.form.get('name')
    age_group.min_years     = request.form.get('min_years')
    age_group.max_years     = request.form.get('max_years')
    age_group.active        = 1

    if request.form.get('use_average') == 'on':
        age_group.use_average   = 1
    else:
        age_group.use_average   = 0
    
    db.session.add(age_group)
    db.session.commit()

    return redirect('configuration.html?tab=age_group')

@blueprint.route('addCategory', methods=['POST'])
def addCategory():
    category = Category()

    category.name           = request.form.get('name')
    category.min_dancers    = request.form.get('min_dancers')
    category.max_dancers    = request.form.get('max_dancers')
    category.time_lenght    = request.form.get('time_lenght_hour') + ":" + request.form.get('time_lenght_min')
    category.price          = request.form.get('price')
    category.active         = 1

    db.session.add(category)
    db.session.commit()

    return redirect('configuration.html?tab=category')

@blueprint.route('addDiscipline', methods=['POST'])
def addDiscipline():
    discipline = Discipline()

    discipline.discipline   = request.form.get('discipline')
    discipline.active       = 1
    if request.form.get('use_ref_date') == 'on':
        discipline.use_ref_date   = 1
    else:
        discipline.use_ref_date   = 0
    
    db.session.add(discipline)
    db.session.commit()

    return redirect('configuration.html?tab=discipline')

@blueprint.route('addLevel', methods=['POST'])
def addLevel():
    level = Level()

    level.name      = request.form.get('name')
    level.active    = 1

    db.session.add(level)
    db.session.commit()

    return redirect('configuration.html?tab=level')

@blueprint.route('addGrade', methods=['POST'])
def addGrade():
    grades = Grades()

    grades.name         = request.form.get('name')
    grades.max_number   = request.form.get('max_number')

    db.session.add(grades)
    db.session.commit()

    return redirect('configuration.html?tab=grades')

@blueprint.route('addFederation', methods=['POST'])
def addFederation():
    federation = Federation()

    federation.name      = request.form.get('name')
    federation.active    = 1

    db.session.add(federation)
    db.session.commit()

    return redirect('configuration.html?tab=federation')

@blueprint.route('deleteFederation', methods=['POST'])
def deleteFederation():
    id = request.form.get('id')
    federation = Federation().query.filter(Federation.id == id).first()

    federation.active = 0
    db.session.commit()

    return redirect('configuration.html')

@blueprint.route('deleteLevel', methods=['POST'])
def deleteLevel():
    id = request.form.get('id')
    level = Level().query.filter(Level.id == id).first()

    level.active = 0
    db.session.commit()

    return redirect('configuration.html?tab=level')

@blueprint.route('deleteDiscipline', methods=['POST'])
def deleteDiscipline():
    id = request.form.get('id')
    discipline = Discipline().query.filter(Discipline.id == id).first()

    discipline.active = 0
    db.session.commit()

    return redirect('configuration.html?tab=discipline')

@blueprint.route('deleteCategory', methods=['POST'])
def deleteCategory():
    id = request.form.get('id')
    category = Category().query.filter(Category.id == id).first()

    category.active = 0
    db.session.commit()

    return redirect('configuration.html?tab=category')

@blueprint.route('deleteAgeGroup', methods=['POST'])
def deleteAgeGroup():
    id = request.form.get('id')
    age_group = Age_group().query.filter(Age_group.id == id).first()

    age_group.active = 0
    db.session.commit()

    return redirect('configuration.html?tab=age_group')

@blueprint.route('judge_live', methods=['POST'])
def judge_live():
    judge = request.get_json()

    judge_id = judge['judge'] 

    data = getJudgingData()

    return json.dumps(data)

@blueprint.route('judge_live_organizer', methods=['POST'])
def judge_live_organizer():
    head = request.get_json()

    id_head = head['id_head'] 

    data = getJudgingDataOrganizer(id_head)

    return json.dumps(data)

@blueprint.route('judge_grade', methods=['POST'])
def judge_grade():
    grades = request.form['grades']

    id_judge = request.form['id_judge']
    id_application = request.form['id_application']

    gradesObject = json.loads(grades)
    for i in gradesObject:
        grade = gradesObject[i]
        id_grade = i

        application_judging = Application_judging.query.filter(
            Application_judging.id_judge == id_judge,
            Application_judging.id_application == id_application,
            Application_judging.id_grade == id_grade).first()
        if application_judging:
            application_judging.grade = grade
            db.session.commit()
        else:
            application_judging = Application_judging(id_application, id_judge, id_grade, grade)
            db.session.add(application_judging)
            db.session.commit()

    return ''

def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'events'

        return segment

    except:
        return None