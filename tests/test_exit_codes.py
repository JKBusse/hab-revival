from hba import exit_codes


def test_exit_code_table_matches_the_spec():
    assert (exit_codes.EXIT_OK, exit_codes.EXIT_ERROR, exit_codes.EXIT_CONFIG,
            exit_codes.EXIT_NO_GPU, exit_codes.EXIT_WATCHDOG) == (0, 1, 2, 3, 4)


def test_every_code_has_a_reason_for_the_log():
    for code in range(5):
        assert exit_codes.REASONS[code]
