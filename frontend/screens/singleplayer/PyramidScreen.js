import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { COLORS, SIZES, GLOBAL_STYLES } from '../../theme';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

export default function PyramidScreen({ navigation }) {
  const [pyramidData, setPyramidData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [lives, setLives] = useState(3);
  const [gameOver, setGameOver] = useState(false);
  const [searchVisible, setSearchVisible] = useState(false);

  useEffect(() => {
    fetchNewPyramid();
  }, []);

  const fetchNewPyramid = async () => {
    setLoading(true);
    setGameOver(false);
    setLives(3);
    try {
      const res = await api.get('/game/pyramid/generate');
      setPyramidData(res.data);
    } catch (err) {
      Alert.alert("Hata", "Oyun verisi çekilemedi.");
    } finally {
      setLoading(false);
    }
  };

  const handleGuessSubmit = (selectedItem) => {
    setSearchVisible(false);
    
    // Zaten oyun bittiyse tahmin yapılamaz
    if (gameOver) return;

    // Seçilen oyuncu listede var mı kontrol et
    const matchedIndex = pyramidData.items.findIndex(item => item.id === selectedItem.id);
    
    if (matchedIndex !== -1) {
      const item = pyramidData.items[matchedIndex];
      if (!item.hidden) {
        // Listede var ama zaten açılmış
        handleWrongGuess("Bu oyuncu zaten listede açık!");
      } else {
        // Doğru tahmin!
        const newItems = [...pyramidData.items];
        newItems[matchedIndex].hidden = false;
        newItems[matchedIndex].justGuessed = true; // Yeşile boyamak için bayrak
        
        setPyramidData({ ...pyramidData, items: newItems });
        
        // Bütün gizliler açıldı mı kontrol et
        const allRevealed = newItems.every(i => !i.hidden);
        if (allRevealed) {
          setGameOver(true);
          setTimeout(() => {
            Alert.alert("İnanılmaz!", "Piramitteki tüm oyuncuları buldun!", [{ text: "Yeni Oyun", onPress: fetchNewPyramid }]);
          }, 500);
        }
      }
    } else {
      // Yanlış tahmin!
      handleWrongGuess("Yanlış Tahmin! Bu oyuncu ilk 10'da değil.");
    }
  };

  const handleWrongGuess = (message) => {
    const newLives = lives - 1;
    setLives(newLives);
    
    if (newLives <= 0) {
      // Oyun bitti, hepsini göster
      setGameOver(true);
      const revealedItems = pyramidData.items.map(item => ({
        ...item,
        hidden: false,
        missed: item.hidden // Bilemediği için kırmızı yap
      }));
      setPyramidData({ ...pyramidData, items: revealedItems });
      
      Alert.alert("Oyun Bitti", message + "\nCanın kalmadı! Bütün liste açıldı.");
    } else {
      Alert.alert("Hata", message + `\nKalan Can: ${newLives}`);
    }
  };

  if (loading) {
    return (
      <View style={[GLOBAL_STYLES.screen, GLOBAL_STYLES.center]}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={[GLOBAL_STYLES.textBody, { marginTop: 10 }]}>Piramit Hazırlanıyor...</Text>
      </View>
    );
  }

  if (!pyramidData) {
    return (
      <View style={[GLOBAL_STYLES.screen, GLOBAL_STYLES.center]}>
        <Text style={GLOBAL_STYLES.textBody}>Veri çekilemedi.</Text>
        <TouchableOpacity style={styles.actionBtn} onPress={fetchNewPyramid}>
          <Text style={styles.actionBtnText}>Yenile</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={GLOBAL_STYLES.screen}>
      <View style={styles.header}>
        <Text style={[GLOBAL_STYLES.textTitle, { color: COLORS.primary, fontSize: 32 }]}>{pyramidData.title}</Text>
        <Text style={[GLOBAL_STYLES.textBody, { color: COLORS.primary, fontSize: 20, marginTop: 5, textAlign: 'center' }]}>
          {pyramidData.subtitle}
        </Text>
      </View>

      <View style={styles.listContainer}>
        {pyramidData.items.map((item, idx) => {
          let bgColor = 'rgba(255,255,255,0.05)';
          let borderColor = 'rgba(255,255,255,0.1)';
          
          if (item.justGuessed) {
            bgColor = 'rgba(0, 255, 163, 0.2)';
            borderColor = 'rgba(0, 255, 163, 0.8)';
          } else if (item.missed) {
            bgColor = 'rgba(255, 68, 68, 0.2)';
            borderColor = 'rgba(255, 68, 68, 0.8)';
          }

          return (
            <View key={idx} style={[styles.listItem, { backgroundColor: bgColor, borderColor: borderColor }]}>
              <View style={styles.rankBadge}>
                <Text style={styles.rankText}>{item.rank}</Text>
              </View>
              <View style={styles.nameContainer}>
                {item.hidden ? (
                  <Text style={styles.hiddenText}>???</Text>
                ) : (
                  <Text style={styles.playerName}>{item.name}</Text>
                )}
              </View>
              <View style={styles.scoreContainer}>
                {item.hidden ? (
                  <Text style={styles.hiddenText}>?</Text>
                ) : (
                  <Text style={styles.scoreText}>{item.score}</Text>
                )}
              </View>
            </View>
          );
        })}
      </View>

      <View style={styles.livesContainer}>
        {[...Array(3)].map((_, i) => (
          <Text key={i} style={[styles.heart, { opacity: i < lives ? 1 : 0.2 }]}>❤️</Text>
        ))}
      </View>

      {!gameOver ? (
        <TouchableOpacity style={styles.guessBtn} onPress={() => setSearchVisible(true)}>
          <Text style={styles.guessBtnText}>Oyuncu Tahmin Et</Text>
        </TouchableOpacity>
      ) : (
        <TouchableOpacity style={[styles.guessBtn, { backgroundColor: COLORS.secondary }]} onPress={fetchNewPyramid}>
          <Text style={styles.guessBtnText}>Yeni Piramit</Text>
        </TouchableOpacity>
      )}

      <SearchModal 
        visible={searchVisible} 
        onClose={() => setSearchVisible(false)}
        onSelect={handleGuessSubmit}
        searchType={1} // Player search
      />
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    padding: 20,
    paddingBottom: 10,
    alignItems: 'center',
  },
  livesContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 5,
  },
  heart: {
    fontSize: 24,
    marginHorizontal: 5,
  },
  listContainer: {
    flex: 1,
    paddingHorizontal: 15,
    justifyContent: 'space-evenly',
  },
  listItem: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    borderWidth: 1,
    borderRadius: SIZES.radius,
    marginVertical: 2,
    maxHeight: 50,
  },
  rankBadge: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: 'rgba(255,255,255,0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  rankText: {
    color: COLORS.secondary,
    fontWeight: 'bold',
    fontSize: 16,
  },
  nameContainer: {
    flex: 1,
  },
  playerName: {
    color: COLORS.text,
    fontSize: 16,
    fontWeight: 'bold',
  },
  hiddenText: {
    color: 'rgba(255,255,255,0.3)',
    fontSize: 16,
    letterSpacing: 2,
  },
  scoreContainer: {
    width: 50,
    alignItems: 'flex-end',
  },
  scoreText: {
    color: COLORS.primary,
    fontSize: 18,
    fontWeight: 'bold',
  },
  guessBtn: {
    margin: 20,
    backgroundColor: COLORS.primary,
    padding: 15,
    borderRadius: SIZES.radius,
    alignItems: 'center',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  guessBtnText: {
    color: '#000',
    fontSize: SIZES.medium,
    fontWeight: 'bold',
  },
  actionBtn: {
    marginTop: 20,
    backgroundColor: 'rgba(255,255,255,0.1)',
    padding: 15,
    borderRadius: SIZES.radius,
  },
  actionBtnText: {
    color: COLORS.text,
  }
});
