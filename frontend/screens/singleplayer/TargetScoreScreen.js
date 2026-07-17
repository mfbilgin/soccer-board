import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, Image, ScrollView, ImageBackground } from 'react-native';
import { COLORS, SIZES, FONTS, GLOBAL_STYLES } from '../../theme';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

export default function TargetScoreScreen({ navigation }) {
    const [puzzle, setPuzzle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedPlayers, setSelectedPlayers] = useState([]);
    
    // Modal states
    const [isSearchVisible, setSearchVisible] = useState(false);
    const [currentSlotIndex, setCurrentSlotIndex] = useState(-1);
    
    // Result states
    const [validating, setValidating] = useState(false);

    useEffect(() => {
        loadPuzzle();
    }, []);

    const loadPuzzle = async () => {
        try {
            setLoading(true);
            const res = await api.get('/mode31/generate');
            setPuzzle(res.data);
            setSelectedPlayers(new Array(res.data.player_count).fill(null));
        } catch (err) {
            Alert.alert("Hata", "Bulmaca yüklenemedi.");
        } finally {
            setLoading(false);
        }
    };

    const openSearch = (index) => {
        setCurrentSlotIndex(index);
        setSearchVisible(true);
    };

    const handlePlayerSelect = async (player) => {
        // 1. Mükerrer oyuncu kontrolü
        if (selectedPlayers.some(p => p?.id === player.id)) {
            Alert.alert("Geçersiz Seçim", "Bu oyuncuyu zaten seçtiniz!");
            return;
        }

        setSearchVisible(false);
        setValidating(true);

        try {
            // 2. Anlık Dummy Engeli (GDD kuralı)
            const res = await api.post('/mode31/validate-single', {
                league: puzzle.league,
                metric: puzzle.metric,
                player_id: player.id
            });

            if (res.data.valid) {
                const newPlayers = [...selectedPlayers];
                newPlayers[currentSlotIndex] = player;
                setSelectedPlayers(newPlayers);
            } else {
                Alert.alert("Hatalı Seçim", res.data.message);
            }
        } catch (err) {
            Alert.alert("Hata", "Oyuncu doğrulanırken bir hata oluştu.");
        } finally {
            setValidating(false);
        }
    };

    const clearSlot = (index) => {
        const newPlayers = [...selectedPlayers];
        newPlayers[index] = null;
        setSelectedPlayers(newPlayers);
    };

    const submitGuess = async () => {
        if (selectedPlayers.some(p => p === null)) {
            Alert.alert("Hata", "Tüm kutuları doldurmalısın!");
            return;
        }

        try {
            setValidating(true);
            const playerIds = selectedPlayers.map(p => p.id);
            const res = await api.post('/mode31/validate', {
                league: puzzle.league,
                metric: puzzle.metric,
                player_ids: playerIds,
                target: puzzle.target
            });
            
            navigation.replace('TargetScoreResult', { result: res.data, puzzle: puzzle });
            
        } catch (err) {
            Alert.alert("Hata", "Tahmin gönderilirken bir hata oluştu.");
        } finally {
            setValidating(false);
        }
    };

    const metricLabel = {
        goals: 'Gol',
        assists: 'Asist',
        appearances: 'Maç',
        yellow_cards: 'Sarı Kart',
        red_cards: 'Kırmızı Kart',
        minutes_played: 'Oynanan Dakika',
        caps: 'Milli Maç'
    }[puzzle?.metric] || puzzle?.metric;

    if (loading || !puzzle) {
        return (
            <View style={[GLOBAL_STYLES.screen, GLOBAL_STYLES.center]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={{color: COLORS.text, marginTop: 10}}>Bulmaca Hazırlanıyor...</Text>
            </View>
        );
    }

    const isSmall = puzzle.player_count > 3;

    return (
        <ImageBackground 
            source={require('../../assets/background.png')} 
            style={GLOBAL_STYLES.screen}
            imageStyle={{ opacity: 0.15 }}
            resizeMode="cover"
        >
        <ScrollView contentContainerStyle={{paddingBottom: 40}}>
            <View style={styles.targetCard}>
                <Text style={styles.targetLeague}>{puzzle.league_name || puzzle.league}</Text>
                <Text style={styles.targetMain}>
                    Toplam {puzzle.target} {metricLabel}
                </Text>
                <Text style={styles.targetSub}>
                    {puzzle.player_count} Futbolcu Seçerek Hedefe Yaklaş!
                </Text>
            </View>

            <View style={styles.slotsContainer}>
                {selectedPlayers.map((player, index) => (
                    <View key={index} style={{ position: 'relative' }}>
                        <TouchableOpacity 
                            style={[
                                styles.playerSlotBase, 
                                player ? styles.slotFilled : {},
                                isSmall ? styles.playerSlotSmall : styles.playerSlotBig
                            ]}
                            onPress={() => openSearch(index)}
                            disabled={player !== null}
                        >
                            {player ? (
                                <View style={styles.playerContentCol}>
                                    <Text style={[styles.playerName, {textAlign: 'center'}]}>
                                        {player.name}
                                    </Text>
                                </View>
                            ) : (
                                <Text style={styles.slotPlaceholder}>Futbolcu Seç +</Text>
                            )}
                        </TouchableOpacity>
                        {player !== null && (
                            <TouchableOpacity 
                                style={{
                                    position: 'absolute', top: -10, right: -10,
                                    backgroundColor: '#e74c3c', width: 34, height: 34,
                                    borderRadius: 17, justifyContent: 'center', alignItems: 'center',
                                    borderWidth: 2, borderColor: '#FFF', zIndex: 10
                                }}
                                onPress={() => clearSlot(index)}
                            >
                                <Text style={{color: '#FFF', fontWeight: 'bold', fontSize: 16}}>X</Text>
                            </TouchableOpacity>
                        )}
                    </View>
                ))}
            </View>

            <View style={{padding: 20, marginBottom: 50}}>
                <TouchableOpacity 
                    style={[
                        GLOBAL_STYLES.primaryButton, 
                        (validating || !selectedPlayers.every(p => p !== null)) 
                            ? {opacity: 0.5, backgroundColor: COLORS.secondary} 
                            : {backgroundColor: COLORS.primary}
                    ]} 
                    onPress={submitGuess}
                    disabled={validating || !selectedPlayers.every(p => p !== null)}
                >
                    {validating ? (
                        <ActivityIndicator color={COLORS.background} />
                    ) : (
                        <Text style={GLOBAL_STYLES.primaryButtonText}>
                            {selectedPlayers.every(p => p !== null) 
                                ? "Bitir" 
                                : `Kutuları Doldur (${selectedPlayers.filter(p => p !== null).length}/${selectedPlayers.length})`}
                        </Text>
                    )}
                </TouchableOpacity>
            </View>

            <SearchModal 
                visible={isSearchVisible}
                onClose={() => setSearchVisible(false)}
                onSelect={handlePlayerSelect}
                searchType={1}
            />
        </ScrollView>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    targetCard: {
        backgroundColor: '#0e3609',
        padding: 25,
        margin: 20,
        borderRadius: 24,
        alignItems: 'center',
        borderWidth: 4,
        borderColor: '#4a840a',
        borderBottomWidth: 8,
    },
    targetLeague: {
        color: '#95c029',
        fontSize: 28,
        fontFamily: FONTS.headingBlack,
        marginBottom: 5,
        textAlign: 'center'
    },
    targetMain: {
        color: '#FFF',
        fontSize: 32,
        fontFamily: FONTS.headingBlack,
        marginBottom: 5,
        textAlign: 'center'
    },
    targetSub: {
        color: '#FFF',
        fontSize: 14,
        fontFamily: FONTS.headingBlack,
        textAlign: 'center',
        opacity: 0.9
    },
    slotsContainer: {
        padding: 15,
        gap: 10
    },
    playerSlotBase: {
        backgroundColor: '#4a840a',
        borderWidth: 4,
        borderColor: '#95c029',
        borderBottomWidth: 8,
        borderRadius: 20,
        alignItems: 'center',
        justifyContent: 'center',
    },
    playerSlotBig: {
        padding: 15,
        minHeight: 100,
    },
    playerSlotSmall: {
        padding: 10,
        minHeight: 60,
    },
    playerContentCol: {
        alignItems: 'center',
    },
    playerContentRow: {
        flexDirection: 'row',
        alignItems: 'center',
        width: '100%',
        paddingHorizontal: 10,
    },
    slotFilled: {
        borderColor: '#fcc205',
        backgroundColor: '#0e3609',
        borderBottomWidth: 4,
    },
    slotPlaceholder: {
        color: '#FFF',
        fontFamily: FONTS.headingBlack,
        fontSize: 18,
    },
    playerImageBig: {
        width: 60,
        height: 60,
        borderRadius: 30,
        marginBottom: 10,
    },
    playerImageSmall: {
        width: 40,
        height: 40,
        borderRadius: 20,
        marginRight: 15,
    },
    playerName: {
        color: '#FFF',
        fontFamily: FONTS.headingBlack,
        fontSize: 20,
        marginBottom: 5
    }
});
