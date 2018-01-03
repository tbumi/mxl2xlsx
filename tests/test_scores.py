from pathlib import Path

from click.testing import CliRunner

from mxl2xlsx.convert import main


def test_scores():
    runner = CliRunner()
    for score in Path('test_scores/').iterdir():
        if score.match('*.xml'):
            test_file = score.with_suffix('.test.xlsx')
            result = runner.invoke(main, [str(score), str(test_file)])

            assert result.exit_code == 0
            assert result.exception is None
            # TODO compare contents of test_file and score.with_suffix('.xlsx')


if __name__ == '__main__':
    test_scores()
