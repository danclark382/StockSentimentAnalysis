import React from 'react';
import { 
  Segment,
  Divider,
  Grid,
  Header,
} from 'semantic-ui-react';
import TickerCard from './TickerCard';
import EntityType from '../constants/EntityType';

class CardSection extends React.Component {
  
  state = {
    showModal: false,
    modalInput: '',
  }

  subscribe = () => {
    this.props.addEntity(this.props.entityType, this.state.modalInput);
    this.setState({ showModal: false });
  }

  removeEntity = (key) => this.props.removeEntity(this.props.entityType, key);

  handleMessage = (e) => this.setState({modalInput: e.target.value});

  showModal = () => this.setState({ showModal: true });
  
  closeModal = () => this.setState({ showModal: false });
  
  getPlaceholderForEntityType = (entityType) => {
    switch(entityType) {
      case EntityType.USER:
        return 'realDonaldTrump';
      case EntityType.TICKER:
        return 'APPL';
      case EntityType.ETF:
        return 'SPY';
      case EntityType.INDEX:
        return 'DIA';
      default:
        return '';
    }
  }

  render() {

    const { showModal } = this.state;
    const { entityType, loading, data } = this.props;


    let inputPlaceholder = this.getPlaceholderForEntityType(entityType);

    return (
      <Segment loading={loading} inverted>
        <Divider horizontal inverted section>
          <h2>{entityType}{entityType === EntityType.INDEX? 'es' : 's'}</h2>
        </Divider>
        {data.length === 0 && !loading ? 
          <Header icon textAlign='center' as='h3' inverted>Currently listening to no {entityType}{entityType === EntityType.INDEX? 'es' : 's'}..</Header>
        : 
        <div>
          <Grid stackable columns={4}>
          {data.map((item, index) =>
            <Grid.Column key={index}>
              <TickerCard key={index} ticker={item} removeEntity={this.removeEntity}/>
            </Grid.Column>
          )}
          </Grid>
          <br/>
        </div>
        } 
        {/* Add entity popup */}
        {/* {!loading && 
        <div>
          <Button onClick={this.showModal} color='grey' inverted>Subscribe to {entityType}</Button>
          <Modal open={showModal} centered dimmer='blurring' size='mini'>
            <Modal.Header>Add {entityType}</Modal.Header>
            <Modal.Content>
              <Form>
                <Form.Input label={entityType} onChange={this.handleMessage.bind(this)} placeholder={inputPlaceholder} />
                <Button color='yellow' onClick={this.subscribe}>Subscribe</Button>
                <Button color='black' onClick={this.closeModal}>Cancel</Button>
              </Form>
            </Modal.Content>
          </Modal>
        </div>
        } */}
      </Segment>
    );
  }
}

export default CardSection;