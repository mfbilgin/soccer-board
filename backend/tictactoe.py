import random
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Tuple, Dict
import uuid

import models

_CACHE = {}

class TicTacToeEngine:
    def __init__(self, db: Session):
        self.db = db
        if not _CACHE:
            self._initialize_pools()
        self.popular_team_ids = _CACHE['popular_team_ids']
        self.popular_player_ids = _CACHE['popular_player_ids']
        self.team_players = _CACHE['team_players']
        self.player_teams = _CACHE['player_teams']

    def _initialize_pools(self):
        print("Initializing TicTacToe cache in memory...")
        elite_teams = self.db.query(models.Team.id).filter(models.Team.known_as != None).all()
        popular_team_ids = [t[0] for t in elite_teams]

        top_players = self.db.query(
            models.PlayerClubStats.player_id
        ).group_by(models.PlayerClubStats.player_id).order_by(
            func.sum(models.PlayerClubStats.appearances).desc()
        ).limit(1500).all()
        popular_player_ids = [p[0] for p in top_players]

        all_histories = self.db.query(models.PlayerClubStats.player_id, models.PlayerClubStats.team_id).all()
        
        team_players = {}
        player_teams = {}
        
        for pid, tid in all_histories:
            if tid not in team_players:
                team_players[tid] = set()
            team_players[tid].add(pid)
            
            if pid not in player_teams:
                player_teams[pid] = set()
            player_teams[pid].add(tid)

        _CACHE['popular_team_ids'] = popular_team_ids
        _CACHE['popular_player_ids'] = popular_player_ids
        _CACHE['team_players'] = team_players
        _CACHE['player_teams'] = player_teams
        print("Cache initialized!")

    def _check_team_intersection(self, team1_id: int, team2_id: int) -> bool:
        t1_players = self.team_players.get(team1_id, set())
        t2_players = self.team_players.get(team2_id, set())
        return bool(t1_players & t2_players)

    def _check_player_intersection(self, player1_id: int, player2_id: int) -> bool:
        p1_teams = self.player_teams.get(player1_id, set())
        p2_teams = self.player_teams.get(player2_id, set())
        return bool(p1_teams & p2_teams)

    def generate_type1_grid(self) -> Dict:
        """Takım x Takım matrisi üretir (Akıllı Seçim)"""
        for _ in range(500):
            r1 = random.choice(self.popular_team_ids)
            
            r1_players = self.team_players.get(r1, set())
            valid_col_ids = []
            for t_id in self.popular_team_ids:
                if t_id != r1 and bool(r1_players & self.team_players.get(t_id, set())):
                    valid_col_ids.append(t_id)
            
            if len(valid_col_ids) < 3:
                continue
                
            # 2. Üç adet geçerli sütun takımı seç
            cols = random.sample(valid_col_ids, 3)
            
            # 3. Bu 3 sütunla da ortak oyuncusu olan diğer satırları bul
            # (Basitlik için popüler takımları tarayıp, 3 sütunla da eşleşenleri filtreliyoruz)
            valid_row_candidates = []
            for candidate in self.popular_team_ids:
                if candidate == r1 or candidate in cols:
                    continue
                if self._check_team_intersection(candidate, cols[0]) and \
                   self._check_team_intersection(candidate, cols[1]) and \
                   self._check_team_intersection(candidate, cols[2]):
                    valid_row_candidates.append(candidate)
                    
            if len(valid_row_candidates) < 2:
                continue
                
            # 4. Kalan iki satırı seç
            rows = [r1] + random.sample(valid_row_candidates, 2)
            
            # Matris bulundu!
            random.shuffle(rows) # Karıştır ki r1 hep en üstte olmasın
            return self._format_grid_response(rows, cols, 1)

        raise Exception("Failed to generate a valid Type 1 grid.")

    def generate_type2_grid(self) -> Dict:
        """Oyuncu x Oyuncu matrisi üretir (Akıllı Seçim)"""
        for _ in range(500):
            r1 = random.choice(self.popular_player_ids)
            
            r1_teams = self.player_teams.get(r1, set())
            valid_col_ids = []
            for p_id in self.popular_player_ids:
                if p_id != r1 and bool(r1_teams & self.player_teams.get(p_id, set())):
                    valid_col_ids.append(p_id)
            
            if len(valid_col_ids) < 3:
                continue
                
            cols = random.sample(valid_col_ids, 3)
            
            valid_row_candidates = []
            for candidate in self.popular_player_ids:
                if candidate == r1 or candidate in cols:
                    continue
                if self._check_player_intersection(candidate, cols[0]) and \
                   self._check_player_intersection(candidate, cols[1]) and \
                   self._check_player_intersection(candidate, cols[2]):
                    valid_row_candidates.append(candidate)
                    
            if len(valid_row_candidates) < 2:
                continue
                
            rows = [r1] + random.sample(valid_row_candidates, 2)
            random.shuffle(rows)
            return self._format_grid_response(rows, cols, 2)

        raise Exception("Failed to generate a valid Type 2 grid.")

    def _format_grid_response(self, row_ids: List[int], col_ids: List[int], grid_type: int) -> Dict:
        grid_id = str(uuid.uuid4())
        
        row_items = []
        col_items = []
        
        if grid_type == 1:
            # Takım detayı
            db_rows = self.db.query(models.Team).filter(models.Team.id.in_(row_ids)).all()
            db_cols = self.db.query(models.Team).filter(models.Team.id.in_(col_ids)).all()
            
            # ID sırasını korumak için manual eşleştirme
            row_map = {t.id: t for t in db_rows}
            col_map = {t.id: t for t in db_cols}
            
            for rid in row_ids:
                row_items.append({"id": rid, "name": row_map[rid].known_as if row_map[rid].known_as else row_map[rid].name})
            for cid in col_ids:
                col_items.append({"id": cid, "name": col_map[cid].known_as if col_map[cid].known_as else col_map[cid].name})
                
        elif grid_type == 2:
            # Oyuncu detayı
            db_rows = self.db.query(models.Player).filter(models.Player.id.in_(row_ids)).all()
            db_cols = self.db.query(models.Player).filter(models.Player.id.in_(col_ids)).all()
            
            row_map = {p.id: p for p in db_rows}
            col_map = {p.id: p for p in db_cols}
            
            for rid in row_ids:
                row_items.append({"id": rid, "name": row_map[rid].known_as})
            for cid in col_ids:
                col_items.append({"id": cid, "name": col_map[cid].known_as})

        return {
            "grid_id": grid_id,
            "type": grid_type,
            "rows": row_items,
            "cols": col_items
        }

    def validate_guess(self, row_id: int, col_id: int, guess_id: int, grid_type: int) -> Tuple[bool, str, str]:
        """Kullanıcının tahminini doğrular"""
        if grid_type == 1:
            # Kullanıcı bir Player ID'si tahmin etti. 
            # Bu oyuncu Row (Team) ve Col (Team) takımlarında oynadı mı?
            played_row = self.db.query(models.PlayerClubStats).filter(
                models.PlayerClubStats.player_id == guess_id,
                models.PlayerClubStats.team_id == row_id
            ).first()
            
            played_col = self.db.query(models.PlayerClubStats).filter(
                models.PlayerClubStats.player_id == guess_id,
                models.PlayerClubStats.team_id == col_id
            ).first()
            
            if played_row and played_col:
                player = self.db.query(models.Player).filter(models.Player.id == guess_id).first()
                return True, "Doğru Cevap!", player.known_as if player else "Bilinmeyen"
                
            player = self.db.query(models.Player).filter(models.Player.id == guess_id).first()
            p_name = player.known_as if player else "Bu oyuncu"
            
            if not played_row and not played_col:
                row_t = self.db.query(models.Team).filter(models.Team.id == row_id).first()
                col_t = self.db.query(models.Team).filter(models.Team.id == col_id).first()
                r_name = (row_t.known_as if row_t.known_as else row_t.name) if row_t else ""
                c_name = (col_t.known_as if col_t.known_as else col_t.name) if col_t else ""
                return False, f"Yanlış Cevap. {p_name}, ne {r_name} ne de {c_name} takımında oynadı.", None
            elif not played_row:
                row_t = self.db.query(models.Team).filter(models.Team.id == row_id).first()
                r_name = (row_t.known_as if row_t.known_as else row_t.name) if row_t else ""
                return False, f"Yanlış Cevap. {p_name}, {r_name} takımında hiç oynamadı!", None
            else:
                col_t = self.db.query(models.Team).filter(models.Team.id == col_id).first()
                c_name = (col_t.known_as if col_t.known_as else col_t.name) if col_t else ""
                return False, f"Yanlış Cevap. {p_name}, {c_name} takımında hiç oynamadı!", None
            
        elif grid_type == 2:
            # Kullanıcı bir Team ID'si tahmin etti.
            # Row (Player) ve Col (Player) bu takımda oynadı mı?
            played_row = self.db.query(models.PlayerClubStats).filter(
                models.PlayerClubStats.player_id == row_id,
                models.PlayerClubStats.team_id == guess_id
            ).first()
            
            played_col = self.db.query(models.PlayerClubStats).filter(
                models.PlayerClubStats.player_id == col_id,
                models.PlayerClubStats.team_id == guess_id
            ).first()
            
            if played_row and played_col:
                team = self.db.query(models.Team).filter(models.Team.id == guess_id).first()
                team_name = (team.known_as if team.known_as else team.name) if team else "Bilinmeyen"
                return True, "Doğru Cevap!", team_name
                
            team = self.db.query(models.Team).filter(models.Team.id == guess_id).first()
            t_name = (team.known_as if team.known_as else team.name) if team else "Bu takım"
            
            if not played_row and not played_col:
                row_p = self.db.query(models.Player).filter(models.Player.id == row_id).first()
                col_p = self.db.query(models.Player).filter(models.Player.id == col_id).first()
                r_name = row_p.known_as if row_p else ""
                c_name = col_p.known_as if col_p else ""
                return False, f"Yanlış Cevap. {r_name} ve {c_name}, {t_name} takımında hiç oynamadı.", None
            elif not played_row:
                row_p = self.db.query(models.Player).filter(models.Player.id == row_id).first()
                r_name = row_p.known_as if row_p else ""
                return False, f"Yanlış Cevap. {r_name}, {t_name} takımında hiç oynamadı!", None
            else:
                col_p = self.db.query(models.Player).filter(models.Player.id == col_id).first()
                c_name = col_p.known_as if col_p else ""
                return False, f"Yanlış Cevap. {c_name}, {t_name} takımında hiç oynamadı!", None

        return False, "Geçersiz matris türü.", None
