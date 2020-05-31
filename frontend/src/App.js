import React from 'react'; 
import './app.scss';
import StreamsTable from './components/StreamsTable'
import Pagination from './components/Pagination'
import { Button, Nav, Spinner } from 'react-bootstrap';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { streams: [],
                    currentPage: 1,
                    currentStreams: null,
                    streamsPerPage: 10
                  }
  }

  componentDidMount() {
    this.callStreamsAPI()
  }

  callStreamsAPI() {
    fetch("http://localhost:5000/")
        .then(res =>  res.json())
        .then(res => this.setState({streams: res.streams}))
        .then(() => {
          this.setCurrentStreams();
        })
        .catch(err => err);

  }

  setCurrentStreams() {
    const indexOfLastStream = this.state.currentPage * this.state.streamsPerPage;
    const indexOfFirstStream = indexOfLastStream - this.state.streamsPerPage;
    const currentStreams = this.state.streams.slice(indexOfFirstStream, indexOfLastStream);

    this.setState({
      currentStreams: currentStreams
    });
  }

  refreshPage() {
    window.location.reload(false);
  }

  render() {
    return (
      <div className="App">
        <div className="header">

          <div className="header-title">
            Monitoring APP
          </div>

          <div className="header-description">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum         
          </div>

          <div className="links">
            <Nav defaultActiveKey="/home" as="ul">
              <Nav.Item as="li">
                <Nav.Link href="/statistics">Show Statistics</Nav.Link>
              </Nav.Item>
            </Nav>
          </div>
        </div>
        
        <div className="stream-table">
          {this.renderStreamTable() }
        </div>
      </div>
    );
  }

  renderStreamTable = () => {
    if (this.state.currentStreams === null) {
      return <div className ="loading-panel"> 
            <Spinner animation="border" variant="primary" role="status" style={{width: "5rem", height: "5rem"}}>
              <span className="sr-only">Loading...</span>
            </Spinner>
            </div>
    } else {
      return <>
             <div className = "buttons-panel">
               <Button variant="dark" size="md" className="refresh-btn" onClick= {this.refreshPage}>Refresh</Button>
            </div>
            <StreamsTable streams={this.state.currentStreams}/>
            <div className="pagination">
              <Pagination streamsPerPage={this.state.streamsPerPage} totalStreams={this.state.streams.length}
              paginate={this.paginate} currentPage={this.state.currentPage}/>
            </div>
            </>
    }
  }

  paginate = (pageNumber) => {
    this.setState({
      currentPage: pageNumber
    }, () => {
      this.setCurrentStreams();
    })
  }

}