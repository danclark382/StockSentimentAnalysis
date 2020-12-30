import React from 'react';
import logo from './assets/logo.png';
import './App.css';
import firebase from './constants/firebase';
import { 
  Image,
  Container,
} from 'semantic-ui-react'
import CardSection from './components/CardSection';
import TopMenu from './components/TopMenu';
import EntityType from './constants/EntityType';

class App extends React.Component {
  
  constructor(props) {
    super(props);

    this.state = { 
      users: [],
      etfs: [],
      indexes: [],
      tickers: [],
      usersLoading: false,
      etfsLoading: false,
      indexesLoading: false,
      tickersLoading: false,
    };

    //this.usersRef = firebase.database().ref('/users'); 
    //this.etfsRef = firebase.database().ref('/etfs'); 
    //this.indexesRef = firebase.database().ref('/indexes'); 
    this.tickersRef = firebase.database().ref('/tickers'); 
  }

  componentDidMount() { 
    this.subscribeToFeed();
  }

  subscribeToFeed = () => {
    // this.subscribeToUsers();
    this.subscribeToTickers();
    // this.subscribeToEtfs();
    // this.subscribeToIndexes();
  }

  transformDataToArray(data) {
    if(data == null) return [];

    var keys = Object.keys(data);
    data = Object.values(data);
    
    for(var i = 0; i < data.length; i++){
      data[i].key = keys[i];
    }

    return data;
  }

  subscribeToUsers = () => {
    this.usersRef.on('value', snapshot => {
      this.setState({ usersLoading: true }, () => {
        var data = this.transformDataToArray(snapshot.val());
        this.setState({ 
          users: data,
          usersLoading: false
        });
      });
    });
  } 

  subscribeToTickers = () => {
    this.tickersRef.on('value', snapshot => {
      this.setState({ tickersLoading: true }, () => {
        var data = this.transformDataToArray(snapshot.val());
        //console.log(data);
        this.setState({ 
          tickers: data,
          tickersLoading: false
        });
      });
    });
  } 

  subscribeToEtfs = () => {
    this.etfsRef.on('value', snapshot => {
      this.setState({ etfsLoading: true }, () => {
        var data = this.transformDataToArray(snapshot.val());
        this.setState({ 
          etfs: data,
          etfsLoading: false
        });
      });
    });
  } 

  subscribeToIndexes = () => {
    this.indexesRef.on('value', snapshot => {
      this.setState({ indexesLoading: true }, () => {
        var data = this.transformDataToArray(snapshot.val());
        this.setState({ 
          indexes: data,
          indexesLoading: false
        });
      });
    });
  } 

  addEntity = (entityType, entityId) => {
    let data = { key: entityId };

    switch(entityType) {
      case EntityType.USER:
        this.usersRef.update({ [entityId]: data });
        break;
      case EntityType.TICKER:
        this.tickersRef.update({ [entityId]: data });
        break;
      case EntityType.ETF:
        this.etfsRef.update({ [entityId]: data });
        break;
      case EntityType.INDEX:
        this.indexesRef.update({ [entityId]: data });
        break;
      default:
        break;
    }
  }

  removeEntity = (entityType, entityId) => {
    switch(entityType) {
      case EntityType.USER:
        this.usersRef.child(entityId).remove();
        break;
      case EntityType.TICKER:
        this.tickersRef.child(entityId).remove();
        break;
      case EntityType.ETF:
        this.etfsRef.child(entityId).remove();
        break;
      case EntityType.INDEX:
        this.indexesRef.child(entityId).remove();
        break;
      default:
        break;
    }
  }

  render() {

    const { 
      users, 
      usersLoading, 
      tickers, 
      tickersLoading,
      etfs,
      etfsLoading,
      indexes,
      indexesLoading
    } = this.state;

    return (
      <Container className="App">
        <TopMenu activeItem={'users'} />
        <header className="App-header">
          <Image src={logo} className="App-logo" alt="logo" />
        </header>
        <body>
          {/* <CardSection entityType={EntityType.USER} data={users} loading={usersLoading} addEntity={this.addEntity} removeEntity={this.removeEntity}/> */}
          <CardSection entityType={EntityType.TICKER} data={tickers} loading={tickersLoading} addEntity={this.addEntity} removeEntity={this.removeEntity}/>
          {/* <CardSection entityType={EntityType.ETF} data={etfs} loading={etfsLoading} addEntity={this.addEntity} removeEntity={this.removeEntity}/> */}
          {/* <CardSection entityType={EntityType.INDEX} data={indexes} loading={indexesLoading} addEntity={this.addEntity} removeEntity={this.removeEntity}/> */}
          <br/>
          <br/>
          <br/>

        </body>
      </Container>
    );
  }
}

export default App;
