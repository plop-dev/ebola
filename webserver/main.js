const dotenv = require('dotenv');
const express = require('express');
const app = express();

const PORT = 4100;
const SOCKET_PORT = 4101;
dotenv.config();

app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));

app.get('/', (req, res) => {
	res.render('index');
});

app.listen(PORT, () => {
	console.log(`web app listening on port ${PORT}`);
});
