from pydantic import BaseModel


# Schema for Football Match Schedule
class FootballMatchSchema(BaseModel):
    league_or_tournament: str
    team_1: str
    team_2: str
    venue: str
    time: str


# Schema for Football Match Results
class FootballMatchResultSchema(BaseModel):
    league_or_tournament: str
    home_team: str
    away_team: str
    score: str
