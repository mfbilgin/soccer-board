from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    known_as = Column(String, nullable=False, index=True)
    search_name = Column(String, index=True, nullable=True)
    nationality = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    position = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, nullable=True)

    # Relationships
    club_stats = relationship("PlayerClubStat", back_populates="player")
    national_stats = relationship("PlayerNationalStat", back_populates="player")
    transfers = relationship("PlayerTransfer", back_populates="player")
    honours = relationship("PlayerHonour", back_populates="player")

    def __repr__(self):
        return f"<Player(known_as='{self.known_as}')>"

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    short_name = Column(String, nullable=True)
    country = Column(String, nullable=True)
    type = Column(String, nullable=True) # 'club' or 'national'
    logo_url = Column(String, nullable=True)

    def __repr__(self):
        return f"<Team(name='{self.name}', type='{self.type}')>"

class Competition(Base):
    __tablename__ = 'competitions'
    id = Column(Integer, primary_key=True)
    api_id = Column(String, unique=True, nullable=False, index=True) # TMAPI uses strings like 'GB1' or 'CL'
    name = Column(String, nullable=False)
    type = Column(String, nullable=True) # domestic_league, domestic_cup, etc.
    country = Column(String, nullable=True)

    def __repr__(self):
        return f"<Competition(name='{self.name}')>"

class PlayerClubStat(Base):
    __tablename__ = 'player_club_stats'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, index=True)
    competition_id = Column(Integer, ForeignKey('competitions.id'), nullable=False, index=True)
    season = Column(String, nullable=False, index=True)
    appearances = Column(Integer, default=0)
    started_matches = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    penalty_goals = Column(Integer, default=0)
    penalty_misses = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    shirt_number = Column(Integer, nullable=True)

    # Relationships
    player = relationship("Player", back_populates="club_stats")
    team = relationship("Team")
    competition = relationship("Competition")

class PlayerNationalStat(Base):
    __tablename__ = 'player_national_stats'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, index=True) # Must be a national team
    caps = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)

    # Relationships
    player = relationship("Player", back_populates="national_stats")
    team = relationship("Team")

class PlayerTransfer(Base):
    __tablename__ = 'player_transfers'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)
    from_team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    to_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    transfer_date = Column(String, nullable=True)
    transfer_fee = Column(String, nullable=True) # Stored as string for flexibility (e.g., 'Free', '€50.00m')
    market_value = Column(String, nullable=True)

    # Relationships
    player = relationship("Player", back_populates="transfers")
    from_team = relationship("Team", foreign_keys=[from_team_id])
    to_team = relationship("Team", foreign_keys=[to_team_id])

class PlayerHonour(Base):
    __tablename__ = 'player_honours'
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)
    competition_id = Column(Integer, ForeignKey('competitions.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    season = Column(String, nullable=True)

    # Relationships
    player = relationship("Player", back_populates="honours")
    competition = relationship("Competition")
    team = relationship("Team")

# --- USER, AUTH, AND SOCIAL MODELS (UNCHANGED BUT KEPT) ---
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    chips = Column(Integer, default=1000)
    gems = Column(Integer, default=20)
    rating = Column(Integer, default=100)

class Friendship(Base):
    __tablename__ = 'friendships'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    friend_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(String, default="pending")
