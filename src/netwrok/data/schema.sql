--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: add_new_currency_to_wallets(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_new_currency_to_wallets() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
insert into wallet(member_id, currency_id, balance)
select id, NEW.id, 0 
from member;
return NEW;
END;$$;


--
-- Name: add_role(integer, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION add_role(integer, text) RETURNS text[]
    LANGUAGE sql
    AS $_$

update member set roles = roles || text($2) where id = $1
returning roles;

$_$;


--
-- Name: create_wallets_for_new_member(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION create_wallets_for_new_member() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
insert into wallet(member_id, currency_id, balance) select NEW.id, id, 0 from currency;
return NEW;
END;$$;


--
-- Name: remove_role(integer, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION remove_role(integer, text) RETURNS text[]
    LANGUAGE sql
    AS $_$

update member set roles = array_remove(roles, text($2)) where id = $1
returning roles;

$_$;


--
-- Name: transfer_currency(integer, integer, integer, double precision); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION transfer_currency(currency_id integer, from_member_id integer, to_member_id integer, amount double precision) RETURNS integer
    LANGUAGE plpgsql
    AS $$DECLARE
tx_id int4;
src_wallet_id int4;
dst_wallet_id int4;

BEGIN
insert into wallet_transaction(created) select now() returning id into tx_id;
select id into src_wallet_id from wallet A where member_id = from_member_id and A.currency_id = transfer_currency.currency_id;
select id into dst_wallet_id from wallet A where member_id = to_member_id and A.currency_id = transfer_currency.currency_id;

insert into journal(wallet_id, tx_id, credit, debit) select src_wallet_id, tx_id, 0, amount;
insert into journal(wallet_id, tx_id, credit, debit) select dst_wallet_id, tx_id, amount, 0;

update wallet set balance = balance + amount where id = dst_wallet_id;
update wallet set balance = balance - amount where id = src_wallet_id;
return tx_id;
END;
$$;


--
-- Name: transfer_currency(integer, integer, integer, double precision, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION transfer_currency(currency_id integer, from_member_id integer, to_member_id integer, amount double precision, narrative text) RETURNS integer
    LANGUAGE plpgsql
    AS $$DECLARE
tx_id int4;
src_wallet_id int4;
dst_wallet_id int4;

BEGIN
insert into wallet_transaction(narrative, created) select narrative, now() returning id into tx_id;
select id into src_wallet_id from wallet A where member_id = from_member_id and A.currency_id = transfer_currency.currency_id;
select id into dst_wallet_id from wallet A where member_id = to_member_id and A.currency_id = transfer_currency.currency_id;

insert into journal(wallet_id, tx_id, credit, debit) select src_wallet_id, tx_id, 0, amount;
insert into journal(wallet_id, tx_id, credit, debit) select dst_wallet_id, tx_id, amount, 0;

update wallet set balance = balance + amount where id = dst_wallet_id;
update wallet set balance = balance - amount where id = src_wallet_id;
return tx_id;
END;
$$;


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: alliance; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE alliance (
    id integer NOT NULL,
    name text NOT NULL,
    type text,
    created timestamp without time zone DEFAULT now()
);


--
-- Name: alliance_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE alliance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: alliance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE alliance_id_seq OWNED BY alliance.id;


--
-- Name: alliance_store; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE alliance_store (
    id integer NOT NULL,
    alliance_id integer NOT NULL,
    key text NOT NULL,
    value text,
    created timestamp without time zone DEFAULT now() NOT NULL,
    row_version integer DEFAULT 0
);


--
-- Name: alliance_store_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE alliance_store_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: alliance_store_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE alliance_store_id_seq OWNED BY alliance_store.id;


--
-- Name: analytics; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE analytics (
    id integer NOT NULL,
    member_id integer,
    path text,
    event text,
    created timestamp without time zone DEFAULT now()
);


--
-- Name: TABLE analytics; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE analytics IS 'No foreign key on this table, as member deletion should not cascade to analytics records.';


--
-- Name: analytics_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE analytics_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: analytics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE analytics_id_seq OWNED BY analytics.id;


--
-- Name: badge; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE badge (
    id integer NOT NULL,
    member_id integer NOT NULL,
    name text NOT NULL,
    description text,
    created timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: badge_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE badge_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: badge_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE badge_id_seq OWNED BY badge.id;


--
-- Name: clan; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE clan (
    id integer NOT NULL,
    name character varying(256) NOT NULL,
    type character varying(32),
    created timestamp without time zone DEFAULT now() NOT NULL,
    alliance_id integer
);


--
-- Name: clan_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE clan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: clan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE clan_id_seq OWNED BY clan.id;


--
-- Name: clan_store; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE clan_store (
    id integer NOT NULL,
    clan_id integer NOT NULL,
    key text NOT NULL,
    value text,
    created timestamp without time zone DEFAULT now() NOT NULL,
    row_version integer DEFAULT 0
);


--
-- Name: clan_store_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE clan_store_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: clan_store_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE clan_store_id_seq OWNED BY clan_store.id;


--
-- Name: contact; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE contact (
    id integer NOT NULL,
    owner_id integer NOT NULL,
    member_id integer NOT NULL,
    type character varying(16),
    created timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE contacts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE contacts_id_seq OWNED BY contact.id;


--
-- Name: currency; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE currency (
    id integer NOT NULL,
    name text NOT NULL
);


--
-- Name: currency_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE currency_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: currency_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE currency_id_seq OWNED BY currency.id;


--
-- Name: inbox; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE inbox (
    id integer NOT NULL,
    member_id integer NOT NULL,
    from_member_id integer,
    type character varying(32),
    body text NOT NULL,
    read boolean DEFAULT false NOT NULL,
    created timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: inbox_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE inbox_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: inbox_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE inbox_id_seq OWNED BY inbox.id;


--
-- Name: journal; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE journal (
    id integer NOT NULL,
    wallet_id integer NOT NULL,
    credit double precision NOT NULL,
    tx_id integer NOT NULL,
    debit double precision NOT NULL
);


--
-- Name: journal_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE journal_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: journal_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE journal_id_seq OWNED BY journal.id;


--
-- Name: mailqueue; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE mailqueue (
    id integer NOT NULL,
    member_id integer,
    address character varying(256) NOT NULL,
    subject character varying(256),
    body text,
    sent boolean DEFAULT false NOT NULL,
    created timestamp without time zone DEFAULT now() NOT NULL,
    error boolean DEFAULT false NOT NULL
);


--
-- Name: mailqueue_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE mailqueue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mailqueue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE mailqueue_id_seq OWNED BY mailqueue.id;


--
-- Name: member; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE member (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(256) NOT NULL,
    created timestamp without time zone DEFAULT now() NOT NULL,
    handle character varying(255) NOT NULL,
    clan_id integer,
    roles text[] DEFAULT '{}'::text[] NOT NULL
);


--
-- Name: member_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE member_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: member_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE member_id_seq OWNED BY member.id;


--
-- Name: member_store; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE member_store (
    id integer NOT NULL,
    member_id integer NOT NULL,
    key text NOT NULL,
    value text,
    created timestamp without time zone DEFAULT now() NOT NULL,
    row_version integer DEFAULT 0
);


--
-- Name: member_store_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE member_store_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: member_store_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE member_store_id_seq OWNED BY member_store.id;


--
-- Name: object; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE object (
    id integer NOT NULL,
    member_id integer NOT NULL,
    key character varying(255) NOT NULL,
    value text,
    created timestamp without time zone DEFAULT now(),
    clan_id integer,
    alliance_id integer
);


--
-- Name: object_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE object_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: object_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE object_id_seq OWNED BY object.id;


--
-- Name: password_reset_request; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE password_reset_request (
    id integer NOT NULL,
    member_id integer NOT NULL,
    token character varying(8) NOT NULL,
    expires timestamp without time zone DEFAULT (now() + '24:00:00'::interval) NOT NULL
);


--
-- Name: password_reset_request_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE password_reset_request_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: password_reset_request_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE password_reset_request_id_seq OWNED BY password_reset_request.id;


--
-- Name: wallet; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE wallet (
    id integer NOT NULL,
    member_id integer,
    currency_id integer NOT NULL,
    balance double precision DEFAULT 0 NOT NULL
);


--
-- Name: wallet_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE wallet_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wallet_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE wallet_id_seq OWNED BY wallet.id;


--
-- Name: wallet_transaction; Type: TABLE; Schema: public; Owner: -; Tablespace: 
--

CREATE TABLE wallet_transaction (
    id integer NOT NULL,
    created timestamp without time zone DEFAULT now(),
    narrative text
);


--
-- Name: wallet_transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE wallet_transaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wallet_transaction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE wallet_transaction_id_seq OWNED BY wallet_transaction.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY alliance ALTER COLUMN id SET DEFAULT nextval('alliance_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY alliance_store ALTER COLUMN id SET DEFAULT nextval('alliance_store_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY analytics ALTER COLUMN id SET DEFAULT nextval('analytics_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY badge ALTER COLUMN id SET DEFAULT nextval('badge_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY clan ALTER COLUMN id SET DEFAULT nextval('clan_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY clan_store ALTER COLUMN id SET DEFAULT nextval('clan_store_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY contact ALTER COLUMN id SET DEFAULT nextval('contacts_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY currency ALTER COLUMN id SET DEFAULT nextval('currency_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY inbox ALTER COLUMN id SET DEFAULT nextval('inbox_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY journal ALTER COLUMN id SET DEFAULT nextval('journal_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY mailqueue ALTER COLUMN id SET DEFAULT nextval('mailqueue_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY member ALTER COLUMN id SET DEFAULT nextval('member_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY member_store ALTER COLUMN id SET DEFAULT nextval('member_store_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY object ALTER COLUMN id SET DEFAULT nextval('object_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY password_reset_request ALTER COLUMN id SET DEFAULT nextval('password_reset_request_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallet ALTER COLUMN id SET DEFAULT nextval('wallet_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallet_transaction ALTER COLUMN id SET DEFAULT nextval('wallet_transaction_id_seq'::regclass);


--
-- Name: alliance_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY alliance
    ADD CONSTRAINT alliance_pkey PRIMARY KEY (id);


--
-- Name: alliance_store_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY alliance_store
    ADD CONSTRAINT alliance_store_pkey PRIMARY KEY (id);


--
-- Name: analytics_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY analytics
    ADD CONSTRAINT analytics_pkey PRIMARY KEY (id);


--
-- Name: badge_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY badge
    ADD CONSTRAINT badge_pkey PRIMARY KEY (id);


--
-- Name: clan_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY clan
    ADD CONSTRAINT clan_pkey PRIMARY KEY (id);


--
-- Name: clan_store_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY clan_store
    ADD CONSTRAINT clan_store_pkey PRIMARY KEY (id);


--
-- Name: contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY contact
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);


--
-- Name: currency_name_key; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY currency
    ADD CONSTRAINT currency_name_key UNIQUE (name);


--
-- Name: currency_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY currency
    ADD CONSTRAINT currency_pkey PRIMARY KEY (id);


--
-- Name: inbox_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY inbox
    ADD CONSTRAINT inbox_pkey PRIMARY KEY (id);


--
-- Name: journal_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY journal
    ADD CONSTRAINT journal_pkey PRIMARY KEY (id);


--
-- Name: mailqueue_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY mailqueue
    ADD CONSTRAINT mailqueue_pkey PRIMARY KEY (id);


--
-- Name: member_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY member
    ADD CONSTRAINT member_pkey PRIMARY KEY (id);


--
-- Name: member_store_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY member_store
    ADD CONSTRAINT member_store_pkey PRIMARY KEY (id);


--
-- Name: objects_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY object
    ADD CONSTRAINT objects_pkey PRIMARY KEY (id);


--
-- Name: password_reset_request_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY password_reset_request
    ADD CONSTRAINT password_reset_request_pkey PRIMARY KEY (id);


--
-- Name: wallet_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY wallet
    ADD CONSTRAINT wallet_pkey PRIMARY KEY (id);


--
-- Name: wallet_transaction_pkey; Type: CONSTRAINT; Schema: public; Owner: -; Tablespace: 
--

ALTER TABLE ONLY wallet_transaction
    ADD CONSTRAINT wallet_transaction_pkey PRIMARY KEY (id);


--
-- Name: alliance_id_key; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX alliance_id_key ON alliance USING btree (id);


--
-- Name: alliance_lower_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX alliance_lower_idx ON alliance USING btree (lower(name));


--
-- Name: alliance_store_alliance_id_key_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX alliance_store_alliance_id_key_idx ON alliance_store USING btree (alliance_id, key);


--
-- Name: clan_id_key; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX clan_id_key ON clan USING btree (id);


--
-- Name: clan_lower_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX clan_lower_idx ON clan USING btree (lower((name)::text));


--
-- Name: clan_store_clan_id_key_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX clan_store_clan_id_key_idx ON clan_store USING btree (clan_id, key);


--
-- Name: currency_id_key; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX currency_id_key ON currency USING btree (id);


--
-- Name: member_email_key; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX member_email_key ON member USING btree (lower((email)::text));


--
-- Name: member_handle_key; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX member_handle_key ON member USING btree (lower((handle)::text));


--
-- Name: member_id_key; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX member_id_key ON member USING btree (id);


--
-- Name: member_store_member_id_key_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX member_store_member_id_key_idx ON member_store USING btree (member_id, key);


--
-- Name: wallet_id_key; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX wallet_id_key ON wallet USING btree (id);


--
-- Name: wallet_member_id_currency_id_idx; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX wallet_member_id_currency_id_idx ON wallet USING btree (member_id, currency_id);


--
-- Name: wallet_transaction_id_key; Type: INDEX; Schema: public; Owner: -; Tablespace: 
--

CREATE UNIQUE INDEX wallet_transaction_id_key ON wallet_transaction USING btree (id);


--
-- Name: add_new_currency_to_wallets; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER add_new_currency_to_wallets AFTER INSERT ON currency FOR EACH ROW EXECUTE PROCEDURE add_new_currency_to_wallets();


--
-- Name: create_wallets; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER create_wallets AFTER INSERT ON member FOR EACH ROW EXECUTE PROCEDURE create_wallets_for_new_member();


--
-- Name: alliance_store_alliance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY alliance_store
    ADD CONSTRAINT alliance_store_alliance_id_fkey FOREIGN KEY (alliance_id) REFERENCES alliance(id);


--
-- Name: badge_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY badge
    ADD CONSTRAINT badge_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE;


--
-- Name: clan_alliance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY clan
    ADD CONSTRAINT clan_alliance_id_fkey FOREIGN KEY (alliance_id) REFERENCES alliance(id) ON DELETE SET NULL;


--
-- Name: clan_store_clan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY clan_store
    ADD CONSTRAINT clan_store_clan_id_fkey FOREIGN KEY (clan_id) REFERENCES clan(id);


--
-- Name: contacts_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY contact
    ADD CONSTRAINT contacts_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: contacts_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY contact
    ADD CONSTRAINT contacts_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES member(id);


--
-- Name: inbox_from_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY inbox
    ADD CONSTRAINT inbox_from_member_id_fkey FOREIGN KEY (from_member_id) REFERENCES member(id) ON DELETE SET NULL;


--
-- Name: inbox_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY inbox
    ADD CONSTRAINT inbox_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE;


--
-- Name: journal_from_wallet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY journal
    ADD CONSTRAINT journal_from_wallet_id_fkey FOREIGN KEY (wallet_id) REFERENCES wallet(id) ON DELETE CASCADE;


--
-- Name: journal_tx_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY journal
    ADD CONSTRAINT journal_tx_id_fkey FOREIGN KEY (tx_id) REFERENCES wallet_transaction(id) ON DELETE CASCADE;


--
-- Name: mailqueue_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY mailqueue
    ADD CONSTRAINT mailqueue_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE;


--
-- Name: member_clan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY member
    ADD CONSTRAINT member_clan_id_fkey FOREIGN KEY (clan_id) REFERENCES clan(id) ON DELETE SET NULL;


--
-- Name: member_store_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY member_store
    ADD CONSTRAINT member_store_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id);


--
-- Name: object_alliance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY object
    ADD CONSTRAINT object_alliance_id_fkey FOREIGN KEY (alliance_id) REFERENCES alliance(id) ON DELETE CASCADE;


--
-- Name: object_clan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY object
    ADD CONSTRAINT object_clan_id_fkey FOREIGN KEY (clan_id) REFERENCES clan(id) ON DELETE CASCADE;


--
-- Name: object_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY object
    ADD CONSTRAINT object_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE;


--
-- Name: password_reset_request_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY password_reset_request
    ADD CONSTRAINT password_reset_request_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE;


--
-- Name: wallet_currency_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallet
    ADD CONSTRAINT wallet_currency_id_fkey FOREIGN KEY (currency_id) REFERENCES currency(id) ON DELETE CASCADE;


--
-- Name: wallet_member_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY wallet
    ADD CONSTRAINT wallet_member_id_fkey FOREIGN KEY (member_id) REFERENCES member(id) ON DELETE CASCADE;


--
-- Name: public; Type: ACL; Schema: -; Owner: -
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

