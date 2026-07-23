import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Dimensions, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, SIZES, FONTS } from '../../theme';

const { width } = Dimensions.get('window');

const GAME_MODES = [
    { id: 'mode_3_1', title: 'Hedef Tutturma', icon: 'scan-circle-outline', desc: 'Kariyer istatistiklerini birleştirerek hedefe ulaş.', route: 'TargetScore', params: {}, active: true },
    { id: 'tictactoe_1', title: 'Takım XOX', icon: 'grid-outline', desc: 'Takımların ortak oyuncularını bul.', route: 'TicTacToe', params: { gridType: 1 }, active: true },
    { id: 'tictactoe_2', title: 'Oyuncu XOX', icon: 'people-outline', desc: 'Oyuncuların ortak takımlarını bul.', route: 'TicTacToe', params: { gridType: 2 }, active: true },
    { id: 'pyramid', title: 'Top 10 Piramidi', icon: 'podium-outline', desc: 'En iyi 10 oyuncuyu tahmin et.', route: 'Pyramid', params: {}, active: true },
    { id: 'career_guess', title: 'Kariyer Yolu', icon: 'airplane-outline', desc: 'Transfer geçmişine bakarak futbolcuyu tahmin et.', route: 'CareerGuess', params: {}, active: true },
    { id: 'extreme_squad', title: 'Ekstrem Kadro', icon: 'body-outline', desc: 'Verilen 11 takımdan en genç/en uzun kadroyu kur.', route: 'ExtremeSquad', params: {}, active: true },
    { id: 'flag_eleven', title: 'Bayrak XI', icon: 'flag-outline', desc: 'Bayraklardan kadronun hangi takım olduğunu bul.', route: 'FlagEleven', params: {}, active: true },
    { id: 'tictactoe_4x4', title: '4x4 Matris', icon: 'apps-outline', desc: 'Devasa 4x4 matrisi çöz.', route: 'TicTacToe4x4', params: {}, active: false },
    { id: 'chain_reaction', title: 'Örgü (Zincir)', icon: 'link-outline', desc: 'Oyuncu-Takım zincirini kur.', route: 'ChainReaction', params: {}, active: false },
];

export default function SingleplayerScreen({ navigation }) {

    const handleModePress = (mode) => {
        if (!mode.active) {
            Alert.alert("Yakında", "Bu oyun modu henüz aktif değil.");
            return;
        }
        navigation.navigate(mode.route, mode.params);
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
                    <Text style={styles.headerTitle}>Tek Oyunculu</Text>
                </View>

                {/* Dummy placeholder to balance the back button visually */}
                <View style={{ width: 28 }} />
            </View>

            <View style={styles.content}>
                <Text style={styles.sectionTitle}>Antrenman Modu</Text>
                <Text style={styles.sectionSub}>Kendini geliştir ve yeteneklerini sına.</Text>

                <ScrollView 
                    horizontal 
                    showsHorizontalScrollIndicator={false} 
                    contentContainerStyle={{ alignItems: 'center' }}
                    snapToInterval={width}
                    decelerationRate="fast"
                    snapToAlignment="center"
                    disableIntervalMomentum={true}
                >
                    {GAME_MODES.map((mode) => {
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
                                        <Ionicons name={mode.icon} size={50} color={'#fcc205'} />
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
        backgroundColor: '#4a840a',
        borderRadius: 32,
        padding: 30,
        borderWidth: 4,
        borderColor: '#95c029',
        borderBottomWidth: 12,
        alignItems: 'center',
        justifyContent: 'center',
        marginTop: 10,
    },
    modeIconBox: {
        width: 120, height: 120,
        borderRadius: 60,
        backgroundColor: '#0e3609',
        justifyContent: 'center', alignItems: 'center',
        marginBottom: 30,
        borderWidth: 4, borderColor: '#95c029'
    },
    modeTitle: { color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 30, marginBottom: 10, textAlign: 'center' },
    modeDesc: { color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 14, textAlign: 'center', lineHeight: 22, opacity: 0.9 },
    badgeContainer: {
        position: 'absolute',
        top: 20, right: 20,
        backgroundColor: 'rgba(202, 10, 15, 0.2)',
        paddingHorizontal: 12, paddingVertical: 6,
        borderRadius: 8, borderWidth: 1, borderColor: COLORS.danger
    },
    badgeText: { color: COLORS.danger, fontFamily: FONTS.mono, fontSize: 10, fontWeight: 'bold' },
});
