# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
import base64
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash, jsonify, session, Markup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import login_required, LoginManager, current_user
from jinja2 import TemplateNotFound, Template
from apps.home.models import *
from apps.authentication.models import Users
from apps import db, login_manager
from werkzeug.utils import secure_filename
from base64 import b64encode
from datetime import datetime, date
from operator import itemgetter
import os
import json

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import inspect

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
        dancer.image        = ''
        if dancer.picture is not None:
            message_bytes   = base64.b64decode(dancer.picture)
            picture         = message_bytes.decode('ascii')
            dancer.image    = IMAGE_FOLDER_DANCERS + picture
        dancersAll.append(dancer)

    return dancersAll

def getEvents():

    events      = Events.query.filter_by(active=1).all()
    eventsAll   = []
    for event in events:
        #message_bytes   = base64.b64decode(event.picture)
        #picture         = message_bytes.decode('ascii')
        #event.image     = IMAGE_FOLDER_EVENTS + picture
        event.image = ''
        ecoh  = Event_category_ordering_head.query.filter_by(id_event=event.id).all()
        event.list = ecoh
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
        category_c["time_lenght"]   = category_temp.time_lenght
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
        
        level_a       = Level.query.filter_by(id=a.level).first()
        
        a.age_group_name    = age_group_a.name
        a.category_name     = category_a.name
        if a.discipline:
            discipline_a  = Discipline.query.filter_by(id=a.discipline).first()
            a.discipline_name   = discipline_a.discipline
        a.level_name        = level_a.name
        a.federation_name   = ''
        if a.federation:
            federation_a        = Federation.query.filter_by(id=a.federation).first()
            a.federation_name   = federation_a.name


        studio = User_data.query.filter_by(id_user=a.user_id).first()

        if studio is not None:
            a.studio    = studio.studio
        else:
            a.studio    = ''

        if a.audio is not None:
            message_bytes_a = base64.b64decode(a.audio)
            audio = message_bytes_a.decode('ascii')
            a.song = AUDIO_FOLDER + audio
        total_grade = 0
        position = 0
        position_count = 0
        a.grades = []
        app_judging = Application_judging.query.filter_by(id_application=a.id).all()
        total_grade_by_sudac = {}
        total_position_by_sudac = {}
        grade_sudac_remove = []
        position_sudac_remove = []
        if app_judging:
            for aj in app_judging:
                judge   = Judges.query.filter_by(id_user=aj.id_judge).first()
                aj_b = {}
                aj_b['judge']       = judge.id
                aj_b['grade']       = aj.grade
                aj_b['id_grade']    = aj.id_grade
                grade   = Grades.query.filter_by(id=aj.id_grade).first()
                if grade.type == 'basic':
                    total_grade = total_grade + float(aj.grade)
                if grade.type == 'penalty':
                    total_grade = total_grade + float(aj.grade)
                if grade.type == 'position':
                    position = position + float(aj.grade)
                    position_count = position_count + 1
                    total_position_by_sudac[aj.id_judge] = float(aj.grade)

                if total_grade_by_sudac.get(aj.id_judge) == None:
                    total_grade_by_sudac[aj.id_judge] = 0
                else:
                    if grade.type == 'basic':
                        total_grade_by_sudac[aj.id_judge] = total_grade_by_sudac[aj.id_judge] + float(aj.grade)
                    if grade.type == 'penalty':
                        total_grade_by_sudac[aj.id_judge] = total_grade_by_sudac[aj.id_judge] + float(aj.grade)

                a.grades.append(aj_b)
        a.judging_grade = total_grade
        total_grade_by_sudac = dict(sorted(total_grade_by_sudac.items(), key=lambda item: item[1]))
        total_position_by_sudac = dict(sorted(total_position_by_sudac.items(), key=lambda x: x[1]))
        {k: v for k, v in sorted(total_grade_by_sudac.items(), key=lambda item: item[1])}
        if len(total_grade_by_sudac) > 2:
            l = 0
            for key, value in total_grade_by_sudac.items():
                if l == 0:
                    total_grade = total_grade - value
                    judge   = Judges.query.filter_by(id_user=key).first()
                    grade_sudac_remove.append(judge.id)
                if l == (len(total_grade_by_sudac) - 1):
                    total_grade = total_grade - value
                    judge   = Judges.query.filter_by(id_user=key).first()
                    grade_sudac_remove.append(judge.id)
                l += 1
        a.judging_grade_twirling = total_grade
        if position_count > 0 :
            a.position = position / position_count

            if position_count > 2:
                l = 0
                for key, value in total_position_by_sudac.items():
                    if l == 0:
                        position = position - value
                        position_count = position_count - 1
                        judge   = Judges.query.filter_by(id_user=key).first()
                        position_sudac_remove.append(judge.id)
                    if l == (len(total_position_by_sudac) - 1):
                        position = position - value
                        position_count = position_count - 1
                        judge   = Judges.query.filter_by(id_user=key).first()
                        position_sudac_remove.append(judge.id)
                    l += 1
            a.position_twirling = position / position_count

        else:
            a.position = 100
            a.position_twirling = 100
        date_temp = datetime.strptime(a.entered_date, '%Y-%m-%d %H:%M:%S')
        
        a.position_sudac_remove = position_sudac_remove
        a.grade_sudac_remove = grade_sudac_remove

        a.entered_date = date_temp.strftime("%d.%m.%Y %H:%M:%S")
        a.dancers = []
        app_dancers = Application_dancer.query.filter_by(id_application=a.id).all()
        application_dancers = []

        today = datetime.today()
        total_age_average = 0
        total_dancers = 0
        if app_dancers:
            for ad in app_dancers:
                total_dancers += 1
                
                ad_temp   = Dancers.query.filter_by(id=ad.id_dancer).first()
                if ad_temp is not None:
                    if ad_temp.birth_date is not None:
                        ad_a = {}
                        ad_a["id"]          = ad_temp.id
                        ad_a["name"]        = ad_temp.name
                        ad_a["lastname"]    = ad_temp.lastname
                        ad_a["birth_date"]  = ad_temp.birth_date

                        dancer_birth_date = datetime.strptime(ad_temp.birth_date, '%Y-%m-%d')
                        age_difference = today - dancer_birth_date
                        age_difference_number  = age_difference.days / 365
                        total_age_average = total_age_average + age_difference_number

                        ad_a["picture"] = ''
                        if ad_temp.picture:
                            message_bytes = base64.b64decode(ad_temp.picture)
                            picture = message_bytes.decode('ascii')
                            ad_a["picture"] = IMAGE_FOLDER_DANCERS + picture
                        ad_a["sex"]     = ad_temp.sex
                        application_dancers.append(ad_a)
            a.dancers = (application_dancers)

            age_average = total_age_average / total_dancers

            a.age_average = age_average
        applicationsAll.append(a)

    

    return applicationsAll

