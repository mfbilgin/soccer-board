import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Animated, Easing, Alert, ActivityIndicator, TextInput, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, FONTS, GLOBAL_STYLES } from '../../theme';
import SocketService from '../../services/SocketService';
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

export default function MultiplayerFlagElevenScreen({ route, navigation }) {
    const { tier } = route.params;
    const [gameState, setGameState] = useState('finding'); // finding, playing, result
    const [user, setUser] = useState(null);
    const [positions, setPositions] = useState(null);
    const [guess, setGuess] = useState('');
    const [wrongCount, setWrongCount] = useState(0);
    const [timeLeft, setTimeLeft] = useState(30);
    const [resultData, setResultData] = useState(null);
    const [opponentDisconnected, setOpponentDisconnected] = useState(false);

    const turnEndRef = useRef(0);
    const pulseAnim = useRef(new Animated.Value(1)).current;
    const opacityAnim = useRef(new Animated.Value(0.5)).current;
    const [searchTime, setSearchTime] = useState(0);

    useEffect(() => {
        loadProfile();

        const initSocket = async () => {
            try {
                await SocketService.connect();
                SocketService.on('match_found', handleMatchFound);
                SocketService.on('game_update', handleGameUpdate);
                SocketService.on('game_over', handleGameResult);
                SocketService.on('flag_eleven_wrong', handleWrongGuess);
                SocketService.on('player_disconnected', () => setOpponentDisconnected(true));
                SocketService.on('player_reconnected', () => setOpponentDisconnected(false));
                SocketService.on('error', handleError);

                SocketService.send('join_queue', { game_mode: 'flag_eleven', tier });
            } catch (err) {
                Alert.alert('Bağlantı Hatası', 'Sunucuya bağlanılamadı.');
                navigation.goBack();
            }
        };

        initSocket();

        return () => {
            SocketService.off('match_found', handleMatchFound);
            SocketService.off('game_update', handleGameUpdate);
            SocketService.off('game_over', handleGameResult);
            SocketService.off('flag_eleven_wrong', handleWrongGuess);
            SocketService.off('player_disconnected');
            SocketService.off('player_reconnected');
            SocketService.off('error', handleError);
            SocketService.disconnect();
        };
    }, []);

    useEffect(() => {
        let timer;
        if (gameState === 'finding') {
            timer = setInterval(() => setSearchTime(prev => prev + 1), 1000);
            Animated.loop(
                Animated.parallel([
                    Animated.timing(pulseAnim, { toValue: 2, duration: 1500, easing: Easing.out(Easing.ease), useNativeDriver: true }),
                    Animated.timing(opacityAnim, { toValue: 0, duration: 1500, easing: Easing.out(Easing.ease), useNativeDriver: true })
                ])
            ).start();
        } else if (gameState === 'playing' && !opponentDisconnected) {
            timer = setInterval(() => {
                const now = Date.now() / 1000;
                let rem = Math.ceil(turnEndRef.current - now);
                if (rem < 0) rem = 0;
                setTimeLeft(rem);
            }, 1000);
        }
        return () => clearInterval(timer);
    }, [gameState, opponentDisconnected]);

    const loadProfile = async () => {
        try {
            const res = await api.get('/auth/me');
            setUser(res.data);
        } catch (err) {
            console.log(err);
        }
    };

    const handleMatchFound = () => setGameState('playing');

    const handleGameUpdate = (data) => {
        if (data.action === 'flag_eleven_ready') {
            setPositions(data.positions);
            turnEndRef.current = data.turn_end_time;
            setWrongCount(0);
            setGuess('');
        }
    };

    const handleWrongGuess = (data) => {
        setWrongCount(data.wrong_count);
        setGuess('');
        Alert.alert('Yanlış!', data.wrong_count >= 3 ? 'Hakların bitti, rakip hâlâ deneyebilir.' : `${3 - data.wrong_count} hakkın kaldı.`);
    };

    const handleGameResult = (data) => {
        setResultData(data);
        setGameState('result');
    };

    const handleError = (err) => {
        Alert.alert('Hata', err.message || 'Bir hata oluştu.');
        navigation.goBack();
    };

    const handleCancel = () => {
        SocketService.send('leave_queue', { game_mode: 'flag_eleven', tier });
        SocketService.disconnect();
        navigation.goBack();
    };

    const submitGuess = () => {
        if (!guess.trim() || wrongCount >= 3) return;
        SocketService.send('flag_eleven_guess', { team_guess: guess.trim() });
    };

    const renderFinding = () => {
        const formatTime = (secs) => {
            const m = Math.floor(secs / 60).toString().padStart(2, '0');
            const s = (secs % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        };
        return (
            <View style={{ flex: 1, alignItems: 'center' }}>
                <View style={styles.radarContainer}>
                    <Animated.View style={[styles.radarPulse, { transform: [{ scale: pulseAnim }], opacity: opacityAnim }]} />
                    <View style={styles.radarCenter}><Text style={{ fontSize: 40 }}>🎯</Text></View>
                </View>
                <Text style={styles.findingTitle}>Rakip Aranıyor...</Text>
                <Text style={styles.findingTime}>Tahmini süre: {formatTime(searchTime)}</Text>
                <TouchableOpacity style={styles.cancelBtn} onPress={handleCancel}>
                    <Text style={styles.cancelBtnText}>✕ İPTAL ET</Text>
                </TouchableOpacity>
            </View>
        );
    };

    const renderPlaying = () => {
        if (!positions) return null;
        const groups = groupPositions(positions);
        const outOfGuesses = wrongCount >= 3;

        return (
            <ImageBackground source={require('../../assets/background.png')} style={GLOBAL_STYLES.screen} imageStyle={{ opacity: 0.15 }} resizeMode="cover">
                <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
                    <View style={styles.turnIndicator}>
                        <Text style={{ color: timeLeft <= 10 ? COLORS.danger : COLORS.primary, fontSize: 28, fontWeight: 'bold' }}>⏱️ {timeLeft}s</Text>
                        <Text style={{ color: '#FFF', fontFamily: FONTS.mono, marginTop: 5 }}>Hakların: {3 - wrongCount}/3</Text>
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
                            style={[styles.input, outOfGuesses && { opacity: 0.5 }]}
                            placeholder={outOfGuesses ? 'Hakların bitti, rakip bekleniyor...' : 'Takım adını yaz...'}
                            placeholderTextColor={COLORS.textMuted}
                            value={guess}
                            onChangeText={setGuess}
                            onSubmitEditing={submitGuess}
                            editable={!outOfGuesses}
                        />
                        <TouchableOpacity
                            style={[GLOBAL_STYLES.primaryButton, { marginTop: 15 }, outOfGuesses && { opacity: 0.5 }]}
                            onPress={submitGuess}
                            disabled={outOfGuesses}
                        >
                            <Text style={GLOBAL_STYLES.primaryButtonText}>TAHMİN ET</Text>
                        </TouchableOpacity>
                    </View>
                </ScrollView>

                {opponentDisconnected && (
                    <View style={[StyleSheet.absoluteFill, { backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'center', alignItems: 'center', zIndex: 999 }]}>
                        <ActivityIndicator size="large" color={COLORS.primary} style={{ marginBottom: 20 }} />
                        <Text style={{ color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 24, textAlign: 'center' }}>Rakibin bağlantısı koptu!</Text>
                        <Text style={{ color: COLORS.primary, fontFamily: FONTS.mono, fontSize: 16, marginTop: 10, textAlign: 'center' }}>Geri dönmesi bekleniyor...{'\n'}(Maksimum 15 Saniye)</Text>
                    </View>
                )}
            </ImageBackground>
        );
    };

    const renderResult = () => {
        if (!resultData) return null;
        const isWinner = resultData.winner_id === String(user?.id);
        const isDraw = resultData.winner_id === null;

        return (
            <ScrollView contentContainerStyle={{ padding: 20, alignItems: 'center', paddingBottom: 60 }}>
                <Text style={{ color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 36, marginBottom: 20, textAlign: 'center' }}>
                    {isDraw ? 'BERABERE 🤝' : isWinner ? 'KAZANDIN! 🎉' : 'KAYBETTİN 😔'}
                </Text>
                <Text style={{ color: COLORS.primary, fontFamily: FONTS.headingBlack, fontSize: 22, marginBottom: 30 }}>
                    Cevap: {resultData.team_name}
                </Text>
                <TouchableOpacity style={[GLOBAL_STYLES.primaryButton, { width: '100%' }]} onPress={() => navigation.navigate('MainTabs')}>
                    <Text style={GLOBAL_STYLES.primaryButtonText}>LOBİYE DÖN</Text>
                </TouchableOpacity>
            </ScrollView>
        );
    };

    return (
        <SafeAreaView style={styles.container}>
            {gameState === 'finding' && renderFinding()}
            {gameState === 'playing' && renderPlaying()}
            {gameState === 'result' && renderResult()}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    radarContainer: { width: 200, height: 200, justifyContent: 'center', alignItems: 'center', marginTop: 60, marginBottom: 40 },
    radarPulse: { position: 'absolute', width: 100, height: 100, borderRadius: 50, backgroundColor: COLORS.primary },
    radarCenter: { width: 100, height: 100, borderRadius: 50, borderWidth: 4, borderColor: COLORS.primary, backgroundColor: COLORS.surface, justifyContent: 'center', alignItems: 'center' },
    findingTitle: { color: COLORS.primary, fontFamily: FONTS.headingBlack, fontSize: 28 },
    findingTime: { color: COLORS.textMuted, fontFamily: FONTS.mono, fontSize: 16, marginTop: 10 },
    cancelBtn: { backgroundColor: '#f2b50b', paddingVertical: 15, paddingHorizontal: 40, borderRadius: 16, marginTop: 'auto', marginBottom: 40, borderWidth: 3, borderColor: '#d4a202', borderBottomWidth: 6 },
    cancelBtnText: { color: '#0e3609', fontFamily: FONTS.headingBlack, fontSize: 16 },

    turnIndicator: { alignItems: 'center', padding: 15, backgroundColor: '#0e3609', borderRadius: 16, marginBottom: 20 },

    roleRow: { marginBottom: 12 },
    roleLabel: { color: COLORS.textMuted, fontFamily: FONTS.mono, fontSize: 12, marginBottom: 6 },
    flagRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
    flagPill: { backgroundColor: 'rgba(255,255,255,0.05)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)', borderRadius: 12, paddingVertical: 8, paddingHorizontal: 12 },
    flagText: { color: COLORS.text, fontFamily: FONTS.mono, fontSize: 13 },

    input: { backgroundColor: 'rgba(255,255,255,0.05)', color: COLORS.text, height: 50, borderRadius: 12, paddingHorizontal: 15, fontSize: 16, borderWidth: 1, borderColor: COLORS.primary },
});
