create table fields(
	id INTEGER primary key autoincrement ,
	nom CHAR(30) NOT NULL,
	type CHAR(30) NOT NULL,
	date_debut DATE,
	coordonnees INTEGER,
	filiere CHAR(30),
	site CHAR(30),
	data_immutable CHAR,
	data_mutable CHAR,
	status CHAR,
	log CHAR
);



create table log(

	nom CHAR(30) NOT NULL,
	date CHAR(30),
	logg CHAR
);



