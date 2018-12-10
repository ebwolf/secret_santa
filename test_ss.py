import pytest
import time
import pprint

from secret_santa import SecretSanta, MissingSantasKey, NotEnoughSantas

MAX_STRESS_ITERATIONS = 1000
MAX_STRESS_TIME = 1


def test_init_only_not_enough_santas():
    """Test: Input Data has enough Santas
    """
    ss = SecretSanta()
    with pytest.raises(NotEnoughSantas, message="Expecting NotEnoughSantas"):
        ss.initialize("test_data_bad_not_enough.json")


def test_init_no_santas():
    """Test: Input data does not have proper JSON key
    """
    ss = SecretSanta()
    with pytest.raises(MissingSantasKey, message="Expecting MissingSantasKey"):
        ss.initialize("test_data_bad_no_santas.json")


def test_no_self_gifting():
    """make sure a Santa doesn't get assigned to self
    """
    ss = SecretSanta()
    ss.initialize("test_data_good.json")
    ss.assign_santas_with_retry()

    for santa in ss.secret_santas.keys():
        gifted = ss.get(santa)
        assert santa != gifted

def test_no_repeats_for_three_years():
    """make sure a Santa doesn't get assigned the same Gifted over 3 year period
       Due to randomness, this will use a stress test
    """
    for stress in range(MAX_STRESS_ITERATIONS):
        # Prepare three years of Santa assignments
        ss = SecretSanta()
        ss.year = '2016'

        ss.initialize("test_data_stress.json")
        ss.assign_santas_with_retry()
        ss.secret_santas_years[ss.year] = ss.secret_santas.copy()
        ss.valid_years.append(ss.year)

        ss.year = '2017'
        ss.reassign_santas(ss.year)
        ss.secret_santas_years[ss.year] = ss.secret_santas.copy()
        ss.valid_years.append(ss.year)

        ss.year = '2018'
        ss.reassign_santas(ss.year)
        ss.secret_santas_years[ss.year] = ss.secret_santas.copy()
        ss.valid_years.append(ss.year)

        for santa in ss.secret_santas.keys():
            ss.year = '2016'
            gifted_2016 = ss.get(santa)
            ss.year = '2017'
            gifted_2017 = ss.get(santa)
            ss.year = '2018'
            gifted_2018 = ss.get(santa)

            assert gifted_2016 != gifted_2017
            assert gifted_2017 != gifted_2018
            assert gifted_2016 != gifted_2018

    print("Completed {} iterations successfully.".format(stress))


def test_load_save():
    """Test initializing, saving, and reloading
    """
    ss1 = SecretSanta()
    ss1.initialize("test_data_good.json")
    ss1.assign_santas_with_retry()
    ss1.save()

    ss2 = SecretSanta()
    ss2.load()

    # Make sure the Secret Santas have persisted
    for santa in ss2.secret_santas:
        assert(ss1.get(santa) == ss2.get(santa))


def test_stress_santa_assignments():
    """Stress test the santa assignments
        - Can we run the assignments operation 10000 times in 1 second?
    """
    ss = SecretSanta()
    ss.year = 2017
    ss.initialize("test_data_stress.json")

    start = time.time()

    # 1000 iterations
    for stress in range(MAX_STRESS_ITERATIONS):
        ss.assign_santas_with_retry()

    end = time.time()

    assert(stress == MAX_STRESS_ITERATIONS-1)

    assert(end - start < MAX_STRESS_TIME)

    ss.year = 2018

    start = time.time()

    # 1000 iterations
    for stress in range(MAX_STRESS_ITERATIONS):
        ss.assign_santas_with_retry()

    end = time.time()

    assert(stress == MAX_STRESS_ITERATIONS-1)

    assert(end - start < MAX_STRESS_TIME)

    ss.year = 2019

    start = time.time()

    # 1000 iterations
    for stress in range(MAX_STRESS_ITERATIONS):
        ss.assign_santas_with_retry()

    end = time.time()

    assert(stress == MAX_STRESS_ITERATIONS-1)

    assert(end - start < MAX_STRESS_TIME)

