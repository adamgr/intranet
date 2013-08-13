# -*- coding: utf-8 -*-
import json

from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.sql.expression import exists
from sqlalchemy.sql import and_

from intranet3.models import DBSession
from intranet3.models import Team


def badrequest_json(data):
    response = HTTPBadRequest()
    response.body = json.dumps(data)
    response.content_type = 'application/json'
    return response
    

def check_team_json(data):
    errors = {'errors': False}
    
    if data.has_key('name'):
        data['name'] = str(data['name']).strip()
        if not 0 < len(data['name']) < 255:
            errors = {'errors': True, 'name': 'length'}
    else:
        errors = {'errors': True, 'name': 'no_field'}
    
    if errors['errors']:
        return False, errors
    else:
        return True, data

        
def pass_name_team(name=None, team_id=False):
    if team_id:
        if DBSession.query(exists().where(and_(Team.name==name, Team.id!=team_id))).scalar():
            return False
    else:
        if DBSession.query(exists().where(Team.name==name)).scalar():
            return False
            
    return True
    
