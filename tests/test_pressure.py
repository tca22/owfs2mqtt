from app.pressure import calculate_pressure

def test_pressure_matches_fhem_formula():
    pressure, accuracy = calculate_pressure(1.31)
    expected = (1.31 - 0.5) * 150 / 4 * 0.0689476
    assert pressure == round(expected, 2)
    assert accuracy == round(expected / 200, 2)

def test_pressure_limit():
    assert calculate_pressure(4.5) == (None, None)
