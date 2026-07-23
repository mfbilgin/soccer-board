import React from 'react';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { View, Text, ActivityIndicator, ImageBackground } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

import { useFonts, Outfit_700Bold, Outfit_900Black } from '@expo-google-fonts/outfit';
import { Inter_400Regular, Inter_700Bold } from '@expo-google-fonts/inter';
import { JetBrainsMono_500Medium } from '@expo-google-fonts/jetbrains-mono';

import LoginScreen from './screens/auth/LoginScreen';
import RegisterScreen from './screens/auth/RegisterScreen';
import HomeScreen from './screens/main/HomeScreen';
import SingleplayerScreen from './screens/singleplayer/SingleplayerScreen';
import TicTacToeScreen from './screens/singleplayer/TicTacToeScreen';
import TicTacToeResultScreen from './screens/singleplayer/TicTacToeResultScreen';
import PyramidScreen from './screens/singleplayer/PyramidScreen';
import CareerGuessScreen from './screens/singleplayer/CareerGuessScreen';
import LobbyScreen from './screens/multiplayer/LobbyScreen';
import RoomSelectionScreen from './screens/multiplayer/RoomSelectionScreen';
import TargetScoreScreen from './screens/singleplayer/TargetScoreScreen';
import MultiplayerTargetScoreScreen from './screens/multiplayer/MultiplayerTargetScoreScreen';
import MultiplayerTicTacToeScreen from './screens/multiplayer/MultiplayerTicTacToeScreen';
import ChainReactionScreen from './screens/multiplayer/ChainReactionScreen';
import ExtremeSquadScreen from './screens/singleplayer/ExtremeSquadScreen';
import MultiplayerExtremeSquadScreen from './screens/multiplayer/MultiplayerExtremeSquadScreen';
import FindTwoScreen from './screens/multiplayer/FindTwoScreen';
import FlagElevenScreen from './screens/singleplayer/FlagElevenScreen';
import MultiplayerFlagElevenScreen from './screens/multiplayer/MultiplayerFlagElevenScreen';
import TargetScoreResultScreen from './screens/singleplayer/TargetScoreResultScreen';
import CustomTabBar from './components/CustomTabBar';
import { COLORS, FONTS } from './theme';

import UpdateOverlay from './components/UpdateOverlay';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Dummy components for tabs
const DummyScreen = () => <View style={{flex:1, backgroundColor: COLORS.darkBase}} />;

const navTheme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    background: 'transparent',
  },
};

function MainTabs() {
  return (
    <Tab.Navigator
      tabBar={(props) => <CustomTabBar {...props} />}
      screenOptions={{ headerShown: false }}
    >
      <Tab.Screen name="Oyna" component={HomeScreen} />
      <Tab.Screen name="Sıralama" component={DummyScreen} />
      <Tab.Screen name="Market" component={DummyScreen} />
      <Tab.Screen name="Sosyal" component={DummyScreen} />
      <Tab.Screen name="Profil" component={DummyScreen} />
    </Tab.Navigator>
  );
}

export default function App() {
  const [fontsLoaded] = useFonts({
    Outfit_700Bold,
    Outfit_900Black,
    Inter_400Regular,
    Inter_700Bold,
    JetBrainsMono_500Medium
  });

  if (!fontsLoaded) {
    return (
      <View style={{flex: 1, backgroundColor: COLORS.darkBase, justifyContent: 'center', alignItems: 'center'}}>
        <ActivityIndicator size="large" color="#c3f400" />
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <ImageBackground 
        source={require('./assets/bg.png')} 
        style={{flex: 1, backgroundColor: COLORS.darkBase}}
        blurRadius={3} // Slight blur for depth
      >
        <NavigationContainer theme={navTheme}>
          <StatusBar style="light" />
        <Stack.Navigator 
          initialRouteName="Login"
          screenOptions={{
            headerStyle: { backgroundColor: COLORS.background },
            headerTintColor: COLORS.text,
            headerShadowVisible: false,
            headerBackTitleVisible: false,
            headerTitleStyle: { fontFamily: FONTS.heading },
            contentStyle: { backgroundColor: 'transparent' },
            animation: 'fade',
          }}
        >
        <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
        <Stack.Screen name="Register" component={RegisterScreen} options={{ headerShown: false }} />
        <Stack.Screen name="MainTabs" component={MainTabs} options={{ headerShown: false }} />
        <Stack.Screen name="Singleplayer" component={SingleplayerScreen} options={{ headerShown: false }} />
        <Stack.Screen name="TicTacToe" component={TicTacToeScreen} options={{ title: 'Futbol Tic-Tac-Toe' }} />
        <Stack.Screen name="TicTacToeResult" component={TicTacToeResultScreen} options={{ title: 'Oyun Sonucu', headerShown: false }} />
        <Stack.Screen name="Pyramid" component={PyramidScreen} options={{ title: 'Top 10 Piramidi' }} />
        <Stack.Screen name="CareerGuess" component={CareerGuessScreen} options={{ headerShown: false }} />
        <Stack.Screen name="Lobby" component={LobbyScreen} options={{ headerShown: false }} />
        <Stack.Screen name="RoomSelection" component={RoomSelectionScreen} options={{ headerShown: false }} />
        <Stack.Screen name="TargetScore" component={TargetScoreScreen} options={{ title: 'Hedef Tutturma' }} />
        <Stack.Screen name="MultiplayerTargetScore" component={MultiplayerTargetScoreScreen} options={{ headerShown: false }} />
        <Stack.Screen name="MultiplayerTicTacToe" component={MultiplayerTicTacToeScreen} options={{ headerShown: false }} />
        <Stack.Screen name="ChainReaction" component={ChainReactionScreen} options={{ headerShown: false }} />
        <Stack.Screen name="ExtremeSquad" component={ExtremeSquadScreen} options={{ title: 'Ekstrem Kadro' }} />
        <Stack.Screen name="MultiplayerExtremeSquad" component={MultiplayerExtremeSquadScreen} options={{ headerShown: false }} />
        <Stack.Screen name="FindTwo" component={FindTwoScreen} options={{ headerShown: false }} />
        <Stack.Screen name="FlagEleven" component={FlagElevenScreen} options={{ title: 'Bayrak XI' }} />
        <Stack.Screen name="MultiplayerFlagEleven" component={MultiplayerFlagElevenScreen} options={{ headerShown: false }} />
        <Stack.Screen name="TargetScoreResult" component={TargetScoreResultScreen} options={{ title: 'Sonuç', headerShown: false }} />
      </Stack.Navigator>
    </NavigationContainer>
    <UpdateOverlay />
    </ImageBackground>
    </SafeAreaProvider>
  );
}
