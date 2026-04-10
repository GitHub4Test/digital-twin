from apps.frontend.app.src.twin_model import predict_next


def test_predict_next_short_list():
    # with fewer than 3 values function returns last value
    assert predict_next([10]) == 10
    assert predict_next([1, 2]) == 2


def test_predict_next_linear_trend():
    # linear sequence should predict the next value (1,2,3) -> 4
    pred = predict_next([1, 2, 3])
    assert isinstance(pred, (int, float))
    assert round(pred, 2) == 4.00
