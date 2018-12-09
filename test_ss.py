import pytest
import time
from secret_santa import SecretSanta, MissingSantasKey, NotEnoughSantas


def test_init_only_one_santa():
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
    STRESS_ITERATIONS = 10000
    STRESS_MAX_TIME = 1
    ss = SecretSanta()
    ss.initialize("test_data_stress.json")

    start = time.time()

    # 1000 iterations
    for stress in range(STRESS_ITERATIONS):
        ss.assign_santas_with_retry()

    end = time.time()

    assert(stress == STRESS_ITERATIONS-1)

    assert(end - start < STRESS_MAX_TIME)