def getEventActiveCategorys(id_event, id_head = 0):

    applications    = Application.query.filter_by(id_event = id_event).order_by(Application.entered_date).all()
        
    distinctCombinations = []
    for a in applications:
        dc = {}
        if a.age_group:
            age_group_a   = Age_group.query.filter_by(id=a.age_group).first()
            dc["age_group"]         = a.age_group
            dc["age_group_name"]    = age_group_a.name
        else:
            dc["age_group"]         = 0
            dc["age_group_name"]    = ''

        if a.category:
            category_a    = Category.query.filter_by(id=a.category).first()
            dc["category"]      = a.category
            dc["category_name"] = category_a.name
        else:
            dc["category"]      = 0
            dc["category_name"] = ''
        if a.discipline:
            discipline_a  = Discipline.query.filter_by(id=a.discipline).first()
            dc["discipline"]        = a.discipline
            dc["discipline_name"]   = discipline_a.discipline
        else:
            dc["discipline"]        = 0
            dc["discipline_name"]   = ''

        if a.level:
            level_a       = Level.query.filter_by(id=a.level).first()
            dc["level"]         = a.level
            dc["level_name"]    = level_a.name
        else:
            dc["level"]         = 0
            dc["level_name"]    = ''


        dc["list"]              = ''
        dc["ordering"]          = 0
        dc["live"]              = 0

        if(id_head > 0):
            ecoh  = Event_category_ordering_head.query.filter_by(id=id_head).first()
            event_category_ordering  = Event_category_ordering.query.filter_by(id_head=id_head,id_age_group=a.age_group,id_discipline=a.discipline,id_category=a.category,id_level=a.level).first()
            if event_category_ordering is not None:
                dc["ordering"]  = event_category_ordering.eo
                dc["live"]      = event_category_ordering.live
            
            ecoh  = Event_category_ordering_head.query.filter_by(id_event=id_event).all()

            for e in ecoh:
                event_category_ordering  = Event_category_ordering.query.filter_by(id_head=e.id,id_age_group=a.age_group,id_discipline=a.discipline,id_category=a.category,id_level=a.level).first()
                if event_category_ordering is not None:
                    dc["list"]  = dc["list"] + e.date + ' / ' + e.time
                    dc["live"]  = event_category_ordering.live
        else:
            ecoh  = Event_category_ordering_head.query.filter_by(id_event=id_event).all()

            for e in ecoh:
                event_category_ordering  = Event_category_ordering.query.filter_by(id_head=e.id,id_age_group=a.age_group,id_discipline=a.discipline,id_category=a.category,id_level=a.level).first()
                if event_category_ordering is not None:
                    dc["ordering"]  = event_category_ordering.eo
                    dc["list"]      = dc["list"] + e.date + ' / ' + e.time
                    dc["live"]      = event_category_ordering.live

        if dc not in distinctCombinations:
            distinctCombinations.append(dc)
    distinctCombinations.sort(key=lambda x: x.get('ordering'))

    return distinctCombinations

