import React, { useEffect, useState, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Dimensions, ImageBackground, Modal, Animated, Easing } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, SIZES, FONTS } from '../../theme';
import api from '../../api';
import { Image } from 'expo-image';
import { Ionicons } from '@expo/vector-icons';
import Svg, { Defs, Pattern, Circle, Rect } from 'react-native-svg';

const { width } = Dimensions.get('window');

export default function HomeScreen({ navigation }) {
    const [user, setUser] = useState(null);
    const [questsModalVisible, setQuestsModalVisible] = useState(false);
    const [avatarModalVisible, setAvatarModalVisible] = useState(false);
    
    // Zıplayan top (DVD Screensaver) animasyon değerleri
    const animX = useRef(new Animated.Value(0)).current;
    const animY = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        loadProfile();
        
        const ballSize = 140; // Topun boyutunu 80'den 140'a çıkardım
        const { width, height } = Dimensions.get('window');
        const maxX = width - ballSize;
        const maxY = height - ballSize - 85; // Alt kısımdaki menülerin arkasına saklanmaması için zıplama sınırı yukarı çekildi

        Animated.loop(
            Animated.sequence([
                Animated.timing(animX, { toValue: maxX, duration: 3500, easing: Easing.linear, useNativeDriver: true }),
                Animated.timing(animX, { toValue: 0, duration: 3500, easing: Easing.linear, useNativeDriver: true })
            ])
        ).start();

        Animated.loop(
            Animated.sequence([
                Animated.timing(animY, { toValue: maxY, duration: 4800, easing: Easing.linear, useNativeDriver: true }),
                Animated.timing(animY, { toValue: 0, duration: 4800, easing: Easing.linear, useNativeDriver: true })
            ])
        ).start();
    }, []);

    const loadProfile = async () => {
        try {
            const res = await api.get('/auth/me');
            setUser(res.data);
        } catch (err) {
            console.log(err);
        }
    };

    const formatNumber = (num) => {
        if (!num) return '0';
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    };

    const renderQuestsModal = () => (
        <Modal
            animationType="fade"
            transparent={true}
            visible={questsModalVisible}
            onRequestClose={() => setQuestsModalVisible(false)}
        >
            <View style={styles.modalOverlay}>
                <View style={styles.modalContent}>
                    <View style={styles.modalHeader}>
                        <Text style={styles.modalTitle}>Günlük Görevler</Text>
                        <TouchableOpacity onPress={() => setQuestsModalVisible(false)}>
                            <Ionicons name="close" size={28} color={COLORS.text} />
                        </TouchableOpacity>
                    </View>

                    {/* Top Buttons */}
                    <View style={styles.modalTopButtons}>
                        <TouchableOpacity style={styles.modalActionBtn}>
                            <Ionicons name="play-circle" size={24} color={COLORS.text} style={{marginBottom: 5}}/>
                            <Text style={styles.modalActionBtnText}>Video İzle</Text>
                            <Text style={styles.modalActionBtnSub}>+10 💎</Text>
                        </TouchableOpacity>
                        
                        <TouchableOpacity style={[styles.modalActionBtn, {backgroundColor: COLORS.secondary}]}>
                            <Ionicons name="gift" size={24} color={COLORS.textDark} style={{marginBottom: 5}}/>
                            <Text style={[styles.modalActionBtnText, {color: COLORS.textDark}]}>Günlük Ödül</Text>
                            <Text style={[styles.modalActionBtnSub, {color: COLORS.textDark}]}>Hazır!</Text>
                        </TouchableOpacity>
                    </View>

                    {/* Task List */}
                    <ScrollView style={styles.modalTaskList}>
                        {[
                            { title: '3 Maça Tahmin Yap', progress: 3, target: 3, reward: '+50 💎' },
                            { title: '1 Rakibi Yen', progress: 0, target: 1, reward: '+100 💎' },
                            { title: '5 Günlük Seri', progress: 5, target: 5, reward: '+500 💰' },
                        ].map((task, idx) => {
                            const isCompleted = task.progress >= task.target;
                            const progressPct = Math.min((task.progress / task.target) * 100, 100);
                            
                            return (
                                <View key={idx} style={styles.modalTaskRow}>
                                    <View style={styles.modalTaskInfo}>
                                        <View style={{flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8}}>
                                            <Text style={styles.modalTaskTitle}>{task.title}</Text>
                                            <Text style={styles.modalTaskReward}>{task.reward}</Text>
                                        </View>
                                        
                                        <View style={styles.progressBarBg}>
                                            <View style={[styles.progressBarFill, { width: `${progressPct}%` }]} />
                                        </View>
                                        <Text style={styles.progressText}>{task.progress}/{task.target}</Text>
                                    </View>
                                    
                                    <TouchableOpacity 
                                        style={[styles.collectBtn, isCompleted ? styles.collectBtnActive : styles.collectBtnInactive]}
                                        disabled={!isCompleted}
                                    >
                                        <Text style={[styles.collectBtnText, isCompleted ? {color: COLORS.textDark} : {color: COLORS.textMuted}]}>
                                            {isCompleted ? 'Topla' : 'Bekleniyor'}
                                        </Text>
                                    </TouchableOpacity>
                                </View>
                            );
                        })}
                    </ScrollView>
                </View>
            </View>
        </Modal>
    );

    const renderAvatarModal = () => (
        <Modal
            animationType="fade"
            transparent={true}
            visible={avatarModalVisible}
            onRequestClose={() => setAvatarModalVisible(false)}
        >
            <View style={styles.modalOverlay}>
                <View style={styles.avatarModalContent}>
                    <TouchableOpacity 
                        style={styles.closeAvatarBtn}
                        onPress={() => setAvatarModalVisible(false)}
                    >
                        <Ionicons name="close" size={30} color={COLORS.text} />
                    </TouchableOpacity>
                    
                    <View style={styles.largeAvatarCircle}>
                        <Ionicons name="person" size={80} color={COLORS.surface} />
                    </View>
                    <Text style={styles.largeAvatarName}>{user ? user.username : 'Oyuncu'}</Text>
                </View>
            </View>
        </Modal>
    );

    return (
        <ImageBackground 
            source={require('../../assets/background.png')} 
            style={styles.container}
            imageStyle={{ opacity: 0.25 }}
            resizeMode="cover"
        >
            {/* Arkaplanda Zıplayan Top (DVD Logosu Mantığı) */}
            <Animated.View style={{
                position: 'absolute',
                top: 0, left: 0,
                width: 140, height: 140,
                opacity: 0.3, // Kendi PNG'niz olduğu için daha net görünmesi adına saydamlığı biraz artırdım
                transform: [
                    { translateX: animX },
                    { translateY: animY }
                ]
            }}>
                <Image 
                    source={require('../../assets/ball.png')} 
                    style={{ width: 140, height: 140 }} 
                    contentFit="contain" 
                />
            </Animated.View>
            
            <SafeAreaView style={styles.safeArea}>
                <View style={styles.scrollContent}>
                    
                    {/* BÖLÜM 1: ÜST BAR */}
                    <View style={styles.topBarContainer}>
                        
                        {/* 1.1 Sol Profil Kartı */}
                        <View style={styles.profileCard}>
                            {/* Texture Overlay */}
                            <View style={[StyleSheet.absoluteFill, { borderRadius: SIZES.radiusLg, overflow: 'hidden' }]}>
                                <Svg width="100%" height="100%" opacity={0.12}>
                                    <Defs>
                                        <Pattern id="roughTexture" width="6" height="6" patternUnits="userSpaceOnUse">
                                            <Circle cx="1.5" cy="1.5" r="1.2" fill="#0e3609" />
                                            <Circle cx="4.5" cy="4.5" r="1.2" fill="#0e3609" />
                                        </Pattern>
                                    </Defs>
                                    <Rect width="100%" height="100%" fill="url(#roughTexture)" />
                                </Svg>
                            </View>
                            <View style={styles.profileHeader}>
                                <TouchableOpacity 
                                    style={styles.avatarContainer}
                                    activeOpacity={0.7}
                                    onPress={() => setAvatarModalVisible(true)}
                                >
                                    <View style={styles.avatarCircle}>
                                        <Ionicons name="person" size={24} color="#0e3609" />
                                    </View>
                                </TouchableOpacity>
                                <Text style={styles.playerName} numberOfLines={1}>{user ? user.username : 'Oyuncu'}</Text>
                            </View>
                            
                            <TouchableOpacity 
                                style={styles.currencyContainer}
                                activeOpacity={0.7}
                                onPress={() => navigation.navigate('Market')}
                            >
                                <View style={styles.currencyPill}>
                                    <View style={styles.currencyIconBg}>
                                        <Text style={styles.currencyEmoji}>🪙</Text>
                                    </View>
                                    <Text style={styles.currencyText}>{formatNumber(user?.chips || 27083)}</Text>
                                </View>
                                
                                <View style={[styles.currencyPill, {marginTop: 6}]}>
                                    <View style={styles.currencyIconBg}>
                                        <Text style={styles.currencyEmoji}>💎</Text>
                                    </View>
                                    <Text style={styles.currencyText}>{formatNumber(133)}</Text>
                                </View>
                            </TouchableOpacity>
                        </View>

                        {/* 1.2 Sağ Günlük Görevler Kartı */}
                        <TouchableOpacity 
                            style={styles.questsCard}
                            activeOpacity={0.8}
                            onPress={() => setQuestsModalVisible(true)}
                        >
                            {/* Texture Overlay */}
                            <View style={[StyleSheet.absoluteFill, { borderRadius: SIZES.radiusLg, overflow: 'hidden' }]}>
                                <Svg width="100%" height="100%" opacity={0.15}>
                                    <Defs>
                                        <Pattern id="roughTextureQuests" width="6" height="6" patternUnits="userSpaceOnUse">
                                            <Circle cx="1.5" cy="1.5" r="1.2" fill="#000000" />
                                            <Circle cx="4.5" cy="4.5" r="1.2" fill="#000000" />
                                        </Pattern>
                                    </Defs>
                                    <Rect width="100%" height="100%" fill="url(#roughTextureQuests)" />
                                </Svg>
                            </View>

                            <View style={{flexDirection: 'row', justifyContent: 'center', alignItems: 'center', position: 'relative'}}>
                                <Text style={styles.questsCardTitle}>Görevler</Text>
                                <View style={[styles.notificationBadge, { position: 'absolute', right: 0 }]}>
                                    <Text style={styles.notificationText}>1</Text>
                                </View>
                            </View>
                            
                            <View style={styles.questCenterIcon}>
                                <Ionicons name="calendar-outline" size={32} color="#fcc205" />
                            </View>
                            
                            <View style={{marginTop: 'auto'}}>
                                <View style={{flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4}}>
                                    <Text style={styles.questSummaryText}>Günlük İlerleme</Text>
                                    <Text style={styles.questSummaryPct}>%60</Text>
                                </View>
                                <View style={styles.progressBarBg}>
                                    <View style={[styles.progressBarFill, { width: '60%' }]} />
                                </View>
                            </View>
                        </TouchableOpacity>

                    </View>

                    {/* BÖLÜM 2: ORTA KISIM */}
                    <View style={styles.middleSection}>
                        
                        {/* ONLINE */}
                        <View style={{ position: 'relative' }}>
                            {/* Dekoratif Çizgiler (Sağ Üst Çizgiler) */}
                            <View style={{position: 'absolute', top: -5, right: 5, zIndex: 10, flexDirection: 'row', gap: 4, transform: [{rotate: '45deg'}]}}>
                                <View style={{width: 4, height: 10, backgroundColor: '#FFF', borderRadius: 2}} />
                                <View style={{width: 4, height: 16, backgroundColor: '#FFF', borderRadius: 2, transform: [{translateY: -4}]}} />
                                <View style={{width: 4, height: 10, backgroundColor: '#FFF', borderRadius: 2}} />
                            </View>

                            <TouchableOpacity 
                                activeOpacity={0.8}
                                onPress={() => navigation.navigate('Lobby')}
                            >
                                <View style={styles.onlineBtnOuter}>
                                    <View style={styles.onlineBtnInner}>
                                        <View style={styles.onlineBtn}>
                                            {/* Dotted Background Layer */}
                                            <View style={[StyleSheet.absoluteFill, { borderRadius: 22, overflow: 'hidden' }]}>
                                                <Svg width="100%" height="100%">
                                                    <Defs>
                                                        <Pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">
                                                            <Circle cx="8" cy="8" r="2.5" fill="#e6ebd8" />
                                                        </Pattern>
                                                    </Defs>
                                                    <Rect width="100%" height="100%" fill="url(#dots)" />
                                                </Svg>
                                            </View>
                                            <View style={styles.onlineInnerContent}>
                                                <Text style={styles.onlineTitle} numberOfLines={1} adjustsFontSizeToFit>ONLINE</Text>
                                                <Text style={styles.onlineSub} numberOfLines={1} adjustsFontSizeToFit>DÜNYADAKİ OYUNCULARA KARŞI OYNA!</Text>
                                            </View>
                                        </View>
                                    </View>
                                </View>
                            </TouchableOpacity>
                        </View>

                        {/* ROW BUTTONS */}
                        <View style={styles.rowButtons}>
                            
                            {/* OFFLINE */}
                            <View style={{ flex: 1, position: 'relative' }}>
                                {/* Sol Üst Sarı Çizgiler */}
                                <View style={{position: 'absolute', top: -10, left: -5, zIndex: 10, flexDirection: 'row', gap: 4, transform: [{rotate: '-45deg'}]}}>
                                    <View style={{width: 4, height: 10, backgroundColor: '#f2b50b', borderRadius: 2}} />
                                    <View style={{width: 4, height: 16, backgroundColor: '#f2b50b', borderRadius: 2, transform: [{translateY: -4}]}} />
                                    <View style={{width: 4, height: 10, backgroundColor: '#f2b50b', borderRadius: 2}} />
                                </View>
                                
                                <TouchableOpacity 
                                    style={styles.offlineBtn} 
                                    activeOpacity={0.8}
                                    onPress={() => navigation.navigate('Singleplayer')}
                                >
                                    {/* Texture Overlay */}
                                    <View style={[StyleSheet.absoluteFill, { borderRadius: 18, overflow: 'hidden' }]}>
                                        <Svg width="100%" height="100%" opacity={0.15}>
                                            <Defs>
                                                <Pattern id="roughTextureOffline" width="6" height="6" patternUnits="userSpaceOnUse">
                                                    <Circle cx="1.5" cy="1.5" r="1.2" fill="#0e3609" />
                                                    <Circle cx="4.5" cy="4.5" r="1.2" fill="#0e3609" />
                                                </Pattern>
                                            </Defs>
                                            <Rect width="100%" height="100%" fill="url(#roughTextureOffline)" />
                                        </Svg>
                                    </View>

                                    <Ionicons name="football" size={46} color="#FFF" style={{marginBottom: 2}}/>
                                    <Text style={styles.offlineTitle} numberOfLines={1} adjustsFontSizeToFit>OFFLINE</Text>
                                    <Text style={styles.offlineSub} numberOfLines={1} adjustsFontSizeToFit>YETENEKLERİNİ GELİŞTİR</Text>
                                </TouchableOpacity>
                            </View>

                            {/* PARTY */}
                            <View style={{ flex: 1, position: 'relative' }}>
                                {/* Sağ Üst Sarı Çizgiler */}
                                <View style={{position: 'absolute', top: -10, right: -5, zIndex: 10, flexDirection: 'row', gap: 4, transform: [{rotate: '45deg'}]}}>
                                    <View style={{width: 4, height: 10, backgroundColor: '#f2b50b', borderRadius: 2}} />
                                    <View style={{width: 4, height: 16, backgroundColor: '#f2b50b', borderRadius: 2, transform: [{translateY: -4}]}} />
                                    <View style={{width: 4, height: 10, backgroundColor: '#f2b50b', borderRadius: 2}} />
                                </View>

                                <TouchableOpacity 
                                    style={styles.partyBtn} 
                                    activeOpacity={0.8}
                                    onPress={() => navigation.navigate('RoomSelection')}
                                >
                                    {/* Texture Overlay */}
                                    <View style={[StyleSheet.absoluteFill, { borderRadius: 18, overflow: 'hidden' }]}>
                                        <Svg width="100%" height="100%" opacity={0.12}>
                                            <Defs>
                                                <Pattern id="roughTextureParty" width="6" height="6" patternUnits="userSpaceOnUse">
                                                    <Circle cx="1.5" cy="1.5" r="1.2" fill="#000000" />
                                                    <Circle cx="4.5" cy="4.5" r="1.2" fill="#000000" />
                                                </Pattern>
                                            </Defs>
                                            <Rect width="100%" height="100%" fill="url(#roughTextureParty)" />
                                        </Svg>
                                    </View>

                                    <Ionicons name="game-controller" size={46} color="#25671f" style={{marginBottom: 2}}/>
                                    <Text style={styles.partyTitle} numberOfLines={1} adjustsFontSizeToFit>PARTY</Text>
                                    <Text style={styles.partySub} numberOfLines={1} adjustsFontSizeToFit>ARKADAŞLARINLA OYNA</Text>
                                </TouchableOpacity>
                            </View>

                        </View>
                    </View>

                    {/* BÖLÜM 3: MİNİ LİDERLİK TABLOSU */}
                    <View style={styles.leaderboardSection}>
                        <View style={styles.leaderboardHeader}>
                            <View style={{flexDirection: 'row', alignItems: 'center'}}>
                                <Ionicons name="trophy" size={20} color={COLORS.secondary} style={{marginRight: 6}}/>
                                <Text style={styles.leaderboardTitle}>Haftanın Liderleri</Text>
                            </View>
                            <TouchableOpacity onPress={() => navigation.navigate('Sıralama')}>
                                <Text style={styles.leaderboardLink}>Tümünü Gör</Text>
                            </TouchableOpacity>
                        </View>

                        <View style={styles.leaderboardCard}>
                            {/* 1. Sıra */}
                            <View style={styles.lbRow}>
                                <View style={[styles.lbRankBadge, {backgroundColor: '#FFD700'}]}><Text style={styles.lbRankText}>1</Text></View>
                                <View style={styles.lbAvatar}><Ionicons name="person" size={14} color={COLORS.surface}/></View>
                                <Text style={styles.lbName}>ProGamer99</Text>
                                <Text style={styles.lbScore}>15.4K 🏆</Text>
                            </View>
                            
                            <View style={styles.lbDivider} />
                            
                            {/* 2. Sıra */}
                            <View style={styles.lbRow}>
                                <View style={[styles.lbRankBadge, {backgroundColor: '#C0C0C0'}]}><Text style={styles.lbRankText}>2</Text></View>
                                <View style={styles.lbAvatar}><Ionicons name="person" size={14} color={COLORS.surface}/></View>
                                <Text style={styles.lbName}>King_of_Goals</Text>
                                <Text style={styles.lbScore}>12.1K 🏆</Text>
                            </View>
                            
                            <View style={styles.lbDivider} />
                            
                            {/* 3. Sıra */}
                            <View style={styles.lbRow}>
                                <View style={[styles.lbRankBadge, {backgroundColor: '#CD7F32'}]}><Text style={styles.lbRankText}>3</Text></View>
                                <View style={styles.lbAvatar}><Ionicons name="person" size={14} color={COLORS.surface}/></View>
                                <Text style={styles.lbName}>MessiFan10</Text>
                                <Text style={styles.lbScore}>9.8K 🏆</Text>
                            </View>
                        </View>
                    </View>

                </View>
            </SafeAreaView>
            
            {renderQuestsModal()}
            {renderAvatarModal()}
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: COLORS.darkBase },
    safeArea: { flex: 1 },
    scrollContent: { 
        flex: 1,
        paddingHorizontal: 20, 
        paddingTop: 20, 
        paddingBottom: 25,
        justifyContent: 'space-evenly',
    },
    
    // --- 1. ÜST BAR ---
    topBarContainer: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        gap: 10,
    },
    
    // 1.1 Sol Profil Kartı
    profileCard: {
        flex: 1,
        backgroundColor: '#4a840a',
        borderRadius: SIZES.radiusLg,
        padding: 12,
        paddingBottom: 16,
        borderWidth: 2,
        borderColor: '#0e3609',
        justifyContent: 'space-between',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 5,
        elevation: 6,
    },
    profileHeader: {
        flexDirection: 'row',
        alignItems: 'center'
    },
    avatarContainer: {
        marginRight: 8,
    },
    avatarCircle: {
        width: 44,
        height: 44,
        borderRadius: 22,
        backgroundColor: '#fff',
        justifyContent: 'center',
        alignItems: 'center',
    },
    editIconBadge: {
        position: 'absolute',
        bottom: -2,
        right: -2,
        backgroundColor: COLORS.primary,
        width: 18,
        height: 18,
        borderRadius: 9,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1,
        borderColor: COLORS.surface,
    },
    playerName: {
        color: '#faf3eb',
        fontFamily: FONTS.heading,
        fontSize: 18,
        flex: 1,
    },
    currencyContainer: {
        marginTop: 10,
    },
    currencyPill: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#95c029',
        borderRadius: SIZES.radius,
        paddingVertical: 4,
        paddingHorizontal: 6,
        justifyContent: 'space-between',
    },
    currencyIconBg: {
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 6,
    },
    currencyEmoji: {
        fontSize: 16,
    },
    currencyText: {
        color: '#0e3609',
        fontFamily: FONTS.headingBlack,
        fontSize: 15,
        textAlign: 'right',
        flex: 1,
    },

    // 1.2 Sağ Görev Kartı
    questsCard: {
        flex: 1,
        backgroundColor: '#0e3609',
        borderRadius: SIZES.radiusLg,
        padding: 12,
        paddingBottom: 16,
        borderWidth: 2,
        borderColor: '#4a840a',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 5,
        elevation: 6,
    },
    questsCardTitle: {
        color: '#fcc205',
        fontFamily: FONTS.headingBlack,
        fontSize: 14,
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },
    notificationBadge: {
        backgroundColor: COLORS.danger,
        width: 16,
        height: 16,
        borderRadius: 8,
        justifyContent: 'center',
        alignItems: 'center',
    },
    notificationText: {
        color: '#fff',
        fontSize: 10,
        fontFamily: FONTS.headingBlack,
    },
    questCenterIcon: {
        alignItems: 'center',
        justifyContent: 'center',
        marginVertical: 4,
    },
    questSummaryText: {
        color: '#FFF',
        fontFamily: FONTS.body,
        fontSize: 10,
    },
    questSummaryPct: {
        color: '#95c029',
        fontFamily: FONTS.mono,
        fontSize: 10,
        fontWeight: 'bold',
    },

    // --- MODAL STYLES ---
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.7)',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 20,
    },
    modalContent: {
        width: '100%',
        backgroundColor: COLORS.surface,
        borderRadius: SIZES.radiusXl,
        padding: 20,
        borderWidth: 2,
        borderColor: COLORS.surfaceVariant,
    },
    modalHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 20,
    },
    modalTitle: {
        color: COLORS.text,
        fontFamily: FONTS.headingBlack,
        fontSize: 22,
    },
    modalTopButtons: {
        flexDirection: 'row',
        gap: 10,
        marginBottom: 20,
    },
    modalActionBtn: {
        flex: 1,
        backgroundColor: COLORS.primary,
        borderRadius: SIZES.radiusMd,
        padding: 15,
        alignItems: 'center',
    },
    modalActionBtnText: {
        color: COLORS.text,
        fontFamily: FONTS.heading,
        fontSize: 14,
    },
    modalActionBtnSub: {
        color: COLORS.text,
        fontFamily: FONTS.mono,
        fontSize: 12,
        opacity: 0.8,
        marginTop: 2,
    },
    modalTaskList: {
        maxHeight: 300,
    },
    modalTaskRow: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: 'rgba(0,0,0,0.2)',
        borderRadius: SIZES.radius,
        padding: 15,
        marginBottom: 10,
    },
    modalTaskInfo: {
        flex: 1,
        marginRight: 15,
    },
    modalTaskTitle: {
        color: COLORS.text,
        fontFamily: FONTS.heading,
        fontSize: 14,
    },
    modalTaskReward: {
        color: COLORS.secondary,
        fontFamily: FONTS.mono,
        fontSize: 14,
        fontWeight: 'bold',
    },
    progressBarBg: {
        height: 8,
        backgroundColor: 'rgba(255,255,255,0.1)',
        borderRadius: 4,
        overflow: 'hidden',
        marginVertical: 6,
    },
    progressBarFill: {
        height: '100%',
        backgroundColor: COLORS.primary,
    },
    progressText: {
        color: COLORS.textMuted,
        fontFamily: FONTS.mono,
        fontSize: 10,
        textAlign: 'right',
    },
    collectBtn: {
        paddingHorizontal: 12,
        paddingVertical: 10,
        borderRadius: SIZES.radius,
        justifyContent: 'center',
        alignItems: 'center',
    },
    collectBtnActive: {
        backgroundColor: COLORS.secondary,
    },
    collectBtnInactive: {
        backgroundColor: 'rgba(255,255,255,0.1)',
    },
    collectBtnText: {
        fontFamily: FONTS.heading,
        fontSize: 12,
    },

    // --- 2. ORTA KISIM (Oyun Modları) ---
    middleSection: {
        gap: 15,
    },
    
    // Online Button
    onlineBtnOuter: {
        backgroundColor: '#0e3609',
        borderRadius: 32,
        padding: 4, // reduced
        paddingBottom: 10, // reduced
        marginTop: 10,
        transform: [{ rotate: '2.5deg' }],
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.4,
        shadowRadius: 5,
        elevation: 8,
    },
    onlineBtnInner: {
        backgroundColor: '#95c029',
        borderRadius: 26,
        padding: 4,
    },
    onlineBtn: {
        backgroundColor: '#F7F9F4',
        borderRadius: 22,
        paddingVertical: 25, // reduced from 35
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 2,
        borderColor: '#E5E5E5',
        borderStyle: 'dashed',
    },
    onlineInnerContent: {
        alignItems: 'center',
        transform: [{ rotate: '-2.5deg' }],
    },
    onlineTitle: {
        color: COLORS.surface,
        fontFamily: FONTS.headingBlack,
        fontSize: 66, // increased
        letterSpacing: 1,
        lineHeight: 66,
    },
    onlineSub: {
        color: COLORS.surface,
        fontFamily: FONTS.headingBlack,
        fontSize: 16, // increased
        letterSpacing: 0.5,
        marginTop: 5,
    },

    // Row Buttons
    rowButtons: {
        flexDirection: 'row',
        gap: 15,
    },
    
    // Offline Button
    offlineBtn: {
        width: '100%',
        backgroundColor: '#4a840a',
        borderRadius: 18,
        paddingVertical: 18, // reduced from 24
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 4,
        borderColor: '#95c029',
        borderBottomWidth: 8,
        marginTop: 10,
    },
    offlineTitle: {
        color: '#FFF',
        fontFamily: FONTS.headingBlack,
        fontSize: 32, // increased
        letterSpacing: 0.5,
        lineHeight: 32,
    },
    offlineSub: {
        color: '#FFF',
        fontFamily: FONTS.headingBlack,
        fontSize: 12, // increased
        marginTop: 2,
        opacity: 0.9,
    },

    // Party Button
    partyBtn: {
        width: '100%',
        backgroundColor: '#fcc205',
        borderRadius: 18,
        paddingVertical: 18, // reduced from 24
        alignItems: 'center',
        justifyContent: 'center',
        borderWidth: 4,
        borderColor: '#d4a202',
        borderBottomWidth: 8,
        marginTop: 10,
    },
    partyTitle: {
        color: '#25671f',
        fontFamily: FONTS.headingBlack,
        fontSize: 32, // increased
        letterSpacing: 0.5,
        lineHeight: 32,
    },
    partySub: {
        color: '#25671f',
        fontFamily: FONTS.headingBlack,
        fontSize: 12, // increased
        marginTop: 2,
        opacity: 0.9,
    },

    // --- 3. MİNİ LİDERLİK TABLOSU ---
    leaderboardSection: {
        marginTop: 15, // reduced from 25
    },
    leaderboardHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 10,
        paddingHorizontal: 5,
    },
    leaderboardTitle: {
        color: COLORS.text,
        fontFamily: FONTS.headingBlack,
        fontSize: 16,
        textTransform: 'uppercase',
    },
    leaderboardLink: {
        color: COLORS.secondary,
        fontFamily: FONTS.heading,
        fontSize: 12,
    },
    leaderboardCard: {
        backgroundColor: 'rgba(255,255,255,0.08)',
        borderRadius: SIZES.radiusLg,
        padding: 15,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.1)',
    },
    lbRow: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 5,
    },
    lbRankBadge: {
        width: 24,
        height: 24,
        borderRadius: 12,
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 2,
    },
    lbRankText: {
        color: COLORS.darkBase,
        fontFamily: FONTS.headingBlack,
        fontSize: 12,
    },
    lbAvatar: {
        width: 28,
        height: 28,
        borderRadius: 14,
        backgroundColor: '#FFF',
        justifyContent: 'center',
        alignItems: 'center',
        marginRight: 10,
    },
    lbName: {
        color: COLORS.text,
        fontFamily: FONTS.heading,
        fontSize: 14,
        flex: 1,
    },
    lbScore: {
        color: COLORS.secondary,
        fontFamily: FONTS.mono,
        fontSize: 13,
        fontWeight: 'bold',
    },
    lbDivider: {
        height: 1,
        backgroundColor: 'rgba(255,255,255,0.05)',
        marginVertical: 8,
    },

    // --- AVATAR MODAL ---
    avatarModalContent: {
        backgroundColor: COLORS.surface,
        borderRadius: SIZES.radiusXl,
        padding: 30,
        alignItems: 'center',
        borderWidth: 2,
        borderColor: COLORS.surfaceVariant,
        width: 250,
    },
    closeAvatarBtn: {
        position: 'absolute',
        top: 10,
        right: 10,
        padding: 5,
    },
    largeAvatarCircle: {
        width: 120,
        height: 120,
        borderRadius: 60,
        backgroundColor: '#fff',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 20,
        marginTop: 10,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 5,
        elevation: 6,
    },
    largeAvatarName: {
        color: COLORS.text,
        fontFamily: FONTS.headingBlack,
        fontSize: 22,
    }
});
