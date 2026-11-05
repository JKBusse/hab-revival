from hba.decision import DecisionState, decide, initial_state
from hba.ports import Box

CONF = 0.4


def car(top=250, width=80, conf=0.9):
    return Box(x1=100, y1=top, x2=100 + width, y2=top + 50, cls=1, conf=conf)


def irrelevant(conf=0.9):
    return car(top=100, conf=conf)  # obere Kante zu hoch


def step(state, boxes, t):
    """Ein Frame zur Sekunde t (Detektion und Status in derselben Sekunde)."""
    return decide(state, boxes, t, t, CONF)


# --- Abgeblendet beim Start -------------------------------------------------

def test_start_without_vehicle_stays_dimmed_for_three_seconds():
    state = initial_state(100)
    statuses = []
    for t in (100, 101, 102, 103, 104):
        state, status = step(state, [], t)
        statuses.append(status)
    assert statuses == [0, 0, 0, 1, 1]


# --- Sofortiges Abblenden ---------------------------------------------------

def test_oncoming_traffic_dims_in_the_same_frame():
    state = DecisionState(last_detect=100, last_frame_with_boxes=0)
    _, status = step(state, [], 200)
    assert status == 1
    _, status = step(state, [car()], 200)
    assert status == 0


# --- Verzögertes Aufblenden -------------------------------------------------

def test_vehicle_disappears_status_returns_after_three_seconds():
    state, status = step(initial_state(0), [car()], 200)
    assert status == 0
    state, status = step(state, [], 202)
    assert status == 0  # vor 2 Sekunden erkannt
    state, status = step(state, [], 203)
    assert status == 1  # vor 3 Sekunden erkannt: frei


def test_single_missed_frame_keeps_status_dimmed():
    state, _ = step(initial_state(0), [car()], 200)
    state, status = step(state, [], 201)  # Fahrzeug in diesem Frame nicht erkannt
    assert status == 0


# --- Aktualisierung höchstens einmal pro Sekunde ----------------------------

def test_continuous_detection_updates_about_once_per_second_and_stays_dimmed():
    state = initial_state(0)
    updates, statuses = [], []
    for t in (200, 200, 200, 201, 201, 202, 202, 203):
        state, status = step(state, [car()], t)
        updates.append(state.last_detect)
        statuses.append(status)
    assert updates == [200, 200, 200, 201, 201, 202, 202, 203]
    assert set(statuses) == {0}


def test_throttle_blocks_a_second_update_in_the_same_second():
    # Ein Frame mit Box in Sekunde 200 setzt die Drossel. Ein weiterer relevanter Frame
    # in derselben Sekunde aktualisiert den Zeitpunkt nicht.
    state, _ = step(initial_state(0), [irrelevant()], 200)
    assert state.last_frame_with_boxes == 200
    state, _ = step(state, [car()], 200)
    assert state.last_detect == 0  # unverändert (Legacy-Eigenheit: Drossel unabhängig von Relevanz)


# --- Legacy-Eigenheiten (werden in multi-box-decision geändert) -------------

def test_legacy_second_vehicle_relevant_first_not_does_not_update():
    """Zweites Fahrzeug relevant, erstes nicht: Zeitpunkt wird NICHT aktualisiert."""
    state = DecisionState(last_detect=100, last_frame_with_boxes=0)
    state, status = step(state, [irrelevant(), car()], 200)
    assert state.last_detect == 100
    assert status == 1  # Fernlicht trotz sichtbarem Gegenverkehr freigegeben


def test_legacy_confidence_is_taken_from_the_last_box():
    state = DecisionState(last_detect=100, last_frame_with_boxes=0)
    low_last = [car(conf=0.9), car(conf=0.3)]
    state, _ = step(state, low_last, 200)
    assert state.last_detect == 100  # letzte Box unter der Schwelle
    state2, _ = step(DecisionState(100, 0), [car(conf=0.3), car(conf=0.9)], 200)
    assert state2.last_detect == 200  # letzte Box über der Schwelle


def test_separate_seconds_for_detection_and_status():
    # Detektion bei Sekunde 200, Status bei 203: liegt genau 3 s dahinter, also frei.
    _, status = decide(DecisionState(100, 0), [car()], 200, 203, CONF)
    assert status == 1


def test_decide_does_not_mutate_state():
    state = DecisionState(100, 0)
    decide(state, [car()], 200, 200, CONF)
    assert state == DecisionState(100, 0)
