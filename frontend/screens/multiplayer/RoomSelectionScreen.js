import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Dimensions, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SIZES, FONTS } from '../../theme';
import api from '../../api';

const { width } = Dimensions.get('window');

// 16 Tiers grouped into "Klasman"
const TIERS = [
    { tier: 100, label: 'Acemi Odası', reward: 180, class: 'bronz', icon: 'shield-outline', color: '#CD7F32' },
    { tier: 250, label: 'Çaylak Odası', reward: 450, class: 'bronz', icon: 'shield-half-outline', color: '#CD7F32' },
    { tier: 400, label: 'Kalfa Odası', reward: 720, class: 'bronz', icon: 'shield', color: '#CD7F32' },
    { tier: 1000, label: 'Amatör Odası', reward: 1800, class: 'bronz', icon: 'star-outline', color: '#CD7F32' },

    { tier: 2500, label: 'Gelişim Odası', reward: 4500, class: 'gumus', icon: 'medal-outline', color: '#C0C0C0' },
    { tier: 5000, label: 'Yetenek Odası', reward: 9000, class: 'gumus', icon: 'ribbon-outline', color: '#C0C0C0' },
    { tier: 10000, label: 'Profesyonel Odası', reward: 18000, class: 'gumus', icon: 'trophy-outline', color: '#C0C0C0' },
    { tier: 25000, label: 'Uzman Odası', reward: 45000, class: 'gumus', icon: 'star-half-outline', color: '#C0C0C0' },

    { tier: 50000, label: 'Elit Oda', reward: 90000, class: 'altin', icon: 'flash-outline', color: '#FFD700' },
    { tier: 100000, label: 'Usta Odası', reward: 180000, class: 'altin', icon: 'flame-outline', color: '#FFD700' },
    { tier: 250000, label: 'Şampiyon Odası', reward: 450000, class: 'altin', icon: 'star', color: '#FFD700' },

    { tier: 500000, label: 'Efsane Odası', reward: 900000, class: 'elmas', icon: 'diamond-outline', color: '#00FFFF' },
    { tier: 1000000, label: 'Mitik Oda', reward: 1800000, class: 'elmas', icon: 'planet-outline', color: '#00FFFF' },
    { tier: 2500000, label: 'Yenilmez Odası', reward: 4500000, class: 'elmas', icon: 'rocket-outline', color: '#00FFFF' },

    { tier: 5000000, label: 'Omega Odası', reward: 9000000, class: 'kozmik', icon: 'infinite-outline', color: '#9D00FF' },
    { tier: 10000000, label: 'Kozmik Oda', reward: 18000000, class: 'kozmik', icon: 'skull-outline', color: COLORS.primary },
];

