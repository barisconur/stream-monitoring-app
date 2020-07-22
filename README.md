# stream-monitoring-app
It's my senior project displaying watched video content from Youtube and Udemy by the LAN devices by performing arp poisoning attack.

## Attention
Last commit containing bar charts and graphical representations about the total downloads by specific device is missing.

## Project Description
In this project, we analyzed the encrypted network traffic between video streaming platforms which are 
Udemy and Youtube, and clients by using an HTTPS proxy. We enhanced a system handling each request 
to the video platforms by target devices in the local area network. We forwarded network traffic of each 
target device to the admin computer by performing ARP poisoning attack. Then we analyzed all network 
flow of multiple devices by running multiple scripts that are responsible for identifying network packets and 
then send them to the MongoDB database instance. Afterwards, we implemented a web application 
displaying each client’s video history in terms of viewed video title, bandwidth usage during watching the 
video, statistical graphs such as total download amount in this week for each device. The system works like 
a network packet sniffer but we are filtering network packets by looking for urls that are requested by clients 
and only we are capturing, parsing and storing Youtube and Udemy network traffic. 

## Project Report and Demo Links
* Report link: https://drive.google.com/file/d/1OdfXPgMXHGvC7wrvxtnr-mgdxW8Ak8lP/view?usp=sharing
* Demo link: https://drive.google.com/file/d/1oU085Q845DdiLBy-DUj9pVyAEg11vUIP/view?usp=sharing

## Technologies used

### arpspoof

### HTTPS Proxy 
* mitmproxy Python API

### Frontend

* React.js
* Bootstrap
* Sass
* Yarn

### Backend

* Express.js

### Database

* MongoDB Atlas
