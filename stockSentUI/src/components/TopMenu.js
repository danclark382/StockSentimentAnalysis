import React from 'react';
import { 
  Menu,
  Segment,
} from 'semantic-ui-react';

class TopMenu extends React.Component {

  constructor(props){
    super(props);
    this.state = {
      activeItem: props.activeItem,
    }
  }
  
  handleItemClick = (e, { name }) => {
    this.setState({ activeItem: name })
  }

  render() {
    const { activeItem } = this.state;

    return (
      <Segment inverted>
          <Menu inverted secondary>
            {/* <Menu.Item
              name='users'
              active={activeItem === 'users'}
              onClick={this.handleItemClick}
            /> */}
            {/* <Menu.Item
              name='tickers'
              active={activeItem === 'tickers'}
              onClick={this.handleItemClick}
            /> */}
            {/* <Menu.Item
              name='etfs'
              active={activeItem === 'etfs'}
              onClick={this.handleItemClick}
            />
            <Menu.Item
              name='indexes'
              active={activeItem === 'indexes'}
              onClick={this.handleItemClick}
            /> */}
            <Menu.Menu position='right'>
              <Menu.Item
                name='about'
                active={activeItem === 'about'}
                onClick={this.handleItemClick}
              />
            </Menu.Menu>
          </Menu>
        </Segment>
    );
  }
}

export default TopMenu;