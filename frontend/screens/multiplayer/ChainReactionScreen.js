import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, FONTS, GLOBAL_STYLES } from '../../theme';
import SocketService from '../../services/SocketService';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

export default function ChainReactionScreen({ route, navigation }) {
    const { tier } = route.params;
    const [gameState, setGameState] = useState('lobby'); // lobby, playing, result
    const [user, setUser] = useState(null);
    const [lobbyPlayers, setLobbyPlayers] = useState({});

    const [chain, setChain] = useState([]);
    const [turnOrder, setTurnOrder] = useState([]);
    const [activePlayer, setActivePlayer] = useState(null);
    const [eliminated, setEliminated] = useState([]);
    const [timeLeft, setTimeLeft] = useState(15);
    const [turnEndTime, setTurnEndTime] = useState(0);
    const [lastMessage, setLastMessage] = useState(null);

    const [isSearchVisible, setSearchVisible] = useState(false);
    const [resultData, setResultData] = useState(null);

    const turnEndRef = useRef(0);

    useEffect(() => {
        loadProfile();

        const initSocket = async () => {
            try {
                await SocketService.connect();
                SocketService.on('lobby_update', handleLobbyUpdate);
                SocketService.on('lobby_left', () => navigation.goBack());
                SocketService.on('player_left', handleLobbyUpdate);
                SocketService.on('game_update', handleGameUpdate);
                SocketService.on('game_over', handleGameResult);
                SocketService.on('error', handleError);

                SocketService.send('join_chain_lobby', { tier });
            } catch (err) {
                Alert.alert('Bağlantı Hatası', 'Sunucuya bağlanılamadı.');
                navigation.goBack();
            }
        };

        initSocket();

        return () => {
            SocketService.off('lobby_update', handleLobbyUpdate);
            SocketService.off('lobby_left');
            SocketService.off('player_left', handleLobbyUpdate);
            SocketService.off('game_update', handleGameUpdate);
            SocketService.off('game_over', handleGameResult);
            SocketService.off('error', handleError);
            SocketService.disconnect();
        };
    }, []);

    useEffect(() => {
        if (gameState !== 'playing') return;
        const timer = setInterval(() => {
            const now = Date.now() / 1000;
            let rem = Math.ceil(turnEndRef.current - now);
            if (rem < 0) rem = 0;
            setTimeLeft(rem);
        }, 1000);
        return () => clearInterval(timer);
    }, [gameState]);

    const loadProfile = async () => {
        try {
            const res = await api.get('/auth/me');
            setUser(res.data);
        } catch (err) {
            console.log(err);
        }
    };

    const handleLobbyUpdate = (data) => {
        if (data.players) setLobbyPlayers(data.players);
    };

    const handleGameUpdate = (data) => {
        if (data.action === 'chain_ready') {
            setChain([data.start_entity ? { type: 'player', id: data.start_entity.id, name: data.start_entity.name } : null].filter(Boolean));
            setTurnOrder(data.turn_order);
            setActivePlayer(data.active_player);
            setEliminated([]);
            turnEndRef.current = data.turn_end_time;
            setGameState('playing');
        } else if (data.action === 'chain_turn_switch') {
            setActivePlayer(data.active_player);
            turnEndRef.current = data.turn_end_time;
        } else if (data.action === 'chain_correct_answer') {
            setChain(prev => [...prev, data.entity]);
            setLastMessage(null);
        } else if (data.action === 'chain_reset') {
            setLastMessage('Zincir tıkandı, yeni zincir başlıyor!');
            setChain([{ type: 'player', id: data.start_entity.id, name: data.start_entity.name }]);
        } else if (data.action === 'chain_player_eliminated') {
            setEliminated(prev => [...prev, data.user_id]);
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

    useEffect(() => {
        SocketService.on('chain_wrong_answer', () => {
            Alert.alert('Yanlış Cevap', 'Bu cevap zincire uymuyor, tekrar dene.');
        });
        return () => SocketService.off('chain_wrong_answer');
    }, []);

    const handleCancelLobby = () => {
        SocketService.send('leave_chain_lobby', {});
    };

    const openSearch = () => {
        if (activePlayer !== String(user?.id)) return;
        setSearchVisible(true);
    };

    const nextExpectedType = () => {
        if (chain.length === 0) return 'player';
        return chain[chain.length - 1].type === 'player' ? 'team' : 'player';
    };

    const handleEntitySelect = (entity) => {
        setSearchVisible(false);
        SocketService.send('chain_answer', {
            entity_id: entity.id,
            entity_type: nextExpectedType(),
        });
    };

    const renderLobby = () => {
        const count = Object.keys(lobbyPlayers).length;
        return (
            <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', padding: 20 }}>
                <Text style={styles.title}>Zincir Oyunu Lobisi</Text>
                <Text style={styles.subtitle}>{count}/6 oyuncu bekleniyor (min 2)</Text>
                <View style={styles.playerList}>
                    {Object.entries(lobbyPlayers).map(([uid, p]) => (
                        <View key={uid} style={styles.playerPill}>
                            <Text style={styles.playerPillText}>{p.username}</Text>
                        </View>
                    ))}
                </View>
                <TouchableOpacity style={styles.cancelBtn} onPress={handleCancelLobby}>
                    <Text style={styles.cancelBtnText}>✕ İPTAL ET</Text>
                </TouchableOpacity>
            </View>
        );
    };

    const renderPlaying = () => {
        const isMyTurn = activePlayer === String(user?.id);
        const iAmEliminated = eliminated.includes(String(user?.id));
        const expected = nextExpectedType();

        return (
            <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
                <View style={styles.turnIndicator}>
                    <Text style={[styles.turnText, { color: isMyTurn ? COLORS.primary : '#FFF' }]}>
                        {iAmEliminated ? 'Elendin (izleyici)' : isMyTurn ? 'Sıra Sende' : 'Diğer Oyuncu Bekleniyor...'}
                    </Text>
                    {!iAmEliminated && (
                        <Text style={{ color: isMyTurn ? COLORS.primary : '#FFF', fontSize: 24, fontWeight: 'bold' }}>⏱️ {timeLeft}s</Text>
                    )}
                </View>

                {lastMessage && <Text style={styles.infoBanner}>{lastMessage}</Text>}

                <View style={styles.chainBox}>
                    {chain.map((node, idx) => (
                        <View key={idx} style={[styles.chainNode, node.type === 'player' ? styles.nodePlayer : styles.nodeTeam]}>
                            <Text style={styles.chainNodeText}>{node.name}</Text>
                        </View>
                    ))}
                </View>

                {isMyTurn && !iAmEliminated && (
                    <TouchableOpacity style={[GLOBAL_STYLES.primaryButton, { marginTop: 20 }]} onPress={openSearch}>
                        <Text style={GLOBAL_STYLES.primaryButtonText}>
                            {expected === 'player' ? 'Bir Oyuncu Söyle' : 'Bir Takım Söyle'}
                        </Text>
                    </TouchableOpacity>
                )}

                <SearchModal
                    visible={isSearchVisible}
                    onClose={() => setSearchVisible(false)}
                    onSelect={handleEntitySelect}
                    searchType={expected === 'player' ? 1 : 2}
                />
            </ScrollView>
        );
    };

    const renderResult = () => {
        if (!resultData) return null;
        const isWinner = resultData.winner_id === String(user?.id);
        const isDraw = resultData.winner_id === null;

        return (
            <ScrollView contentContainerStyle={{ padding: 20, alignItems: 'center', paddingBottom: 60 }}>
                <Text style={{ color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 36, marginBottom: 20, textAlign: 'center' }}>
                    {isDraw ? 'KİMSE KAZANAMADI' : isWinner ? 'KAZANDIN! 🎉' : 'ELENDİN 😔'}
                </Text>

                <View style={styles.chainBox}>
                    {(resultData.chain || []).map((node, idx) => (
                        <View key={idx} style={[styles.chainNode, node.type === 'player' ? styles.nodePlayer : styles.nodeTeam]}>
                            <Text style={styles.chainNodeText}>{node.name}</Text>
                        </View>
                    ))}
                </View>

                <TouchableOpacity style={[GLOBAL_STYLES.primaryButton, { width: '100%', marginTop: 30 }]} onPress={() => navigation.navigate('MainTabs')}>
                    <Text style={GLOBAL_STYLES.primaryButtonText}>LOBİYE DÖN</Text>
                </TouchableOpacity>
            </ScrollView>
        );
    };

    return (
        <SafeAreaView style={styles.container}>
            <ImageBackground source={require('../../assets/background.png')} style={{ flex: 1 }} imageStyle={{ opacity: 0.15 }} resizeMode="cover">
                {gameState === 'lobby' && renderLobby()}
                {gameState === 'playing' && renderPlaying()}
                {gameState === 'result' && renderResult()}
            </ImageBackground>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    title: { color: COLORS.primary, fontFamily: FONTS.headingBlack, fontSize: 28, textAlign: 'center' },
    subtitle: { color: COLORS.textMuted, fontFamily: FONTS.mono, fontSize: 14, marginTop: 10, marginBottom: 30 },
    playerList: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', gap: 8, marginBottom: 40 },
    playerPill: { backgroundColor: 'rgba(255,255,255,0.05)', paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20 },
    playerPillText: { color: COLORS.text, fontFamily: FONTS.mono, fontSize: 12 },
    cancelBtn: {
        backgroundColor: '#f2b50b',
        paddingVertical: 15,
        paddingHorizontal: 40,
        borderRadius: 16,
        borderWidth: 3,
        borderColor: '#d4a202',
        borderBottomWidth: 6,
    },
    cancelBtnText: { color: '#0e3609', fontFamily: FONTS.headingBlack, fontSize: 16 },

    turnIndicator: { alignItems: 'center', padding: 20, backgroundColor: '#0e3609', borderRadius: 16, marginBottom: 15 },
    turnText: { fontFamily: FONTS.headingBlack, fontSize: 20, marginBottom: 5 },
    infoBanner: { color: COLORS.primary, textAlign: 'center', fontFamily: FONTS.mono, marginBottom: 15 },

    chainBox: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, justifyContent: 'center' },
    chainNode: { paddingHorizontal: 14, paddingVertical: 10, borderRadius: 12, borderWidth: 1 },
    nodePlayer: { backgroundColor: 'rgba(195, 244, 0, 0.1)', borderColor: COLORS.primary },
    nodeTeam: { backgroundColor: 'rgba(231, 76, 60, 0.1)', borderColor: COLORS.danger },
    chainNodeText: { color: COLORS.text, fontFamily: FONTS.mono, fontSize: 13 },
});
