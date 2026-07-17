import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { GLOBAL_STYLES, COLORS, SIZES } from '../../utils/styles';

export default function TicTacToeResultScreen({ route, navigation }) {
  const { grid, cellAnswers, answers, xp_gained } = route.params;

  const returnHome = () => {
    navigation.popToTop();
  };

  return (
    <ScrollView contentContainerStyle={{flexGrow:1}} style={GLOBAL_STYLES.screen}>
      <View style={styles.header}>
        <Text style={GLOBAL_STYLES.textTitle}>Sonuç</Text>
        <Text style={[GLOBAL_STYLES.textBody, { color: COLORS.secondary }]}>Tür: {grid.type === 1 ? 'Takım x Takım' : 'Oyuncu x Oyuncu'}</Text>
        <Text style={styles.xpText}>Kazanılan XP: +{xp_gained}</Text>
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
            
            {/* Oyun Hücreleri (Sonuçlar) */}
            {grid.cols.map((col, cIdx) => {
              const userGuess = cellAnswers[`${rIdx}-${cIdx}`];
              const correctAnswer = answers[`${row.id}-${col.id}`] || "?";
              
              let isCorrect = false;
              let displayText = "";
              
              if (userGuess && !userGuess.isSurrender) {
                isCorrect = true;
                displayText = userGuess.name;
              } else {
                displayText = correctAnswer;
              }

              return (
                <View 
                  key={`cell-${rIdx}-${cIdx}`} 
                  style={[
                    styles.playCell, 
                    isCorrect ? styles.playCellCorrect : styles.playCellMissed
                  ]}
                >
                  <View style={{alignItems: 'center'}}>
                    <Text style={[styles.playCellTextDone, {color: isCorrect ? COLORS.primary : '#e74c3c'}]}>
                      {isCorrect ? "✓" : "✗"}
                    </Text>
                    <Text style={{color: isCorrect ? '#fff' : '#e74c3c', fontSize: 10, textAlign: 'center', marginTop: 5}} numberOfLines={2}>
                      {displayText}
                    </Text>
                  </View>
                </View>
              )
            })}
          </View>
        ))}
      </View>

      <View style={{flexDirection: 'row', justifyContent: 'center', marginTop: 30, marginBottom: 50}}>
        <TouchableOpacity style={styles.newGameBtn} onPress={returnHome}>
          <Text style={styles.newGameBtnText}>Ana Menüye Dön</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  header: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  xpText: {
    color: '#f1c40f',
    fontSize: SIZES.large,
    fontWeight: 'bold',
    marginTop: 10,
    textShadowColor: 'rgba(0,0,0,0.5)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 3,
  },
  gridContainer: {
    padding: 10,
    marginTop: 10,
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
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
  },
  playCellCorrect: {
    backgroundColor: 'rgba(0, 255, 163, 0.2)',
    borderColor: 'rgba(0, 255, 163, 0.8)',
  },
  playCellMissed: {
    backgroundColor: 'rgba(231, 76, 60, 0.1)',
    borderColor: 'rgba(231, 76, 60, 0.5)',
  },
  playCellTextDone: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  newGameBtn: {
    backgroundColor: COLORS.primary,
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: SIZES.radius,
    alignItems: 'center',
  },
  newGameBtnText: {
    color: '#000',
    fontSize: SIZES.medium,
    fontWeight: 'bold',
  }
});
