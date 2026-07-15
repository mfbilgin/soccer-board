import React, { useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Dimensions, Animated } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONTS } from '../theme';

const { width } = Dimensions.get('window');

export default function CustomTabBar({ state, descriptors, navigation }) {
    const tabWidth = width / state.routes.length;
    const slideAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        Animated.spring(slideAnim, {
            toValue: state.index * tabWidth,
            useNativeDriver: true,
            bounciness: 12,
            speed: 14,
        }).start();
    }, [state.index, tabWidth]);

    return (
        <SafeAreaView style={styles.safeArea} edges={['bottom']}>
            <View style={styles.tabBarBackground}>
                {/* Kaybolan/Kayan Animasyonlu Arka Plan (Pill) */}
                <Animated.View 
                    style={[
                        styles.slidingPill, 
                        { width: tabWidth, transform: [{ translateX: slideAnim }] }
                    ]} 
                >
                    <View style={styles.pillInner} />
                </Animated.View>

                {/* Tab Butonları */}
                {state.routes.map((route, index) => {
                    const { options } = descriptors[route.key];
                    const label = options.title !== undefined ? options.title : route.name;
                    const isFocused = state.index === index;

                    const onPress = () => {
                        const event = navigation.emit({
                            type: 'tabPress',
                            target: route.key,
                            canPreventDefault: true,
                        });

                        if (!isFocused && !event.defaultPrevented) {
                            navigation.navigate(route.name);
                        }
                    };

                    let iconName = 'ellipse';
                    if (route.name === 'Oyna') iconName = isFocused ? 'home' : 'home-outline';
                    else if (route.name === 'Sıralama') iconName = isFocused ? 'trophy' : 'trophy-outline';
                    else if (route.name === 'Market') iconName = isFocused ? 'cart' : 'cart-outline';
                    else if (route.name === 'Sosyal') iconName = isFocused ? 'people' : 'people-outline';
                    else if (route.name === 'Profil') iconName = isFocused ? 'person' : 'person-outline';

                    return (
                        <TouchableOpacity
                            key={index}
                            activeOpacity={1}
                            accessibilityRole="button"
                            accessibilityState={isFocused ? { selected: true } : {}}
                            onPress={onPress}
                            style={styles.tabButton}
                        >
                            <Ionicons 
                                name={iconName} 
                                size={isFocused ? 26 : 24} 
                                color={isFocused ? COLORS.secondary : COLORS.textMuted} 
                            />
                            <Text style={[
                                styles.tabText, 
                                { color: isFocused ? COLORS.secondary : COLORS.textMuted },
                                isFocused && styles.tabTextFocused
                            ]}>
                                {label === 'Oyna' ? 'ANA SAYFA' : label.toUpperCase()}
                            </Text>
                        </TouchableOpacity>
                    );
                })}
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    safeArea: {
        backgroundColor: COLORS.surface,
    },
    tabBarBackground: {
        flexDirection: 'row',
        backgroundColor: COLORS.darkBase, 
        height: 85,
        paddingBottom: 10, // Alt kısımdan boşluk bırakarak ikonları yukarı iter
        elevation: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -4 },
        shadowOpacity: 0.5,
        shadowRadius: 10,
        position: 'relative',
        alignItems: 'center',
        borderTopWidth: 1,
        borderTopColor: 'rgba(255,255,255,0.05)',
    },
    slidingPill: {
        position: 'absolute',
        height: 65,
        top: 5,
        left: 0,
        justifyContent: 'center',
        alignItems: 'center',
    },
    pillInner: {
        width: '85%',
        height: '100%',
        backgroundColor: COLORS.primary, // Parlak çim yeşili
        borderRadius: 20,
        borderWidth: 2,
        borderColor: '#54b917', // Hafif parlama efekti için dış çerçeve
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 3 },
        shadowOpacity: 0.4,
        shadowRadius: 4,
        elevation: 5,
    },
    tabButton: {
        flex: 1,
        height: '100%',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1, // Kayan haptın üzerinde olması için
    },
    tabText: {
        fontFamily: FONTS.headingBlack,
        fontSize: 10,
        marginTop: 4,
    },
    tabTextFocused: {
        fontSize: 11, // Aktifken bir tık büyüsün
    }
});
