from dataclasses import dataclass
from re import A
import pytest
from hamcrest import *
from scoreboard import *


class Test_scoreboard:
    def test_has_score_total_score_of_0_initially(self):
        board = Board("Team1")
        assert_that(board.score(), equal_to(0))

    def test_counts_scores_from_all_score_components(self):
        board = Board("Team1", [DummyScoreSource("Team1", 1), DummyScoreSource("Team1", 2)])
        assert_that(board.score(), equal_to(3))


class Test_ContainerSource:
    def test_is_nul_initially(self):
        source = ContainerSource(max_containers=5, container_services = self)
        self.container_count = 5
        assert_that(source.score("some_team"), equal_to(0))

    def test_is_max_containers_minus_the_number_of_container_services_times_2(self):
        source = ContainerSource(max_containers=5, container_services = self)
        self.container_count = 3
        assert_that(source.score("some_team"), equal_to(4))

    def count(self, team):
        return self.container_count


class Test_EndToEndTestSource:
    def test_is_0_initially(self):
        source = EndToEndTestSource(test_failures = DummyTestFailures("some_team", 0))
        assert_that(source.score("some_team"), equal_to(0))

    def test_is_the_negative_value_of_the_test_failures(self):
        source = EndToEndTestSource(test_failures = DummyTestFailures("some_team", 2))
        assert_that(source.score("some_team"), equal_to(-2))


class Test_DiversityScore:
    def test_is_0_initially(self):
        source = DiversitySource(service_diversity = DummyServiceDiversity("some_team", 0))
        assert_that(source.score("some_team"), equal_to(0))

    def test_is_twice_the_diversity_size(self):
        source = DiversitySource(service_diversity = DummyServiceDiversity("some_team", 3))
        assert_that(source.score("some_team"), equal_to(6))


class SQLiteTests:
    @pytest.fixture(autouse=True)
    def setup(self):
        self._db = SQLDatabase.create("tests/db/test_db.sqlite")


class TestSQLiteBasedContainerServices(SQLiteTests):

    def test_is_0_initially(self):
        container_services = SQLiteBasedContainerServices.create(self._db)
        assert_that(container_services.count("some_team"), equal_to(0))

    def test_is_the_number_of_services_stored(self):
        container_services = SQLiteBasedContainerServices.create(self._db)
        container_services.save_count("some_team", 3)
        assert_that(container_services.count("some_team"), equal_to(3))

    def test_stored_number_is_of_that_team(self):
        container_services = SQLiteBasedContainerServices.create(self._db)
        container_services.save_count("some_team", 3)
        assert_that(container_services.count("other_team"), equal_to(0))


class TestSQLiteBasedServiceDiversity(SQLiteTests):
        
    def test_is_0_initially(self):
        container_services = ServiceDiversity(SQLiteBasedServiceDiversity.create(self._db))
        assert_that(container_services.size("some_team"), equal_to(0))

    def test_inccrease_increases_the_diversity(self):
        container_services = ServiceDiversity(SQLiteBasedServiceDiversity.create(self._db))
        container_services.increase("some_team")
        container_services.increase("some_team")
        assert_that(container_services.size("some_team"), equal_to(2))

    def test_inccreases_for_specific_team(self):
        container_services = ServiceDiversity(SQLiteBasedServiceDiversity.create(self._db))
        container_services.increase("some_team")
        container_services.increase("other_team")
        assert_that(container_services.size("some_team"), equal_to(1))


class TestSQLiteBasedTestFailures(SQLiteTests):

    def test_is_0_initially(self):
        container_services = Failures(SQLiteBasedTestFailures.create(self._db))
        assert_that(container_services.count("some_team"), equal_to(0))

    def test_increase_increases_the_number_of_failures(self):
        container_services = Failures(SQLiteBasedTestFailures.create(self._db))
        container_services.increase("some_team")
        container_services.increase("some_team")
        assert_that(container_services.count("some_team"), equal_to(2))

    def test_inccreases_for_specific_team(self):
        container_services = Failures(SQLiteBasedTestFailures.create(self._db))
        container_services.increase("some_team")
        container_services.increase("other_team")
        assert_that(container_services.count("some_team"), equal_to(1))



@dataclass
class DummyServiceDiversity:
    _team: str
    _diversity: int
    def size(self, team):
        if self._team != team: return -1
        return self._diversity

@dataclass
class DummyTestFailures:
    _team: str
    _failures: int
    def count(self, team):
        if self._team != team: return -1
        return self._failures

@dataclass
class DummyScoreSource:
    _team: str
    _score: int
    def score(self, team):
        if self._team != team: return -1
        return self._score
