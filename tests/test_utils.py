from mxl2xlsx import utils


def test_absolute2relative():
    assert utils.absolute2relative(0, 'C', 0, 2) == 'Z'
    assert utils.absolute2relative(0, 'C', 0, 4) == 'q'
    assert utils.absolute2relative(0, 'D', 0, 4) == 'w'
    assert utils.absolute2relative(0, 'D', 1, 4) == '3'
    assert utils.absolute2relative(0, 'B', -1, 4) == '7'
    assert utils.absolute2relative(-5, 'C', 0, 4) == 'm'
    assert utils.absolute2relative(1, 'C', 0, 4) == 'r'
    assert utils.absolute2relative(-1, 'E', 0, 2) == 'M'
