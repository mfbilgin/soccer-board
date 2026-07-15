from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=True)
    name = Column(String, nullable=True)
    known_as = Column(String, nullable=True)
    search_name = Column(String, index=True, nullable=True)
    nationality = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    position = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_updated = Column(String, nullable=True)

    # Relationships
    club_stats = relationship("PlayerClubStats", back_populates="player")
    national_stats = relationship("PlayerNationalStats", back_populates="player")
    transfers = relationship("PlayerTransfer", back_populates="player")

    def __repr__(self):
        return f"<Player(known_as='{self.known_as}')>"

class Team(Base):
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=True)
    name = Column(String, nullable=False)
    short_name = Column(String, nullable=True)
    country = Column(String, nullable=True)
    type = Column(String, nullable=True) # club, national
    logo_url = Column(String, nullable=True)

    # Relationships
    club_stats = relationship("PlayerClubStats", back_populates="team")
    national_stats = relationship("PlayerNationalStats", back_populates="team")

    def __repr__(self):
        return f"<Team(name='{self.name}')>"

class Competition(Base):
    __tablename__ = 'competitions'

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True) # domestic_league, domestic_cup, etc.
    country = Column(String, nullable=True)

    # Relationships
    club_stats = relationship("PlayerClubStats", back_populates="competition")

    def __repr__(self):
        return f"<Competition(name='{self.name}')>"

class PlayerClubStats(Base):
    __tablename__ = 'player_club_stats'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), index=True, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), index=True, nullable=False)
    competition_id = Column(Integer, ForeignKey('competitions.id'), index=True, nullable=False)
    season = Column(String, index=True, nullable=True)
    
    appearances = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    started_matches = Column(Integer, default=0)
    penalty_goals = Column(Integer, default=0)
    penalty_misses = Column(Integer, default=0)
    shirt_number = Column(String, nullable=True)

    # Relationships
    player = relationship("Player", back_populates="club_stats")
    team = relationship("Team", back_populates="club_stats")
    competition = relationship("Competition", back_populates="club_stats")

    def __repr__(self):
        return f"<PlayerClubStats(player_id={self.player_id}, team_id={self.team_id}, season={self.season})>"

class PlayerNationalStats(Base):
    __tablename__ = 'player_national_stats'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), index=True, nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), index=True, nullable=False)
    
    caps = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)

    # Relationships
    player = relationship("Player", back_populates="national_stats")
    team = relationship("Team", back_populates="national_stats")

    def __repr__(self):
        return f"<PlayerNationalStats(player_id={self.player_id}, team_id={self.team_id})>"

class PlayerTransfer(Base):
    __tablename__ = 'player_transfers'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), index=True, nullable=False)
    from_team_id = Column(Integer, ForeignKey('teams.id'), index=True, nullable=True)
    to_team_id = Column(Integer, ForeignKey('teams.id'), index=True, nullable=True)
    transfer_date = Column(String, nullable=True)
    transfer_fee = Column(String, nullable=True) # could be numeric or string based on how it's formatted
    market_value = Column(String, nullable=True)

    # Relationships
    player = relationship("Player", back_populates="transfers")
    from_team = relationship("Team", foreign_keys=[from_team_id])
    to_team = relationship("Team", foreign_keys=[to_team_id])

    def __repr__(self):
        return f"<PlayerTransfer(player_id={self.player_id}, from={self.from_team_id}, to={self.to_team_id})>"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Ekonomi ve Gelişim
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    chips = Column(Integer, default=1000)
    gems = Column(Integer, default=20)
    rating = Column(Integer, default=100) # Rekabetçi ELO / Rating
    
    def __repr__(self):
        return f"<User(username='{self.username}', level={self.level})>"

class Friendship(Base):
    __tablename__ = 'friendships'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    friend_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String, default="pending") # "pending", "accepted"
