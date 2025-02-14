CREATE TABLE public.projeto (
	id varchar(15) NOT NULL,
	projeto varchar(250) NOT NULL,
	resposaveis varchar(255) NOT NULL,
	status varchar(50) NOT NULL,
	"data" timestamp NULL,
	evolucao int4 DEFAULT 0 NULL,
	link varchar(255) NOT NULL,
	pcr text NOT NULL,
	setor varchar(100) NOT NULL,
	atualizacao timestamp NULL,
	CONSTRAINT projeto_pkey PRIMARY KEY (id)
);

CREATE TABLE public.comentario (
	id varchar(15) NOT NULL,
	id_projeto varchar(15) NOT NULL,
	autor varchar(50) NOT NULL,
	texto text NOT NULL,
	atualizacao timestamp NOT NULL,
	CONSTRAINT comentario_pkey PRIMARY KEY (id)
);

CREATE TABLE public.controle (
	id serial4 NOT NULL,
	atualizacao timestamp NULL,
	CONSTRAINT controle_pkey PRIMARY KEY (id)
);