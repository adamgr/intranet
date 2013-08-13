# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, orm
from sqlalchemy.types import Integer, String
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import exists

from intranet3.models import Base, User, DBSession

class Team(Base):
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String(255), unique=True, nullable=False)
    team_members = orm.relationship('TeamMember', backref='team', lazy='dynamic')
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name}
        
    def validate(self):
        error = {'errors': False, 'name': []}
        if len(self.name)>255:
            error['errors'] = True
            error['name'].append('for_long')
        if DBSession.query(exists().where(Team.name==self.name)).scalar():
            error['errors'] = True
            error['name'].append('exists')
        if error['errors'] == True:
            return error
        else:
            return True
        
    
class TeamMember(Base):
    __tablename__ = 'team_members'
    
    id = Column(Integer, nullable=False, index=True, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    
    __table_args__ = (UniqueConstraint('team_id', 'user_id', name='team_members_team_id_user_id_unique'), {})
