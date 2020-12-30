import React from 'react';
import { 
  Card,
  Button,
} from 'semantic-ui-react'

class AddCard extends React.Component {

  constructor(props) {
    super(props);
    this.state = { 
      showAddPopup: false
    }
  }
  openAddUserPopup = () => {
    this.setState({ showAddPopup: true});
  }

  render() {
    const { entity } = this.props;

    return (
      <Card>
        <Card.Content textAlign='center'>
          <Button color='blue' onClick={this.openAddUserPopup}>Add {entity}</Button>
        </Card.Content>
      </Card>
    );
  }
}

export default AddCard;