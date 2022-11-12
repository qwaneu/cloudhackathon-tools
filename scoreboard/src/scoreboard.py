from dataclasses import dataclass
from socket import socket
from typing import Any, List
import sqlite3
import os



class Board:
    def __init__(self, teams:List[str], sources:List[Any]=[]):
        self._teams = teams
        self._sources = sources
        
    def score(self, team):
        return sum([source.score(team) for source in self._sources])

    def show(self):
        print("Scoreboard\n")
        
        print(self._teams_string())
        print("")
        for source in self._sources:
            print(self._source_string(source))

    def _teams_string(self):
        return "".join([f"{team:<22}{self.score(team):<5}" for team in self._teams])

    def _source_string(self, source):
        return "".join([f"{source.label(team):<22}{source.score(team):<5}" for team in self._teams])

class ContainerSource:
    def __init__(self, max_containers, container_services):
        self._max_containers = max_containers
        self._container_services = container_services

    def score(self, team):
        return (self._max_containers - self._container_services.count(team)) * 2
            
    def label(self, team):
        return f"{'Containers:':<15}{self._container_services.count(team):>3} |"


class EndToEndTestSource:
    def __init__(self, test_failures):
        self._test_failures = test_failures
        
    def score(self, team):
        return -self._test_failures.count(team)

    def label(self, team):
        return f"{'Test failures:':<15}{self._test_failures.count(team):>3} |"


class DiversitySource:
    def __init__(self, service_diversity):
        self._service_diversity = service_diversity
        
    def score(self, team):
        return self._service_diversity.size(team) * 2

    def label(self, team):
        return f"{'Diversity:':<15}{self._service_diversity.size(team):>3} |"

class ServiceDiversity:
    def __init__(self, diversity):
        self._diversity = diversity
        
    def increase(self, team):
        self._diversity.save_size(team, self._diversity.size(team) + 1);

    def decrease(self, team):
        self._diversity.save_size(team, self._diversity.size(team) - 1);

    def size(self, team):
        return self._diversity.size(team)


class Failures:
    def __init__(self, test_failures):
        self._test_failures = test_failures
        
    def increase(self, team):
        self._test_failures.save(team, self._test_failures.count(team) + 1);

    def decrease(self, team):
        self._test_failures.save(team, self._test_failures.count(team) - 1);

    def count(self, team):
        return self._test_failures.count(team)


class SQLiteBasedContainerServices:
    @staticmethod
    def create(database):
        return SQLiteBasedContainerServices(database)._init_table()

    def __init__(self, database):
        self._db = database

    def _init_table(self):
        self._db.executescript("create table if not exists container_service_counts(team varchar(40) primary key, count int not null);")
        return self

    def save_count(self, team, count):
        if self._fetch_counts(team) is None:
            self._db.execute("insert into container_service_counts(team, count) values('{team}',{count});".format(team=team,count=0))
        self._db.execute("update container_service_counts set count={count} where team='{team}'".format(team=team, count=count))
        self._db.commit()

    def count(self, team):
        result = self._fetch_counts(team)
        return result and result[0] or 0

    def _fetch_counts(self, team):
        return self._db.execute("SELECT count FROM container_service_counts where team = '{team}';".format(team=team)).fetchone()

class SQLiteBasedServiceDiversity:
    @staticmethod
    def create(database):
        return SQLiteBasedServiceDiversity(database)._init_table()

    def __init__(self, database):
        self._db = database

    def _init_table(self):
        self._db.executescript("create table if not exists service_diversity_sizes(team varchar(40) primary key, size int not null);")
        return self

    def save_size(self, team, size):
        if self._fetch_sizes(team) is None:
            self._db.execute("insert into service_diversity_sizes(team, size) values('{team}',0);".format(team=team))
        self._db.execute("update service_diversity_sizes set size={size} where team='{team}'".format(team=team, size=size))
        self._db.commit()


    def size(self, team):
        result = self._fetch_sizes(team)
        return result and result[0] or 0

    def _fetch_sizes(self, team):
        return self._db.execute("SELECT size FROM service_diversity_sizes where team='{team}';".format(team=team)).fetchone()

class SQLiteBasedTestFailures:
    @staticmethod
    def create(database):
        return SQLiteBasedTestFailures(database)._init_table()

    def __init__(self, database):
        self._db = database

    def _init_table(self):
        self._db.executescript("create table if not exists failure_counts(team varchar(40) primary key, count int not null);")
        return self

    def save(self, team, count):
        if self._fetch_failures(team) is None:
            self._db.execute("insert into failure_counts(team, count) values('{team}',0);".format(team=team))
        self._db.execute("update failure_counts set count={count} where team='{team}'".format(team=team, count=count))
        self._db.commit()


    def count(self, team):
        result = self._fetch_failures(team)
        return result and result[0] or 0
    
    def _fetch_failures(self, team):
        return self._db.execute("SELECT count FROM failure_counts where team='{team}';".format(team=team)).fetchone()

