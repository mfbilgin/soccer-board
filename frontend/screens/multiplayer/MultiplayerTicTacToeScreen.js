import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated, Easing, Alert, ScrollView, Image, ActivityIndicator, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, SIZES, FONTS, GLOBAL_STYLES } from '../../theme';
import SocketService from '../../services/SocketService';
import api from '../../api';
import SearchModal from '../../components/SearchModal';
import { Ionicons } from '@expo/vector-icons';

export default function MultiplayerTicTacToeScreen({ route, navigation }) {
    const { tier, modeId } = route.params; // tictactoe_1 or tictactoe_2
    const [gameState, setGameState] = useState('finding'); // finding, playing, result
    const [user, setUser] = useState(null);
    const [gameData, setGameData] = useState(null);
    const [resultData, setResultData] = useState(null);
    const [timeLeft, setTimeLeft] = useState(30);

    const [board, setBoard] = useState({});
    const [activePlayer, setActivePlayer] = useState(null);
    const [playerSymbols, setPlayerSymbols] = useState({});
    const [answers, setAnswers] = useState(null);
    
    // Gameplay states
    const [isSearchVisible, setSearchVisible] = useState(false);
    const [selectedCell, setSelectedCell] = useState(null);
    const [opponentDisconnected, setOpponentDisconnected] = useState(false);

    // Radar Animation
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

                SocketService.send('join_queue', { game_mode: modeId, tier });
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
            timer = setInterval(() => {
                setSearchTime(prev => prev + 1);
            }, 1000);
            
            Animated.loop(
                Animated.parallel([
                    Animated.timing(pulseAnim, { toValue: 2, duration: 1500, easing: Easing.out(Easing.ease), useNativeDriver: true }),
                    Animated.timing(opacityAnim, { toValue: 0, duration: 1500, easing: Easing.out(Easing.ease), useNativeDriver: true })
                ])
            ).start();
        } else if (gameState === 'playing' && !opponentDisconnected) {
            timer = setInterval(() => {
                const endTime = gameData?.turn_end_time || 0;
                const now = Date.now() / 1000;
                let rem = Math.ceil(endTime - now);
                if (rem < 0) rem = 0;
                setTimeLeft(rem);
            }, 1000);
        }
        return () => clearInterval(timer);
    }, [gameState, gameData?.turn_end_time, opponentDisconnected]);

    const loadProfile = async () => {
        try {
            const res = await api.get('/auth/me');
            setUser(res.data);
        } catch (err) {
            console.log(err);
        }
    };

    const handleMatchFound = (data) => {
        setGameState('playing');
    };

    const handleGameUpdate = (data) => {
        if (data.action === 'tictactoe_ready') {
            setGameData(data);
            setActivePlayer(data.active_player);
            setPlayerSymbols(data.player_symbols);
            setBoard({});
        } else if (data.action === 'tictactoe_turn_switch') {
            setGameData(prev => ({ ...prev, turn_end_time: data.turn_end_time }));
            setActivePlayer(data.active_player);
            if (data.board) {
                setBoard(data.board);
            }
        }
    };

    const handleGameResult = (data) => {
        setSearchVisible(false);
        setResultData(data);
        if (data.board) setBoard(data.board);
        if (data.answers) setAnswers(data.answers);
        setGameState('result');
    };

    const handleError = (err) => {
        Alert.alert('Hata', err.message || "Bir hata oluştu.");
        navigation.goBack();
    };

    const handleCancel = () => {
        SocketService.send('leave_queue', { game_mode: modeId, tier });
        SocketService.disconnect();
        navigation.goBack();
    };

    const handlePass = () => {
        if (activePlayer !== String(user?.id)) return;
        SocketService.send('tictactoe_pass', {});
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

    const openSearch = (rIdx, cIdx) => {
        if (activePlayer !== String(user?.id)) {
            Alert.alert("Sıra Sende Değil!", "Lütfen rakibin hamlesini bekle.");
            return;
        }
        if (board[`${rIdx}-${cIdx}`]) return;
        
        setSelectedCell({rIdx, cIdx});
        setSearchVisible(true);
    };

    const handlePlayerSelect = (entity) => {
        setSearchVisible(false);
        SocketService.send('tictactoe_guess', {
            rIdx: selectedCell.rIdx,
            cIdx: selectedCell.cIdx,
            entity_id: entity.id
        });
    };

    const renderGrid = () => {
        const grid = gameData?.grid;
        if (!grid) return null;

        const { rows, cols } = grid;

        return (
            <View style={styles.gridWrapper}>
                {/* Header Row */}
                <View style={styles.row}>
                    <View style={[styles.headerCell, styles.cornerCell]} />
                    {cols.map((col, cIdx) => (
                        <View key={`col-${cIdx}`} style={styles.headerCell}>
                            <Image source={{ uri: col.image_url }} style={styles.headerImage} />
                            <Text style={styles.headerText} numberOfLines={1}>{col.name}</Text>
                        </View>
                    ))}
                </View>

                {/* Grid Rows */}
                {rows.map((row, rIdx) => (
                    <View key={`row-${rIdx}`} style={styles.row}>
                        <View style={styles.headerCell}>
                            <Image source={{ uri: row.image_url }} style={styles.headerImage} />
                            <Text style={styles.headerText} numberOfLines={1}>{row.name}</Text>
                        </View>

                        {cols.map((col, cIdx) => {
                            const cellKey = `${rIdx}-${cIdx}`;
                            const cellData = board[cellKey];
                            const isMyTurn = activePlayer === String(user?.id);
                            
                            let answerText = null;
                            if (gameState === 'result' && !cellData && answers) {
                                answerText = answers[cellKey];
                            }

                            return (
                                <TouchableOpacity 
                                    key={cellKey} 
                                    style={[
                                        styles.cell, 
                                        cellData && (cellData.symbol === 'X' ? styles.cellX : styles.cellO)
                                    ]}
                                    onPress={() => gameState === 'playing' && openSearch(rIdx, cIdx)}
                                    disabled={gameState !== 'playing' || !!cellData || !isMyTurn}
                                    activeOpacity={0.7}
                                >
                                    {cellData ? (
                                        <Text style={[styles.cellText, { color: cellData.symbol === 'X' ? COLORS.primary : COLORS.danger }]}>
                                            {cellData.symbol}
                                        </Text>
                                    ) : answerText ? (
                                        <Text style={styles.answerText}>{answerText}</Text>
                                    ) : (
                                        <Text style={{color: 'rgba(255,255,255,0.1)', fontSize: 24}}>+</Text>
                                    )}
                                </TouchableOpacity>
                            );
                        })}
                    </View>
                ))}
            </View>
        );
    };

    const renderGameplay = () => {
        const isMyTurn = activePlayer === String(user?.id);
        const mySymbol = playerSymbols[String(user?.id)];

        return (
            <ImageBackground source={require('../../assets/background.png')} style={GLOBAL_STYLES.screen} imageStyle={{ opacity: 0.15 }} resizeMode="cover">
            <ScrollView contentContainerStyle={{paddingBottom: 40}}>
                
                <View style={styles.turnIndicator}>
                    <Text style={[styles.turnText, {color: isMyTurn ? COLORS.primary : '#FFF'}]}>
                        {isMyTurn ? "Sıra Sende" : "Rakip Bekleniyor..."}
                    </Text>
                    <Text style={{color: isMyTurn ? COLORS.primary : '#FFF', fontSize: 24, fontWeight: 'bold'}}>⏱️ {timeLeft}s</Text>
                    <Text style={{color: '#FFF', marginTop: 5, fontFamily: FONTS.mono, opacity: 0.8}}>Sen: {mySymbol}</Text>
                </View>

                {renderGrid()}

                <View style={{padding: 20, marginBottom: 50}}>
                    {isMyTurn && (
                        <TouchableOpacity 
                            style={[GLOBAL_STYLES.primaryButton, {backgroundColor: COLORS.secondary, marginBottom: 15}]} 
                            onPress={handlePass}
                        >
                            <Text style={GLOBAL_STYLES.primaryButtonText}>Bulamadım / Pas Geç</Text>
                        </TouchableOpacity>
                    )}

                    <TouchableOpacity 
                        style={[GLOBAL_STYLES.primaryButton, {backgroundColor: '#e74c3c'}]} 
                        onPress={handleSurrender}
                    >
                        <Text style={[GLOBAL_STYLES.primaryButtonText, {color: '#FFF'}]}>Teslim Ol</Text>
                    </TouchableOpacity>
                </View>

                <SearchModal 
                    visible={isSearchVisible}
                    onClose={() => setSearchVisible(false)}
                    onSelect={handlePlayerSelect}
                    searchType={gameData?.grid?.type === 1 ? 1 : 2}
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
            <ScrollView contentContainerStyle={{padding: 20, alignItems: 'center', paddingBottom: 60}} showsVerticalScrollIndicator={false}>
                <Text style={{color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 40, marginBottom: 20, textAlign: 'center'}}>
                    {isDraw ? 'BERABERE 🤝' : isWinner ? 'KAZANDIN! 🎉' : 'KAYBETTİN 😔'}
                </Text>
                
                <View style={{backgroundColor: '#0e3609', width: '100%', borderRadius: 24, padding: 25, borderWidth: 4, borderColor: '#4a840a', borderBottomWidth: 8, alignItems: 'center', marginBottom: 20}}>
                    <Text style={{color: '#95c029', fontFamily: FONTS.headingBlack, fontSize: 18, marginBottom: 15, textTransform: 'uppercase', letterSpacing: 1}}>Maç Sonucu</Text>
                    
                    {Object.keys(resultData.results).map(uid => {
                        const r = resultData.results[uid];
                        const isMe = uid === String(user?.id);
                        
                        return (
                            <View key={uid} style={{flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', width: '100%', backgroundColor: isMe ? '#4a840a' : 'rgba(255,255,255,0.05)', padding: 15, borderRadius: 16, marginBottom: 10, borderWidth: isMe ? 3 : 0, borderColor: '#95c029'}}>
                                <Text style={{color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 18}}>{isMe ? 'Sen' : 'Rakip'}</Text>
                                <View style={{alignItems: 'flex-end'}}>
                                    <Text style={{color: isMe ? '#fcc205' : '#FFF', fontFamily: FONTS.headingBlack, fontSize: 20}}>{r.message}</Text>
                                </View>
                            </View>
                        );
                    })}
                </View>

                {renderGrid()}

                <TouchableOpacity style={[styles.actionBtn, styles.actionBtnPrimary, {width: '100%', marginTop: 30}]} onPress={() => navigation.navigate('MainTabs')}>
                    <Text style={styles.actionBtnTextPrimary}>LOBİYE DÖN</Text>
                </TouchableOpacity>
            </ScrollView>
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
                    <Text style={styles.logoText}>XOX Savaşı</Text>
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
    },
    findingTitle: { color: COLORS.primary, fontFamily: FONTS.headingBlack, fontSize: 28 },
    findingTime: { color: COLORS.textMuted, fontFamily: FONTS.mono, fontSize: 16, marginTop: 10 },
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
    
    turnIndicator: {
        alignItems: 'center',
        padding: 20,
        backgroundColor: '#0e3609',
        borderBottomWidth: 4,
        borderColor: '#4a840a'
    },
    turnText: {
        fontFamily: FONTS.headingBlack,
        fontSize: 22,
        marginBottom: 5
    },

    gridWrapper: {
        padding: 10,
        alignSelf: 'center',
        marginTop: 20
    },
    row: {
        flexDirection: 'row',
    },
    headerCell: {
        width: 85,
        height: 85,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 4,
    },
    cornerCell: {
        backgroundColor: 'transparent',
    },
    headerImage: {
        width: 45,
        height: 45,
        resizeMode: 'contain',
        marginBottom: 4,
    },
    headerText: {
        color: COLORS.text,
        fontFamily: FONTS.mono,
        fontSize: 10,
        textAlign: 'center',
    },
    cell: {
        width: 85,
        height: 85,
        backgroundColor: 'rgba(255,255,255,0.05)',
        borderWidth: 2,
        borderColor: 'rgba(255,255,255,0.1)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    cellX: {
        backgroundColor: 'rgba(195, 244, 0, 0.1)',
        borderColor: COLORS.primary,
    },
    cellO: {
        backgroundColor: 'rgba(231, 76, 60, 0.1)',
        borderColor: COLORS.danger,
    },
    cellText: {
        fontFamily: FONTS.headingBlack,
        fontSize: 48,
        textShadowColor: 'rgba(0,0,0,0.5)',
        textShadowOffset: { width: 2, height: 2 },
        textShadowRadius: 4,
    },
    answerText: {
        color: '#FFF',
        fontFamily: FONTS.mono,
        fontSize: 9,
        textAlign: 'center',
        padding: 2,
    },
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
    }
});
