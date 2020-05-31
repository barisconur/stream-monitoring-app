
import React from 'react'; 
import '../app.scss'
import { Redirect } from 'react-router-dom'
import Pagination from './Pagination'
import { Button, Spinner } from 'react-bootstrap';

export default class ChunksTable extends React.Component {
  constructor(props) {
    super(props);
    this.state = { chunks: [],
                  isBackHomeClicked: false,
                  currentPage: 1,
                  currentChunks: null,
                  chunksPerPage: 20
                };
  }

  componentDidMount() {
    this.callChunksAPI()
  }

  callChunksAPI() {
    fetch("http://localhost:5000/" + this.props.match.params.id +"/chunks")
        .then(res =>  res.json())
        .then(res => this.setState({chunks: res.chunks}))
        .then(() => {
          this.setCurrentChunks();
        })
        .catch(err => err);
  }

  setCurrentChunks() {
    const indexOfLastStream = this.state.currentPage * this.state.chunksPerPage;
    const indexOfFirstStream = indexOfLastStream - this.state.chunksPerPage;
    const currentChunks = this.state.chunks.slice(indexOfFirstStream, indexOfLastStream);

    this.setState({
      currentChunks: currentChunks
    });
  }

  modifyIsHomeClicked = () => {
    this.setState({
      isBackHomeClicked: true
    })
  }

  refreshPage = () => {
    window.location.reload();
  }

  paginate = (pageNumber) => {
    this.setState({
      currentPage: pageNumber
    }, () => {
      this.setCurrentChunks();
    })
  }
  
  render() {
    return (
      <>
        <div className="chunks-table">
          { this.renderChunksTable() }
        </div>
        { this.redirectToHome() }
      </>
    );
  }

  renderChunksTable = () => {
    if (this.state.chunks.length === 0) {
      return <div className ="loading-panel"> 
            <Spinner animation="border" variant="primary" role="status" style={{width: "5rem", height: "5rem"}}>
              <span className="sr-only">Loading...</span>
            </Spinner>
            </div>
    } else {
      return <>
              <div className="return-home-button">
               <Button variant="dark" size="md" className="return-home-btn" onClick= {this.modifyIsHomeClicked}>Return Home</Button>
              </div>
              <div className="buttons-panel">
               <Button variant="dark" size="md" className="refresh-btn" onClick= {this.refreshPage}>Refresh</Button>
              </div>
            { this.renderTable() }
            <div className="pagination">
            <Pagination streamsPerPage={this.state.chunksPerPage} totalStreams={this.state.chunks.length}
              paginate={this.paginate} currentPage={this.state.currentPage}/>
            </div>
            </>
    }
  }

  renderTable = () => {
    if (this.state.currentChunks === null) {
      return
    } else {
      if (this.state.chunks[0].platform === "Udemy") {
        return this.renderUdemyTable()
      } else if (this.state.chunks[0].platform === "YouTube") {
        return this.renderYouTubeTable()
      }
    }

  }

  renderUdemyTable = () => {
    return <>
            <table className="table table-bordered">
            <thead className="thead-dark">
              <tr>
                <th scope="col">Port</th>
                <th scope="col">Request Time</th>
                <th scope="col">Type</th>
                <th scope="col">Resolution</th>
                <th scope="col">Chunk Size(MB)</th>
                <th scope="col">Chunk Order</th>
                <th scope="col">Chunk Duration(sec)</th>
                <th scope="col">Bandwidth(Mbps)</th>
                <th scope="col">Average Bandwidth(Mbps)</th>
                <th scope="col">Codecs</th>
              </tr>
            </thead>
            <tbody> {this.displayEachUdemyChunk(this.state.currentChunks) } </tbody>
           </table>
         </>
  }

  displayEachUdemyChunk = (chunks) => {
    if (this.state.chunks.length === 0) {
      return
    }

    return chunks.map((chunk, key) => {
      console.log(chunk)
      return <tr key={key}>
                <td>Port</td>
                <td>{chunk.request_time}</td>
                <td>{chunk.type}</td>
                <td>{this.parseRes(chunk.res_signiture)}</td>
                <td>{chunk.content_length.toFixed(2)}</td>
                <td>{chunk.iThChunk}</td>
                <td>{chunk.duration}</td>
                <td>{chunk.bandwidth.toFixed(2)}</td>
                <td>{chunk.average_bandwidth.toFixed(2)}</td>
                <td>{chunk.codecs.toString()}</td>   
             </tr>
          })   
        }
      
  renderYouTubeTable = () => {
    return <>
            <table className="table table-bordered">
              <thead className="thead-dark">
                <tr>
                  <th scope="col">Port</th>
                  <th scope="col">Request Time</th>
                  <th scope="col">Type</th>
                  <th scope="col">Resolution</th>
                  <th scope="col">Chunk Size(MB)</th>
                  <th scope="col">Bitrate(Mbps)</th>
                  <th scope="col">Average Bitrate(Mbps)</th>
                  <th scope="col">Codecs</th>
                  <th scope="col">Receive Buffer</th>
                  <th scope="col">Range</th>
                </tr>
            </thead>
            <tbody> {this.displayEachYoutubeChunk(this.state.currentChunks) } </tbody>
           </table>
         </>
  }

  displayEachYoutubeChunk = (chunks) => {
  if (this.state.chunks.length === 0) {
    return
  }

  return chunks.map((chunk, key) => {
    return <tr key={key}>
              <td>Port</td>
              <td>{chunk.request_time}</td>
              <td>{chunk.type}</td>
              <td>{chunk.resolution}</td>
              <td>{chunk.content_length.toFixed(2)}</td>
              <td>{chunk.bitrate.toFixed(2)}</td>
              {this.renderAverageBitrate(chunk) }
              <td>{chunk.codecs}</td>   
              <td>{chunk.buffer}</td>   
              <td>{chunk.range}</td>   
           </tr>
    })   
  }

  renderAverageBitrate = (chunk) => {
    if (chunk.type.includes('audio')) {
      return <td>-</td>
    }

    return <td>{chunk.average_bitrate.toFixed(2)}</td>

  }

  parseRes = (res) => {
    let out = ""
    let arrStr = res.split(/[_]/)
    if (arrStr[0] === 'hls') {
      out = arrStr[1].concat("p")
    } else {
      let widthAndHeight = arrStr[1]
      out = widthAndHeight.split(/[x]/)[1].concat("p")
    }

    return out
  }

  redirectToHome = () => {
    if (this.state.isBackHomeClicked) {
      return <Redirect to={"/"}/>
    } else {
      return null
    }
  }
}