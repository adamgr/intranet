# -*- coding: utf-8 -*-
from sqlalchemy.sql import and_
from pyramid.view import view_config

from intranet3.utils.views import BaseView
from intranet3.models import Team as Team_m, TeamMember, User
from intranet3.helpers import groupby
from intranet3.utils.api import badrequest_json, pass_name_team, check_team_json


@view_config(route_name='api_teams', renderer='json') #GET; POST
class Teams(BaseView):
    
    def _create_dict(self, teams):
        list_teams = []
        for k, values in teams.iteritems():
            list_teams.append({'id': values[0].team_id, 'name': values[0].team.name,\
                               'users': [{'id': v.user.id, 'name': v.user.name,\
                               'img': v.user.avatar_url} for v in values]})
        return list_teams
    
    def get(self): #do poprawy maja byc wziete teamy + uzytkownicy, nie same teammembers
    
        teams_n = Team_m.query.all()
        for t in teams_n:
            print t.name
            for tm in t.team_members:
                print tm.user_id
                print tm.user.name
    
        teams = TeamMember.query.all()
        teams = groupby(teams, lambda t: t.team_id)
        return self._create_dict(teams)
        
    def post(self): #pobranie (sprawdzone ok)
        try:
            json_team = self.request.json_body
        except ValueError:
            return badrequest_json({"errors": True, "json_body": False})
            
        valid, data = check_team_json(json_team)
        if not valid:
            return badrequest_json(data)
        if not pass_name_team(name=data['name']):
            return badrequest_json({'errors': True, 'name': 'exists'})
            
        team = Team_m(name=data['name'])
        self.session.add(team)
        return {}
        

@view_config(route_name='api_team', renderer='json')    
class Team(BaseView): # GET; PUT
      
    def get(self): #pobranie (sprawdzone ok)
        team_id = self.request.matchdict.get('team_id')
        team = Team_m.query.get(team_id)
        if team:
            return team.to_dict()
            
        return badrequest_json({"errors": True, "get_team": False})
        
    def put(self):#update (sprawdzone ok)
        team_id = self.request.matchdict.get('team_id')
        team = Team_m.query.get(team_id)
        if not team:
            return badrequest_json({"errors": True, "get_team": False})
        try:
            json_team = self.request.json_body
        except ValueError:
            return badrequest_json({"errors": True, "json_body": False})
            
        if json_team.has_key('dirty') and json_team['dirty']:
            teams = TeamMember.query.filter(TeamMember.team_id==team.id).all()
            users_json = [u['id'] for u in json_team['users']]
            users_db = [t.user_id for t in teams]
            users_delete = list(set(users_db) - set(users_json))
            users_add = list(set(users_json) - set(users_db))

            if users_delete:
                TeamMember.query.filter(and_(TeamMember.team_id==team.id,\
                                             TeamMember.user_id.in_(users_delete)))\
                                             .delete(synchronize_session=False)
            if users_add:
                self.session.add_all([TeamMember(user_id=u_id, team_id=team.id) for u_id in users_add])
        else:
            valid, data = check_team_json(json_team)
            if not valid:
                return badrequest_json(data)
            if not pass_name_team(name=data['name'], team_id=team.id):
                return badrequest_json({'errors': True, 'name': 'exists'})
                
            team.name = data['name']
        
        return {}
        

@view_config(route_name='api_users', renderer='json')  #GET (sprawdzone ok)
class Users(BaseView):
    def get(self):
        users = User.query.filter(User.is_active==True)\
                          .filter(User.is_not_client())\
                          .filter(User.freelancer==False)\
                          .order_by(User.name).all()
                          
        return [{'id': u.id, 'name': u.name, 'img': u.avatar_url} for u in users];