export default function RoomSelectionScreen({ route, navigation }) {
    const { modeId, modeTitle } = route.params || { modeId: 'mode_3_1', modeTitle: 'Oda Seçimi' };
    const [userChips, setUserChips] = useState(0);

    useEffect(() => {
        loadProfile();
    }, []);

    const loadProfile = async () => {
        try {
            const res = await api.get('/auth/me');
            setUserChips(res.data.chips || 0);
        } catch (err) {
            console.log(err);
        }
    };

    const handleJoin = (tier) => {
        if (userChips < tier) {
            Alert.alert("Yetersiz Bakiye", "Bu odaya girmek için yeterli Chip'iniz yok.");
            return;
        }
        
        if (modeId === 'mode_3_1') {
            navigation.navigate('MultiplayerTargetScore', { tier });
        } else if (modeId === 'tictactoe_1' || modeId === 'tictactoe_2') {
            navigation.navigate('MultiplayerTicTacToe', { tier, modeId });
        } else if (modeId === 'chain_reaction') {
            navigation.navigate('ChainReaction', { tier });
        } else if (modeId === 'extreme_squad') {
            navigation.navigate('MultiplayerExtremeSquad', { tier });
        } else if (modeId === 'find_two') {
            navigation.navigate('FindTwo', { tier });
        } else if (modeId === 'flag_eleven') {
            navigation.navigate('MultiplayerFlagEleven', { tier });
        } else {
            Alert.alert("Yakında", "Bu mod henüz aktif değil.");
        }
    };

    const formatNumber = (num) => {
        if (num >= 1000000) return (num / 1000000) + 'M';
        if (num >= 1000) return (num / 1000) + 'K';
        return num.toString();
    };

    return (
        <SafeAreaView style={styles.container}>
            {/* TOP BAR */}
            <View style={styles.topBar}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <Ionicons name="arrow-back" size={28} color={COLORS.text} />
                </TouchableOpacity>
                
                <View style={styles.headerTitleBox}>
                    <Text style={styles.headerTitle}>{modeTitle}</Text>
                </View>

                <View style={styles.currencyPill}>
                    <Text style={styles.currencyIcon}>💰</Text>
                    <Text style={styles.currencyTextPrimary}>{formatNumber(userChips)}</Text>
                </View>
            </View>

            <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
                <Text style={styles.sectionTitle}>Klasmanlar</Text>
                <Text style={styles.sectionSub}>Bütçene uygun odayı seç ve savaşa katıl.</Text>

                <View style={styles.cardsList}>
                    {TIERS.map((item, index) => {
                        return (
                            <View key={index} style={[styles.horizontalCard, { borderColor: `rgba(${hexToRgb(item.color)}, 0.3)` }]}>
                                
                                <View style={[styles.cardBackgroundTint, { backgroundColor: item.color }]} />

                                <View style={styles.cardLeft}>
                                    <View style={[styles.cardIconBox, { backgroundColor: `rgba(${hexToRgb(item.color)}, 0.15)` }]}>
                                        <Ionicons name={item.icon} size={28} color={item.color} />
                                    </View>
                                    <View style={styles.cardInfo}>
                                        <Text style={styles.cardTitle}>{item.label}</Text>
                                        <View style={styles.rewardBox}>
                                            <Ionicons name="gift-outline" size={14} color={COLORS.textMuted} />
                                            <Text style={styles.cardReward}>Kazan: {formatNumber(item.reward)}</Text>
                                        </View>
                                    </View>
                                </View>
                                
                                <View style={styles.cardRight}>
                                    <TouchableOpacity 
                                        style={[styles.playBtn, { backgroundColor: `rgba(${hexToRgb(item.color)}, 0.15)` }]}
                                        onPress={() => handleJoin(item.tier)}
                                    >
                                        <Text style={[styles.playBtnText, { color: item.color }]}>
                                            GİRİŞ {formatNumber(item.tier)}
                                        </Text>
                                        <Ionicons name="play" size={12} color={item.color} style={{marginLeft: 5}}/>
                                    </TouchableOpacity>
                                </View>
                            </View>
                        );
                    })}
                </View>
                <View style={{height: 50}} />
            </ScrollView>
        </SafeAreaView>
    );
}

function hexToRgb(hex) {
    let c;
    if(/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)){
        c= hex.substring(1).split('');
        if(c.length== 3){
            c= [c[0], c[0], c[1], c[1], c[2], c[2]];
        }
        c= '0x'+c.join('');
        return [(c>>16)&255, (c>>8)&255, c&255].join(',');
    }
    return "195, 244, 0"; 
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    
    topBar: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingTop: 10,
        paddingBottom: 15,
        borderBottomWidth: 1,
        borderBottomColor: 'rgba(255,255,255,0.05)',
        marginBottom: 15,
    },
    backBtn: { padding: 5, marginLeft: -5 },
    headerTitleBox: { flex: 1, alignItems: 'center' },
    headerTitle: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 18, letterSpacing: -0.5 },
    currencyPill: { flexDirection: 'row', alignItems: 'center', gap: 5, backgroundColor: 'rgba(255,255,255,0.05)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
    currencyIcon: { fontSize: 14 },
    currencyTextPrimary: { color: COLORS.primary, fontFamily: FONTS.mono, fontSize: 14, fontWeight: 'bold' },

    scrollContent: { paddingHorizontal: 20 },
    sectionTitle: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: SIZES.title, letterSpacing: -0.5 },
    sectionSub: { color: COLORS.textMuted, fontFamily: FONTS.body, fontSize: 14, marginBottom: 20, marginTop: 2 },

    cardsList: {
        flexDirection: 'column',
        gap: 12,
    },
    horizontalCard: {
        width: '100%',
        backgroundColor: COLORS.surface,
        borderRadius: SIZES.radiusLg,
        padding: 15,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderWidth: 1,
        overflow: 'hidden',
    },
    cardBackgroundTint: {
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        opacity: 0.03,
    },
    cardLeft: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    cardIconBox: {
        width: 50, height: 50,
        borderRadius: 15,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 15,
    },
    cardInfo: { flex: 1 },
    cardTitle: { color: COLORS.text, fontFamily: FONTS.heading, fontSize: 16, marginBottom: 4 },
    rewardBox: { flexDirection: 'row', alignItems: 'center', gap: 4 },
    cardReward: { color: COLORS.textMuted, fontFamily: FONTS.mono, fontSize: 12 },
    
    cardRight: {
        marginLeft: 10,
    },
    playBtn: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 10,
        paddingHorizontal: 15,
        borderRadius: SIZES.radius,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.1)'
    },
    playBtnText: { fontFamily: FONTS.mono, fontSize: 12, fontWeight: 'bold' },
});
