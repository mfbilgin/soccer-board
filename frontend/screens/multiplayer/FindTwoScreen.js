import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Animated, Easing, Alert, ActivityIndicator, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, FONTS, GLOBAL_STYLES } from '../../theme';
import SocketService from '../../services/SocketService';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

export default function FindTwoScreen({ route, navigation }) {
    const { tier } = route.params;
    const [gameState, setGameState] = useState('finding'); // finding, playing, result
    const [user, setUser] = useState(null);
    const [round, setRound] = useState(null);
    const [roundNum, setRoundNum] = useState(1);
    const [score, setScore] = useState({});
    const [timeLeft, setTimeLeft] = useState(30);
    const [locked, setLocked] = useState(false);
    const [lastRoundResult, setLastRoundResult] = useState(null);
    const [resultData, setResultData] = useState(null);
    const [opponentDisconnected, setOpponentDisconnected] = useState(false);

    const [isSearchVisible, setSearchVisible] = useState(false);

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
                SocketService.on('find_two_wrong', handleWrongGuess);
                SocketService.on('player_disconnected', () => setOpponentDisconnected(true));
                SocketService.on('player_reconnected', () => setOpponentDisconnected(false));
                SocketService.on('error', handleError);

                SocketService.send('join_queue', { game_mode: 'find_two', tier });
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
            SocketService.off('find_two_wrong', handleWrongGuess);
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
        if (data.action === 'find_two_round_ready') {
            setRound(data.round);
            setRoundNum(data.round_num);
            setScore(data.score);
            turnEndRef.current = data.turn_end_time;
            setLocked(false);
            setLastRoundResult(null);
        } else if (data.action === 'find_two_round_result') {
            setScore(data.score);
            setLastRoundResult(data.round_winner);
        }
    };

    const handleWrongGuess = () => {
        setLocked(true);
        setTimeout(() => setLocked(false), 3000);
    };

    const handleGameResult = (data) => {
        setSearchVisible(false);
        setResultData(data);
        setGameState('result');
    };

    const handleError = (err) => {
        Alert.alert('Hata', err.message || 'Bir hata oluştu.');
        navigation.goBack();
    };

    const handleCancel = () => {
        SocketService.send('leave_queue', { game_mode: 'find_two', tier });
        SocketService.disconnect();
        navigation.goBack();
    };

    const handlePlayerSelect = (player) => {
        setSearchVisible(false);
        SocketService.send('find_two_guess', { entity_id: player.id });
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
        if (!round) return null;
        const myScore = score[String(user?.id)] || 0;
        const oppUid = Object.keys(score).find(uid => uid !== String(user?.id));
        const oppScore = oppUid ? score[oppUid] : 0;

        return (
            <ImageBackground source={require('../../assets/background.png')} style={GLOBAL_STYLES.screen} imageStyle={{ opacity: 0.15 }} resizeMode="cover">
                <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
                    <View style={styles.scoreBar}>
                        <Text style={styles.scoreText}>Sen: {myScore}</Text>
                        <Text style={{ color: COLORS.textMuted, fontFamily: FONTS.mono }}>Tur {roundNum} (İlk 3'e)</Text>
                        <Text style={styles.scoreText}>Rakip: {oppScore}</Text>
                    </View>

                    <View style={styles.turnIndicator}>
                        <Text style={{ color: timeLeft <= 10 ? COLORS.danger : COLORS.primary, fontSize: 28, fontWeight: 'bold' }}>⏱️ {timeLeft}s</Text>
                        {lastRoundResult !== null && (
                            <Text style={styles.roundBanner}>
                                {lastRoundResult === null ? 'Süre doldu, tur berabere!' : lastRoundResult === String(user?.id) ? 'Bu turu kazandın!' : 'Rakip bu turu kazandı!'}
                            </Text>
                        )}
                    </View>

                    <View style={styles.criteriaBox}>
                        {round.kind === 'team_team' ? (
                            <>
                                <View style={styles.criteriaPill}><Text style={styles.criteriaText}>{round.team_a_name}</Text></View>
                                <Text style={styles.andText}>&</Text>
                                <View style={styles.criteriaPill}><Text style={styles.criteriaText}>{round.team_b_name}</Text></View>
                            </>
                        ) : (
                            <>
                                <View style={styles.criteriaPill}><Text style={styles.criteriaText}>{round.team_a_name}</Text></View>
                                <Text style={styles.andText}>&</Text>
                                <View style={styles.criteriaPill}><Text style={styles.criteriaText}>{round.country}</Text></View>
                            </>
                        )}
                    </View>
                    <Text style={styles.hintText}>Her iki kritere de uyan bir futbolcuyu ilk yazan turu kazanır!</Text>

                    <TouchableOpacity
                        style={[GLOBAL_STYLES.primaryButton, { marginTop: 30 }, locked && { opacity: 0.5, backgroundColor: COLORS.secondary }]}
                        onPress={() => !locked && setSearchVisible(true)}
                        disabled={locked}
                    >
                        <Text style={GLOBAL_STYLES.primaryButtonText}>{locked ? 'Bekle... (3sn ceza)' : 'Oyuncu Yaz'}</Text>
                    </TouchableOpacity>

                    <SearchModal visible={isSearchVisible} onClose={() => setSearchVisible(false)} onSelect={handlePlayerSelect} searchType={1} />
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

        return (
            <ScrollView contentContainerStyle={{ padding: 20, alignItems: 'center', paddingBottom: 60 }}>
                <Text style={{ color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 36, marginBottom: 20, textAlign: 'center' }}>
                    {isWinner ? 'KAZANDIN! 🎉' : 'KAYBETTİN 😔'}
                </Text>
                <Text style={{ color: COLORS.textMuted, fontFamily: FONTS.mono, marginBottom: 20 }}>
                    Skor: {resultData.score ? Object.values(resultData.score).join(' - ') : ''}
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

    scoreBar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
    scoreText: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 20 },

    turnIndicator: { alignItems: 'center', padding: 15, backgroundColor: '#0e3609', borderRadius: 16, marginBottom: 20 },
    roundBanner: { color: COLORS.primary, fontFamily: FONTS.mono, marginTop: 8, textAlign: 'center' },

    criteriaBox: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 15, flexWrap: 'wrap' },
    criteriaPill: { backgroundColor: '#4a840a', borderWidth: 3, borderColor: '#95c029', borderBottomWidth: 6, borderRadius: 16, paddingVertical: 16, paddingHorizontal: 20 },
    criteriaText: { color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 18, textAlign: 'center' },
    andText: { color: COLORS.textMuted, fontFamily: FONTS.headingBlack, fontSize: 20 },
    hintText: { color: COLORS.textMuted, fontFamily: FONTS.body, fontSize: 13, textAlign: 'center', marginTop: 20 },
});