def getEventActiveCategorysByHead(id_event, id_head):

    applications    = Application.query.filter_by(id_event = id_event).order_by(Application.entered_date).all()
        
    distinctCombinations = []
    for a in applications:
        exist = 0
        dc = {}
        if a.age_group:
            age_group_a   = Age_group.query.filter_by(id=a.age_group).first()
            dc["age_group"]         = a.age_group
            dc["age_group_name"]    = age_group_a.name
        else:
            dc["age_group"]         = 0
            dc["age_group_name"]    = ''

        if a.category:
            category_a    = Category.query.filter_by(id=a.category).first()
            dc["category"]      = a.category
            dc["category_name"] = category_a.name
        else:
            dc["category"]      = 0
            dc["category_name"] = ''
        if a.discipline:
            discipline_a  = Discipline.query.filter_by(id=a.discipline).first()
            dc["discipline"]        = a.discipline
            dc["discipline_name"]   = discipline_a.discipline
        else:
            dc["discipline"]        = 0
            dc["discipline_name"]   = ''

        if a.level:
            level_a       = Level.query.filter_by(id=a.level).first()
            dc["level"]         = a.level
            dc["level_name"]    = level_a.name
        else:
            dc["level"]         = 0
            dc["level_name"]    = ''


        dc["list"]              = ''
        dc["ordering"]          = 0
        dc["live"]              = 0

        ecoh  = Event_category_ordering_head.query.filter_by(id=id_head).first()
        event_category_ordering  = Event_category_ordering.query.filter_by(id_head=id_head,id_age_group=a.age_group,id_discipline=a.discipline,id_category=a.category,id_level=a.level).first()
        if event_category_ordering is not None:
            dc["ordering"]  = event_category_ordering.eo
            dc["live"]      = event_category_ordering.live
            exist = 1
        
        ecoh  = Event_category_ordering_head.query.filter_by(id_event=id_event).all()

        if dc not in distinctCombinations and exist == 1:
           
            distinctCombinations.append(dc)

    distinctCombinations.sort(key=lambda x: x.get('ordering'))

    return distinctCombinations

def getEventOrderingHeads(id_event):

    ecoh  = Event_category_ordering_head.query.filter_by(id_event=id_event).all()

    return ecoh

def activeListHead(id_head):
    
    ecoh  = Event_category_ordering_head.query.filter_by(id=id_head).first()

    return ecoh


def getJudges():
    judges   = Judges.query.all()

    return judges

def getJudgingData():

    output = {}
    eco             = Event_category_ordering.query.filter_by(live=1).first()
    if eco:
        ecoh            = Event_category_ordering_head.query.filter_by(id=eco.id_head).first()
        event_grades    = Event_grades.query.filter_by(id_event = ecoh.id_event).all()

        if eco.id_age_group:
            age_group_a   = Age_group.query.filter_by(id=eco.id_age_group).first()
            output["id_age_group"]      = eco.id_age_group
            output["age_group_name"]    = age_group_a.name
        else:
            output["id_age_group"]         = 0
            output["age_group_name"]    = ''

        if eco.id_category:
            category_a    = Category.query.filter_by(id=eco.id_category).first()
            output["id_category"]   = eco.id_category
            output["category_name"] = category_a.name
        else:
            output["id_category"]   = 0
            output["category_name"] = ''
        if eco.id_discipline:
            discipline_a  = Discipline.query.filter_by(id=eco.id_discipline).first()
            output["id_discipline"]     = eco.id_discipline
            output["discipline_name"]   = discipline_a.discipline
        else:
            output["id_discipline"]        = 0
            output["discipline_name"]   = ''

        if eco.id_level:
            level_a       = Level.query.filter_by(id=eco.id_level).first()
            output["id_level"]      = eco.id_level
            output["level_name"]    = level_a.name
        else:
            output["id_level"]      = 0
            output["level_name"]    = ''


        applications    = Application.query.filter_by(id_event = ecoh.id_event, age_group = eco.id_age_group , discipline = eco.id_discipline , category = eco.id_category, level = eco.id_level).order_by(Application.entered_date).all()
    
        output['applications'] = []
        output['event_grades'] = []
        for a in applications:
            temp_a = {}
            temp_a['id'] = a.id
            temp_a['choreography'] = a.choreography
            temp_a['live'] = a.live
            output['applications'].append(temp_a)
        for eg in event_grades:
            grade = Grades.query.filter_by(id=eg.id_grades).first()
            temp_eg = {}
            temp_eg['id'] = grade.id
            temp_eg['name'] = grade.name
            temp_eg['max_number'] = grade.max_number
            temp_eg['type'] = grade.type
            output['event_grades'].append(temp_eg)

    return output