class SQLDatabase:
    @staticmethod
    def create(path):
        if os.path.exists(path): 
            os.remove(path)
        return SQLDatabase.open(path)
    @staticmethod
    def open(path):
        return SQLDatabase(sqlite3.connect(path))

    def __init__(self, db):
        self._db = db
        
    def executescript(self, *args):
        return self._db.executescript(*args)

    def execute(self, *args):
        return self._db.execute(*args)

    def commit(self):
        return self._db.commit()

import click
import subprocess, time

@click.group()
def cli():
    pass

@cli.command()
@click.argument('teams', nargs=-1)
def show(teams):
    db = SQLDatabase.open("scores.db")
    sources = [
        ContainerSource(5, SQLiteBasedContainerServices.create(db)),
        EndToEndTestSource(Failures(SQLiteBasedTestFailures.create(db))),
        DiversitySource(ServiceDiversity(SQLiteBasedServiceDiversity.create(db)))
    ]

    boards = Board(teams,sources)
    boards.show()

@cli.command()
@click.argument('team')
@click.argument('containers_still_alive')
def containers(team, containers_still_alive):
    db = SQLDatabase.open("scores.db")
    cs = SQLiteBasedContainerServices.create(db)
    cs.save_count(team,containers_still_alive)        

@cli.command()
@click.argument('teams', nargs=-1)
def monitor_containers(teams):
    db = SQLDatabase.open("scores.db")
    cs = SQLiteBasedContainerServices.create(db)
    while True:
        subprocess.call('clear')
        for team in teams:
            containers = remove_empty_values(subprocess.check_output(f"ssh {team} docker ps --format '{{{{.Names}}}}'", shell=True).decode('utf-8').strip().split("\n"))
            print(f"{len(containers)} containers running for {team}:")
            for container in containers:
                print(f"\t{container}")
            cs.save_count(team, len(containers))       
        time.sleep(5) 
        

def remove_empty_values(list):
    return [ e for e in list if len(e) != 0]


@cli.command()
@click.argument('team')
def increase_diversity(team):
    db = SQLDatabase.open("scores.db")
    sdiv = ServiceDiversity(SQLiteBasedServiceDiversity.create(db))
    sdiv.increase(team)
    

@cli.command()
@click.argument('team')
def decrease_diversity(team):
    db = SQLDatabase.open("scores.db")
    sdiv = ServiceDiversity(SQLiteBasedServiceDiversity.create(db))
    sdiv.decrease(team)

@cli.command()
@click.argument('team')
def add_failure(team):
    _add_failure(team)
def _add_failure(team):
    db = SQLDatabase.open("scores.db")
    failures = Failures(SQLiteBasedTestFailures.create(db))
    failures.increase(team)
    

@cli.command()
@click.argument('team')
def remove_failure(team):
    db = SQLDatabase.open("scores.db")
    failures = Failures(SQLiteBasedTestFailures.create(db))
    failures.decrease(team)

import socketio
from threading import Thread
import requests
import json
class ResultPoller:
    def __init__(self, team, client):
        self._client = client
        self._team = team
        self._last_received = dict(a=0,b=0)
        self._last_probed = dict(a=0,b=0)

    def run(self):
        @self._client.on('scores')
        def on_scoes(data):
            self._last_received = json.loads(data)

        def connect_to_server():
            self._client.connect(self._url, transports=['polling'])

        self._thread = Thread(target=connect_to_server)
        self._thread.start()
        return self

    def capture_current(self, vote):
        self._last_probed = self._last_received.clone()

    def wait_for_vote(self, vote):
        interval = 0.10
        total_time = 0

        while total_time < 3:
            if self._last_received[vote] > self._last_probed[vote]:
                print(f"vote '{vote}' found")
                self._last_probed = self._last_received.copy()
                return True
            print(".", end='', flush=True)
            time.sleep(interval)
            total_time+=interval

        print('F')
        print(f"vote '{vote}' not found")
        return False

    def stop(self):
        self._client.disconnect()

    def wait(self):
        self._thread.join()

    @property
    def _url(self):
        return f"http://{self._team}.westeurope.cloudapp.azure.com:5001"


@cli.command()
@click.argument('team')
def smoke_test(team):
    result_poller = ResultPoller(team, socketio.Client()).run()
    time.sleep(1)
    print(result_poller._last_probed, result_poller._last_received['b']) 

    if not vote(team, 'a') or not result_poller.wait_for_vote("a"):
        _add_failure(team)
        result_poller.stop()
        result_poller.wait()
        return
    if not vote(team, 'b') or not result_poller.wait_for_vote("b"):
        _add_failure(team)
    result_poller.stop()
    result_poller.wait()
    

def vote(team, v):
    try:
        requests.post(f"http://{team}.westeurope.cloudapp.azure.com:5000", cookies={"voter_id": "42"}, data={"vote":v})
        return True
    except ConnectionError as e:
        print(f"Cannot vote {e}")
        return False
    except Exception as e:
        print(f"Cannot vote {e}")
        return False


if __name__ == "__main__":
    cli()
