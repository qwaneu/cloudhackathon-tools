from dataclasses import dataclass
from typing import Any, List
import sqlite3
import os

class Board:
    def __init__(self, team: str, sources:List[Any]=[]):
        self._team = team
        self._sources = sources
        
    def score(self):
        return sum([source.score(self._team) for source in self._sources])

    def show(self):
        print("score for {team}; total of {score}".format(team=self._team, score=self.score()))
        for source in self._sources:
            source.show(self._team)

class ContainerSource:
    def __init__(self, max_containers, container_services):
        self._max_containers = max_containers
        self._container_services = container_services

    def score(self, team):
        return (self._max_containers - self._container_services.count(team)) * 2
            
    def show(self, team):
        print("Containers still running: {containers}; score: {score}".format(containers=self._container_services.count(team), score=self.score(team)))


class EndToEndTestSource:
    def __init__(self, test_failures):
        self._test_failures = test_failures
        
    def score(self, team):
        return -self._test_failures.count(team)

    def show(self, team):
        print("End to end failures: {failures}; score: {score}".format(failures=self._test_failures.count(team), score=self.score(team)))


class DiversitySource:
    def __init__(self, service_diversity):
        self._service_diversity = service_diversity
        
    def score(self, team):
        return self._service_diversity.size(team) * 2

    def show(self, team):
        print("Diversity of services: {diversity}; score: {score}".format(diversity=self._service_diversity.size(team), score=self.score(team)))

class ServiceDiversity:
    def __init__(self, diversity):
        self._diversity = diversity
        
    def increase(self, team):
        self._diversity.save_size(team, self._diversity.size(team) + 1);

    def size(self, team):
        return self._diversity.size(team)


class Failures:
    def __init__(self, test_failures):
        self._test_failures = test_failures
        
    def increase(self, team):
        self._test_failures.save(team, self._test_failures.count(team) + 1);

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
@click.group()
def cli():
    pass

@cli.command()
def show():
    db = SQLDatabase.open("scores.db")
    Board("waes-lion",[
        ContainerSource(5, SQLiteBasedContainerServices.create(db)),
        EndToEndTestSource(Failures(SQLiteBasedTestFailures.create(db))),
        DiversitySource(ServiceDiversity(SQLiteBasedServiceDiversity.create(db)))
    ]).show()

@cli.command()
@click.argument('team')
@click.argument('containers_still_alive')
def containers(team, containers_still_alive):
    db = SQLDatabase.open("scores.db")
    cs = SQLiteBasedContainerServices.create(db)
    cs.save_count(team,containers_still_alive)        

import subprocess, time
@cli.command()
@click.argument('teams', nargs=-1)
def monitor_containers(teams):
    db = SQLDatabase.open("scores.db")
    cs = SQLiteBasedContainerServices.create(db)
    while True:
        subprocess.call('clear')
        for team in teams:
            containers = subprocess.check_output(f"ssh {team} docker ps --format '{{{{.Names}}}}'", shell=True).decode('utf-8').strip().split("\n")
            print(f"{len(containers)} containers running for {team}:")
            for container in containers:
                print(f"\t{container}")
            cs.save_count(team, len(containers))       
        time.sleep(5) 
        




if __name__ == "__main__":
    cli()
