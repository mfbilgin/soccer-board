import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Image, ImageBackground } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, SIZES, FONTS, GLOBAL_STYLES } from '../../theme';

export default function TargetScoreResultScreen({ route, navigation }) {
    const { result, puzzle } = route.params;

    const metricLabel = {
        goals: 'Gol',
        assists: 'Asist',
        appearances: 'Maç',
        yellow_cards: 'Sarı Kart',
        red_cards: 'Kırmızı Kart',
        minutes_played: 'Oynanan Dakika',
        caps: 'Milli Maç'
    }[puzzle.metric] || puzzle.metric;

    // Renk hesaplama mantığı
    let distanceColor = COLORS.danger; // Default red (> 10%)
    let distanceText = "Maalesef Hedefin Uzağında Kaldın!";

    if (result.distance === 0) {
        distanceColor = COLORS.primary; // Neon Green
        distanceText = "MÜKEMMEL! TAM İSABET! 🎯";
    } else if (result.distance <= puzzle.target * 0.1) {
        distanceColor = COLORS.secondary; // Neon Yellow/Orange
        distanceText = "ÇOK YAKLAŞTIN! 📏";
    }

    // XP Bar Percentage
    const xpPercentage = Math.min((result.new_xp / result.required_xp) * 100, 100);

    return (
        <ImageBackground 
            source={require('../../assets/background.png')} 
            style={GLOBAL_STYLES.screen}
            imageStyle={{ opacity: 0.15 }}
            resizeMode="cover"
        >
            <SafeAreaView style={{ flex: 1 }}>
                <ScrollView contentContainerStyle={{paddingBottom: 30}}>
                
                {/* Header / Hedef vs Senin Toplamın */}
                <View style={styles.headerCard}>
                <Text style={styles.leagueText}>{puzzle.league_name || puzzle.league}</Text>
                
                <View style={styles.comparisonRow}>
                    <View style={styles.compBox}>
                        <Text style={styles.compLabel}>HEDEF</Text>
                        <Text style={styles.compValue}>{puzzle.target}</Text>
                    </View>
                    <View style={styles.compDivider}>
                        <Text style={styles.vsText}>VS</Text>
                    </View>
                    <View style={styles.compBox}>
                        <Text style={styles.compLabel}>SENİN TOPLAMIN</Text>
                        <Text style={[styles.compValue, {color: distanceColor}]}>{result.total_sum}</Text>
                    </View>
                </View>

                {/* Fark ve Sonuç Mesajı */}
                <View style={styles.distanceContainer}>
                    <Text style={[styles.distanceTitle, {color: distanceColor}]}>{distanceText}</Text>
                    <Text style={styles.distanceText}>Fark: <Text style={{color: distanceColor, fontWeight: 'bold'}}>{result.distance}</Text> {metricLabel}</Text>
                </View>
            </View>

            {/* XP ve Level Sistemi */}
            <View style={styles.xpCard}>
                {result.leveled_up && (
                    <Text style={styles.levelUpText}>🎉 SEVİYE ATLADIN! 🎉</Text>
                )}
                
                <View style={styles.levelRow}>
                    <Text style={styles.levelLabel}>SEVİYE {result.new_level}</Text>
                    <Text style={styles.xpGainedText}>+{result.xp_gained} XP</Text>
                </View>

                <View style={styles.xpBarContainer}>
                    <View style={[styles.xpBarFill, { width: `${xpPercentage}%` }]} />
                </View>
                <Text style={styles.xpDetailText}>{result.new_xp} / {result.required_xp} XP</Text>
            </View>

            {/* Oyuncu Detayları */}
            <Text style={styles.sectionTitle}>Seçtiğin Futbolcular</Text>
            <View style={styles.playersContainer}>
                {result.details.map((player, index) => (
                    <View key={index} style={styles.playerCard}>
                        <Text style={styles.playerName}>{player.name}</Text>
                        <Text style={styles.playerStat}>{player.value} {metricLabel}</Text>
                    </View>
                ))}
            </View>

            {/* Butonlar */}
            <View style={styles.buttonContainer}>
                <TouchableOpacity 
                    style={[styles.actionBtn, styles.actionBtnPrimary]} 
                    onPress={() => navigation.replace('TargetScore')}
                >
                    <Text style={styles.actionBtnTextPrimary}>YENİ OYUN</Text>
                </TouchableOpacity>

                <TouchableOpacity 
                    style={[styles.actionBtn, styles.actionBtnSecondary]} 
                    onPress={() => navigation.navigate('MainTabs')}
                >
                    <Text style={styles.actionBtnTextSecondary}>ANA MENÜ</Text>
                </TouchableOpacity>
            </View>

                </ScrollView>
            </SafeAreaView>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    buttonContainer: {
        flexDirection: 'row',
        marginTop: 20,
        marginHorizontal: 15,
        justifyContent: 'space-between',
        gap: 10
    },
    actionBtn: {
        flex: 1,
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
    actionBtnSecondary: {
        backgroundColor: '#0e3609',
        borderColor: '#4a840a',
    },
    actionBtnTextPrimary: {
        color: '#FFF',
        fontFamily: FONTS.headingBlack,
        fontSize: 16,
    },
    actionBtnTextSecondary: {
        color: '#95c029',
        fontFamily: FONTS.headingBlack,
        fontSize: 16,
    },
    headerCard: {
        backgroundColor: '#0e3609',
        marginHorizontal: 15,
        marginVertical: 15,
        borderRadius: 20,
        padding: 15,
        borderWidth: 3,
        borderColor: '#4a840a',
        borderBottomWidth: 6,
        alignItems: 'center'
    },
    leagueText: {
        color: '#95c029',
        fontSize: 18,
        marginBottom: 10,
        fontFamily: FONTS.headingBlack,
        textTransform: 'uppercase',
        letterSpacing: 1
    },
    comparisonRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        width: '100%',
        marginBottom: 10
    },
    compBox: {
        alignItems: 'center',
        flex: 1
    },
    compLabel: {
        color: '#FFF',
        fontSize: 10,
        marginBottom: 2,
        fontFamily: FONTS.headingBlack,
        opacity: 0.9
    },
    compValue: {
        color: '#FFF',
        fontSize: 28,
        fontFamily: FONTS.headingBlack,
    },
    compDivider: {
        paddingHorizontal: 15
    },
    vsText: {
        color: 'rgba(255,255,255,0.4)',
        fontSize: 24,
        fontFamily: FONTS.headingBlack,
    },
    distanceContainer: {
        alignItems: 'center',
        marginTop: 5,
        paddingTop: 10,
        borderTopWidth: 1,
        borderColor: 'rgba(255,255,255,0.1)',
        width: '100%'
    },
    distanceTitle: {
        fontSize: 16,
        fontFamily: FONTS.headingBlack,
        marginBottom: 2,
        textAlign: 'center'
    },
    distanceText: {
        color: '#FFF',
        fontFamily: FONTS.headingBlack,
        fontSize: 14
    },
    xpCard: {
        backgroundColor: '#0e3609',
        marginHorizontal: 15,
        padding: 15,
        borderRadius: 20,
        borderWidth: 3,
        borderColor: '#4a840a',
        borderBottomWidth: 6,
        marginBottom: 15
    },
    levelUpText: {
        color: '#fcc205',
        fontSize: 20,
        fontFamily: FONTS.headingBlack,
        textAlign: 'center',
        marginBottom: 10
    },
    levelRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10
    },
    levelLabel: {
        color: '#95c029',
        fontSize: SIZES.large,
        fontFamily: FONTS.headingBlack,
    },
    xpGainedText: {
        color: '#fcc205',
        fontSize: SIZES.medium,
        fontFamily: FONTS.headingBlack,
    },
    xpBarContainer: {
        height: 12,
        backgroundColor: 'rgba(255,255,255,0.1)',
        borderRadius: 6,
        overflow: 'hidden',
        marginBottom: 8
    },
    xpBarFill: {
        height: '100%',
        backgroundColor: COLORS.primary,
        borderRadius: 6
    },
    xpDetailText: {
        color: '#FFF',
        fontSize: SIZES.small,
        textAlign: 'right',
        fontFamily: FONTS.headingBlack,
        opacity: 0.8
    },
    sectionTitle: {
        color: '#FFF',
        fontSize: 14,
        marginLeft: 20,
        marginBottom: 8,
        marginTop: 5,
        fontFamily: FONTS.headingBlack,
        textTransform: 'uppercase',
        letterSpacing: 1
    },
    playersContainer: {
        marginHorizontal: 15,
        gap: 8
    },
    playerCard: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        backgroundColor: '#4a840a',
        padding: 12,
        borderRadius: 14,
        alignItems: 'center',
        borderWidth: 3,
        borderColor: '#95c029',
        borderBottomWidth: 4,
    },
    playerName: {
        color: '#FFF',
        fontSize: 14,
        fontFamily: FONTS.headingBlack,
        flex: 1
    },
    playerStat: {
        color: '#fcc205',
        fontSize: 14,
        fontFamily: FONTS.headingBlack,
    }
});
