/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 * @flow strict-local
 */

import React from 'react';
import type {Node} from 'react';
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  useColorScheme,
  View,
} from 'react-native';

import {
  Colors,
  DebugInstructions,
  Header,
  LearnMoreLinks,
  ReloadInstructions,
} from 'react-native/Libraries/NewAppScreen';

import TrackPlayer from 'react-native-track-player';
import trackPlayer from './player';

const App: () => Node = () => {
  const isDarkMode = useColorScheme() === 'dark';
  const [text, onChangeText] = React.useState("");

  const backgroundStyle = {
    backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
  };

  trackPlayer();

  return (
    <View
      style={{
        flex: 1,
        justifyContent: "center",
        alignItems: "center"
      }}>
        <TextInput
        onChangeText={onChangeText}
        placeholder="useless placeholder"
        value={text}
        />
      <Text>Hello {text}</Text>
    </View>
  );
};

export default App;
