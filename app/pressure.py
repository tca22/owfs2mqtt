def calculate_pressure(vad, min_vad=0.5, span_bar_at_4v=150, bar_to_psi=0.0689476,
                      max_vad=4.5, accuracy_divisor=200):
    vad = float(vad)
    if vad >= max_vad:
        return None, None
    pressure = (vad - min_vad) * span_bar_at_4v / 4.0 * bar_to_psi
    accuracy = pressure / accuracy_divisor
    return round(pressure, 2), round(accuracy, 2)
