/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 * @flow strict-local
 */

import React from 'react';
import { TouchableOpacity, Image } from 'react-native';
import type {Node} from 'react';
import Slider from '@react-native-community/slider';
import TrackPlayer, {State, useProgress, Capability, Event, useTrackPlayerEvents}
from 'react-native-track-player';
import AsyncStorage from '@react-native-async-storage/async-storage';


import {
  StatusBar,
  StyleSheet,
  Text,
  useColorScheme,
  View,
} from 'react-native';

import { create } from 'apisauce'

const likeKey = "likedSongs";

const host = '';
const projectId = '';
const bucketId = '';

// define the api
const api = create({
  baseURL: `http://${host}/80/v1`,
  headers: {'X-Appwrite-Project': `${projectId}`, "Content-type": "application/json"},
})

const events = [
  Event.PlaybackState,
  Event.PlaybackTrackChanged,
  Event.PlaybackQueueEnded
]

const App = () => {
  const isDarkMode = useColorScheme() === 'dark';

  const [songList, setSongList] = React.useState([]);
  const [queueIndex, setQueueIndex] = React.useState(0);

  const [likedSongs, setLikedSongs] = React.useState([]);

  const [isSeeking, setIsSeeking] = React.useState(false);
  //const playerState = usePlaybackState();
  const [playerState, setPlayerState] = React.useState(null)
  const { position, duration } = useProgress();
  //const [curTime, setCurTime] = React.useState(0);
  

  useTrackPlayerEvents(events,  (event) => {
      //console.log(await TrackPlayer.getCurrentTrack())
      if (event.type === Event.PlaybackTrackChanged){
        //console.log(track)
        setQueueIndex(event.nextTrack)
      }
      if (event.type === Event.PlaybackState) {
        console.log(event.state)
        setPlayerState(event.state)
      }
      if (event.type === Event.PlaybackQueueEnded && event.nextTrack !== undefined) {
        TrackPlayer.stop();
      }
    });
  
    const isPlaying = playerState === State.Playing;

  const setUpTrackPlayer = async () => {
    try{
      console.log('setting up...') 
      await TrackPlayer.setupPlayer({
         waitForBuffer: true})
      TrackPlayer.updateOptions({
        capabilities: [
          Capability.Play,
          Capability.Pause,
          Capability.JumpForward,
          Capability.JumpBackward
        ],
        compactCapabilities: [
          Capability.Play,
          Capability.Pause,
          Capability.JumpForward,
          Capability.JumpBackward
        ],
      });
      // useTrackPlayerEvents([Event.PlaybackTrackChanged],  ({track, position, nextTrack}) => {
      //   //console.log(await TrackPlayer.getCurrentTrack())
      //   console.log(track)
      //   setQueueIndex(nextTrack)
      // });
      //TrackPlayer.add(music)
      api.get(`/storage/buckets/${bucketId}/files`)
        .then(response => {
          let i = 1;
          let resSongList = [];
          response.data.files.map((file) => {
            musicJson = {title: file.name, url: `http://${host}/v1/storage/buckets/${bucketId}/files/${file.$id}/view?project=${projectId}`, 
            id: i, duration: 173, artist: "User1", $id: file.$id}
            resSongList = [...resSongList, musicJson]
            i += 1;
          })
          setSongList(resSongList)          
        })
        .catch((err) => console.log(err))
      console.log('set up')
    }
    catch (e){
      console.log(e)
    }
  };

  React.useEffect( () => {

    setUpTrackPlayer();
    
    //setUpTrackPlayer();
    //return () => TrackPlayer.destroy()
  }, []);

  React.useEffect(() => {
    console.log(songList);
    if (songList.length > 0) {
      TrackPlayer.add(songList);
      console.log(duration)
      TrackPlayer.play();
      let refreshPlay = setInterval( () => {
        if (playerState !== State.Stopped &&  playerState !== State.Playing) {
          TrackPlayer.play();
          setPlayerState(State.Playing);
        } else {
          clearInterval(refreshPlay);
        }
      }, 1000);
    }
  }, [songList])

  React.useEffect(() => {
    AsyncStorage.getItem(likeKey)
                .then((likedSongsString) => {
                  const likedSongsList = (likedSongsString) ? JSON.parse(likedSongsString) : []
                  console.log(`liked songs ${likedSongs}`)
                  setLikedSongs(likedSongsList)
                });
  }, []);

  const formatTime = (position) =>{
    
    let time = Math.floor(position);
    let sec = time % 60;
    let min = Math.floor(time/60);
    return `${min < 10 ? '0' : ''}${min}:${sec < 10 ? '0' : ''}${sec}`
  }


  const Item = ({ song, isLiked, index}) => (
    <View style={[styles.item, index == queueIndex && styles.activeItem]}>
      <TouchableOpacity onPress={() => {
        TrackPlayer.skip(index)}}>
        <Text style={{color: 'white'}}>{song.title}</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => likeHandler(song.$id, isLiked)} style={{marginLeft: 'auto'}}>
          <Image source={isLiked ? require("./assets/redHeart.png") : require("./assets/heart.png")} style={{ width: 30,height: 30}} />
        </TouchableOpacity>
    </View>
  );

  
