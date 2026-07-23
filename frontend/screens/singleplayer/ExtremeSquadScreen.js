import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Alert, ScrollView, ImageBackground } from 'react-native';
import { COLORS, FONTS, GLOBAL_STYLES } from '../../theme';
import api from '../../api';
import SearchModal from '../../components/SearchModal';

const ROLE_LABELS = { Goalkeeper: 'Kaleci', Defender: 'Defans', Midfield: 'Ortasaha', Attack: 'Forvet' };

export default function ExtremeSquadScreen({ navigation }) {
    const [puzzle, setPuzzle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [squad, setSquad] = useState([]); // slot_id sirasinda dolu/null
    const [validating, setValidating] = useState(false);
    const [timeLeft, setTimeLeft] = useState(90);
    const [result, setResult] = useState(null);

    const [isSearchVisible, setSearchVisible] = useState(false);
    const [currentSlotIndex, setCurrentSlotIndex] = useState(-1);

    const submittedRef = useRef(false);
    const squadRef = useRef([]);
    const puzzleRef = useRef(null);

    useEffect(() => {
        loadPuzzle();
    }, []);

    useEffect(() => {
        if (!puzzle || result) return;
        const timer = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    clearInterval(timer);
                    if (!submittedRef.current) submitSquad(true);
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(timer);
    }, [puzzle, result]);

    const loadPuzzle = async () => {
        try {
            setLoading(true);
            const res = await api.get('/games/extreme-squad/generate');
            setPuzzle(res.data);
            puzzleRef.current = res.data;
            const empty = res.data.slots.map(() => null);
            setSquad(empty);
            squadRef.current = empty;
            setTimeLeft(90);
        } catch (err) {
            Alert.alert("Hata", "Bulmaca yüklenemedi.");
        } finally {
            setLoading(false);
        }
    };

    const openSearch = (index) => {
        setCurrentSlotIndex(index);
        setSearchVisible(true);
    };

    const handlePlayerSelect = async (player) => {
        if (squad.some(p => p?.id === player.id)) {
            Alert.alert("Geçersiz Seçim", "Bu oyuncuyu zaten seçtiniz!");
            return;
        }

        setSearchVisible(false);
        setValidating(true);

        try {
            const slot = puzzle.slots[currentSlotIndex];
            const res = await api.post('/games/extreme-squad/validate-single', {
                team_id: slot.team_id,
                role: slot.role,
                player_id: player.id,
            });

            if (res.data.valid) {
                const newSquad = [...squadRef.current];
                newSquad[currentSlotIndex] = { id: player.id, name: player.name, birth_date: res.data.birth_date, height_cm: res.data.height_cm };
                squadRef.current = newSquad;
                setSquad(newSquad);
            } else {
                Alert.alert("Hatalı Seçim", res.data.message);
            }
        } catch (err) {
            Alert.alert("Hata", "Oyuncu doğrulanırken bir hata oluştu.");
        } finally {
            setValidating(false);
        }
    };

    const clearSlot = (index) => {
        const newSquad = [...squadRef.current];
        newSquad[index] = null;
        squadRef.current = newSquad;
        setSquad(newSquad);
    };

    const submitSquad = async (auto = false) => {
        if (submittedRef.current) return;
        submittedRef.current = true;

        try {
            setValidating(true);
            const p = puzzleRef.current;
            const playerIds = squadRef.current.map(s => s ? s.id : null);
            const res = await api.post('/games/extreme-squad/validate', {
                criterion: p.criterion,
                slots: p.slots,
                player_ids: playerIds,
            });
            setResult(res.data);
        } catch (err) {
            Alert.alert("Hata", "Kadro gönderilirken bir hata oluştu.");
            submittedRef.current = false;
        } finally {
            setValidating(false);
        }
    };

    if (loading || !puzzle) {
        return (
            <View style={[GLOBAL_STYLES.screen, GLOBAL_STYLES.center]}>
                <ActivityIndicator size="large" color={COLORS.primary} />
                <Text style={{ color: COLORS.text, marginTop: 10 }}>Bulmaca Hazırlanıyor...</Text>
            </View>
        );
    }

    if (result) {
        return (
            <ScrollView contentContainerStyle={{ padding: 20, alignItems: 'center', paddingBottom: 60 }}>
                <Text style={{ color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 32, marginBottom: 10, textAlign: 'center' }}>
                    {result.valid ? `${result.xp_gained} XP KAZANDIN!` : 'KADRO GEÇERSİZ'}
                </Text>
                {result.valid && (
                    <Text style={{ color: COLORS.textMuted, fontFamily: FONTS.mono, marginBottom: 20 }}>
                        Toplam: {result.total_value} — Teorik En İyi: {result.theoretical_best} (fark: {result.distance})
                    </Text>
                )}

                <View style={{ width: '100%', gap: 8 }}>
                    {result.details.map((d, idx) => (
                        <View key={idx} style={[styles.resultRow, { borderColor: d.valid ? COLORS.primary : COLORS.danger }]}>
                            <Text style={styles.resultRoleText}>{ROLE_LABELS[puzzle.slots[idx].role]} · {puzzle.slots[idx].team_name}</Text>
                            <Text style={{ color: d.valid ? COLORS.primary : COLORS.danger, fontFamily: FONTS.mono }}>
                                {d.name || '—'} {d.valid ? `(${d.value})` : '(geçersiz)'}
                            </Text>
                        </View>
                    ))}
                </View>

                <TouchableOpacity style={[GLOBAL_STYLES.primaryButton, { width: '100%', marginTop: 30 }]} onPress={() => navigation.goBack()}>
                    <Text style={GLOBAL_STYLES.primaryButtonText}>GERİ DÖN</Text>
                </TouchableOpacity>
            </ScrollView>
        );
    }

    const filledCount = squad.filter(Boolean).length;

    return (
        <ImageBackground source={require('../../assets/background.png')} style={GLOBAL_STYLES.screen} imageStyle={{ opacity: 0.15 }} resizeMode="cover">
            <View style={{ flex: 1, paddingBottom: 40 }}>
                <View style={styles.headerCard}>
                    <Text style={styles.headerTitle}>{puzzle.criterion === 'tallest' ? 'En Uzun Kadro' : 'En Genç Kadro'}</Text>
                    <Text style={styles.headerSub}>1-4-3-3 dizilimini, her slot için verilen takımdan kur</Text>
                    <Text style={[styles.timerText, { color: timeLeft <= 15 ? COLORS.danger : COLORS.primary }]}>⏱️ {timeLeft}s</Text>
                </View>

                <ScrollView contentContainerStyle={{ padding: 15, gap: 10 }}>
                    {puzzle.slots.map((slot, index) => {
                        const player = squad[index];
                        return (
                            <View key={slot.slot_id} style={{ position: 'relative' }}>
                                <TouchableOpacity
                                    style={[styles.slotBase, player && styles.slotFilled]}
                                    onPress={() => openSearch(index)}
                                    disabled={!!player}
                                >
                                    <Text style={styles.slotLabel}>{ROLE_LABELS[slot.role]} · {slot.team_name}</Text>
                                    <Text style={player ? styles.slotPlayerName : styles.slotPlaceholder}>
                                        {player ? player.name : 'Oyuncu Seç +'}
                                    </Text>
                                </TouchableOpacity>
                                {player && (
                                    <TouchableOpacity style={styles.clearBtn} onPress={() => clearSlot(index)}>
                                        <Text style={{ color: '#FFF', fontWeight: 'bold', fontSize: 16 }}>X</Text>
                                    </TouchableOpacity>
                                )}
                            </View>
                        );
                    })}
                </ScrollView>

                <View style={{ padding: 20 }}>
                    <TouchableOpacity
                        style={[GLOBAL_STYLES.primaryButton, (validating || filledCount < 11) ? { opacity: 0.5, backgroundColor: COLORS.secondary } : { backgroundColor: COLORS.primary }]}
                        onPress={() => submitSquad(false)}
                        disabled={validating || filledCount < 11}
                    >
                        {validating ? (
                            <ActivityIndicator color={COLORS.background} />
                        ) : (
                            <Text style={GLOBAL_STYLES.primaryButtonText}>
                                {filledCount === 11 ? 'Bitir' : `Slotları Doldur (${filledCount}/11)`}
                            </Text>
                        )}
                    </TouchableOpacity>
                </View>

                <SearchModal
                    visible={isSearchVisible}
                    onClose={() => setSearchVisible(false)}
                    onSelect={handlePlayerSelect}
                    searchType={1}
                />
            </View>
        </ImageBackground>
    );
}

const styles = StyleSheet.create({
    headerCard: { backgroundColor: '#0e3609', padding: 20, margin: 20, borderRadius: 24, alignItems: 'center', borderWidth: 4, borderColor: '#4a840a', borderBottomWidth: 8 },
    headerTitle: { color: '#95c029', fontSize: 26, fontFamily: FONTS.headingBlack, textAlign: 'center' },
    headerSub: { color: '#FFF', fontSize: 13, fontFamily: FONTS.body, textAlign: 'center', marginTop: 5, opacity: 0.9 },
    timerText: { fontSize: 24, fontFamily: FONTS.headingBlack, marginTop: 10 },

    slotBase: { backgroundColor: '#4a840a', borderWidth: 3, borderColor: '#95c029', borderBottomWidth: 6, borderRadius: 16, padding: 14 },
    slotFilled: { borderColor: '#fcc205', backgroundColor: '#0e3609', borderBottomWidth: 3 },
    slotLabel: { color: 'rgba(255,255,255,0.7)', fontFamily: FONTS.mono, fontSize: 11, marginBottom: 4 },
    slotPlaceholder: { color: '#FFF', fontFamily: FONTS.headingBlack, fontSize: 16 },
    slotPlayerName: { color: '#fcc205', fontFamily: FONTS.headingBlack, fontSize: 16 },
    clearBtn: { position: 'absolute', top: -10, right: -10, backgroundColor: '#e74c3c', width: 30, height: 30, borderRadius: 15, justifyContent: 'center', alignItems: 'center', borderWidth: 2, borderColor: '#FFF' },

    resultRow: { padding: 12, borderRadius: 12, borderWidth: 1, backgroundColor: 'rgba(255,255,255,0.05)' },
    resultRoleText: { color: COLORS.textMuted, fontFamily: FONTS.mono, fontSize: 11, marginBottom: 4 },
});
