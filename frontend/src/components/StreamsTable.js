import React from 'react'; 
import '../app.scss'
import { Redirect } from 'react-router-dom'

export default class StreamsTable extends React.Component {
  
  state = {
    selectedRow: null
  }

  render() {
    return (
      <>
      
        <table className="table table-bordered">
          <thead className="thead-dark">
            <tr>
              <th scope="col">Port</th>
              <th scope="col">First Request</th>
              <th scope="col">Last Request</th>
              <th scope="col">Platform</th>
              <th scope="col">Stream Length(H:M:S)</th>
              <th scope="col">Live</th>
              <th scope="col">Parent Title</th>
              <th scope="col">Stream Title</th>
              <th scope="col">Url</th>
              <th scope="col">Forward Link</th>
              <th scope="col">Average Bandwidth(Mbps)</th>
              <th scope="col">Average Bitrate(Mbps)</th>
              <th scope="col">Video Chunk Count</th>
              <th scope="col">Audio Chunk Count</th>
              <th scope="col">Video Resolutions</th>
              <th scope="col">Audio Resolutions</th>
              <th scope="col">Download Size(MB)</th>
            </tr>
          </thead>
           <tbody> {this.displayEachStream(this.props.streams) } </tbody>
        </table>

        { this.redirectToChunksPage(this.state.selectedRow) }
      </>
    );
  }

  displayEachStream = (streams) => {  
    if (this.props.streams.length === 0) {
      return
    }

    return streams.map((stream, key) => {
      if (stream.platform === 'Udemy') {
        let video_res = this.calculateDiffRes(stream.platform, stream.video_resolutions)
        return <tr key={key} onClick= {() => this.updateRow(stream)}>
                <td>Port number(NOT DONE)</td>
                <td>{stream.first_request_time}</td>
                <td>{stream.last_request_time}</td>
                <td>{stream.platform}</td>
                <td>{this.convertSecondsToProperFormat(stream.video_length)}</td>
                <td>{String(stream.is_live)}</td>
                <td>{stream.course_title}</td>
                <td>{stream.lecture_title}</td>
                <td>{stream.course_url}</td>
                <td>{stream.forward_link}</td>
                <td>{stream.average_bandwidth.toFixed(2)}</td>
                <td>-</td>
                <td>{stream.video_chunk_count}</td>
                <td>-</td>
                <td> {video_res.toString()} </td>
                <td>-</td>
                <td>{stream.download_size.toFixed(2)}</td>
              </tr>
      } else if (stream.platform === 'YouTube') {
        let video_res = this.calculateDiffRes(stream.platform, stream.video_resolutions)
        let audio_res = this.calculateAudioDiffRes(stream.audio_resolutions)

        return <tr key={key} onClick= {() => this.updateRow(stream)}>
                <td>Port number(NOT DONE)</td>
                <td>{stream.first_request_time}</td>
                <td>{stream.last_request_time}</td>
                <td>{stream.platform}</td>
                <td>{this.convertSecondsToProperFormat(stream.video_length)}</td>
                <td>{String(stream.is_live)}</td>
                <td>-</td>
                <td>{stream.video_title}</td>
                <td>{stream.video_url}</td>
                <td>{stream.forward_link}</td>
  
                <td>-</td>
                <td>{stream.average_video_bitrate.toFixed(2)}</td>
                <td>{stream.video_chunk_count}</td>
                <td>{stream.audio_chunk_count}</td>
                <td> {video_res.toString()} </td>
                <td> {audio_res.toString()} </td>
                <td>{stream.download_size.toFixed(2)}</td>
              </tr>
      }
    })
  }

  updateRow = (stream) => {
    let unique_id = stream['id']
    this.setState({
      selectedRow: unique_id,
      
    })
  }

  convertSecondsToProperFormat = (stream_length) => {
    if (stream_length === -1) {
      return "-"
    }
    let str = ""
    let hours = Math.floor(stream_length / 3600);
    stream_length %= 3600;
    let minutes = Math.floor(stream_length / 60);
    let seconds = stream_length % 60;

    if (hours !== 0) {
      if (hours < 10) {
        str = str + "0" + hours.toString() + ":"
      } else {
        str = str + hours.toString() + ":"
      }
    } else {
      str = str + "00:"
    }
    
    if (minutes !== 0) {
      if (minutes < 10) {
        str = str + "0" + minutes.toString() + ":"
      } else {
        str = str + minutes.toString() + ":"
      }
    } else {
      str = str + "00:"
    }

    if (seconds !== 0) {
      if (seconds < 10) {
        str = str + "0" + seconds.toString()
      } else {
        str = str + seconds.toString()
      }
    } else {
      str = str + "00"
    }

    return str
  }

  calculateDiffRes = (platform, resolutions) => {
    if (platform === "Udemy") {
      const parsedRes = this.parseResolutions(resolutions)
      resolutions = parsedRes
    }

    let uniqueRes = []
    
    resolutions.forEach((res) => {
      if (uniqueRes.includes(res)) {
        return
      }
      uniqueRes.push(res)
    })

    return uniqueRes
  }

  parseResolutions = (resolutions) => {
    let parsedElements = []
    resolutions.forEach((res) => {
      let arrStr = res.split(/[_]/)
      if (arrStr[0] === 'hls') {
         parsedElements.push(arrStr[1].concat("p"))
      } else {
        let widthAndHeight = arrStr[1]
        let sp = widthAndHeight.split(/[x]/)
        
        parsedElements.push(sp[1].concat("p"))
      }
    })

    return parsedElements
  }

  calculateAudioDiffRes = (resolutions) => {
    let uniqueRes = []
    resolutions.forEach((res) => {
      if (uniqueRes.includes(res)) {
        return
      }
      uniqueRes.push(res)
    })

    return uniqueRes
  }

  redirectToChunksPage = (id) => {
    if (this.state.selectedRow === null) {
      return 
    } 
    return <Redirect to={id + "/chunks"} />
  }
}