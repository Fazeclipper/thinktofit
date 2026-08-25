from routes import calculate_bmi


def test_bmi_healthy_weight():
    bmi, category = calculate_bmi(70, 175)
    assert 22 < bmi < 23
    assert category == 'Healthy weight'


def test_bmi_underweight():
    _, category = calculate_bmi(45, 175)
    assert category == 'Underweight'


def test_bmi_overweight():
    _, category = calculate_bmi(85, 175)
    assert category == 'Overweight'


def test_bmi_obesity():
    _, category = calculate_bmi(110, 175)
    assert category == 'Obesity'
