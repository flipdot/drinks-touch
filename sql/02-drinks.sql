--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: drink; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE public.drink (
    id integer NOT NULL,
    ean character varying(20),
    name character varying(40),
    size numeric,
    "timestamp" timestamp without time zone,
    type character varying(50)
);


ALTER TABLE public.drink OWNER TO postgres;

--
-- Name: drink_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.drink_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.drink_id_seq OWNER TO postgres;

--
-- Name: drink_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.drink_id_seq OWNED BY public.drink.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.drink ALTER COLUMN id SET DEFAULT nextval('public.drink_id_seq'::regclass);


--
-- Data for Name: drink; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.drink (id, ean, name, size, "timestamp", type) FROM stdin;
20	4260107220015	fritz-kola (0.33)	0.33	2016-12-07 00:10:24.818539	cola
31	4260107222262	fritz-kola (0.5)	0.5	2017-03-28 20:59:01.326216	cola
33	4014964111555	Köstritzer	0.5	\N	bier
34	4009401560300	Caldener Medium	0.5	\N	wasser
35	/02524813	Zwanzig Zilberlinge	0.5	\N	wasser
36	4003892013512	Jacobinus Bierspezialität	0.5	2017-08-08 23:27:41.935014	bier
37	4306376050370	Waldecker Sport	0.7	2018-05-22 20:12:11.488533	saft
38	4306376870046	Waldecker Sport	1.0	2018-06-05 17:40:55.113301	saft
39	4104640020124	Apfelschorle	0.75	2018-06-05 17:41:28.21306	saft
15	4008948194016	Jever Fun Alkoholfrei	0.5	2016-12-07 00:06:25.114132	saft
40	619659137915	Zehntel SD-Karte	0.1	\N	hardware
2	4029764001807	Club-Mate	0.5	2016-08-28 20:24:59.423597	mate
3	41001318	BECKS	0.5	2016-08-28 20:25:00.24342	bier
4	4069800005871	Nörten-Hardenberger	0.33	2016-08-28 20:25:01.098931	bier
6	4008948027000	JEVER	0.5	2016-08-28 20:25:02.824964	bier
7	4002846034504	MIO-MIO-MATE	0.5	2016-08-28 20:25:03.657011	mate
8	4260031874278	flora power	0.33	2016-08-28 20:25:04.497183	mate
10	4002846034306	Mio Mio Cola	0.5	2016-08-28 20:40:07.374024	cola
13	4029764001401	Club-Mate Granat	0.5	2016-12-06 23:03:48.08653	mate
14	87126853	Coca-Cola	0.33	2016-12-06 23:05:41.377041	cola
16	4008287072129	Krombacher Radler	0.5	2016-12-07 00:07:02.883156	bier
17	4009401560409	Caldener Sanft	1.0	2016-12-07 00:07:57.957231	wasser
18	4311596435968	Edeka Mineralwasser	1.5	2016-12-07 00:08:45.349772	wasser
21	4002631015916	Mixery	0.33	2016-12-07 00:11:06.792486	bier
22	4002631016715	Mixery Guarana	0.33	2016-12-07 00:11:46.172754	bier
23	4029764001883	Club-Mate Cola	0.33	2016-12-07 00:12:52.132212	cola
24	4004078005345	Einbecker Winter-Bock	0.33	2016-12-07 00:13:41.358712	bier
25	4104640040528	Fortuna Apfelschorle	0.5	2016-12-07 00:14:27.423869	saft
26	4008287072228	Krombacher Radler	0.33	2017-03-09 23:39:37.464	bier
9	4003892009218	Esch-weger	0.33	2016-08-28 20:25:05.32553	bier
27	54490123	Coca-Cola	0.5	2017-03-09 23:41:31.899	cola
5	4003892009010	Esch-weger	0.5	2016-08-28 20:25:01.973955	bier
28	4311501480953	2 Müsliregel G&G	0.025	2017-03-26 12:35:56.172424	snack
29	41001301	BECKS klein	0.33	2017-03-26 12:54:13.004207	bier
32	4002846034603	MIO MIO Ginger	0.5	2017-06-06 21:10:19.258224	mate
19	4002846034559	Mio-Mio Banana	0.5	2016-12-07 00:09:34.989512	mate
\.


--
-- Name: drink_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.drink_id_seq', 40, true);


--
-- PostgreSQL database dump complete
--

