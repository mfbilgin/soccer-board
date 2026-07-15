import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import { COLORS, SIZES, GLOBAL_STYLES, FONTS } from '../../theme';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

export default function CareerGuessScreen({ navigation }) {
    const [puzzle, setPuzzle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [guessesLeft, setGuessesLeft] = useState(5);
    const [isSearchVisible, setSearchVisible] = useState(false);
    const [validating, setValidating] = useState(false);
    const [gameOver, setGameOver] = useState(false);
    const [gameWon, setGameWon] = useState(false);

    useEffect(() => {
        loadPuzzle();
    }, []);

    const loadPuzzle = async () => {
        try {
            setLoading(true);
            const res = await api.get('/game/career-guess/generate');
            setPuzzle(res.data);
            setGuessesLeft(5);
            setGameOver(false);
            setGameWon(false);
        } catch (err) {
            Alert.alert("Hata", "Bulmaca yüklenemedi.");
            navigation.goBack();
        } finally {
            setLoading(false);
        }
    };

    const handlePlayerSelect = async (player) => {
        setSearchVisible(false);
        if (gameOver || gameWon) return;

        try {
            setValidating(true);
            const res = await api.get(`/game/career-guess/verify?player_id=${player.id}&target_id=${puzzle.target_player_id}`);
            
            if (res.data.correct) {
                setGameWon(true);
                Alert.alert("Tebrikler!", `Doğru bildin! Oyuncu: ${puzzle.target_player_name}`);
            } else {
                const newGuesses = guessesLeft - 1;
                setGuessesLeft(newGuesses);
                if (newGuesses <= 0) {
                    setGameOver(true);
                    Alert.alert("Oyun Bitti", `Bilemedin! Doğru cevap: ${puzzle.target_player_name}`);
                } else {
                    Alert.alert("Yanlış", `Yanlış tahmin. Kalan hakkın: ${newGuesses}`);
                }
            }
        } catch (err) {
            Alert.alert("Hata", "Tahmin doğrulanırken bir hata oluştu.");
        } finally {
            setValidating(false);
        }
    };

    if (loading || !puzzle) {
        return (
            <SafeAreaView style={[styles.container, GLOBAL_STYLES.center]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={{color: COLORS.text, marginTop: 10, fontFamily: FONTS.body}}>Kariyer Hazırlanıyor...</Text>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <View style={styles.topBar}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <Ionicons name="arrow-back" size={28} color={COLORS.text} />
                </TouchableOpacity>
                <View style={styles.headerTitleBox}>
                    <Text style={styles.headerTitle}>Kariyer Yolu</Text>
                    <Text style={styles.headerSub}>Kalan Hak: {guessesLeft}</Text>
                </View>
                <View style={{ width: 28 }} />
            </View>

            <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 50 }}>
                <Text style={styles.instruction}>Bu takımlarda sırasıyla oynamış futbolcu kimdir?</Text>
                
                <View style={styles.timelineContainer}>
                    {puzzle.career.map((item, index) => (
                        <View key={index} style={styles.timelineItem}>
                            <View style={styles.timelineLineContainer}>
                                <View style={styles.timelineDot} />
                                {index < puzzle.career.length - 1 && <View style={styles.timelineLine} />}
                            </View>
                            <View style={styles.teamCard}>
                                <View style={styles.teamInfo}>
                                    <Text style={styles.teamName}>{item.team_name}</Text>
                                    {item.start_year ? (
                                        <Text style={styles.teamYears}>
                                            {item.start_year} - {item.end_year || 'Günümüz'}
                                        </Text>
                                    ) : null}
                                </View>
                            </View>
                        </View>
                    ))}
                </View>

                {(!gameOver && !gameWon) ? (
                    <TouchableOpacity 
                        style={[GLOBAL_STYLES.primaryButton, { marginTop: 30 }, validating && { opacity: 0.5 }]} 
                        onPress={() => setSearchVisible(true)}
                        disabled={validating}
                    >
                        {validating ? (
                            <ActivityIndicator color={COLORS.background} />
                        ) : (
                            <Text style={GLOBAL_STYLES.primaryButtonText}>Tahmin Et</Text>
                        )}
                    </TouchableOpacity>
                ) : (
                    <TouchableOpacity 
                        style={[GLOBAL_STYLES.primaryButton, { marginTop: 30, backgroundColor: COLORS.secondary }]} 
                        onPress={loadPuzzle}
                    >
                        <Text style={GLOBAL_STYLES.primaryButtonText}>Tekrar Oyna</Text>
                    </TouchableOpacity>
                )}
            </ScrollView>

            <SearchModal 
                visible={isSearchVisible}
                onClose={() => setSearchVisible(false)}
                onSelect={handlePlayerSelect}
                searchType={1}
            />
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    topBar: {
        flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
        paddingHorizontal: 20, paddingTop: 10, paddingBottom: 15,
        borderBottomWidth: 1, borderBottomColor: 'rgba(255,255,255,0.05)'
    },
    backBtn: { padding: 5, marginLeft: -5 },
    headerTitleBox: { flex: 1, alignItems: 'center' },
    headerTitle: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 18 },
    headerSub: { color: COLORS.primary, fontFamily: FONTS.headingBlack, fontSize: 12, marginTop: 2 },
    
    instruction: {
        color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 22,
        textAlign: 'center', marginBottom: 30, lineHeight: 28
    },
    
    timelineContainer: {
        paddingLeft: 10,
    },
    timelineItem: {
        flexDirection: 'row',
        marginBottom: 20,
    },
    timelineLineContainer: {
        width: 30,
        alignItems: 'center',
    },
    timelineDot: {
        width: 14, height: 14, borderRadius: 7,
        backgroundColor: COLORS.primary,
        zIndex: 2,
    },
    timelineLine: {
        position: 'absolute',
        top: 14, bottom: -20,
        width: 2,
        backgroundColor: 'rgba(57, 255, 20, 0.3)',
        zIndex: 1,
    },
    teamCard: {
        flex: 1,
        backgroundColor: 'rgba(255,255,255,0.05)',
        borderRadius: 12,
        padding: 15,
        marginLeft: 15,
        justifyContent: 'center',
        borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)'
    },
    teamInfo: {
        flex: 1,
    },
    teamName: {
        color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 18,
    },
    teamYears: {
        color: COLORS.textMuted, fontFamily: FONTS.body, fontSize: 14, marginTop: 4,
    }
});
