import React from 'react';
import { 
  Card,
  Image,
  Progress,
} from 'semantic-ui-react'

class TickerCard extends React.Component {

  removeEntity = () => this.props.removeEntity(this.props.ticker.key);

  render() {
    
    const { ticker } = this.props;

    let percent = ticker.Average_Sentiment_Score? 
      (ticker.Average_Sentiment_Score > 0? ticker.Average_Sentiment_Score * 100 : ticker.Average_Sentiment_Score * 100 * -1) 
        : 100;

    let color = ticker.Average_Sentiment_Score? 
      (ticker.Average_Sentiment_Score > 0? 'green' : 'red')
        : 'grey';

    return (
      <Card>
        <Card.Content textAlign='center'>
          <Image src={ticker.logo} circular size='tiny' spaced/>
          <Card.Header style={{marginTop: 7}}>{ticker.key?  ticker.key : "Loading.."}</Card.Header>
          <Card.Meta>@{ticker.id}</Card.Meta>
          <Card.Description>${ticker.price}</Card.Description>
          <h4 style={{marginTop: 15, color: 'black'}} as='h4'>Overall Sentiment:</h4>
          <Progress
            style={{ marginTop: 10 }}
            percent={percent} 
            color={color} 
            size='tiny' 
            active
            label={ticker.Average_Sentiment_Score}
          >
          </Progress>
          <Card.Content header="Test"> </Card.Content>
          <h5 style={{marginTop: 12, color: 'black'}} as='h4'>Latest Tweet ({ticker.Most_Recent_Tweet.Sentiment_Score}):</h5>
          <Card.Description>{ticker.Most_Recent_Tweet.Tweet}</Card.Description>
          <h5 style={{marginTop: 12, color: 'black'}} as='h4'>Most Positive ({ticker.Most_Positive_Tweet.Sentiment_Score}):</h5>
          <Card.Description>{ticker.Most_Positive_Tweet.Tweet}</Card.Description>
          <h5 style={{marginTop: 12, color: 'black'}} as='h4'>Most Negative ({ticker.Most_Negative_Tweet.Sentiment_Score}):</h5>
          <Card.Description>{ticker.Most_Negative_Tweet.Tweet}</Card.Description>
          <br/>
          <Card.Meta>Updated - {ticker.last_updated}</Card.Meta>
        </Card.Content>
      </Card>
    );
  }
}

export default TickerCard;