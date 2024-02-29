CREATE TABLE "projeto" (
  "id" VARCHAR(15) NOT NULL PRIMARY KEY,
  "projeto" VARCHAR(250) NOT NULL,
  "resposaveis" VARCHAR(255) NOT NULL,
  "status" VARCHAR(50) NOT NULL,
  "data" DATE,
  "evolucao" INTEGER,
  "link" VARCHAR(255) NOT NULL,
  "pcr" TEXT NOT NULL
)

CREATE TABLE "comentario" (
  "id" VARCHAR(15) NOT NULL PRIMARY KEY,
  "id_projeto" VARCHAR(15) NOT NULL,
  "autor" VARCHAR(50) NOT NULL,
  "texto" TEXT NOT NULL,
  "atualizacao" DATETIME NOT NULL
);
