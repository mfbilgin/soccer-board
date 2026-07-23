import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, ScrollView, ImageBackground } from 'react-native';
import { COLORS, FONTS, GLOBAL_STYLES } from '../../theme';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

export default function InitialsGuessScreen({ navigation }) {
    const [round, setRound] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isSearchVisible, setSearchVisible] = useState(false);
    const [verifying, setVerifying] = useState(false);
    const [revealed, setRevealed] = useState(null);

    const roundRef = useRef(null);

    useEffect(() => {
        loadRound();
    }, []);

    const loadRound = async () => {
        try {
            setLoading(true);
            setRevealed(null);
            const res = await api.get('/game/initials-guess/letter-pools');
            setRound(res.data);
            roundRef.current = res.data;
        } catch (err) {
            Alert.alert('Hata', 'Bulmaca yüklenemedi.');
        } finally {
            setLoading(false);
        }
    };

    const handlePlayerSelect = async (player) => {
        setSearchVisible(false);
        setVerifying(true);
        try {
            const r = roundRef.current;
            const res = await api.post('/game/initials-guess/verify', {
                start_letter: r.start_letter,
                end_letter: r.end_letter,
                player_id: player.id,
            });

            if (res.data.correct) {
                setRevealed(player.name);
            } else {
                Alert.alert('Yanlış', `${player.name} bu harflere uymuyor. Tekrar dene.`);
            }
        } catch (err) {
            Alert.alert('Hata', 'Tahmin doğrulanırken bir hata oluştu.');
        } finally {
            setVerifying(false);
        }
    };

    const giveUp = async () => {
        try {
            const r = roundRef.current;
            const res = await api.get(`/game/initials-guess/reveal?start_letter=${r.start_letter}&end_letter=${r.end_letter}`);
            setRevealed(res.data.answer);
        } catch (err) {
            Alert.alert('Hata', 'Cevap alınamadı.');
        }
    };

    if (loading || !round) {
        return (
            <View style={[GLOBAL_STYLES.screen, GLOBAL_STYLES.center]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={{ color: COLORS.text, marginTop: 10 }}>Harfler Belirleniyor...</Text>
            </View>
        );
    }

    if (revealed) {
        return (
            <ScrollView contentContainerStyle={{ padding: 20, alignItems: 'center', paddingBottom: 60 }}>
                <Text style={{ color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 32, marginBottom: 20, textAlign: 'center' }}>
                    BULDUN! 🎉
                </Text>
                <Text style={{ color: COLORS.primary, fontFamily: FONTS.headingBlack, fontSize: 22, marginBottom: 30 }}>
                    {revealed}
                </Text>
                <TouchableOpacity style={[GLOBAL_STYLES.primaryButton, { width: '100%' }]} onPress={loadRound}>
                    <Text style={GLOBAL_STYLES.primaryButtonText}>YENİ BULMACA</Text>
                </TouchableOpacity>
            </ScrollView>
        );
    }

    return (
        <ImageBackground source={require('../../assets/background.png')} style={GLOBAL_STYLES.screen} imageStyle={{ opacity: 0.15 }} resizeMode="cover">
            <View style={{ flex: 1, padding: 20, justifyContent: 'center' }}>
                <View style={styles.headerCard}>
                    <Text style={styles.headerTitle}>Harf Düellosu</Text>
                    <Text style={styles.headerSub}>Bu harflerle başlayıp biten bir futbolcu bul</Text>
                    <View style={styles.lettersRow}>
                        <View style={styles.letterBox}><Text style={styles.letterText}>{round.start_letter}</Text></View>
                        <Text style={styles.dots}>. . .</Text>
                        <View style={styles.letterBox}><Text style={styles.letterText}>{round.end_letter}</Text></View>
                    </View>
                </View>

                <TouchableOpacity
                    style={[GLOBAL_STYLES.primaryButton, { marginTop: 30 }, verifying && { opacity: 0.5 }]}
                    onPress={() => setSearchVisible(true)}
                    disabled={verifying}
                >
                    {verifying ? <ActivityIndicator color={COLORS.background} /> : <Text style={GLOBAL_STYLES.primaryButtonText}>OYUNCU YAZ</Text>}
                </TouchableOpacity>

                <TouchableOpacity style={[GLOBAL_STYLES.primaryButton, { marginTop: 15, backgroundColor: '#e74c3c' }]} onPress={giveUp}>
                    <Text style={[GLOBAL_STYLES.primaryButtonText, { color: '#FFF' }]}>Pes Et</Text>
                </TouchableOpacity>

                <SearchModal visible={isSearchVisible} onClose={() => setSearchVisible(false)} onSelect={handlePlayerSelect} searchType={1} />
            </View>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    headerCard: { backgroundColor: '#0e3609', padding: 25, borderRadius: 24, alignItems: 'center', borderWidth: 4, borderColor: '#4a840a', borderBottomWidth: 8 },
    headerTitle: { color: '#95c029', fontSize: 26, fontFamily: FONTS.headingBlack, textAlign: 'center' },
    headerSub: { color: '#FFF', fontSize: 13, fontFamily: FONTS.body, textAlign: 'center', marginTop: 5, opacity: 0.9, marginBottom: 20 },
    lettersRow: { flexDirection: 'row', alignItems: 'center', gap: 15 },
    letterBox: { width: 60, height: 60, borderRadius: 16, backgroundColor: '#4a840a', borderWidth: 3, borderColor: '#95c029', justifyContent: 'center', alignItems: 'center' },
    letterText: { color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 30 },
    dots: { color: COLORS.textMuted, fontSize: 20 },
});
