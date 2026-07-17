import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, Image } from 'react-native';
import { COLORS, SIZES, GLOBAL_STYLES } from '../../theme';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

export default function TicTacToeScreen({ route }) {
  const [grid, setGrid] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Oynanış state'leri
  const [searchVisible, setSearchVisible] = useState(false);
  const [activeCell, setActiveCell] = useState(null); // {rIdx, cIdx, rowId, colId}
  const [cellAnswers, setCellAnswers] = useState({}); // key: `${rIdx}-${cIdx}`, value: item (oyuncu/takım resim vs)
  const [isSurrendered, setIsSurrendered] = useState(false);

  useEffect(() => {
    fetchNewGrid();
  }, []);

  useEffect(() => {
    // Matrisin tüm hücreleri dolduysa oyunu bitir
    if (Object.keys(cellAnswers).length === 9 && !isSurrendered) {
      setTimeout(() => {
        surrenderGame();
      }, 500); // UI güncellendikten yarım saniye sonra göster
    }
  }, [cellAnswers]);

  const fetchNewGrid = async () => {
    setLoading(true);
    setCellAnswers({});
    setIsSurrendered(false);
    try {
      const gridType = route.params?.gridType || 1;
      const res = await api.get('/game/tictactoe/grid?type=' + gridType);
      setGrid(res.data);
    } catch (err) {
      Alert.alert("Hata", "Oyun verisi çekilemedi.");
    } finally {
      setLoading(false);
    }
  };

  const handleCellPress = (rIdx, cIdx, row, col) => {
    // Eğer o hücre zaten bilindiyse veya pes edildiyse tıklanmasın
    if (cellAnswers[`${rIdx}-${cIdx}`] || isSurrendered) return;
    
    setActiveCell({ rIdx, cIdx, rowId: row.id, colId: col.id });
    setSearchVisible(true);
  };

  const handleGuessSubmit = async (selectedItem) => {
    setSearchVisible(false);
    
    try {
      const payload = {
        grid_id: grid.grid_id,
        row_id: activeCell.rowId,
        col_id: activeCell.colId,
        guess_id: selectedItem.id,
        type: grid.type
      };

      const res = await api.post('/game/tictactoe/guess', payload);
      
      if (res.data.correct) {
        // Doğru cevap! Hücreyi yeşile boya ve resmi ekle
        setCellAnswers(prev => ({
          ...prev,
          [`${activeCell.rIdx}-${activeCell.cIdx}`]: selectedItem
        }));
      } else {
        // Yanlış cevap!
        Alert.alert("Hatalı Tahmin!", res.data.message);
      }
    } catch (err) {
      Alert.alert("Hata", "Tahmin gönderilirken bir sorun oluştu.");
    }
  };

  const surrenderGame = async () => {
    try {
      const correctCount = Object.values(cellAnswers).filter(a => !a.isSurrender).length;
      const payload = {
        grid_type: grid.type,
        row_ids: grid.rows.map(r => r.id),
        col_ids: grid.cols.map(c => c.id),
        correct_count: correctCount
      };
      const res = await api.post('/game/tictactoe/surrender', payload);
      const answers = res.data.answers;
      const xp_gained = res.data.xp_gained || 0;
      
      setIsSurrendered(true);
      navigation.replace('TicTacToeResult', { grid, cellAnswers, answers, xp_gained });
    } catch (err) {
      Alert.alert("Hata", "Pes etme işlemi başarısız oldu.");
    }
  };

  if (loading) {
    return (
      <View style={[GLOBAL_STYLES.screen, GLOBAL_STYLES.center]}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={[GLOBAL_STYLES.textBody, { marginTop: 10 }]}>Oyun Hazırlanıyor...</Text>
      </View>
    );
  }

  if (!grid) {
    return (
      <View style={[GLOBAL_STYLES.screen, GLOBAL_STYLES.center]}>
        <Text style={GLOBAL_STYLES.textBody}>Veri çekilemedi. Lütfen tekrar deneyin.</Text>
        <TouchableOpacity style={styles.newGameBtn} onPress={fetchNewGrid}>
          <Text style={styles.newGameBtnText}>Yenile</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={GLOBAL_STYLES.screen}>
      <View style={styles.header}>
        <Text style={GLOBAL_STYLES.textTitle}>Sıra Sende</Text>
        <Text style={[GLOBAL_STYLES.textBody, { color: COLORS.secondary }]}>Tür: {grid.type === 1 ? 'Takım x Takım' : 'Oyuncu x Oyuncu'}</Text>
      </View>

      <View style={styles.gridContainer}>
        {/* Sütun Başlıkları */}
        <View style={styles.row}>
          <View style={styles.cellEmpty} />
          {grid.cols.map((col, idx) => (
            <View key={`col-${idx}`} style={styles.headerCell}>
              <Text style={styles.headerText} numberOfLines={3} adjustsFontSizeToFit>{col.name}</Text>
            </View>
          ))}
        </View>

        {/* Satırlar ve Hücreler */}
        {grid.rows.map((row, rIdx) => (
          <View key={`row-${rIdx}`} style={styles.row}>
            {/* Satır Başlığı */}
            <View style={styles.headerCell}>
              <Text style={styles.headerText} numberOfLines={3} adjustsFontSizeToFit>{row.name}</Text>
            </View>
            
            {/* Oyun Hücreleri (Oynanacak Alanlar) */}
            {grid.cols.map((col, cIdx) => {
              const answer = cellAnswers[`${rIdx}-${cIdx}`];
              return (
                <TouchableOpacity 
                  key={`cell-${rIdx}-${cIdx}`} 
                  style={[
                    styles.playCell, 
                    answer ? styles.playCellCorrect : null
                  ]}
                  onPress={() => handleCellPress(rIdx, cIdx, row, col)}
                >
                  {answer ? (
                    <View style={{alignItems: 'center'}}>
                      {answer.isSurrender ? (
                        <Text style={[styles.playCellTextDone, {color: '#e74c3c'}]}>?</Text>
                      ) : (
                        <Text style={styles.playCellTextDone}>✓</Text>
                      )}
                      <Text style={{color: answer.isSurrender ? '#e74c3c' : '#fff', fontSize: 10, textAlign: 'center', marginTop: 5}} numberOfLines={2}>{answer.name}</Text>
                    </View>
                  ) : (
                    <Text style={styles.playCellText}>+</Text>
                  )}
                </TouchableOpacity>
              )
            })}
          </View>
        ))}
      </View>

      <View style={{flexDirection: 'row', justifyContent: 'center', gap: 10, marginTop: 20}}>
        {(!isSurrendered && Object.keys(cellAnswers).length < 9) && (
          <TouchableOpacity style={[styles.newGameBtn, {backgroundColor: '#e74c3c'}]} onPress={surrenderGame}>
            <Text style={styles.newGameBtnText}>Oyunu Bitir</Text>
          </TouchableOpacity>
        )}
        <TouchableOpacity style={styles.newGameBtn} onPress={fetchNewGrid}>
          <Text style={styles.newGameBtnText}>Yenile</Text>
        </TouchableOpacity>
      </View>

      <SearchModal  
        visible={searchVisible} 
        onClose={() => setSearchVisible(false)}
        onSelect={handleGuessSubmit}
        searchType={grid.type} // grid type 1 (teamxteam) expects a player search (searchType 1)
      />
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  gridContainer: {
    padding: 10,
    marginTop: 20,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  cellEmpty: {
    width: 80,
    height: 80,
    margin: 5,
  },
  headerCell: {
    width: 80,
    height: 80,
    margin: 5,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  icon: {
    width: 50,
    height: 50,
    resizeMode: 'contain',
  },
  headerText: {
    color: COLORS.secondary,
    fontWeight: 'bold',
    fontSize: SIZES.small,
    textAlign: 'center',
    paddingHorizontal: 2,
  },
  playCell: {
    width: 80,
    height: 80,
    margin: 5,
    backgroundColor: 'rgba(0, 255, 163, 0.05)',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(0, 255, 163, 0.2)',
  },
  playCellCorrect: {
    backgroundColor: 'rgba(0, 255, 163, 0.2)',
    borderColor: 'rgba(0, 255, 163, 0.8)',
    shadowColor: COLORS.primary,
    shadowOpacity: 0.5,
    shadowRadius: 10,
  },
  playCellText: {
    color: 'rgba(0, 255, 163, 0.3)',
    fontSize: 30,
    fontWeight: 'bold',
  },
  playCellTextDone: {
    color: COLORS.primary,
    fontSize: 30,
    fontWeight: 'bold',
  },
  newGameBtn: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    paddingVertical: 15,
    paddingHorizontal: 25,
    borderRadius: SIZES.radius,
    alignItems: 'center',
  },
  newGameBtnText: {
    color: COLORS.text,
    fontSize: SIZES.medium,
  }
});
