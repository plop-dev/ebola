const dotenv = require('dotenv');
const express = require('express');
const app = express();
const { Server } = require('socket.io');

const PORT = 4100;
const SOCKET_PORT = 4101;
dotenv.config();

const io = new Server(SOCKET_PORT);

app.get('/', (req, res) => {
	res.send('hi');
});

io.on('connection', socket => {
	console.log('new connection');

	socket.on('screen-data', data => {
		// res.send(`<h1>${data}</h1>`);
		console.log(data);
	});
});

app.listen(PORT, () => {
	console.log(`web app listening on port ${PORT}`);
});
