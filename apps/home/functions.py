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

def getDancers():

    if current_user.role == 'user':
        dancers = Dancers.query.filter_by(id_user=current_user.id).all()
    else:
        dancers = Dancers.query.all()
    dancersAll = []
    for dancer in dancers:
        message_bytes   = base64.b64decode(dancer.picture)
        picture         = message_bytes.decode('ascii')
        dancer.image    = IMAGE_FOLDER_DANCERS + picture
        dancersAll.append(dancer)

    return dancersAll

def getEvents():

    events      = Events.query.filter_by(active=1).all()
    eventsAll   = []
    for event in events:
        message_bytes   = base64.b64decode(event.picture)
        picture         = message_bytes.decode('ascii')
        event.image     = IMAGE_FOLDER_EVENTS + picture
        eventsAll.append(event)

    return eventsAll


def getEventAgeGroup(id_event):

    age_group   = Event_age_group.query.filter_by(id_event=id_event).all()
    age_groups  = []
    for ag in age_group:
        
        age_group_temp   = Age_group.query.filter_by(id=ag.id_age_group).first()
        age_group_ag = {}
        age_group_ag["id"]          = age_group_temp.id
        age_group_ag["name"]        = age_group_temp.name
        age_group_ag["min_years"]   = age_group_temp.min_years
        age_group_ag["max_years"]   = age_group_temp.max_years
        age_group_ag["use_average"] = age_group_temp.use_average
        age_groups.append(age_group_ag)

    return age_groups

def getEventCategory(id_event):

    category   = Event_category.query.filter_by(id_event=id_event).all()
    categorys = []
    for c in category:
        category_temp   = Category.query.filter_by(id=c.id_category).first()
        category_c = {}
        category_c["id"]            = category_temp.id
        category_c["name"]          = category_temp.name
        category_c["min_dancers"]   = category_temp.min_dancers
        category_c["max_dancers"]   = category_temp.max_dancers
        category_c["price"]         = category_temp.price
        categorys.append(category_c)

    return categorys

def getEventDiscipline(id_event):

    discipline   = Event_discipline.query.filter_by(id_event=id_event).all()
    disciplines = []
    for d in discipline:
        discipline_temp   = Discipline.query.filter_by(id=d.id_discipline).first()
        discipline_d = {}
        discipline_d["id"]              = discipline_temp.id
        discipline_d["discipline"]      = discipline_temp.discipline
        discipline_d["use_ref_date"]    = discipline_temp.use_ref_date
        disciplines.append(discipline_d)

    return disciplines

def getEventLevel(id_event):

    level   = Event_level.query.filter_by(id_event=id_event).all()
    levels = []
    for l in level:
        level_temp   = Level.query.filter_by(id=l.id_level).first()
        level_l = {}
        level_l["id"]   = level_temp.id
        level_l["name"] = level_temp.name
        levels.append(level_l)

    return levels

def getEventFederation(id_event):

    federation   = Event_federation.query.filter_by(id_event=id_event).all()
    federations = []
    for f in federation:
        federation_temp   = Federation.query.filter_by(id=f.id_federation).first()
        federation_f = {}
        federation_f["id"]      = federation_temp.id
        federation_f["name"]    = federation_temp.name
        federations.append(federation_f)
    return federations

def getEventApplications(id_event):

    if current_user.role == 'user':
        applications    = Application.query.filter_by(user_id=current_user.id,id_event = id_event).order_by(Application.entered_date).all()
    else:
        applications    = Application.query.filter_by(id_event = id_event).order_by(Application.entered_date).all()
        
    applicationsAll = []
    for a in applications:
        age_group_a   = Age_group.query.filter_by(id=a.age_group).first()
        category_a    = Category.query.filter_by(id=a.category).first()
        discipline_a  = Discipline.query.filter_by(id=a.discipline).first()
        level_a       = Level.query.filter_by(id=a.level).first()
        federation_a  = Federation.query.filter_by(id=a.federation).first()
        a.age_group_name    = age_group_a.name
        a.category_name     = category_a.name
        a.discipline_name   = discipline_a.discipline
        a.level_name        = level_a.name
        a.federation_name   = federation_a.name

        message_bytes_a = base64.b64decode(a.audio)
        audio = message_bytes_a.decode('ascii')
        a.song = AUDIO_FOLDER + audio
        
        date_temp = datetime.strptime(a.entered_date, '%Y-%m-%d %H:%M:%S')
        a.entered_date = date_temp.strftime("%d.%m.%Y %H:%M:%S")
        a.dancers = []
        app_dancers = Application_dancer.query.filter_by(id_application=a.id).all()
        application_dancers = []
        for ad in app_dancers:
            ad_temp   = Dancers.query.filter_by(id=ad.id_dancer).first()
            ad_a = {}
            ad_a["id"]          = ad_temp.id
            ad_a["name"]        = ad_temp.name
            ad_a["lastname"]    = ad_temp.lastname
            ad_a["birth_date"]  = ad_temp.birth_date

            message_bytes = base64.b64decode(ad_temp.picture)
            picture = message_bytes.decode('ascii')

            ad_a["picture"] = IMAGE_FOLDER_DANCERS + picture
            ad_a["sex"]     = ad_temp.sex
            application_dancers.append(ad_a)
        a.dancers = (application_dancers)
        applicationsAll.append(a)
    return applicationsAll