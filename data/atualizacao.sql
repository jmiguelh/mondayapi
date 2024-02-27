PRAGMA foreign_keys = 0;

CREATE TABLE sqlitestudio_temp_table AS SELECT *
                                          FROM projeto;

DROP TABLE projeto;

CREATE TABLE projeto (
    id          VARCHAR (15)  NOT NULL
                              PRIMARY KEY,
    projeto     VARCHAR (250) NOT NULL,
    resposaveis VARCHAR (255) NOT NULL,
    status      VARCHAR (50)  NOT NULL,
    data        DATETIME,
    evolucao    INTEGER,
    link        VARCHAR (255) NOT NULL,
    pcr         VARCAHR (3)   NOT NULL,
    setor       VARCHAR (20)  NOT NULL,
    atualizacao DATETIME
);

INSERT INTO projeto (
                        id,
                        projeto,
                        resposaveis,
                        status,
                        data,
                        evolucao,
                        link,
                        pcr,
                        setor
                    )
                    SELECT id,
                           projeto,
                           resposaveis,
                           status,
                           data,
                           evolucao,
                           link,
                           pcr,
                           setor
                      FROM sqlitestudio_temp_table;

DROP TABLE sqlitestudio_temp_table;

PRAGMA foreign_keys = 1;
