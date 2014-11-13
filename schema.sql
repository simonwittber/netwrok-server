--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
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


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: analytics; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE analytics (
    id integer NOT NULL,
    member_id integer,
    path text,
    event text,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.analytics OWNER TO simon;

--
-- Name: analytics_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE analytics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analytics_id_seq OWNER TO simon;

--
-- Name: analytics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE analytics_id_seq OWNED BY analytics.id;


--
-- Name: clan; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE clan (
    id integer NOT NULL,
    name character varying(256) NOT NULL,
    type character varying(32),
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.clan OWNER TO simon;

--
-- Name: clan_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE clan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clan_id_seq OWNER TO simon;

--
-- Name: clan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE clan_id_seq OWNED BY clan.id;


--
-- Name: clan_member; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE clan_member (
    id integer NOT NULL,
    clan_id integer,
    member_id integer,
    type character varying(32),
    created timestamp without time zone DEFAULT now(),
    admin boolean DEFAULT false
);


ALTER TABLE public.clan_member OWNER TO simon;

--
-- Name: clan_member_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE clan_member_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clan_member_id_seq OWNER TO simon;

--
-- Name: clan_member_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE clan_member_id_seq OWNED BY clan_member.id;


--
-- Name: clan_object; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE clan_object (
    id integer NOT NULL,
    clan_id integer NOT NULL,
    member_id integer NOT NULL,
    key text,
    value text,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.clan_object OWNER TO simon;

--
-- Name: clan_object_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE clan_object_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clan_object_id_seq OWNER TO simon;

--
-- Name: clan_object_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE clan_object_id_seq OWNED BY clan_object.id;


--
-- Name: contact; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE contact (
    id integer NOT NULL,
    owner_id integer NOT NULL,
    member_id integer NOT NULL,
    type character varying(16),
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.contact OWNER TO simon;

--
-- Name: contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE contacts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contacts_id_seq OWNER TO simon;

--
-- Name: contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE contacts_id_seq OWNED BY contact.id;


--
-- Name: inbox; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE inbox (
    id integer NOT NULL,
    member_id integer NOT NULL,
    from_member_id integer,
    type character varying(32),
    body text,
    read boolean DEFAULT false,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.inbox OWNER TO simon;

--
-- Name: inbox_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE inbox_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inbox_id_seq OWNER TO simon;

--
-- Name: inbox_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE inbox_id_seq OWNED BY inbox.id;


--
-- Name: mailqueue; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE mailqueue (
    id integer NOT NULL,
    member_id integer,
    address character varying(256),
    subject character varying(256),
    body text,
    sent boolean DEFAULT false,
    created timestamp without time zone DEFAULT now(),
    error boolean DEFAULT false
);


ALTER TABLE public.mailqueue OWNER TO simon;

--
-- Name: mailqueue_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE mailqueue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mailqueue_id_seq OWNER TO simon;

--
-- Name: mailqueue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE mailqueue_id_seq OWNED BY mailqueue.id;


--
-- Name: member; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE member (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(256) NOT NULL,
    created timestamp without time zone DEFAULT now(),
    handle character varying(255) NOT NULL
);


ALTER TABLE public.member OWNER TO simon;

--
-- Name: member_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE member_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.member_id_seq OWNER TO simon;

--
-- Name: member_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE member_id_seq OWNED BY member.id;


--
-- Name: object; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE object (
    id integer NOT NULL,
    member_id integer NOT NULL,
    key character varying(255) NOT NULL,
    value text,
    created timestamp without time zone DEFAULT now()
);


ALTER TABLE public.object OWNER TO simon;

--
-- Name: objects_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE objects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.objects_id_seq OWNER TO simon;

--
-- Name: objects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE objects_id_seq OWNED BY object.id;


--
-- Name: password_reset_request; Type: TABLE; Schema: public; Owner: simon; Tablespace: 
--

CREATE TABLE password_reset_request (
    id integer NOT NULL,
    member_id integer NOT NULL,
    token character varying(8),
    expires timestamp without time zone DEFAULT (now() + '24:00:00'::interval)
);


ALTER TABLE public.password_reset_request OWNER TO simon;

--
-- Name: password_reset_request_id_seq; Type: SEQUENCE; Schema: public; Owner: simon
--

CREATE SEQUENCE password_reset_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.password_reset_request_id_seq OWNER TO simon;

--
-- Name: password_reset_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: simon
--

ALTER SEQUENCE password_reset_request_id_seq OWNED BY password_reset_request.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY analytics ALTER COLUMN id SET DEFAULT nextval('analytics_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY clan ALTER COLUMN id SET DEFAULT nextval('clan_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY clan_member ALTER COLUMN id SET DEFAULT nextval('clan_member_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY clan_object ALTER COLUMN id SET DEFAULT nextval('clan_object_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY contact ALTER COLUMN id SET DEFAULT nextval('contacts_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY inbox ALTER COLUMN id SET DEFAULT nextval('inbox_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY mailqueue ALTER COLUMN id SET DEFAULT nextval('mailqueue_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY member ALTER COLUMN id SET DEFAULT nextval('member_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY object ALTER COLUMN id SET DEFAULT nextval('objects_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: simon
--

ALTER TABLE ONLY password_reset_request ALTER COLUMN id SET DEFAULT nextval('password_reset_request_id_seq'::regclass);


--
-- Data for Name: analytics; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY analytics (id, member_id, path, event, created) FROM stdin;
\.


--
-- Name: analytics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('analytics_id_seq', 1, false);


--
-- Data for Name: clan; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY clan (id, name, type, created) FROM stdin;
1	Devs	Dev	2014-11-12 14:16:20.58286
2	Hoomans	A	2014-11-12 22:13:56.569888
\.


--
-- Name: clan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('clan_id_seq', 4, true);


--
-- Data for Name: clan_member; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY clan_member (id, clan_id, member_id, type, created, admin) FROM stdin;
1	1	49	Founder	2014-11-12 14:17:49.719147	t
5	1	53	Member	2014-11-12 22:38:34.783727	t
\.


--
-- Name: clan_member_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('clan_member_id_seq', 5, true);


--
-- Data for Name: clan_object; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY clan_object (id, clan_id, member_id, key, value, created) FROM stdin;
\.


--
-- Name: clan_object_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('clan_object_id_seq', 1, false);


--
-- Data for Name: contact; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY contact (id, owner_id, member_id, type, created) FROM stdin;
\.


--
-- Name: contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('contacts_id_seq', 1, false);


--
-- Data for Name: inbox; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY inbox (id, member_id, from_member_id, type, body, read, created) FROM stdin;
\.


--
-- Name: inbox_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('inbox_id_seq', 1, false);


--
-- Data for Name: mailqueue; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY mailqueue (id, member_id, address, subject, body, sent, created, error) FROM stdin;
51	53	boris@wittber.com	Welcome.	Thanks for registering.	t	2014-11-12 22:33:35.066194	f
\.


--
-- Name: mailqueue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('mailqueue_id_seq', 51, true);


--
-- Data for Name: member; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY member (id, email, password, created, handle) FROM stdin;
49	simon@wittber.com	aa6535359b2872a70e182018a829e0da7a99e0def6ce7d1f0225f0ad1829a9cf	2014-11-10 15:32:09.443081	DoctorConrad
53	boris@wittber.com	0df89317e02535902d116be0f27294a75145339bf4af53fb35131aea8071a0e1	2014-11-12 22:33:34.987099	boris
\.


--
-- Name: member_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('member_id_seq', 62, true);


--
-- Data for Name: object; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY object (id, member_id, key, value, created) FROM stdin;
1	49	name	"Simon Wittber"	2014-11-11 23:41:07.316583
\.


--
-- Name: objects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('objects_id_seq', 1, true);


--
-- Data for Name: password_reset_request; Type: TABLE DATA; Schema: public; Owner: simon
--

COPY password_reset_request (id, member_id, token, expires) FROM stdin;
36	49	1ae31905	2014-11-11 15:32:09.477824
37	49	868bbba9	2014-11-12 22:01:47.278911
38	49	6c1089a0	2014-11-12 22:08:13.731147
39	49	74a8fe8d	2014-11-12 22:08:34.348673
\.


--
-- Name: password_reset_request_id_seq; Type: SEQUENCE SET; Schema: public; Owner: simon
--

SELECT pg_catalog.setval('password_reset_request_id_seq', 39, true);


--
-- Name: analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY analytics
    ADD CONSTRAINT analytics_pkey PRIMARY KEY (id);


--
-- Name: clan_member_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY clan_member
    ADD CONSTRAINT clan_member_pkey PRIMARY KEY (id);


--
-- Name: clan_object_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY clan_object
    ADD CONSTRAINT clan_object_pkey PRIMARY KEY (id);


--
-- Name: clan_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY clan
    ADD CONSTRAINT clan_pkey PRIMARY KEY (id);


--
-- Name: contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY contact
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);


--
-- Name: inbox_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY inbox
    ADD CONSTRAINT inbox_pkey PRIMARY KEY (id);


--
-- Name: mailqueue_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY mailqueue
    ADD CONSTRAINT mailqueue_pkey PRIMARY KEY (id);


--
-- Name: member_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY member
    ADD CONSTRAINT member_pkey PRIMARY KEY (id);


--
-- Name: objects_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY object
    ADD CONSTRAINT objects_pkey PRIMARY KEY (id);


--
-- Name: password_reset_request_pkey; Type: CONSTRAINT; Schema: public; Owner: simon; Tablespace: 
--

ALTER TABLE ONLY password_reset_request
    ADD CONSTRAINT password_reset_request_pkey PRIMARY KEY (id);


--
-- Name: clan_lower_idx; Type: INDEX; Schema: public; Owner: simon; Tablespace: 
--

CREATE UNIQUE INDEX clan_lower_idx ON clan USING btree (lower((name)::text));


--
-- Name: clan_member_member_id_idx; Type: INDEX; Schema: public; Owner: simon; Tablespace: 
--

CREATE UNIQUE INDEX clan_member_member_id_idx ON clan_member USING btree (member_id);


--
-- Name: member_email_key; Type: INDEX; Schema: public; Owner: simon; Tablespace: 
--

CREATE UNIQUE INDEX member_email_key ON member USING btree (lower((email)::text));


--
-- Name: member_handle_key; Type: INDEX; Schema: public; Owner: simon; Tablespace: 
--

CREATE UNIQUE INDEX member_handle_key ON member USING btree (lower((handle)::text));


--
-- Name: analytics_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY analytics
    ADD CONSTRAINT analytics_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: clan_member_clan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY clan_member
    ADD CONSTRAINT clan_member_clan_id_fkey FOREIGN KEY (clan_id) REFERENCES clan(id);


--
-- Name: clan_member_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY clan_member
    ADD CONSTRAINT clan_member_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: clan_object_clan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY clan_object
    ADD CONSTRAINT clan_object_clan_id_fkey FOREIGN KEY (clan_id) REFERENCES clan(id);


--
-- Name: clan_object_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY clan_object
    ADD CONSTRAINT clan_object_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: contacts_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY contact
    ADD CONSTRAINT contacts_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: contacts_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY contact
    ADD CONSTRAINT contacts_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES member(id);


--
-- Name: inbox_from_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY inbox
    ADD CONSTRAINT inbox_from_member_id_fkey FOREIGN KEY (from_member_id) REFERENCES member(id);


--
-- Name: inbox_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY inbox
    ADD CONSTRAINT inbox_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: mailqueue_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY mailqueue
    ADD CONSTRAINT mailqueue_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: objects_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY object
    ADD CONSTRAINT objects_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: password_reset_request_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: simon
--

ALTER TABLE ONLY password_reset_request
    ADD CONSTRAINT password_reset_request_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

