import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Modal, Animated, Easing } from 'react-native';
import * as Updates from 'expo-updates';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONTS } from '../theme';

export default function UpdateOverlay() {
  const { isUpdateAvailable, isUpdatePending, isDownloading } = Updates.useUpdates();
  const [showOverlay, setShowOverlay] = useState(false);
  const [statusText, setStatusText] = useState('Güncelleme Kontrol Ediliyor...');
  const progressAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // If an update is available or downloading, show the overlay
    if (isUpdateAvailable || isDownloading) {
      setShowOverlay(true);
      setStatusText('Yeni Özellikler İndiriliyor...');
      
      // Start a simulated progress bar that goes to 85% over 10 seconds
      Animated.timing(progressAnim, {
        toValue: 85,
        duration: 10000,
        easing: Easing.out(Easing.quad),
        useNativeDriver: false,
      }).start();
    }

    // When download finishes, the update becomes pending (ready to apply)
    if (isUpdatePending) {
      setShowOverlay(true);
      setStatusText('Uygulama Yeniden Başlatılıyor...');
      
      // Instantly jump to 100% when finished
      Animated.timing(progressAnim, {
        toValue: 100,
        duration: 500,
        useNativeDriver: false,
      }).start(() => {
        // Wait a brief moment to show 100%, then reload
        setTimeout(() => {
          Updates.reloadAsync();
        }, 800);
      });
    }
  }, [isUpdateAvailable, isUpdatePending, isDownloading]);

  if (!showOverlay) return null;

  return (
    <Modal visible={true} transparent={true} animationType="fade">
      <View style={styles.container}>
        <View style={styles.card}>
          <Ionicons name="cloud-download" size={60} color={COLORS.primary} style={styles.icon} />
          <Text style={styles.title}>Güncelleme Bulundu!</Text>
          <Text style={styles.subtitle}>{statusText}</Text>
          
          <View style={styles.progressContainer}>
            <Animated.View 
              style={[
                styles.progressBar, 
                { 
                  width: progressAnim.interpolate({
                    inputRange: [0, 100],
                    outputRange: ['0%', '100%']
                  }) 
                }
              ]} 
            />
          </View>
          
          <Text style={styles.warning}>Lütfen uygulamayı kapatmayın...</Text>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'rgba(10, 15, 20, 0.95)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  card: {
    backgroundColor: COLORS.surface,
    width: '100%',
    padding: 30,
    borderRadius: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(195, 244, 0, 0.3)',
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    elevation: 10,
  },
  icon: {
    marginBottom: 20,
    textShadowColor: 'rgba(195, 244, 0, 0.5)',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  title: {
    fontFamily: FONTS.heading,
    fontSize: 24,
    color: COLORS.text,
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontFamily: FONTS.regular,
    fontSize: 16,
    color: COLORS.textMuted,
    marginBottom: 30,
    textAlign: 'center',
  },
  progressContainer: {
    width: '100%',
    height: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 6,
    overflow: 'hidden',
    marginBottom: 15,
  },
  progressBar: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: 6,
  },
  warning: {
    fontFamily: FONTS.medium,
    fontSize: 12,
    color: '#FF6B6B',
    marginTop: 10,
  },
});
