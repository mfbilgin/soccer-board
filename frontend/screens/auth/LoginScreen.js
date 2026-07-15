import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Dimensions, ImageBackground, KeyboardAvoidingView, ScrollView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { COLORS, SIZES, FONTS } from '../../theme';
import * as SecureStore from 'expo-secure-store';
import api from '../../api';
import { Image } from 'expo-image';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

export default function LoginScreen({ navigation }) {
  const [username, setUsername] = useState('player1');
  const [password, setPassword] = useState('pass123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      await SecureStore.setItemAsync('userToken', response.data.access_token);
      navigation.replace('MainTabs');
    } catch (err) {
      setError('Giriş başarısız. Bilgilerinizi kontrol edin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ImageBackground 
        source={require('../../assets/background.png')} 
        style={styles.container}
        imageStyle={{ opacity: 0.25 }}
        resizeMode="cover"
    >
      <SafeAreaView style={styles.safeArea}>
        <KeyboardAvoidingView 
          style={{ flex: 1 }} 
          behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        >
          <ScrollView 
            contentContainerStyle={styles.scrollGrow} 
            keyboardShouldPersistTaps="handled" 
            showsVerticalScrollIndicator={false}
          >
            
            {/* LOGO */}
            <View style={styles.logoContainer}>
                <Image 
                    source={require('../../assets/logo.png')}
                    style={styles.logoImage}
                    contentFit="contain"
                />
                <Text style={styles.logoText}>GoalMaster</Text>
                <Text style={styles.logoSubText}>Futbol Tahmin & Strateji</Text>
            </View>

            {/* LOGIN FORM */}
            <View style={styles.formContainer}>
              <View style={styles.formHeader}>
                <Ionicons name="football" size={24} color={COLORS.secondary} style={{marginRight: 8}}/>
                <Text style={styles.formTitle}>Oyuna Giriş Yap</Text>
              </View>
              <Text style={styles.formSub}>Sahaya çıkmak için efsanevi hesabına giriş yap.</Text>

              <View style={styles.inputWrapper}>
                <Ionicons name="person-outline" size={20} color={COLORS.textMuted} style={styles.inputIcon} />
                <TextInput 
                  style={styles.input}
                  value={username}
                  onChangeText={setUsername}
                  placeholder="Kullanıcı Adı"
                  placeholderTextColor={'rgba(255,255,255,0.3)'}
                  autoCapitalize="none"
                />
              </View>
              
              <View style={styles.inputWrapper}>
                <Ionicons name="lock-closed-outline" size={20} color={COLORS.textMuted} style={styles.inputIcon} />
                <TextInput 
                  style={styles.input}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  placeholder="Şifre"
                  placeholderTextColor={'rgba(255,255,255,0.3)'}
                />
              </View>
              
              {error ? <Text style={styles.errorText}>{error}</Text> : null}

              <TouchableOpacity 
                style={styles.loginBtn}
                onPress={handleLogin}
                disabled={loading}
                activeOpacity={0.8}
              >
                {loading ? (
                  <ActivityIndicator color={COLORS.textDark} />
                ) : (
                  <View style={{flexDirection: 'row', alignItems: 'center'}}>
                    <Text style={styles.btnText}>SAHAYA ÇIK</Text>
                    <Ionicons name="arrow-forward" size={20} color={COLORS.textDark} style={{marginLeft: 8}} />
                  </View>
                )}
              </TouchableOpacity>

              <TouchableOpacity 
                style={styles.registerLink} 
                activeOpacity={0.6}
                onPress={() => navigation.navigate('Register')}
              >
                <Text style={styles.registerLinkText}>
                  Henüz hesabın yok mu? <Text style={styles.registerLinkHighlight}>Kayıt Ol</Text>
                </Text>
              </TouchableOpacity>

              <View style={styles.dividerContainer}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>VEYA</Text>
                <View style={styles.dividerLine} />
              </View>

              {Platform.OS === 'android' ? (
                <TouchableOpacity style={[styles.socialBtn, styles.googleBtn]} activeOpacity={0.8}>
                  <Ionicons name="logo-google" size={20} color="#DB4437" style={{marginRight: 10}} />
                  <Text style={styles.googleBtnText}>Google ile Giriş Yap</Text>
                </TouchableOpacity>
              ) : (
                <TouchableOpacity style={[styles.socialBtn, styles.appleBtn]} activeOpacity={0.8}>
                  <Ionicons name="logo-apple" size={20} color="#FFF" style={{marginRight: 10}} />
                  <Text style={styles.appleBtnText}>Apple ile Giriş Yap</Text>
                </TouchableOpacity>
              )}
            </View>

          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.darkBase,
  },
  safeArea: {
    flex: 1,
  },
  scrollGrow: {
    flexGrow: 1,
    padding: 20,
    justifyContent: 'center',
    paddingBottom: Dimensions.get('window').height * 0.3, // Dinamik boşluk
  },
  
  // Logo
  logoContainer: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoImage: {
    width: 140,
    height: 140,
    marginBottom: 10,
  },
  logoText: {
    color: COLORS.text,
    fontFamily: FONTS.headingBlack,
    fontSize: 32,
    letterSpacing: -0.5,
    textTransform: 'uppercase',
  },
  logoSubText: {
    color: COLORS.secondary,
    fontFamily: FONTS.mono,
    fontSize: 12,
    letterSpacing: 2,
    marginTop: 4,
    textTransform: 'uppercase',
  },

  // Form (Green Theme Card)
  formContainer: {
    width: '100%',
    backgroundColor: COLORS.surface,
    borderRadius: SIZES.radiusLg,
    padding: 25,
    borderWidth: 2,
    borderColor: COLORS.surfaceVariant,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 10,
  },
  formHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  formTitle: {
    color: COLORS.text,
    fontFamily: FONTS.headingBlack,
    fontSize: 22,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  formSub: {
    color: COLORS.textMuted,
    fontFamily: FONTS.body,
    fontSize: 13,
    marginBottom: 25,
    lineHeight: 18,
  },
  
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.2)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    borderRadius: SIZES.radius,
    marginBottom: 15,
    height: 55,
    paddingHorizontal: 15,
  },
  inputIcon: {
    marginRight: 10,
  },
  input: {
    flex: 1,
    color: COLORS.text,
    fontFamily: FONTS.body,
    fontSize: 16,
    height: '100%',
  },
  
  loginBtn: {
    backgroundColor: COLORS.secondary, // Gold/Yellow
    height: 55,
    borderRadius: SIZES.radius,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
    shadowColor: COLORS.secondary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
  },
  btnText: {
    color: COLORS.textDark,
    fontFamily: FONTS.headingBlack,
    fontSize: 16,
    letterSpacing: 1,
  },
  
  errorText: {
    color: COLORS.danger,
    fontFamily: FONTS.body,
    fontSize: 12,
    textAlign: 'center',
    marginBottom: 5,
  },

  registerLink: {
    marginTop: 20,
    marginBottom: 20,
    alignItems: 'center',
  },
  registerLinkText: {
    color: COLORS.textMuted,
    fontFamily: FONTS.body,
    fontSize: 13,
  },
  registerLinkHighlight: {
    color: COLORS.primary, // Bright Grass Green
    fontFamily: FONTS.heading,
    fontWeight: 'bold',
  },
  
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  dividerText: {
    color: COLORS.textMuted,
    paddingHorizontal: 15,
    fontFamily: FONTS.mono,
    fontSize: 10,
    letterSpacing: 1,
  },
  
  socialBtn: {
    flexDirection: 'row',
    height: 50,
    borderRadius: SIZES.radius,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
  },
  googleBtn: {
    backgroundColor: '#FFFFFF',
    borderColor: '#E0E0E0',
  },
  googleBtnText: {
    color: '#333333',
    fontFamily: FONTS.heading,
    fontSize: 14,
  },
  appleBtn: {
    backgroundColor: '#000000',
    borderColor: '#333333',
  },
  appleBtnText: {
    color: '#FFFFFF',
    fontFamily: FONTS.heading,
    fontSize: 14,
  }
});
