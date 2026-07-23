import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Animated, Easing, Alert, ActivityIndicator, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, FONTS, GLOBAL_STYLES } from '../../theme';
import SocketService from '../../services/SocketService';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

const ROLE_LABELS = { Goalkeeper: 'Kaleci', Defender: 'Defans', Midfield: 'Ortasaha', Attack: 'Forvet' };

export default function MultiplayerExtremeSquadScreen({ route, navigation }) {
    const { tier } = route.params;
    const [gameState, setGameState] = useState('finding'); // finding, playing, result
    const [user, setUser] = useState(null);
    const [puzzle, setPuzzle] = useState(null);
    const [squad, setSquad] = useState([]);
    const [opponentLocked, setOpponentLocked] = useState(0);
    const [timeLeft, setTimeLeft] = useState(90);
    const [resultData, setResultData] = useState(null);
    const [opponentDisconnected, setOpponentDisconnected] = useState(false);

    const [isSearchVisible, setSearchVisible] = useState(false);
    const [currentSlotIndex, setCurrentSlotIndex] = useState(-1);

    const submittedRef = useRef(false);
    const squadRef = useRef([]);
    const puzzleRef = useRef(null);

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
                SocketService.on('player_disconnected', () => setOpponentDisconnected(true));
                SocketService.on('player_reconnected', () => setOpponentDisconnected(false));
                SocketService.on('error', handleError);

                SocketService.send('join_queue', { game_mode: 'extreme_squad', tier });
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
                setTimeLeft(prev => {
                    if (prev <= 1) {
                        clearInterval(timer);
                        if (!submittedRef.current) submitSquad();
                        return 0;
                    }
                    return prev - 1;
                });
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
        if (data.action === 'extreme_ready') {
            setPuzzle(data.puzzle);
            puzzleRef.current = data.puzzle;
            const empty = data.puzzle.slots.map(() => null);
            setSquad(empty);
            squadRef.current = empty;
            setOpponentLocked(0);
            setTimeLeft(90);
            submittedRef.current = false;
        } else if (data.action === 'extreme_slot_locked') {
            if (data.user_id !== String(user?.id)) {
                setOpponentLocked(prev => prev + 1);
            }
        }
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
        SocketService.send('leave_queue', { game_mode: 'extreme_squad', tier });
        SocketService.disconnect();
        navigation.goBack();
    };

    const openSearch = (index) => {
        if (squadRef.current[index]) return;
        setCurrentSlotIndex(index);
        setSearchVisible(true);
    };

    const handlePlayerSelect = async (player) => {
        if (squadRef.current.some(p => p?.id === player.id)) {
            Alert.alert('Geçersiz Seçim', 'Bu oyuncuyu zaten seçtiniz!');
            return;
        }

        setSearchVisible(false);
        try {
            const slot = puzzleRef.current.slots[currentSlotIndex];
            const res = await api.post('/games/extreme-squad/validate-single', {
                team_id: slot.team_id,
                role: slot.role,
                player_id: player.id,
            });

            if (res.data.valid) {
                const newSquad = [...squadRef.current];
                newSquad[currentSlotIndex] = { id: player.id, name: player.name };
                squadRef.current = newSquad;
                setSquad(newSquad);
                SocketService.send('extreme_lock_slot', { slot_id: slot.slot_id });
            } else {
                Alert.alert('Hatalı Seçim', res.data.message);
            }
        } catch (err) {
            Alert.alert('Hata', 'Oyuncu doğrulanırken bir hata oluştu.');
        }
    };

    const submitSquad = () => {
        if (submittedRef.current) return;
        submittedRef.current = true;
        const playerIds = squadRef.current.map(s => s ? s.id : null);
        SocketService.send('extreme_submit', { player_ids: playerIds });
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
        if (!puzzle) return null;
        const filledCount = squad.filter(Boolean).length;

        return (
            <ImageBackground source={require('../../assets/background.png')} style={GLOBAL_STYLES.screen} imageStyle={{ opacity: 0.15 }} resizeMode="cover">
                <ScrollView contentContainerStyle={{ paddingBottom: 40 }}>
                    <View style={styles.turnIndicator}>
                        <Text style={styles.turnText}>{puzzle.criterion === 'tallest' ? 'En Uzun Kadro' : 'En Genç Kadro'}</Text>
                        <Text style={{ color: timeLeft <= 15 ? COLORS.danger : COLORS.primary, fontSize: 24, fontWeight: 'bold' }}>⏱️ {timeLeft}s</Text>
                        <Text style={{ color: '#FFF', marginTop: 5, fontFamily: FONTS.mono, opacity: 0.8 }}>
                            Sen: {filledCount}/11 · Rakip: {opponentLocked}/11
                        </Text>
                    </View>

                    <View style={{ padding: 15, gap: 10 }}>
                        {puzzle.slots.map((slot, index) => {
                            const player = squad[index];
                            return (
                                <TouchableOpacity
                                    key={slot.slot_id}
                                    style={[styles.slotBase, player && styles.slotFilled]}
                                    onPress={() => openSearch(index)}
                                    disabled={!!player}
                                >
                                    <Text style={styles.slotLabel}>{ROLE_LABELS[slot.role]} · {slot.team_name}</Text>
                                    <Text style={player ? styles.slotPlayerName : styles.slotPlaceholder}>
                                        {player ? player.name : 'Oyuncu Seç +'}
                                    </Text>
                                </TouchableOpacity>
                            );
                        })}
                    </View>

                    <View style={{ padding: 20 }}>
                        <TouchableOpacity
                            style={[GLOBAL_STYLES.primaryButton, filledCount < 11 ? { opacity: 0.5, backgroundColor: COLORS.secondary } : { backgroundColor: COLORS.primary }]}
                            onPress={submitSquad}
                            disabled={filledCount < 11}
                        >
                            <Text style={GLOBAL_STYLES.primaryButtonText}>
                                {filledCount === 11 ? 'Kilitle ve Gönder' : `Slotları Doldur (${filledCount}/11)`}
                            </Text>
                        </TouchableOpacity>
                    </View>

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
        const isDraw = resultData.winner_id === null;
        const myResult = resultData.results ? resultData.results[String(user?.id)] : null;

        return (
            <ScrollView contentContainerStyle={{ padding: 20, alignItems: 'center', paddingBottom: 60 }}>
                <Text style={{ color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 36, marginBottom: 20, textAlign: 'center' }}>
                    {isDraw ? 'BERABERE 🤝' : isWinner ? 'KAZANDIN! 🎉' : 'KAYBETTİN 😔'}
                </Text>

                {myResult && (
                    <Text style={{ color: COLORS.textMuted, fontFamily: FONTS.mono, marginBottom: 20, textAlign: 'center' }}>
                        {myResult.valid ? `Toplam: ${myResult.total_value} — Teorik En İyi: ${myResult.theoretical_best}` : 'Kadron geçersizdi.'}
                    </Text>
                )}

                <TouchableOpacity style={[GLOBAL_STYLES.primaryButton, { width: '100%', marginTop: 10 }]} onPress={() => navigation.navigate('MainTabs')}>
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

    turnIndicator: { alignItems: 'center', padding: 20, backgroundColor: '#0e3609', borderBottomWidth: 4, borderColor: '#4a840a' },
    turnText: { fontFamily: FONTS.headingBlack, fontSize: 22, marginBottom: 5, color: '#FFF' },

    slotBase: { backgroundColor: '#4a840a', borderWidth: 3, borderColor: '#95c029', borderBottomWidth: 6, borderRadius: 16, padding: 14 },
    slotFilled: { borderColor: '#fcc205', backgroundColor: '#0e3609', borderBottomWidth: 3 },
    slotLabel: { color: 'rgba(255,255,255,0.7)', fontFamily: FONTS.mono, fontSize: 11, marginBottom: 4 },
    slotPlaceholder: { color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 16 },
    slotPlayerName: { color: '#fcc205', fontFamily: FONTS.headingBlack, fontSize: 16 },
});
