const dotenv = require('dotenv');
const express = require('express');
const app = express();

const PORT = 4100;
dotenv.config();

app.set('view engine', 'ejs');
app.use(express.static(__dirname + '/public'));
app.use(express.json());

let ebolas = [
	{
		name: 'Wence',
		status: 'online',
		port: 4101,
		host: '192.168.1.153',
	},
	{
		name: 'ItsArctic',
		status: 'offline',
		port: 4101,
		host: '145.40.191.247',
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
	const ebola = ebolas.find(ebola => ebola.name.toLowerCase().split(' ').join('-') === req.url.split('control/')[1].toLowerCase());

	ebola.status = data.status;
});

app.listen(PORT, () => {
	console.log(`web app listening on port ${PORT}`);
});
