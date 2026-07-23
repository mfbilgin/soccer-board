import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, ScrollView, TextInput, ImageBackground } from 'react-native';
import { COLORS, FONTS, GLOBAL_STYLES } from '../../theme';
import api from '../../api';

const ROLE_ORDER = ['GK', 'DEF', 'MID', 'ATT', 'SUB'];

function groupPositions(positions) {
    const groups = {};
    for (const p of positions) {
        const role = p.slot.replace(/[0-9]/g, '');
        if (!groups[role]) groups[role] = [];
        groups[role].push(p);
    }
    return ROLE_ORDER.filter(r => groups[r]).map(r => ({ role: r, items: groups[r] }));
}

export default function FlagElevenScreen({ navigation }) {
    const [puzzle, setPuzzle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [guess, setGuess] = useState('');
    const [wrongCount, setWrongCount] = useState(0);
    const [hints, setHints] = useState({});
    const [verifying, setVerifying] = useState(false);
    const [gameOver, setGameOver] = useState(null); // { won, teamName }

    const puzzleIdRef = useRef(null);

    useEffect(() => {
        loadPuzzle();
    }, []);

    const loadPuzzle = async () => {
        try {
            setLoading(true);
            setGameOver(null);
            setWrongCount(0);
            setHints({});
            setGuess('');
            const res = await api.get('/game/flag-eleven/generate');
            setPuzzle(res.data);
            puzzleIdRef.current = res.data.puzzle_id;
        } catch (err) {
            Alert.alert('Hata', 'Bulmaca yüklenemedi.');
        } finally {
            setLoading(false);
        }
    };

    const submitGuess = async () => {
        if (!guess.trim() || verifying) return;
        setVerifying(true);
        try {
            const res = await api.post('/game/flag-eleven/verify', {
                puzzle_id: puzzleIdRef.current,
                team_guess: guess.trim(),
            });

            if (res.data.correct) {
                setGameOver({ won: true, teamName: res.data.team_name });
            } else {
                setWrongCount(res.data.wrong_attempts);
                setHints(res.data.hints || {});
                setGuess('');
                if (res.data.wrong_attempts >= 3) {
                    setGameOver({ won: false, teamName: res.data.team_name });
                } else {
                    Alert.alert('Yanlış!', `${3 - res.data.wrong_attempts} hakkın kaldı.`);
                }
            }
        } catch (err) {
            Alert.alert('Hata', 'Tahmin gönderilirken bir hata oluştu.');
        } finally {
            setVerifying(false);
        }
    };

    if (loading || !puzzle) {
        return (
            <View style={[GLOBAL_STYLES.screen, GLOBAL_STYLES.center]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={{ color: COLORS.text, marginTop: 10 }}>Bulmaca Hazırlanıyor...</Text>
            </View>
        );
    }

    if (gameOver) {
        return (
            <ScrollView contentContainerStyle={{ padding: 20, alignItems: 'center', paddingBottom: 60 }}>
                <Text style={{ color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 32, marginBottom: 20, textAlign: 'center' }}>
                    {gameOver.won ? 'BULDUN! 🎉' : 'HAKLARIN BİTTİ 😔'}
                </Text>
                <Text style={{ color: COLORS.primary, fontFamily: FONTS.headingBlack, fontSize: 22, marginBottom: 30 }}>
                    Cevap: {gameOver.teamName}
                </Text>
                <TouchableOpacity style={[GLOBAL_STYLES.primaryButton, { width: '100%' }]} onPress={loadPuzzle}>
                    <Text style={GLOBAL_STYLES.primaryButtonText}>YENİ BULMACA</Text>
                </TouchableOpacity>
            </ScrollView>
        );
    }

    const groups = groupPositions(puzzle.positions);

    return (
        <ImageBackground source={require('../../assets/background.png')} style={GLOBAL_STYLES.screen} imageStyle={{ opacity: 0.15 }} resizeMode="cover">
            <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
                <View style={styles.headerCard}>
                    <Text style={styles.headerTitle}>Bayrak XI</Text>
                    <Text style={styles.headerSub}>Bu kadronun hangi takım olduğunu bul</Text>
                    <Text style={styles.rightsText}>{3 - wrongCount}/3 hak kaldı</Text>
                    {hints.country && <Text style={styles.hintText}>İpucu: Ülke — {hints.country}</Text>}
                    {hints.year && <Text style={styles.hintText}>İpucu: Sezon — {hints.year}</Text>}
                </View>

                {groups.map(g => (
                    <View key={g.role} style={styles.roleRow}>
                        <Text style={styles.roleLabel}>{g.role}</Text>
                        <View style={styles.flagRow}>
                            {g.items.map((p, idx) => (
                                <View key={idx} style={styles.flagPill}>
                                    <Text style={styles.flagText}>{p.nationality}</Text>
                                </View>
                            ))}
                        </View>
                    </View>
                ))}

                <View style={{ marginTop: 20 }}>
                    <TextInput
                        style={styles.input}
                        placeholder="Takım adını yaz..."
                        placeholderTextColor={COLORS.textMuted}
                        value={guess}
                        onChangeText={setGuess}
                        onSubmitEditing={submitGuess}
                    />
                    <TouchableOpacity
                        style={[GLOBAL_STYLES.primaryButton, { marginTop: 15 }, verifying && { opacity: 0.5 }]}
                        onPress={submitGuess}
                        disabled={verifying}
                    >
                        {verifying ? <ActivityIndicator color={COLORS.background} /> : <Text style={GLOBAL_STYLES.primaryButtonText}>TAHMİN ET</Text>}
                    </TouchableOpacity>
                </View>
            </ScrollView>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    headerCard: { backgroundColor: '#0e3609', padding: 20, borderRadius: 24, alignItems: 'center', borderWidth: 4, borderColor: '#4a840a', borderBottomWidth: 8, marginBottom: 20 },
    headerTitle: { color: '#95c029', fontSize: 26, fontFamily: FONTS.headingBlack, textAlign: 'center' },
    headerSub: { color: '#FFF', fontSize: 13, fontFamily: FONTS.body, textAlign: 'center', marginTop: 5, opacity: 0.9 },
    rightsText: { color: COLORS.primary, fontFamily: FONTS.mono, fontSize: 16, marginTop: 10 },
    hintText: { color: '#fcc205', fontFamily: FONTS.mono, fontSize: 13, marginTop: 6 },

    roleRow: { marginBottom: 12 },
    roleLabel: { color: COLORS.textMuted, fontFamily: FONTS.mono, fontSize: 12, marginBottom: 6 },
    flagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
    flagPill: { backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)', borderRadius: 12, paddingVertical: 8, paddingHorizontal: 12 },
    flagText: { color: COLORS.text, fontFamily: FONTS.mono, fontSize: 13 },

    input: { backgroundColor: 'rgba(255,255,255,0.05)', color: COLORS.text, height: 50, borderRadius: 12, paddingHorizontal: 15, fontSize: 16, borderWidth: 1, borderColor: COLORS.primary },
});
