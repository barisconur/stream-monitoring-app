const express = require('express')
const app = express()
app.use(express.json()) 

const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');
const url = "mongodb+srv://admin:ascendant@cluster0-62hqm.mongodb.net/test?retryWrites=true&w=majority";
const dbName = 'VideoProxyDB';

getAllStreams = (req, res) => {
  MongoClient.connect(url, function(err, client) {
    assert.equal(null, err);
    const db = client.db(dbName);
    const cursor = db.collection('Streams').find();
    cursor.toArray(function(err, streams) {
      res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000');
      res.status(200).json({'streams' : streams});
    })
    client.close();
  });
}

getAllChunksOfAStream = (req, res) => {
  MongoClient.connect(url, function(err, client) {
    assert.equal(null, err);
    const db = client.db(dbName);
    const col = db.collection('Video Chunks');
    const matchedItems = col.find( {"id": req.params.id});
    matchedItems.toArray(function(err, chunks) {
      res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000');
      res.status(200).json({'chunks' : chunks});
    })
    client.close();
  });
}

app.get('/', getAllStreams)
app.get('/:id/chunks', getAllChunksOfAStream)

const port = 5000
app.listen(port, () => {
  console.log('App running on port ${port}...')
})