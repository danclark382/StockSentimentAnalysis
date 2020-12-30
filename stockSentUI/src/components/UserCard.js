import React from 'react';
import { 
  Card,
  Image,
  Progress,
  Button,
} from 'semantic-ui-react'

class UserCard extends React.Component {

  removeEntity = () => this.props.removeEntity(this.props.user.key);

  render() {
    
    const { user } = this.props;

    let percent = user.sentiment? 
      (user.sentiment > 0? user.sentiment * 100 : user.sentiment * 100 * -1) 
        : 100;

    let color = user.sentiment? 
      (user.sentiment > 0? 'green' : 'red')
        : 'grey';

    return (
      <Card>
        <Card.Content textAlign='center'>
          <Image src={user.profileUrl} circular size='tiny' spaced/>
          <Card.Header style={{marginTop: 7}}>{user.fullname?  user.fullname : "Loading.."}</Card.Header>
          <Card.Meta>@{user.key}</Card.Meta>
          <Progress
            style={{ marginTop: 10 }}
            percent={percent} 
            color={color} 
            size='tiny' 
            active
            label={user.sentiment}
          >
          </Progress>
          <Button size='mini' onClick={this.removeEntity}>
           Remove
          </Button>
        </Card.Content>
      </Card>
    );
  }
}

export default UserCard;