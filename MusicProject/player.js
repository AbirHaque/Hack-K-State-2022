import TrackPlayer from 'react-native-track-player';

const music = [{
    title: 'death bed',
    artist: 'Powfu',
    artwork: 'https://images-na.ssl-images-amazon.com/images/I/A1LVEJikmZL._AC_SX425_.jpg',
    url: 'https://sample-music.netlify.app/death%20bed.mp3',
    duration: 2 * 60 + 53,
    id: '1',
  },{
    title: 'bad liar',
    artist: 'Imagine Dragons',
    artwork: 'https://images-na.ssl-images-amazon.com/images/I/A1LVEJikmZL._AC_SX425_.jpg',
    url: 'https://sample-music.netlify.app/Bad%20Liar.mp3',
    duration: 2 * 60,
    id: '2',
    track_number: '2'
  }
 ]

const trackPlayer = async () => {
    await TrackPlayer.setupPlayer();

    await TrackPlayer.add(music);

    await TrackPlayer.play();
};

export default trackPlayer;
