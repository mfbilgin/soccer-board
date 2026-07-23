import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Animated, Easing, Alert, ActivityIndicator, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, FONTS, GLOBAL_STYLES } from '../../theme';
import SocketService from '../../services/SocketService';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

export default function MultiplayerInitialsGuessScreen({ route, navigation }) {
    const { tier } = route.params;
    const [gameState, setGameState] = useState('finding'); // finding, picking, guessing, result
    const [user, setUser] = useState(null);
    const [role, setRole] = useState(null); // 'start' | 'end'
    const [myPool, setMyPool] = useState([]);
    const [pickedLetter, setPickedLetter] = useState(null);
    const [roundLetters, setRoundLetters] = useState(null); // {start_letter, end_letter}
    const [roundNum, setRoundNum] = useState(1);
    const [score, setScore] = useState({});
    const [timeLeft, setTimeLeft] = useState(30);
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
                SocketService.on('initials_wrong', handleWrong);
                SocketService.on('player_disconnected', () => setOpponentDisconnected(true));
                SocketService.on('player_reconnected', () => setOpponentDisconnected(false));
                SocketService.on('error', handleError);

                SocketService.send('join_queue', { game_mode: 'initials_guess', tier });
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
            SocketService.off('initials_wrong', handleWrong);
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
        } else if (gameState === 'guessing' && !opponentDisconnected) {
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

    const handleMatchFound = () => setGameState('picking');

    const handleGameUpdate = (data) => {
        if (data.action === 'initials_pick_phase') {
            const myRole = data.start_picker === String(user?.id) ? 'start' : 'end';
            setRole(myRole);
            setMyPool(myRole === 'start' ? data.start_pool : data.end_pool);
            setPickedLetter(null);
            setRoundNum(data.round_num);
            setScore(data.score);
            setLastRoundResult(null);
            setGameState('picking');
        } else if (data.action === 'initials_round_ready') {
            setRoundLetters({ start_letter: data.start_letter, end_letter: data.end_letter });
            turnEndRef.current = data.turn_end_time;
            setGameState('guessing');
        } else if (data.action === 'initials_round_result') {
            setScore(data.score);
            setLastRoundResult(data.round_winner);
        }
    };

    const handleWrong = () => {
        Alert.alert('Yanlış', 'Bu oyuncu harflere uymuyor.');
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
        SocketService.send('leave_queue', { game_mode: 'initials_guess', tier });
        SocketService.disconnect();
        navigation.goBack();
    };

    const pickLetter = (letter) => {
        setPickedLetter(letter);
        SocketService.send('initials_pick_letter', { letter });
    };

    const handlePlayerSelect = (player) => {
        setSearchVisible(false);
        SocketService.send('initials_guess_answer', { entity_id: player.id });
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

    const renderPicking = () => (
        <View style={{ flex: 1, padding: 20, justifyContent: 'center' }}>
            <Text style={styles.pickTitle}>
                {role === 'start' ? 'Başlangıç harfini seç' : 'Bitiş harfini seç'}
            </Text>
            <Text style={styles.pickSub}>Tur {roundNum} · İlk 3'e</Text>
            <View style={styles.letterGrid}>
                {myPool.map(letter => (
                    <TouchableOpacity
                        key={letter}
                        style={[styles.letterChoice, pickedLetter === letter && styles.letterChosen]}
                        onPress={() => !pickedLetter && pickLetter(letter)}
                        disabled={!!pickedLetter}
                    >
                        <Text style={styles.letterChoiceText}>{letter}</Text>
                    </TouchableOpacity>
                ))}
            </View>
            {pickedLetter && <Text style={styles.waitingText}>Rakip bekleniyor...</Text>}
        </View>
    );

    const renderGuessing = () => {
        if (!roundLetters) return null;
        const myScore = score[String(user?.id)] || 0;
        const oppUid = Object.keys(score).find(uid => uid !== String(user?.id));
        const oppScore = oppUid ? score[oppUid] : 0;

        return (
            <ImageBackground source={require('../../assets/background.png')} style={GLOBAL_STYLES.screen} imageStyle={{ opacity: 0.15 }} resizeMode="cover">
                <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
                    <View style={styles.scoreBar}>
                        <Text style={styles.scoreText}>Sen: {myScore}</Text>
                        <Text style={{ color: COLORS.textMuted, fontFamily: FONTS.mono }}>Tur {roundNum}</Text>
                        <Text style={styles.scoreText}>Rakip: {oppScore}</Text>
                    </View>

                    <View style={styles.turnIndicator}>
                        <Text style={{ color: timeLeft <= 10 ? COLORS.danger : COLORS.primary, fontSize: 28, fontWeight: 'bold' }}>⏱️ {timeLeft}s</Text>
                        {lastRoundResult !== undefined && lastRoundResult !== null && (
                            <Text style={styles.roundBanner}>
                                {lastRoundResult === String(user?.id) ? 'Bu turu kazandın!' : 'Rakip bu turu kazandı!'}
                            </Text>
                        )}
                    </View>

                    <View style={styles.lettersRow}>
                        <View style={styles.letterBox}><Text style={styles.letterText}>{roundLetters.start_letter}</Text></View>
                        <Text style={styles.dots}>. . .</Text>
                        <View style={styles.letterBox}><Text style={styles.letterText}>{roundLetters.end_letter}</Text></View>
                    </View>
                    <Text style={styles.hintText}>Bu harflerle başlayıp biten bir futbolcuyu ilk yazan turu kazanır!</Text>

                    <TouchableOpacity style={[GLOBAL_STYLES.primaryButton, { marginTop: 30 }]} onPress={() => setSearchVisible(true)}>
                        <Text style={GLOBAL_STYLES.primaryButtonText}>Oyuncu Yaz</Text>
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
            {gameState === 'picking' && renderPicking()}
            {gameState === 'guessing' && renderGuessing()}
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

    pickTitle: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 24, textAlign: 'center' },
    pickSub: { color: COLORS.textMuted, fontFamily: FONTS.mono, fontSize: 13, textAlign: 'center', marginTop: 8, marginBottom: 30 },
    letterGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', gap: 12 },
    letterChoice: { width: 60, height: 60, borderRadius: 16, backgroundColor: '#4a840a', borderWidth: 3, borderColor: '#95c029', justifyContent: 'center', alignItems: 'center' },
    letterChosen: { backgroundColor: '#0e3609', borderColor: '#fcc205' },
    letterChoiceText: { color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 24 },
    waitingText: { color: COLORS.textMuted, fontFamily: FONTS.mono, textAlign: 'center', marginTop: 20 },

    scoreBar: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
    scoreText: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 20 },
    turnIndicator: { alignItems: 'center', padding: 15, backgroundColor: '#0e3609', borderRadius: 16, marginBottom: 20 },
    roundBanner: { color: COLORS.primary, fontFamily: FONTS.mono, marginTop: 8, textAlign: 'center' },

    lettersRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 15 },
    letterBox: { width: 60, height: 60, borderRadius: 16, backgroundColor: '#4a840a', borderWidth: 3, borderColor: '#95c029', justifyContent: 'center', alignItems: 'center' },
    letterText: { color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 30 },
    dots: { color: COLORS.textMuted, fontSize: 20 },
    hintText: { color: COLORS.textMuted, fontFamily: FONTS.body, fontSize: 13, textAlign: 'center', marginTop: 20 },
});
