import firebase from 'firebase';

const firebaseConfig = {
  apiKey: "AIzaSyCUbLUprqaNEY01KeeUofBf5YgZ-qiNoEE",
  authDomain: "stocksent-1bbf9.firebaseapp.com",
  databaseURL: "https://stocksent-1bbf9.firebaseio.com",
  projectId: "stocksent-1bbf9",
  storageBucket: "stocksent-1bbf9.appspot.com",
  messagingSenderId: "855705239138",
  appId: "1:855705239138:web:9b68babb675899f73c5b3b",
  measurementId: "G-QB39ESGFKJ"
};

const Firebase = firebase.initializeApp(firebaseConfig);

export default Firebase;