const likeHandler = async (songid, isLiked) => {
  let likedSongsList;
  const likedSongsString = await AsyncStorage.getItem(likeKey)
  if (! likedSongsString){
    likedSongsList = [songid]
    await AsyncStorage.setItem(likeKey, JSON.stringify(likedSongsList))
  }
  else if (! isLiked){
    likedSongsList = JSON.parse(likedSongsString)
    likedSongsList.push(songid)
    await AsyncStorage.setItem(likeKey, JSON.stringify(likedSongsList))
  }
  else{
    likedSongsList = JSON.parse(likedSongsString)
    await AsyncStorage.setItem(likeKey, JSON.stringify(likedSongsList.filter((songid_) => songid_ !== songid)))
  }
  setLikedSongs(likedSongsList);
}

  const renderSongs = songList.map((song, index) => <Item song={song} index={index} isLiked={likedSongs.includes(song.$id)}/>)


  return (
    <View style={{
      flex: 1}}>

        <Text style={{fontWeight: 'bold', fontSize: 30, marginLeft: 15}}>
          Mathic
        </Text>
      
        {renderSongs}

      <View style={{
        flexDirection: 'column',
         marginTop: 'auto', backgroundColor: 'gray'}}
            >
      <Text style={{color: 'white'}}>
        {songList.length > queueIndex && songList[queueIndex].title}
      </Text>
              <View style={{
        flexDirection: 'row'}}>
        
      <Slider
            
            value = {position}
            onValueChange={(value) => {
              //setCurTime(value)
              TrackPlayer.pause();
              TrackPlayer.seekTo(value)
              setIsSeeking(true);
              //TrackPlayer.play();
            }}
            style={{flexGrow: 5}}
            minimumValue={0}
            maximumValue={duration}
            minimumTrackTintColor="#FFFFFF"
            maximumTrackTintColor="#000000"
      />
      
      <Text >
        {formatTime(position)}
      </Text>
      </View>
      
      <View style={{justifyContent: "center",
        alignItems: "center", height: 70,
         flexDirection: "row", justifyContent: 'center'}}>
      <TouchableOpacity style={{width: 'auto', marginHorizontal: 5}}
          onPress={() => {
          TrackPlayer.skipToPrevious()}}>
          <Image source={require('./assets/previous.png')} resizeMode='contain'/>
        </TouchableOpacity>
        <TouchableOpacity style={{width: 'auto', marginHorizontal: 5}}
          onPress={() => isPlaying ? TrackPlayer.pause() : TrackPlayer.play()}>
          <Image source={isPlaying ? require('./assets/pause.png') : require('./assets/play.png')} resizeMode='contain' />
        </TouchableOpacity>
      <TouchableOpacity style={{width: 'auto', marginHorizontal: 5}}
          onPress={() => {
            TrackPlayer.skipToNext()}}>
          <Image source={require('./assets/next.png')} resizeMode='contain' />
        </TouchableOpacity>
      </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginTop: StatusBar.currentHeight || 0,
  },
  item: {
    backgroundColor: '#f9c2ff',
    padding: 20,
    marginVertical: 8,
    marginHorizontal: 16,
    flexDirection: "row"
  },
  activeItem: {
    backgroundColor: 'green'
  },
  title: {
    fontSize: 32,
  },
});

export default App;
