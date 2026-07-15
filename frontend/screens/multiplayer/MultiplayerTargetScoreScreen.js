import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated, Easing, Alert, ScrollView, Image, ActivityIndicator, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, SIZES, FONTS, GLOBAL_STYLES } from '../../theme';
import SocketService from '../../services/SocketService';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

export default function MultiplayerTargetScoreScreen({ route, navigation }) {
    const { tier } = route.params;
    const [gameState, setGameState] = useState('finding'); // finding, playing, result
    const [user, setUser] = useState(null);
    const [gameData, setGameData] = useState(null);
    const [resultData, setResultData] = useState(null);
    const [timeLeft, setTimeLeft] = useState(90);

    // Gameplay states
    const [selectedPlayers, setSelectedPlayers] = useState([]);
    const [isSearchVisible, setSearchVisible] = useState(false);
    const [currentSlotIndex, setCurrentSlotIndex] = useState(-1);
    const [validating, setValidating] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [opponentDisconnected, setOpponentDisconnected] = useState(false);

    // Radar Animation
    const pulseAnim = useRef(new Animated.Value(1)).current;
    const opacityAnim = useRef(new Animated.Value(0.5)).current;
    
    // Matchmaking Timer
    const [searchTime, setSearchTime] = useState(0);

    useEffect(() => {
        loadProfile();
        
        const initSocket = async () => {
            try {
                await SocketService.connect();
                SocketService.on('match_found', handleMatchFound);
                SocketService.on('game_update', handleGameUpdate);
                SocketService.on('game_result', handleGameResult);
                SocketService.on('player_disconnected', () => setOpponentDisconnected(true));
                SocketService.on('player_reconnected', () => setOpponentDisconnected(false));
                SocketService.on('error', handleError);

                // Join Queue
                SocketService.send('join_queue', { game_mode: 'mode31', tier });
            } catch (err) {
                Alert.alert('Bağlantı Hatası', 'Sunucuya bağlanılamadı.');
                navigation.goBack();
            }
        };

        initSocket();

        return () => {
            SocketService.off('match_found', handleMatchFound);
            SocketService.off('game_update', handleGameUpdate);
            SocketService.off('game_result', handleGameResult);
            SocketService.off('player_disconnected');
            SocketService.off('player_reconnected');
            SocketService.off('error', handleError);
            SocketService.disconnect();
        };
    }, []);

    useEffect(() => {
        let timer;
        if (gameState === 'finding') {
            timer = setInterval(() => {
                setSearchTime(prev => prev + 1);
            }, 1000);
            
            // Start Radar Animation
            Animated.loop(
                Animated.parallel([
                    Animated.timing(pulseAnim, {
                        toValue: 2,
                        duration: 1500,
                        easing: Easing.out(Easing.ease),
                        useNativeDriver: true,
                    }),
                    Animated.timing(opacityAnim, {
                        toValue: 0,
                        duration: 1500,
                        easing: Easing.out(Easing.ease),
                        useNativeDriver: true,
                    })
                ])
            ).start();
        } else if (gameState === 'playing' && timeLeft > 0 && !submitted && !opponentDisconnected) {
            timer = setInterval(() => {
                setTimeLeft(prev => prev - 1);
            }, 1000);
        } else if (timeLeft === 0 && !submitted) {
            // Auto-submit when time is up
            submitGuess();
        }
        return () => clearInterval(timer);
    }, [gameState, timeLeft, submitted]);

    const loadProfile = async () => {
        try {
            const res = await api.get('/auth/me');
            setUser(res.data);
        } catch (err) {
            console.log(err);
        }
    };

    const handleMatchFound = (data) => {
        setGameData(data);
        if (data.puzzle) {
            setSelectedPlayers(new Array(data.puzzle.player_count).fill(null));
        }
        setGameState('playing');
        setTimeLeft(90);
    };

    const handleGameUpdate = (data) => {
        if (data.action === 'puzzle_ready' && data.puzzle) {
            setGameData(prev => ({ ...prev, puzzle: data.puzzle }));
            setSelectedPlayers(new Array(data.puzzle.player_count).fill(null));
        }
    };

    const handleGameResult = (data) => {
        setSearchVisible(false);
        setResultData(data);
        setGameState('result');
    };

    const handleError = (err) => {
        Alert.alert('Hata', err.message || "Bir hata oluştu.");
        navigation.goBack();
    };

    const handleCancel = () => {
        SocketService.send('leave_queue', { game_mode: 'mode31', tier });
        SocketService.disconnect();
        navigation.goBack();
    };

    const handleSurrender = () => {
        Alert.alert(
            "Teslim Ol",
            "Pes edersen maçı anında kaybedersin. Emin misin?",
            [
                { text: "Vazgeç", style: "cancel" },
                { 
                    text: "Pes Et", 
                    style: "destructive",
                    onPress: () => {
                        setSearchVisible(false);
                        SocketService.send('surrender', {});
                    }
                }
            ]
        );
    };

    const openSearch = (index) => {
        setCurrentSlotIndex(index);
        setSearchVisible(true);
    };

    const handlePlayerSelect = async (player) => {
        if (selectedPlayers.some(p => p?.id === player.id)) {
            Alert.alert("Geçersiz Seçim", "Bu oyuncuyu zaten seçtiniz!");
            return;
        }

        setSearchVisible(false);
        setValidating(true);

        try {
            const res = await api.post('/mode31/validate-single', {
                league: gameData.puzzle.league,
                metric: gameData.puzzle.metric,
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
            Alert.alert("Hata", "Doğrulama yapılamadı.");
        } finally {
            setValidating(false);
        }
    };

    const submitGuess = () => {
        setSearchVisible(false);
        setSubmitted(true);
        const playerIds = selectedPlayers.filter(p => p !== null).map(p => p.id);
        SocketService.send('game_action', { action: 'submit_guess', player_ids: playerIds });
    };

    const renderGameplay = () => {
        const puzzle = gameData?.puzzle;
        if (!puzzle) return null;

        const metricLabel = {
            goals: 'Gol',
            assists: 'Asist',
            appearances: 'Maç',
            yellow_cards: 'Sarı Kart',
            red_cards: 'Kırmızı Kart',
            minutes_played: 'Oynanan Dakika',
            caps: 'Milli Maç'
        }[puzzle.metric] || puzzle.metric;

        const isSmall = puzzle.player_count > 3;

        return (
            <ImageBackground 
                source={require('../../assets/background.png')} 
                style={GLOBAL_STYLES.screen}
                imageStyle={{ opacity: 0.15 }}
                resizeMode="cover"
            >
            <ScrollView contentContainerStyle={{paddingBottom: 40}}>
                <View style={{flexDirection: 'row', justifyContent: 'center', marginVertical: 10}}>
                    <Text style={{color: COLORS.secondary, fontSize: 24, fontWeight: 'bold'}}>⏱️ {timeLeft}s</Text>
                </View>

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
                        <TouchableOpacity 
                            key={index} 
                            style={[
                                styles.playerSlotBase, 
                                player ? styles.slotFilled : {},
                                isSmall ? styles.playerSlotSmall : styles.playerSlotBig
                            ]}
                            onPress={() => openSearch(index)}
                            disabled={player !== null || submitted}
                        >
                            {player ? (
                                <View style={isSmall ? styles.playerContentRow : styles.playerContentCol}>
                                    <Image 
                                        source={{ uri: player.image_url || 'https://cdn-icons-png.flaticon.com/512/847/847969.png' }} 
                                        style={isSmall ? styles.playerImageSmall : styles.playerImageBig} 
                                    />
                                    <Text style={[styles.playerName, isSmall ? {flex: 1, textAlign: 'left'} : {textAlign: 'center'}]}>
                                        {player.name}
                                    </Text>
                                </View>
                            ) : (
                                <Text style={styles.slotPlaceholder}>Futbolcu Seç +</Text>
                            )}
                        </TouchableOpacity>
                    ))}
                </View>

                <View style={{padding: 20, marginBottom: 50}}>
                    <TouchableOpacity 
                        style={[
                            GLOBAL_STYLES.primaryButton, 
                            (validating || submitted || !selectedPlayers.every(p => p !== null)) 
                                ? {opacity: 0.5, backgroundColor: COLORS.secondary} 
                                : {backgroundColor: COLORS.primary}
                        ]} 
                        onPress={submitGuess}
                        disabled={validating || submitted || !selectedPlayers.every(p => p !== null)}
                    >
                        {validating ? (
                            <ActivityIndicator color={COLORS.background} />
                        ) : submitted ? (
                            <Text style={GLOBAL_STYLES.primaryButtonText}>Rakip Bekleniyor...</Text>
                        ) : (
                            <Text style={GLOBAL_STYLES.primaryButtonText}>Kilitle</Text>
                        )}
                    </TouchableOpacity>

                    {!submitted && (
                        <TouchableOpacity 
                            style={[GLOBAL_STYLES.primaryButton, {backgroundColor: '#e74c3c', marginTop: 15}]} 
                            onPress={handleSurrender}
                        >
                            <Text style={[GLOBAL_STYLES.primaryButtonText, {color: '#FFF'}]}>Teslim Ol</Text>
                        </TouchableOpacity>
                    )}
                </View>

                    <SearchModal 
                        visible={isSearchVisible}
                        onClose={() => setSearchVisible(false)}
                        onSelect={handlePlayerSelect}
                        searchType={1}
                    />
                </ScrollView>
                
                {opponentDisconnected && (
                    <View style={[StyleSheet.absoluteFill, {backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'center', alignItems: 'center', zIndex: 999}]}>
                        <ActivityIndicator size="large" color={COLORS.primary} style={{marginBottom: 20}} />
                        <Text style={{color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 24, textAlign: 'center'}}>Rakibin bağlantısı koptu!</Text>
                        <Text style={{color: COLORS.primary, fontFamily: FONTS.mono, fontSize: 16, marginTop: 10, textAlign: 'center'}}>Geri dönmesi bekleniyor...{'\n'}(Maksimum 15 Saniye)</Text>
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
            <View style={[styles.center, {flex: 1}]}>
                <Text style={{color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 40, marginBottom: 20, textAlign: 'center'}}>
                    {isDraw ? 'BERABERE 🤝' : isWinner ? 'KAZANDIN! 🎉' : 'KAYBETTİN 😔'}
                </Text>
                
                <View style={{backgroundColor: '#0e3609', width: '90%', borderRadius: 24, padding: 25, borderWidth: 4, borderColor: '#4a840a', borderBottomWidth: 8, alignItems: 'center'}}>
                    <Text style={{color: '#95c029', fontFamily: FONTS.headingBlack, fontSize: 18, marginBottom: 15, textTransform: 'uppercase', letterSpacing: 1}}>Maç Sonucu</Text>
                    
                    {Object.keys(resultData.results).map(uid => {
                        const r = resultData.results[uid];
                        const isMe = uid === String(user?.id);
                        
                        let displayDistance = r.distance;
                        if (r.distance === 999999) displayDistance = "Hükmen/Pes";
                        
                        return (
                            <View key={uid} style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', width: '100%', backgroundColor: isMe ? '#4a840a' : 'rgba(255,255,255,0.05)', padding: 15, borderRadius: 16, marginBottom: 10, borderWidth: isMe ? 3 : 0, borderColor: '#95c029'}}>
                                <Text style={{color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 18}}>{isMe ? 'Sen' : 'Rakip'}</Text>
                                <View style={{alignItems: 'flex-end'}}>
                                    <Text style={{color: isMe ? '#fcc205' : '#FFF', fontFamily: FONTS.headingBlack, fontSize: 28}}>{r.total_sum}</Text>
                                    <Text style={{color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 12, opacity: 0.8}}>Fark: {displayDistance}</Text>
                                </View>
                            </View>
                        );
                    })}
                </View>

                <TouchableOpacity style={[styles.actionBtn, styles.actionBtnPrimary, {width: '90%', marginTop: 30}]} onPress={() => navigation.navigate('MainTabs')}>
                    <Text style={styles.actionBtnTextPrimary}>LOBİYE DÖN</Text>
                </TouchableOpacity>
            </View>
        );
    };

    const renderFinding = () => {
        const formatTime = (secs) => {
            const m = Math.floor(secs / 60).toString().padStart(2, '0');
            const s = (secs % 60).toString().padStart(2, '0');
            return `${m}:${s}`;
        };

        return (
            <View style={{flex: 1, alignItems: 'center'}}>
                <View style={styles.radarContainer}>
                    <Animated.View style={[styles.radarPulse, { transform: [{scale: pulseAnim}], opacity: opacityAnim }]} />
                    <View style={styles.radarCenter}>
                        <Text style={{fontSize: 40}}>🎯</Text>
                    </View>
                </View>
                <Text style={styles.findingTitle}>Rakip Aranıyor...</Text>
                <Text style={styles.findingTime}>Tahmini süre: {formatTime(searchTime)}</Text>
                <View style={styles.vsContainer}>
                    <View style={styles.playerCardFinding}>
                        <View style={styles.playerAvatarMe}>
                            <Text style={{fontSize: 40}}>😎</Text>
                        </View>
                        <Text style={styles.playerName}>Sen</Text>
                        <Text style={styles.playerRating}>⭐ {user?.rating || 1200}</Text>
                    </View>
                    <View style={styles.vsBadge}>
                        <Text style={styles.vsText}>VS</Text>
                    </View>
                    <View style={styles.playerCardFinding}>
                        <View style={styles.playerAvatarOpponent}>
                            <Text style={{fontSize: 40, opacity: 0.5}}>👤</Text>
                        </View>
                        <Text style={[styles.playerName, {color: COLORS.textMuted}]}>Ara...</Text>
                        <Text style={[styles.playerRating, {color: COLORS.textMuted}]}>⭐ ???</Text>
                    </View>
                </View>
                <TouchableOpacity style={styles.cancelBtn} onPress={handleCancel}>
                    <Text style={styles.cancelBtnText}>✕ İPTAL ET</Text>
                </TouchableOpacity>
            </View>
        );
    };

    return (
        <SafeAreaView style={styles.container}>
            {gameState === 'finding' && (
                <View style={styles.topBar}>
                    <View style={styles.levelBadge}>
                        <Text style={styles.levelText}>LVL</Text>
                        <Text style={styles.levelNum}>{user ? Math.floor(user.rating / 100) : 1}</Text>
                    </View>
                    <Text style={styles.logoText}>Futbol Tahmin</Text>
                    <View style={styles.currencyCol}>
                        <Text style={styles.currencyGem}>💎 1,250</Text>
                        <Text style={styles.currencyChip}>💰 {user?.chips >= 1000 ? (user.chips/1000)+'K' : (user?.chips || 0)}</Text>
                    </View>
                </View>
            )}

            {gameState === 'finding' && renderFinding()}
            {gameState === 'playing' && renderGameplay()}
            {gameState === 'result' && renderResult()}
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    center: { justifyContent: 'center', alignItems: 'center' },
    topBar: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingTop: 10,
    },
    levelBadge: {
        width: 46, height: 46,
        borderRadius: 23,
        borderWidth: 2,
        borderColor: COLORS.primary,
        justifyContent: 'center',
        alignItems: 'center',
    },
    levelText: { color: COLORS.textMuted, fontSize: 10, fontFamily: FONTS.mono },
    levelNum: { color: COLORS.text, fontSize: 14, fontFamily: FONTS.mono, fontWeight: 'bold' },
    logoText: { color: COLORS.primary, fontFamily: FONTS.headingBlack, fontSize: 24, textShadowColor: 'rgba(195, 244, 0, 0.5)', textShadowOffset: {width: 0, height: 0}, textShadowRadius: 10 },
    currencyCol: { alignItems: 'flex-end' },
    currencyGem: { color: '#FFD700', fontFamily: FONTS.mono, fontSize: 12, fontWeight: 'bold' },
    currencyChip: { color: COLORS.secondary, fontFamily: FONTS.mono, fontSize: 12, fontWeight: 'bold' },
    radarContainer: {
        width: 200, height: 200,
        justifyContent: 'center', alignItems: 'center',
        marginTop: 60, marginBottom: 40,
    },
    radarPulse: {
        position: 'absolute',
        width: 100, height: 100,
        borderRadius: 50,
        backgroundColor: COLORS.primary,
    },
    radarCenter: {
        width: 100, height: 100,
        borderRadius: 50,
        borderWidth: 4,
        borderColor: COLORS.primary,
        backgroundColor: COLORS.surface,
        justifyContent: 'center', alignItems: 'center',
        shadowColor: COLORS.primary,
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.8,
        shadowRadius: 20,
        elevation: 10,
    },
    findingTitle: { color: COLORS.primary, fontFamily: FONTS.headingBlack, fontSize: 28, textShadowColor: 'rgba(195, 244, 0, 0.5)', textShadowRadius: 15 },
    findingTime: { color: COLORS.textMuted, fontFamily: FONTS.mono, fontSize: 16, marginTop: 10 },
    vsContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        marginVertical: 30,
        gap: 15
    },
    playerCardFinding: {
        alignItems: 'center',
        backgroundColor: '#0e3609',
        padding: 15,
        borderRadius: 20,
        borderWidth: 4,
        borderColor: '#4a840a',
        borderBottomWidth: 8,
        width: 120,
    },
    playerAvatarMe: {
        width: 70, height: 70, borderRadius: 35,
        backgroundColor: '#4a840a',
        justifyContent: 'center', alignItems: 'center',
        marginBottom: 15,
        borderWidth: 3,
        borderColor: '#95c029'
    },
    playerAvatarOpponent: {
        width: 70, height: 70, borderRadius: 35,
        backgroundColor: 'rgba(255,255,255,0.05)',
        justifyContent: 'center', alignItems: 'center',
        marginBottom: 15,
        borderWidth: 3,
        borderColor: 'rgba(255,255,255,0.1)'
    },
    playerName: {
        color: '#FFF',
        fontFamily: FONTS.headingBlack,
        fontSize: 20,
        marginBottom: 5
    },
    playerRating: { color: COLORS.primary, fontFamily: FONTS.mono, fontSize: 14, fontWeight: 'bold' },
    vsBadge: {
        width: 40, height: 40, borderRadius: 20,
        backgroundColor: COLORS.surfaceVariant,
        justifyContent: 'center', alignItems: 'center',
        borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)',
        zIndex: 10,
    },
    vsText: { color: COLORS.text, fontFamily: FONTS.mono, fontStyle: 'italic', fontSize: 14 },
    cancelBtn: {
        backgroundColor: '#f2b50b',
        paddingVertical: 15,
        paddingHorizontal: 40,
        borderRadius: 16,
        marginTop: 'auto',
        marginBottom: 40,
        borderWidth: 3,
        borderColor: '#d4a202',
        borderBottomWidth: 6,
    },
    cancelBtnText: {
        color: '#0e3609',
        fontFamily: FONTS.headingBlack,
        fontSize: 16,
    },
    title: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 32 },
    text: { color: COLORS.textMuted, fontFamily: FONTS.body, fontSize: 18, marginTop: 10 },
    btn: { backgroundColor: COLORS.primary, padding: 15, borderRadius: 10 },
    btnText: { color: COLORS.textDark, fontFamily: FONTS.heading, fontSize: 16 },

    // Gameplay specific
    actionBtn: {
        paddingVertical: 14,
        borderRadius: 16,
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 3,
        borderBottomWidth: 6,
    },
    actionBtnPrimary: {
        backgroundColor: '#4a840a',
        borderColor: '#95c029',
    },
    actionBtnTextPrimary: {
        color: '#FFF',
        fontFamily: FONTS.headingBlack,
        fontSize: 18,
    },
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
    }
});