def getJudgingDataOrganizer(id_head):

    output = {}
    output['applications'] = []
    if id_head > 0:
        ecoh            = Event_category_ordering_head.query.filter_by(id=id_head).first()
        eco             = Event_category_ordering.query.filter_by(id_head = id_head).order_by(Event_category_ordering.eo).all()
        for e in eco:
            event_judges    = Event_judges.query.filter_by(id_event = ecoh.id_event).all()
            event_grades    = Event_grades.query.filter_by(id_event = ecoh.id_event).all()
            age_group       = Age_group.query.filter_by(id=e.id_age_group).first()
            category        = Category.query.filter_by(id=e.id_category).first()
            discipline      = Discipline.query.filter_by(id=e.id_discipline).first()
            level           = Level.query.filter_by(id=e.id_level).first()
            applications    = Application.query.filter_by(id_event = ecoh.id_event, age_group = e.id_age_group , discipline = e.id_discipline , category = e.id_category, level = e.id_level).order_by(Application.entered_date).all()
            for a in applications:
                temp_a = {}
                temp_a['id'] = a.id
                temp_a['judges'] = []
                temp_b = {}
                for ej in event_judges:
                    
                    judge   = Judges.query.filter_by(id = ej.id_judges).first()
                    temp_b[ej.id_judges] = []
                    temp_c = {}
                    for eg in event_grades:
                        aj      = Application_judging.query.filter_by(id_judge = judge.id_user, id_grade = eg.id_grades, id_application = a.id).first()
                        if aj:
                            temp_c[eg.id_grades] = aj.grade
                    temp_b[ej.id_judges].append(temp_c)
                temp_a['judges'].append(temp_b)
                output['applications'].append(temp_a)


    return output

def getEventJudges(id_event):
    judges   = Event_judges.query.filter_by(id_event=id_event).all()
    output = []
    for j in judges:
        judge = Judges.query.filter_by(id=j.id_judges).first()
        temp_j = {}
        temp_j['id'] = judge.id
        temp_j['name'] = judge.name
        temp_j['lastname'] = judge.lastname
        output.append(temp_j)

    return output

def getEventGrade(id_event):
    event_grades   = Event_grades.query.filter_by(id_event=id_event).all()
    output = []
    for eg in event_grades:
            grade = Grades.query.filter_by(id=eg.id_grades).first()
            temp_eg = {}
            temp_eg['id'] = grade.id
            temp_eg['name'] = grade.name
            temp_eg['max_number'] = grade.max_number
            temp_eg['type'] = grade.type
            output.append(temp_eg)

    return output

def getInvoiceData(id_event):
    output = []
    application   = Application.query.filter_by(id_event=id_event, user_id = current_user.id).all()

    
    for a in application:
        category = Category.query.filter_by(id=a.category).first()
        temp_a = {}
        temp_a['category'] = category.name
        temp_a['price_base'] = category.price
        temp_a['price'] = 0
        temp_a['qty'] = 0
        
        app_dancers = Application_dancer.query.filter_by(id_application=a.id).all()
        for ad in app_dancers:
            temp_a['price'] += category.price
            temp_a['qty']   += 1
        output.append(temp_a)
    
    return output

def getEventDancers(id_event):
    output = []
    unique_list = []
    application   = Application.query.filter_by(id_event=id_event).all()
    for a in application:
        user_data = User_data.query.filter_by(id_user=a.user_id).first()
        app_dancers = Application_dancer.query.filter_by(id_application=a.id).all()
        for ad in app_dancers:
            if ad.id_dancer not in unique_list:
                unique_list.append(ad.id_dancer)
                dancers = Dancers.query.filter_by(id=ad.id_dancer).first()
                if dancers is not None:
                    temp_a = {}
                    temp_a['studio'] = user_data.studio
                    temp_a['name'] = dancers.name
                    temp_a['lastname'] = dancers.lastname
                    temp_a['birth_date'] = dancers.birth_date
                    temp_a['sex'] = dancers.sex
                    output.append(temp_a)
    return output