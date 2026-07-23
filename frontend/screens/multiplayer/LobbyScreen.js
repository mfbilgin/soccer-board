import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Dimensions, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SIZES, FONTS } from '../../theme';
import api from '../../api';

const { width } = Dimensions.get('window');

const GAME_MODES = [
    { id: 'mode_3_1', title: 'Hedef Tutturma', icon: 'scan-circle-outline', desc: 'Sayıları birleştir, tam sayıya ulaş.', active: true },
    { id: 'tictactoe_1', title: 'Takım XOX', icon: 'grid-outline', desc: 'Takımların ortak futbolcularını bul.', active: true },
    { id: 'tictactoe_2', title: 'Oyuncu XOX', icon: 'people-circle-outline', desc: 'Futbolcuların ortak takımlarını bul.', active: true },
    { id: 'chain_reaction', title: 'Zincir Oyunu', icon: 'link-outline', desc: '2-6 kişilik eleme: Oyuncu → Takım → Oyuncu.', active: true },
    { id: 'extreme_squad', title: 'Ekstrem Kadro', icon: 'body-outline', desc: '11 takımdan en genç/en uzun kadroyu ilk kur.', active: true },
    { id: 'find_two', title: 'Kesişim Düellosu', icon: 'flash-outline', desc: '2 takım/ülkede oynayan oyuncuyu ilk yaz.', active: true },
    { id: 'flag_eleven', title: 'Bayrak XI', icon: 'flag-outline', desc: 'Bayraklardan kadronun takımını ilk bul.', active: true },
    { id: 'initials_guess', title: 'Harf Düellosu', icon: 'text-outline', desc: 'Verilen harflerle biten futbolcuyu ilk yaz.', active: true },
    { id: 'pyramid', title: 'Piramit', icon: 'podium-outline', desc: 'En iyileri doğru sırayla diz.', active: false },
    { id: 'tournament', title: 'Turnuva', icon: 'trophy-outline', desc: 'Büyük ödül için yarış.', active: false },
];

export default function LobbyScreen({ navigation }) {
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

    const handleModePress = (mode) => {
        if (!mode.active) {
            Alert.alert("Yakında", "Bu oyun modu henüz aktif değil.");
            return;
        }
        navigation.navigate('RoomSelection', { modeId: mode.id, modeTitle: mode.title });
    };

    const formatNumber = (num) => {
        if (num >= 1000000) return (num / 1000000) + 'M';
        if (num >= 1000) return (num / 1000) + 'K';
        return num.toString();
    };

    const CARD_WIDTH = 280;

    return (
        <SafeAreaView style={styles.container}>
            {/* TOP BAR */}
            <View style={styles.topBar}>
                <TouchableOpacity onPress={() => navigation.goBack()} style={styles.backBtn}>
                    <Ionicons name="arrow-back" size={28} color={COLORS.text} />
                </TouchableOpacity>
                
                <View style={styles.headerTitleBox}>
                    <Text style={styles.headerTitle}>Çok Oyunculu</Text>
                </View>

                <View style={styles.currencyPill}>
                    <Text style={styles.currencyIcon}>💰</Text>
                    <Text style={styles.currencyTextPrimary}>{formatNumber(userChips)}</Text>
                </View>
            </View>

            <View style={styles.content}>
                <Text style={styles.sectionTitle}>Oyun Modunu Seç</Text>
                <Text style={styles.sectionSub}>Rakiplerinle hangi alanda kozlarını paylaşmak istiyorsun?</Text>

                <ScrollView 
                    horizontal 
                    showsHorizontalScrollIndicator={false} 
                    contentContainerStyle={{ alignItems: 'center' }}
                    snapToInterval={width}
                    decelerationRate="fast"
                    snapToAlignment="center"
                    disableIntervalMomentum={true}
                >
                    {GAME_MODES.map((mode, index) => {
                        return (
                            <View key={mode.id} style={{ width: width, alignItems: 'center' }}>
                                <TouchableOpacity 
                                    style={[
                                        styles.modeCard, 
                                        { width: CARD_WIDTH },
                                        !mode.active && { opacity: 0.5 }
                                    ]} 
                                    onPress={() => handleModePress(mode)}
                                    activeOpacity={0.9}
                                >
                                <View style={styles.modeIconBox}>
                                    <Ionicons name={mode.icon} size={60} color={mode.active ? COLORS.primary : COLORS.textMuted} />
                                </View>
                                <Text style={styles.modeTitle}>{mode.title}</Text>
                                <Text style={styles.modeDesc}>{mode.desc}</Text>
                                
                                {!mode.active && (
                                    <View style={styles.badgeContainer}>
                                        <Text style={styles.badgeText}>YAKINDA</Text>
                                    </View>
                                )}
                                </TouchableOpacity>
                            </View>
                        );
                    })}
                </ScrollView>
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.background },
    
    // Top Bar
    topBar: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 20,
        paddingTop: 10,
        paddingBottom: 15,
    },
    backBtn: { padding: 5, marginLeft: -5 },
    headerTitleBox: { flex: 1, alignItems: 'center' },
    headerTitle: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 18, letterSpacing: -0.5 },
    currencyPill: { flexDirection: 'row', alignItems: 'center', gap: 5, backgroundColor: 'rgba(255,255,255,0.05)', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
    currencyIcon: { fontSize: 14 },
    currencyTextPrimary: { color: COLORS.primary, fontFamily: FONTS.mono, fontSize: 14, fontWeight: 'bold' },

    content: {
        flex: 1,
        justifyContent: 'center',
        paddingBottom: 50,
    },
    sectionTitle: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 28, letterSpacing: -1, paddingHorizontal: 20, textAlign: 'center' },
    sectionSub: { color: COLORS.textMuted, fontFamily: FONTS.body, fontSize: 14, paddingHorizontal: 20, textAlign: 'center', marginTop: 10, marginBottom: 40 },

    // Horizontal Mode Cards
    modeCard: {
        height: 380,
        backgroundColor: COLORS.surface,
        borderRadius: SIZES.radiusXl,
        padding: 30,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.05)',
        alignItems: 'center',
        justifyContent: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.3,
        shadowRadius: 20,
        elevation: 10,
    },
    modeIconBox: {
        width: 120, height: 120,
        borderRadius: 60,
        backgroundColor: 'rgba(255,255,255,0.03)',
        justifyContent: 'center', alignItems: 'center',
        marginBottom: 30,
        borderWidth: 1, borderColor: 'rgba(255,255,255,0.05)'
    },
    modeTitle: { color: COLORS.text, fontFamily: FONTS.headingBlack, fontSize: 24, marginBottom: 10, textAlign: 'center' },
    modeDesc: { color: COLORS.textMuted, fontFamily: FONTS.body, fontSize: 14, textAlign: 'center', lineHeight: 22 },
    badgeContainer: {
        position: 'absolute',
        top: 20, right: 20,
        backgroundColor: 'rgba(202, 10, 15, 0.2)',
        paddingHorizontal: 12, paddingVertical: 6,
        borderRadius: 8, borderWidth: 1, borderColor: COLORS.danger
    },
    badgeText: { color: COLORS.danger, fontFamily: FONTS.mono, fontSize: 10, fontWeight: 'bold' },
});
