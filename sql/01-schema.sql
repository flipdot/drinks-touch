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

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


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
-- Name: ldapUsers; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE public."ldapUsers" (
    id integer NOT NULL,
    "ldapId" character varying(20),
    name character varying(50),
    path character varying(50),
    id_card character varying(50),
    is_card boolean
);


ALTER TABLE public."ldapUsers" OWNER TO postgres;

--
-- Name: ldapUsers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."ldapUsers_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."ldapUsers_id_seq" OWNER TO postgres;

--
-- Name: ldapUsers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."ldapUsers_id_seq" OWNED BY public."ldapUsers".id;


--
-- Name: rechargeevent; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE public.rechargeevent (
    id integer NOT NULL,
    user_id character varying(20),
    helper_user_id character varying(20),
    amount numeric,
    "timestamp" timestamp without time zone
);


ALTER TABLE public.rechargeevent OWNER TO postgres;

--
-- Name: rechargeevent_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rechargeevent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rechargeevent_id_seq OWNER TO postgres;

--
-- Name: rechargeevent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rechargeevent_id_seq OWNED BY public.rechargeevent.id;


--
-- Name: scanevent; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE public.scanevent (
    id integer NOT NULL,
    barcode character varying(20),
    user_id character varying(20),
    "timestamp" timestamp without time zone,
    uploaded_to_influx boolean DEFAULT false NOT NULL
);


ALTER TABLE public.scanevent OWNER TO postgres;

--
-- Name: scanevent_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.scanevent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.scanevent_id_seq OWNER TO postgres;

--
-- Name: scanevent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.scanevent_id_seq OWNED BY public.scanevent.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.drink ALTER COLUMN id SET DEFAULT nextval('public.drink_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ldapUsers" ALTER COLUMN id SET DEFAULT nextval('public."ldapUsers_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rechargeevent ALTER COLUMN id SET DEFAULT nextval('public.rechargeevent_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scanevent ALTER COLUMN id SET DEFAULT nextval('public.scanevent_id_seq'::regclass);


--
-- Name: ldapUsers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY public."ldapUsers"
    ADD CONSTRAINT "ldapUsers_pkey" PRIMARY KEY (id);


--
-- Name: rechargeevent_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY public.rechargeevent
    ADD CONSTRAINT rechargeevent_pkey PRIMARY KEY (id);


--
-- Name: scanevent_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY public.scanevent
    ADD CONSTRAINT scanevent_pkey PRIMARY KEY (id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

