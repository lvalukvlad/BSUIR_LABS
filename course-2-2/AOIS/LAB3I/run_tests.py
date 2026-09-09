import unittest
import coverage
import os

if __name__ == '__main__':
    os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))

    cov = coverage.Coverage()
    cov.start()

    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    cov.stop()
    cov.save()
    cov.report()
    cov.html_report(directory='coverage_report')

    # Возвращаем код выхода (0 если все тесты прошли)
    exit(0 if result.wasSuccessful() else 1)